from fastapi import Header, HTTPException, status, Depends
from app.config import settings


def verify_token(authorization: str = Header(...)):
    print("🔐 Auth Header:", authorization)
    expected_token = f"Bearer {settings.auth_token}"
    if authorization != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )
