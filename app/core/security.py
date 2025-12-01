from passlib.context import CryptContext
import logging

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
