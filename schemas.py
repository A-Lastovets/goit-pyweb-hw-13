from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class ContactBase(BaseModel):
    """
    Базова схема для контактів.

    Атрибути:
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (EmailStr): Електронна адреса контакту.
        phone_number (str): Номер телефону контакту.
        birthday (date): Дата народження контакту.
        additional_info (Optional[str]): Додаткова інформація про контакт (необов'язковий параметр).
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    """
    Схема для створення нового контакту. Успадковується від ContactBase.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Схема для оновлення контакту. Успадковується від ContactBase.
    """
    pass

class ContactInDB(ContactBase):
    """
    Схема для представлення контакту з бази даних.

    Атрибути:
        id (int): Унікальний ідентифікатор контакту в базі даних.
    """
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """
    Схема для створення нового користувача.

    Атрибути:
        email (EmailStr): Електронна адреса користувача.
        password (str): Пароль користувача.
    """
    email: EmailStr
    password: str

class User(BaseModel):
    """
    Схема для представлення користувача.

    Атрибути:
        id (int): Унікальний ідентифікатор користувача.
        email (EmailStr): Електронна адреса користувача.
        is_active (bool): Статус активності користувача.
    """
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Схема для представлення токена доступу.

    Атрибути:
        access_token (str): Токен доступу.
        token_type (str): Тип токену (зазвичай "Bearer").
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Схема для представлення даних токену.

    Атрибути:
        email (Optional[str]): Електронна адреса користувача, отримана з токену.
    """
    email: str | None = None
