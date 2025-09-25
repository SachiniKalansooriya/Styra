from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .jwt_utils import verify_token
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        logger.warning('No credentials provided in request')
        raise credentials_exception
    
    user_data = verify_token(credentials.credentials)
    if user_data is None:
        logger.warning(f'JWT verification returned None for token prefix: {str(credentials.credentials)[:20]}')
        raise credentials_exception
    
    return user_data

async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None
    
    user_data = verify_token(credentials.credentials)
    return user_data