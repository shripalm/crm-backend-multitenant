from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import logging
from uuid import UUID

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)

# bcrypt has a hard limit of 72 bytes for the password input. If a UTF-8
# password exceeds 72 bytes it must be truncated before hashing and
# verification. We apply the same deterministic truncation for both hash
# and verify so that verification succeeds for values produced by this
# code. Note: truncation is lossy; consider using a different scheme if
# long passwords are required.
BCRYPT_MAX_BYTES = 72

def _truncate_to_bcrypt_limit(password: str) -> str:
    b = password.encode("utf-8")
    if len(b) <= BCRYPT_MAX_BYTES:
        return password
    truncated = b[:BCRYPT_MAX_BYTES]
    # decode with 'ignore' to avoid cutting a multi-byte sequence raising
    # a UnicodeDecodeError; both hash and verify will use the same string.
    truncated_str = truncated.decode("utf-8", errors="ignore")
    logger.warning("Password exceeded %d bytes (utf-8); truncating before bcrypt hashing", BCRYPT_MAX_BYTES)
    return truncated_str


def hash_password(password: str) -> str:
    """Hash the user password.

    This will truncate the UTF-8 encoded password to bcrypt's 72-byte
    limit before hashing to avoid ValueError from the bcrypt backend.
    """
    logger.debug("Hashing password (not logging the secret)")
    pwd = _truncate_to_bcrypt_limit(password)
    return pwd_context.hash(pwd)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password during login.

    Apply the same truncation to the provided plain password before
    verifying so it matches how passwords were hashed.
    """
    plain = _truncate_to_bcrypt_limit(plain_password)
    return pwd_context.verify(plain, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token (e.g., user_id, email)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    # Convert UUID to string if present
    if "user_id" in to_encode and isinstance(to_encode["user_id"], UUID):
        to_encode["user_id"] = str(to_encode["user_id"])
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Decoded payload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user_id from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload:
        return payload.get("user_id")
    return None
