"""Shared slowapi rate-limiter (Phase 5.3).

Single ``limiter`` instance used as a decorator on protected endpoints
(currently just ``/api/auth/login``). The middleware + exception handler
are wired in ``main.py``. Key function defaults to remote IP address.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings


limiter = Limiter(key_func=get_remote_address, default_limits=[])


def login_rate_limit() -> str:
    """Resolved at request time so changes to settings take effect on reload."""
    return settings.LOGIN_RATE_LIMIT
