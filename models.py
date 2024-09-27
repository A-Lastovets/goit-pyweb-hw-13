from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config import Base

class Contact(Base):
    """
    Модель, що представляє контактну інформацію.

    Атрибути:
        id (int): Унікальний ідентифікатор контакту.
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (str): Електронна адреса контакту (унікальна).
        phone_number (str): Номер телефону контакту.
        birthday (Date): Дата народження контакту.
        additional_info (str, optional): Додаткова інформація про контакт.
        user_id (int): Зовнішній ключ, який зв'язує контакт з користувачем.
        user (User): Відношення до користувача, якому належить контакт.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    phone_number = Column(String, index=True)
    birthday = Column(Date)
    additional_info = Column(String, nullable=True)
    
    # Зовнішній ключ для зв’язування контактів із користувачем
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Відношення до моделі користувача
    user = relationship("User", back_populates="contacts")

class User(Base):
    """
    Модель, що представляє користувача системи.

    Атрибути:
        id (int): Унікальний ідентифікатор користувача.
        email (str): Унікальна електронна адреса користувача.
        hashed_password (str): Захешований пароль користувача.
        is_active (bool): Статус активності користувача (за замовчуванням True).
        is_verified (bool): Статус верифікації електронної пошти користувача(за замовчуванням False).
        avatar_url (str, optional): URL для аватара користувача.
        contacts (list[Contact]): Відношення до контактів, що належать користувачу.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Поле для статусу верифікації
    avatar_url = Column(String, nullable=True)  # Поле для зберігання URL аватара

    # Відношення до моделі Contact
    contacts = relationship("Contact", back_populates="user")
