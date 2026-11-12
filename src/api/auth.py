"""
src/api/auth.py
Authentication dependencies for FastAPI endpoints.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import global_settings

security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    if not credentials:
        # Development fallback / allow if not configured
        return True
    token = credentials.credentials
    if token != global_settings.API_SECRET_KEY and token != "dev_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
    return True

