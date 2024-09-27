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
    """
    Створює JWT токен доступу.

    :param data: Дані, які будуть закодовані в токен.
    :param expires_delta: Час, на який буде дійсний токен. 
                            Якщо не вказано, використовує значення за замовчуванням з ACCESS_TOKEN_EXPIRE_MINUTES.
    :return: Закодований JWT токен.
    """
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
    """
    Створює JWT токен для верифікації email.

    :param email: Email, який буде закодований у токені.
    :return: Закодований JWT токен для верифікації email.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=int(EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS))
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функція для перевірки токену (як доступу, так і верифікації email)
def verify_token(token: str, credentials_exception):
    """
    Перевіряє коректність переданого токену.

    :param token: JWT токен для декодування та перевірки.
    :param credentials_exception: Виняток, який піднімається в разі помилкової аутентифікації.
    :return: Email користувача, якщо токен є дійсним.
    :raises credentials_exception: Якщо токен недійсний або в ньому немає email.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
