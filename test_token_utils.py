import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
import pytest
from auth import create_access_token, create_email_verification_token, verify_token

class CredentialsException(Exception):
    pass

# Тестування створення токену доступу
def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0  # Перевіряємо, що токен не порожній

# Тестування створення токену для верифікації email
def test_create_email_verification_token():
    email = "test@example.com"
    token = create_email_verification_token(email)
    
    assert isinstance(token, str)
    assert len(token) > 0  # Перевіряємо, що токен не порожній

# Тестування перевірки дійсного токену
def test_verify_token_valid():
    email = "test@example.com"
    token = create_email_verification_token(email)
    
    verified_email = verify_token(token, CredentialsException)
    
    assert verified_email == email

# Тестування перевірки недійсного токену
def test_verify_token_invalid():
    invalid_token = "invalid_token"
    
    with pytest.raises(CredentialsException):
        verify_token(invalid_token, CredentialsException)

# Тестування перевірки токену без email
def test_verify_token_missing_email():
    # Створюємо токен без поля 'sub'
    expire = timedelta(minutes=1)
    to_encode = {"exp": datetime.utcnow() + expire}
    token = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm='HS256')
    
    with pytest.raises(CredentialsException):
        verify_token(token, CredentialsException)
