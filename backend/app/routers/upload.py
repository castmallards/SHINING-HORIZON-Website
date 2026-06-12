"""Image upload endpoint (Phase 3.4).

Delegates persistence + variant generation to ``services.image.process_upload``.
The DB stores the returned ``base_path`` (extension-less, folder-prefixed);
templates pick a size via the ``variant`` filter.
"""
from __future__ import annotations

import glob
import os
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, HttpUrl

from ..config import settings
from ..models.user import User
from ..services.auth import get_current_user
from ..services.document import (
    ALLOWED_DOCUMENT_EXTS,
    MAX_DOCUMENT_SIZE,
    VALID_DOCUMENT_FOLDERS,
    DocumentProcessingError,
    process_document_upload,
)
from ..services.image import (
    ALLOWED_EXTS,
    VALID_FOLDERS,
    ImageProcessingError,
    process_upload,
)


router = APIRouter(prefix="/upload", tags=["Upload"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB — keep aligned with services/image limits

_BLOCKED_HOST = re.compile(
    r"^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)",
    re.I,
)

_EXT_BY_MIME = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "image/avif": "avif",
}


class ImageFromUrlBody(BaseModel):
    url: HttpUrl = Field(..., description="Public http(s) image URL")


def _filename_from_url(url: str, content_type: str) -> str:
    path = urlparse(str(url)).path
    name = os.path.basename(path) if path else ""
    if name and "." in name:
        ext = name.rsplit(".", 1)[-1].lower()
        if ext in ALLOWED_EXTS:
            return name
    ext = _EXT_BY_MIME.get(content_type.split(";")[0].strip().lower(), "jpg")
    return f"imported.{ext}"


def _fetch_image_from_url(url: str) -> tuple[bytes, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http(s) URLs are allowed")

    host = (parsed.hostname or "").lower()
    if not host or host == "localhost" or _BLOCKED_HOST.match(host):
        raise HTTPException(status_code=400, detail="URL host is not allowed")

    request = Request(
        url,
        headers={"User-Agent": "ShiningHorizon-Admin/1.0 (image import)"},
    )
    def _bytes_look_like_image(data: bytes) -> bool:
        if data.startswith(b"\xff\xd8\xff"):
            return True
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        if data[:6] in (b"GIF87a", b"GIF89a"):
            return True
        if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WEBP":
            return True
        if data.lstrip().startswith((b"<svg", b"<?xml")):
            return True
        return False

    try:
        with urlopen(request, timeout=20) as response:
            content_type = (response.headers.get("Content-Type") or "").lower()
            data = response.read(MAX_FILE_SIZE + 1)
            if not content_type.startswith("image/"):
                if not _bytes_look_like_image(data):
                    raise HTTPException(
                        status_code=400,
                        detail=f"URL did not return an image (got {content_type or 'unknown'})",
                    )
                content_type = "image/jpeg"
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not download image: {exc}",
        ) from exc

    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Max size: 5MB")
    if not data:
        raise HTTPException(status_code=400, detail="Downloaded image is empty")

    return data, _filename_from_url(url, content_type)


@router.post("/image/{folder}")
async def upload_image(
    folder: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if folder not in VALID_FOLDERS:
        raise HTTPException(status_code=400, detail=f"Invalid folder. Must be one of: {list(VALID_FOLDERS)}")

    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing an extension")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {sorted(ALLOWED_EXTS)}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size: 5MB")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        stored = process_upload(folder, file.filename, content)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # The DB stores ``stored.base_path`` (e.g. "uploads/products/<id>"). Templates
    # call ``image | variant('card')`` to pick the right WebP size.
    return {
        "path": stored.base_path,
        "url": stored.original_url,
        "is_svg": stored.is_svg,
    }


@router.post("/image-from-url/{folder}")
async def upload_image_from_url(
    folder: str,
    body: ImageFromUrlBody,
    current_user: User = Depends(get_current_user),
):
    """Import an image from a public URL (e.g. dragged from Google Images)."""
    if folder not in VALID_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder. Must be one of: {list(VALID_FOLDERS)}",
        )

    url = str(body.url)
    content, filename = _fetch_image_from_url(url)

    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {sorted(ALLOWED_EXTS)}",
        )

    try:
        stored = process_upload(folder, filename, content)
    except ImageProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "path": stored.base_path,
        "url": stored.original_url,
        "is_svg": stored.is_svg,
    }


@router.post("/document/{folder}")
async def upload_document(
    folder: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF datasheet. Stored path is suitable for ``product.datasheet_url``."""
    if folder not in VALID_DOCUMENT_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder. Must be one of: {sorted(VALID_DOCUMENT_FOLDERS)}",
        )

    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing an extension")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {sorted(ALLOWED_DOCUMENT_EXTS)}",
        )

    content = await file.read()
    if len(content) > MAX_DOCUMENT_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size: 20MB")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        stored = process_document_upload(folder, file.filename, content)
    except DocumentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"path": stored.path, "url": stored.url}


@router.delete("/document")
async def delete_document(
    path: str,
    current_user: User = Depends(get_current_user),
):
    """Remove an uploaded PDF from disk."""
    normalised = path.strip().removeprefix("/").removeprefix("backend/")
    parts = normalised.split("/")
    if (
        len(parts) < 4
        or parts[0] != "uploads"
        or parts[1] not in VALID_DOCUMENT_FOLDERS
        or parts[2] != "documents"
    ):
        raise HTTPException(status_code=400, detail="Invalid path")

    filename = parts[-1]
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid path")

    abs_path = os.path.join(settings.UPLOAD_DIR, *parts[1:])
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail="Document not found")

    os.remove(abs_path)
    return {"message": "Document deleted successfully"}


@router.delete("/image")
async def delete_image(
    path: str,
    current_user: User = Depends(get_current_user),
):
    """Remove an image and any generated variants.

    Accepts either a v2 base path (``uploads/{folder}/{id}``) or a legacy
    full path (``backend/uploads/...``).
    """
    normalised = path.strip().removeprefix("/").removeprefix("backend/")

    parts = normalised.split("/")
    if len(parts) < 3 or parts[0] != "uploads" or parts[1] not in VALID_FOLDERS:
        raise HTTPException(status_code=400, detail="Invalid path")

    folder = parts[1]
    folder_dir = os.path.join(settings.UPLOAD_DIR, folder)
    asset = parts[-1]
    image_id = asset.split(".", 1)[0]

    removed: list[str] = []

    # Variant WebPs
    for variant_name in ("thumb", "card", "hero"):
        candidate = os.path.join(folder_dir, variant_name, f"{image_id}.webp")
        if os.path.exists(candidate):
            os.remove(candidate)
            removed.append(candidate)

    # Original (raster lives under originals/, vector lives at the folder root)
    for candidate in glob.glob(os.path.join(folder_dir, "originals", f"{image_id}.*")):
        os.remove(candidate)
        removed.append(candidate)
    for candidate in glob.glob(os.path.join(folder_dir, f"{image_id}.*")):
        os.remove(candidate)
        removed.append(candidate)

    # Legacy: pre-v2 records stored the file directly at uploads/{folder}/{filename}
    if "." in asset:
        legacy = os.path.join(folder_dir, asset)
        if os.path.exists(legacy):
            os.remove(legacy)
            removed.append(legacy)

    if not removed:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully", "removed": len(removed)}
