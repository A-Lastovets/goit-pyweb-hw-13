from datetime import datetime, timedelta, timezone
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES = os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES")  # Тривалість дії токена

def create_email_verification_token(email: str, expires_delta: timedelta = None):
    """Генерує токен для підтвердження електронної пошти."""
    to_encode = {"sub": email}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_email_token(token: str):
    """Перевіряє токен для підтвердження електронної пошти."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise ValueError("Invalid token")
        return email
    except Exception:
        raise ValueError("Invalid token")
