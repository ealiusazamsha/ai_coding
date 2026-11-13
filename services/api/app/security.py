"""Verify a Supabase access token server-side; never trust user supplied IDs."""
from uuid import UUID
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .config import settings

bearer = HTTPBearer(auto_error=False)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> UUID:
    config = settings()
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if not config.supabase_url or not config.supabase_publishable_key:
        raise HTTPException(status_code=503, detail="Supabase Auth not configured")
    try:
        with httpx.Client(timeout=8) as client:
            result = client.get(
                f"{config.supabase_url}/auth/v1/user",
                headers={
                    "apikey": config.supabase_publishable_key,
                    "Authorization": f"Bearer {credentials.credentials}",
                },
            )
        if result.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
        return UUID(str(result.json()["id"]))
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Unable to verify access token")
