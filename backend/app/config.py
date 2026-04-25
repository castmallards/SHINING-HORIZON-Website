import os
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Sentinel value used in .env.example. App refuses to boot if the live SECRET_KEY equals this.
_PLACEHOLDER_SECRETS = {
    "CHANGE_ME_TO_A_64_CHAR_RANDOM_STRING",
    "your-secret-key-change-in-production-min-32-chars",
    "your-super-secret-key-change-this-in-production-min-32-chars",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── App ──
    APP_NAME: str = "Shining Horizon"
    DEBUG: bool = False

    # ── Database ──
    DATABASE_URL: str = "sqlite:///./shining_horizon.db"

    # ── Authentication ──
    # No default. Must be provided via env. App raises on startup if missing/placeholder.
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ── Cookies (admin session) ──
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str = ""

    # ── Uploads ──
    UPLOAD_DIR_NAME: str = Field(default="uploads", alias="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024

    # ── CORS ──
    # Accepts comma-separated string in env, exposed as parsed list.
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # ── Security headers (Phase 5.5) ──
    # HSTS only makes sense behind HTTPS — leave off in dev so http://localhost works.
    ENABLE_HSTS: bool = False
    HSTS_MAX_AGE: int = 31536000  # 1 year

    # ── Rate limiting (Phase 5.3) ──
    # Login throttle: N attempts per window per client IP.
    LOGIN_RATE_LIMIT: str = "5/15minutes"

    # ── Computed paths ──
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def UPLOAD_DIR(self) -> str:
        return os.path.join(self.BASE_DIR, self.UPLOAD_DIR_NAME)

    @property
    def FRONTEND_DIR(self) -> str:
        # Project root (parent of backend/)
        return os.path.dirname(self.BASE_DIR)

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @field_validator("SECRET_KEY")
    @classmethod
    def _secret_key_must_be_set(cls, v: str) -> str:
        if not v or v in _PLACEHOLDER_SECRETS:
            raise ValueError(
                "SECRET_KEY is missing or set to the placeholder value. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\" "
                "and put it in backend/.env"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v


settings = Settings()
