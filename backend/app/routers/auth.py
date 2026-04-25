"""Authentication endpoints (Phase 4.1 — cookie session, Phase 5.3 — rate limit)."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..rate_limit import limiter
from ..schemas.user import Token, UserLogin, UserResponse
from ..services.auth import SESSION_COOKIE, AuthService, get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_session_cookie(response: Response, token: str) -> None:
    """Set the httpOnly session cookie used by the admin SPA.

    SameSite=Lax keeps the cookie on top-level navigations from the admin
    pages while blocking cross-site form submits.
    """
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        domain=settings.COOKIE_DOMAIN or None,
    )


@router.post("/login", response_model=Token)
@limiter.limit(lambda: settings.LOGIN_RATE_LIMIT)
def login(request: Request, credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    _set_session_cookie(response, access_token)

    # Token also returned in the body for legacy CLI/Swagger consumers; the
    # admin SPA ignores it and reads from cookies.
    return Token(access_token=access_token, user=UserResponse.model_validate(user))


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE, path="/", domain=settings.COOKIE_DOMAIN or None)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not AuthService.verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password",
        )

    current_user.password_hash = AuthService.hash_password(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
