from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# Завантаження змінних середовища
load_dotenv()

SECRET_KEY = f"{os.getenv('SECRET_KEY')}"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = f"{os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')}"
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = f"{os.getenv('EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS')}"  # Термін дії токену для верифікації email

# Функція для створення токену доступу (при вході)
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функція для створення токену верифікації email
def create_email_verification_token(email: str):
    expire = datetime.now(timezone.utc) + timedelta(hours=int(EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS))
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функція для перевірки токену (як доступу, так і верифікації email)
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
