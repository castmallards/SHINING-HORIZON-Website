"""Image variant pipeline (Phase 3.3, 3.5, 3.6).

Per ARCHITECTURE.md §6 every uploaded raster image is normalised to three
WebP variants stored alongside the original:

    backend/uploads/{folder}/originals/{uuid}.{ext}      # untouched source
    backend/uploads/{folder}/thumb/{uuid}.webp           # 300x300, q=80
    backend/uploads/{folder}/card/{uuid}.webp            # 600x600, q=85
    backend/uploads/{folder}/hero/{uuid}.webp            # 1600x900, q=85

Database stores the **base path** ``uploads/{folder}/{uuid}`` (no extension).
Templates pick the variant they need via the Jinja2 ``variant`` filter.

SVGs bypass variant generation: they are stored once at
``uploads/{folder}/{uuid}.svg`` and the ``variant`` filter returns the same
URL regardless of size.
"""
from __future__ import annotations

import io
import os
import uuid
from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageOps, UnidentifiedImageError

from ..config import settings


# ─── Variant definitions ──────────────────────────────────────────────

@dataclass(frozen=True)
class Variant:
    name: str
    max_width: int
    max_height: int
    quality: int


VARIANTS: tuple[Variant, ...] = (
    Variant("thumb", 300, 300, 80),
    Variant("card", 600, 600, 85),
    Variant("hero", 1600, 900, 85),
)
VARIANT_NAMES = {v.name for v in VARIANTS}

ALLOWED_RASTER_EXTS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_VECTOR_EXTS = {"svg"}
ALLOWED_EXTS = ALLOWED_RASTER_EXTS | ALLOWED_VECTOR_EXTS

VALID_FOLDERS = ("products", "categories", "brands", "subcategories")


class ImageProcessingError(Exception):
    """Raised when an upload payload cannot be turned into the standard variants."""


# ─── Public API ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class StoredImage:
    """Result of `process_upload`. ``base_path`` is what the caller stores in DB."""

    base_path: str            # e.g. "uploads/products/abcd1234"
    original_url: str         # e.g. "/uploads/products/originals/abcd1234.png"
    is_svg: bool


def process_upload(folder: str, filename: str, content: bytes) -> StoredImage:
    """Persist an uploaded image (and variants for raster sources) to disk."""
    if folder not in VALID_FOLDERS:
        raise ImageProcessingError(f"Invalid folder '{folder}'. Expected one of {VALID_FOLDERS}.")

    ext = _safe_ext(filename)
    if ext not in ALLOWED_EXTS:
        raise ImageProcessingError(f"Unsupported extension '.{ext}'. Allowed: {sorted(ALLOWED_EXTS)}.")

    image_id = uuid.uuid4().hex
    base_dir = os.path.join(settings.UPLOAD_DIR, folder)

    if ext in ALLOWED_VECTOR_EXTS:
        # SVGs bypass variant generation (Phase 3.6). Store the extension in the
        # base path so variant_url's legacy passthrough returns the same URL
        # regardless of which size a template asks for.
        target = os.path.join(base_dir, f"{image_id}.{ext}")
        os.makedirs(base_dir, exist_ok=True)
        with open(target, "wb") as f:
            f.write(content)
        return StoredImage(
            base_path=f"uploads/{folder}/{image_id}.{ext}",
            original_url=f"/uploads/{folder}/{image_id}.{ext}",
            is_svg=True,
        )

    # ── Raster path: keep original + emit three WebP variants ──
    try:
        with Image.open(io.BytesIO(content)) as img:
            img.load()
            normalised = _normalise(img)
    except (UnidentifiedImageError, OSError) as e:
        raise ImageProcessingError(f"Could not decode image: {e}") from e

    originals_dir = os.path.join(base_dir, "originals")
    os.makedirs(originals_dir, exist_ok=True)
    original_path = os.path.join(originals_dir, f"{image_id}.{ext}")
    with open(original_path, "wb") as f:
        f.write(content)

    for variant in VARIANTS:
        out_dir = os.path.join(base_dir, variant.name)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{image_id}.webp")
        _write_variant(normalised, out_path, variant)

    return StoredImage(
        base_path=f"uploads/{folder}/{image_id}",
        original_url=f"/uploads/{folder}/originals/{image_id}.{ext}",
        is_svg=False,
    )


def variant_url(base_path: Optional[str], variant_name: str = "card") -> Optional[str]:
    """Translate a stored ``base_path`` (or legacy URL) into a public variant URL.

    Backward-compatible: pre-v2 records hold absolute or pre-built paths like
    ``/uploads/products/foo.jpg`` or ``backend/uploads/...``. For those we
    surface the original asset unchanged so existing data keeps rendering.
    """
    if not base_path:
        return None
    if variant_name not in VARIANT_NAMES:
        variant_name = "card"

    path = base_path.strip()

    # Legacy absolute or backend-prefixed paths — pass through as-is.
    if path.startswith(("http://", "https://", "data:")):
        return path
    if path.startswith("/static/") or path.startswith("/uploads/"):
        return path
    if path.startswith("backend/"):
        return "/" + path.removeprefix("backend/")
    if path.endswith(".svg"):
        # Stored as base path without extension is unusual for SVG, but if a
        # full filename was stored, hand it back as a /uploads URL.
        return _to_uploads_url(path)
    if "." in os.path.basename(path):
        # Looks like a full file path with extension — legacy raster image.
        return _to_uploads_url(path)

    # Modern v2 base path: ``uploads/{folder}/{id}`` → variant WebP.
    folder, image_id = _split_base_path(path)
    if folder is None:
        return _to_uploads_url(path)
    return f"/uploads/{folder}/{variant_name}/{image_id}.webp"


# ─── Internals ────────────────────────────────────────────────────────

def _safe_ext(filename: str) -> str:
    if "." not in (filename or ""):
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def _normalise(img: Image.Image) -> Image.Image:
    """Apply EXIF rotation and convert to a mode WebP can encode."""
    img = ImageOps.exif_transpose(img)
    if img.mode in ("P", "LA"):
        img = img.convert("RGBA")
    elif img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    return img


def _write_variant(source: Image.Image, out_path: str, variant: Variant) -> None:
    img = source.copy()
    img.thumbnail((variant.max_width, variant.max_height), Image.Resampling.LANCZOS)
    save_kwargs = {"format": "WEBP", "quality": variant.quality, "method": 6}
    if img.mode == "RGBA":
        save_kwargs["lossless"] = False
    img.save(out_path, **save_kwargs)


def _split_base_path(path: str) -> tuple[Optional[str], Optional[str]]:
    parts = path.removeprefix("/").split("/")
    if len(parts) >= 3 and parts[0] == "uploads" and parts[1] in VALID_FOLDERS:
        return parts[1], parts[2]
    return None, None


def _to_uploads_url(path: str) -> str:
    """Coerce a legacy ``uploads/foo/bar.jpg`` style path to a public URL."""
    p = path.removeprefix("/")
    if not p.startswith("uploads/"):
        p = f"uploads/{p}"
    return "/" + p
