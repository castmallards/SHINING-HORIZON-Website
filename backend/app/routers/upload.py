"""Image upload endpoint (Phase 3.4).

Delegates persistence + variant generation to ``services.image.process_upload``.
The DB stores the returned ``base_path`` (extension-less, folder-prefixed);
templates pick a size via the ``variant`` filter.
"""
from __future__ import annotations

import glob
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..config import settings
from ..models.user import User
from ..services.auth import get_current_user
from ..services.image import (
    ALLOWED_EXTS,
    VALID_FOLDERS,
    ImageProcessingError,
    process_upload,
)


router = APIRouter(prefix="/upload", tags=["Upload"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB — keep aligned with services/image limits


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
