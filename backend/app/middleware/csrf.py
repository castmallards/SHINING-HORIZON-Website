"""Double-submit-cookie CSRF protection (Phase 4.2).

The middleware:
  1. Issues a random ``csrf_token`` cookie (NOT httpOnly so JS can read it)
     on the first response that doesn't already carry one.
  2. On state-changing requests (POST/PUT/PATCH/DELETE) under ``/api/*`` it
     requires the request's ``X-CSRF-Token`` header to match the cookie.
  3. Login is exempt — there is no session yet, so no cookie to compare.
  4. Public SSR routes are exempt — they aren't admin-mutating.
"""
from __future__ import annotations

import secrets
from typing import Iterable, Optional

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _new_token() -> str:
    return secrets.token_urlsafe(32)


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        protected_prefixes: Iterable[str] = ("/api/",),
        exempt_paths: Iterable[str] = ("/api/auth/login",),
        cookie_secure: bool = False,
        cookie_domain: Optional[str] = None,
    ):
        super().__init__(app)
        self._protected = tuple(protected_prefixes)
        self._exempt = set(exempt_paths)
        self._cookie_secure = cookie_secure
        self._cookie_domain = cookie_domain or None

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()

        is_protected = path.startswith(self._protected) and path not in self._exempt
        if is_protected and method not in SAFE_METHODS:
            cookie_token = request.cookies.get(CSRF_COOKIE)
            header_token = request.headers.get(CSRF_HEADER)
            if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token missing or invalid"},
                )

        response: Response = await call_next(request)

        # Mint a CSRF cookie on every response that doesn't already carry one.
        # The admin SPA reads it via ``document.cookie`` and echoes it back as
        # the ``X-CSRF-Token`` header on mutating fetches.
        if CSRF_COOKIE not in request.cookies:
            response.set_cookie(
                key=CSRF_COOKIE,
                value=_new_token(),
                httponly=False,  # JS must be able to read it for the header
                secure=self._cookie_secure,
                samesite="lax",
                path="/",
                domain=self._cookie_domain,
            )
        return response
