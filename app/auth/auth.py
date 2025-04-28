from fastapi import Header, HTTPException, status
from app.config import settings


async def verify_token(
    authorization: str = Header(..., description="Bearer authentication token"),
) -> None:
    """Verify the Authorization header for protected endpoints."""
    expected_token = f"Bearer {settings.auth_token}"

    if authorization != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )
