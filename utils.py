# utils.py
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGO = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Truncate password to 72 bytes to avoid bcrypt limitation
    return pwd_context.hash(password[:72])


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(password, hashed)
    except Exception as e:
        # Handle bcrypt compatibility issues
        print(f"Password verification error: {e}")
        return False


def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)
    return encoded_jwt


def decode_token(token: str):
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.JWTError:
        raise Exception("Invalid token")


def get_current_user(token: str):
    """Extract user information from token"""
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise Exception("Invalid token")
        return username
    except Exception:
        raise Exception("Invalid token")
