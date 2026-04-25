"""Security headers middleware (Phase 5.5).

Adds defensive HTTP response headers on every response:

  * ``X-Content-Type-Options: nosniff`` — disables MIME sniffing.
  * ``X-Frame-Options: SAMEORIGIN`` — clickjacking protection.
  * ``Referrer-Policy: strict-origin-when-cross-origin`` — limits referrer leakage.
  * ``Permissions-Policy`` — disables a handful of powerful browser features
    we don't use (camera/microphone/geolocation/etc).
  * ``Strict-Transport-Security`` — only when ``hsts`` is enabled (production
    behind HTTPS). Defaults to off so local http dev still works.
  * ``Content-Security-Policy`` — moderate policy that allows the third-party
    CDNs the templates already pull from (Tailwind, AOS, Quill, Google Fonts)
    while denying inline frames/objects. CSP is the loudest header — keep
    additions deliberate.
"""
from __future__ import annotations

from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


_DEFAULT_CSP = "; ".join([
    "default-src 'self'",
    # Tailwind CDN (cdn.tailwindcss.com), AOS (unpkg.com), Quill (cdn.quilljs.com).
    # 'unsafe-inline' is required for the inline <script> tailwind config block
    # in _head.html and inline event handlers throughout the admin pages.
    "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdn.quilljs.com",
    # 'unsafe-inline' for inline <style> blocks in _head.html and admin pages.
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com https://cdn.quilljs.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "img-src 'self' data: https: blob:",
    "connect-src 'self'",
    "frame-ancestors 'self'",
    "form-action 'self'",
    "base-uri 'self'",
    "object-src 'none'",
])


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        csp: Optional[str] = _DEFAULT_CSP,
        hsts: bool = False,
        hsts_max_age: int = 31536000,
    ):
        super().__init__(app)
        self._csp = csp
        self._hsts = hsts
        self._hsts_max_age = hsts_max_age

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        h = response.headers
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "SAMEORIGIN")
        h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        h.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
        )
        if self._csp:
            h.setdefault("Content-Security-Policy", self._csp)
        if self._hsts:
            h.setdefault(
                "Strict-Transport-Security",
                f"max-age={self._hsts_max_age}; includeSubDomains",
            )
        return response
