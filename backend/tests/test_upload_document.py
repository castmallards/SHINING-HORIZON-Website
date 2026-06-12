"""PDF document upload tests."""

import os

from tests.conftest import csrf_headers

from app.config import settings

_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 3 3]/Parent 2 0 R>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f \n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF"
)


def test_upload_document_requires_auth(client):
    response = client.post(
        "/api/upload/document/products",
        files={"file": ("datasheet.pdf", _MINIMAL_PDF, "application/pdf")},
    )
    assert response.status_code in (401, 403)


def test_upload_document_success(auth_client):
    response = auth_client.post(
        "/api/upload/document/products",
        files={"file": ("datasheet.pdf", _MINIMAL_PDF, "application/pdf")},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["url"].startswith("/uploads/products/documents/")
    assert body["url"].endswith(".pdf")

    abs_path = os.path.join(
        settings.UPLOAD_DIR,
        body["url"].removeprefix("/uploads/").replace("/", os.sep),
    )
    assert os.path.isfile(abs_path)


def test_upload_document_accepts_pdf_with_utf8_bom(auth_client):
    bom_pdf = b"\xef\xbb\xbf%PDF-1.4\n%%EOF"
    response = auth_client.post(
        "/api/upload/document/products",
        files={"file": ("datasheet.pdf", bom_pdf, "application/pdf")},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    assert response.json()["url"].endswith(".pdf")


def test_upload_document_rejects_non_pdf(auth_client):
    response = auth_client.post(
        "/api/upload/document/products",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400
