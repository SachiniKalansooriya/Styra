from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# JWT Configuration
DEFAULT_SECRET = "styra-ai-wardrobe-super-secret-key-change-in-production"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", DEFAULT_SECRET)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # minutes

# Warn if using default secret in non-development environments
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
if SECRET_KEY == DEFAULT_SECRET and ENVIRONMENT != 'development':
    logger.warning("Using default JWT secret in non-development environment — rotate your JWT_SECRET_KEY in production!")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use numeric timestamps for exp/iat to avoid ambiguity across JWT libraries
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Validate token type
        if payload.get('type') != 'access':
            logger.warning('JWT token has invalid type claim')
            return None

        user_sub = payload.get("sub")
        if user_sub is None:
            logger.warning('JWT token missing "sub" claim')
            return None

        try:
            user_id = int(user_sub)
        except Exception:
            logger.warning('JWT "sub" claim is not an integer')
            return None

        # Check expiration (exp stored as numeric timestamp)
        exp = payload.get("exp")
        if exp is not None:
            try:
                exp_ts = int(exp)
                if datetime.utcnow().timestamp() > exp_ts:
                    logger.info('JWT token expired')
                    return None
            except Exception:
                logger.warning('Invalid exp claim in JWT token')
                return None

        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "exp": exp
        }
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None