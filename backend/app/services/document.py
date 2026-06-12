"""PDF document upload storage for product datasheets."""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from ..config import settings

VALID_DOCUMENT_FOLDERS = frozenset({"products"})
ALLOWED_DOCUMENT_EXTS = frozenset({"pdf"})
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB


class DocumentProcessingError(Exception):
    """Raised when an upload payload cannot be stored as a document."""


@dataclass(frozen=True)
class StoredDocument:
    """Result of ``process_document_upload``. ``path`` is stored in ``datasheet_url``."""

    path: str   # e.g. "/uploads/products/documents/abcd1234.pdf"
    url: str    # same as path — public URL for links


def _looks_like_pdf(content: bytes) -> bool:
    if not content:
        return False
    # Allow UTF-8 BOM / leading whitespace; some tools prepend bytes before %PDF-.
    trimmed = content.lstrip(b"\xef\xbb\xbf \t\r\n")
    if trimmed.startswith(b"%PDF-"):
        return True
    return b"%PDF-" in content[:8192]


def process_document_upload(folder: str, filename: str, content: bytes) -> StoredDocument:
    if folder not in VALID_DOCUMENT_FOLDERS:
        raise DocumentProcessingError(
            f"Invalid folder '{folder}'. Expected one of {sorted(VALID_DOCUMENT_FOLDERS)}."
        )
    if not content:
        raise DocumentProcessingError("Uploaded file is empty")
    if len(content) > MAX_DOCUMENT_SIZE:
        raise DocumentProcessingError("File too large. Max size: 20MB")

    ext = filename.rsplit(".", 1)[-1].lower() if filename and "." in filename else ""
    if ext not in ALLOWED_DOCUMENT_EXTS:
        raise DocumentProcessingError(f"Invalid file type. Allowed: {sorted(ALLOWED_DOCUMENT_EXTS)}")
    if not _looks_like_pdf(content):
        raise DocumentProcessingError("File does not look like a valid PDF")

    doc_id = uuid.uuid4().hex
    rel_dir = os.path.join(folder, "documents")
    abs_dir = os.path.join(settings.UPLOAD_DIR, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)

    stored_name = f"{doc_id}.pdf"
    abs_path = os.path.join(abs_dir, stored_name)
    try:
        with open(abs_path, "wb") as handle:
            handle.write(content)
    except OSError as exc:
        raise DocumentProcessingError(f"Could not save PDF to disk: {exc}") from exc

    public_path = f"/uploads/{rel_dir.replace(os.sep, '/')}/{stored_name}"
    return StoredDocument(path=public_path, url=public_path)
