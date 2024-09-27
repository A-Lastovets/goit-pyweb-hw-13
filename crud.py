from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
from models import User
from schemas import UserCreate

# Функції CRUD для контактів
def create_contact(db: Session, contact: schemas.ContactCreate):
    """
    Створює новий контакт у базі даних.

    :param db: Сесія бази даних.
    :param contact: Об'єкт ContactCreate зі схем.
    :return: Створений об'єкт контакту.
    """
    db_contact = models.Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contact(db: Session, contact_id: int):
    """
    Отримує контакт за його ідентифікатором.

    :param db: Сесія бази даних.
    :param contact_id: Ідентифікатор контакту.
    :return: Об'єкт контакту або None, якщо не знайдено.
    """
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    """
    Отримує список контактів з можливістю пропуску та обмеження кількості.

    :param db: Сесія бази даних.
    :param skip: Кількість контактів для пропуску.
    :param limit: Максимальна кількість контактів для отримання.
    :return: Список контактів.
    """
    return db.query(models.Contact).offset(skip).limit(limit).all()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    """
    Оновлює інформацію про контакт.

    :param db: Сесія бази даних.
    :param contact_id: Ідентифікатор контакту для оновлення.
    :param contact: Об'єкт ContactUpdate зі схем.
    :return: Оновлений об'єкт контакту або None, якщо не знайдено.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int):
    """
    Видаляє контакт за його ідентифікатором.

    :param db: Сесія бази даних.
    :param contact_id: Ідентифікатор контакту для видалення.
    :return: Видалений об'єкт контакту або None, якщо не знайдено.
    """
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

# Шифрування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Перевіряє відповідність звичайного пароля хешованому паролю.

    :param plain_password: Звичайний пароль.
    :param hashed_password: Хешований пароль.
    :return: True, якщо пароль правильний, False в іншому випадку.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Генерує хеш пароля.

    :param password: Звичайний пароль.
    :return: Хешований пароль.
    """
    return pwd_context.hash(password)

# Функції CRUD для користувачів
def create_user(db: Session, user: UserCreate):
    """
    Створює нового користувача з хешованим паролем.

    :param db: Сесія бази даних.
    :param user: Об'єкт UserCreate зі схем.
    :return: Створений об'єкт користувача або None, якщо користувач вже існує.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        return None  # Користувач з таким email вже існує
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Аутентифікує користувача за email і паролем.

    :param db: Сесія бази даних.
    :param email: Email користувача.
    :param password: Звичайний пароль.
    :return: Об'єкт користувача або None, якщо аутентифікація не вдалася.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user_by_email(db: Session, email: str):
    """
    Отримує користувача за його email.

    :param db: Сесія бази даних.
    :param email: Email користувача.
    :return: Об'єкт користувача або None, якщо не знайдено.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_contacts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Отримує контакти користувача за його ідентифікатором.

    :param db: Сесія бази даних.
    :param user_id: Ідентифікатор користувача.
    :param skip: Кількість контактів для пропуску.
    :param limit: Максимальна кількість контактів для отримання.
    :return: Список контактів користувача.
    """
    return db.query(models.Contact).filter(models.Contact.user_id == user_id).offset(skip).limit(limit).all()

# Оновлення статусу верифікації користувача
def verify_user_email(db: Session, email: str):
    """
    Верифікує email користувача.

    :param db: Сесія бази даних.
    :param email: Email користувача.
    :return: Оновлений об'єкт користувача або None, якщо не знайдено.
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_verified = True  # Додаємо поле is_verified у модель User
        db.commit()
        db.refresh(user)
    return user

# Перевірка, чи вже верифікований користувач
def is_user_verified(db: Session, email: str):
    """
    Перевіряє, чи верифіковано користувача за його email.

    :param db: Сесія бази даних.
    :param email: Email користувача.
    :return: True, якщо користувач верифікований, інакше False.
    """
    user = db.query(User).filter(User.email == email).first()
    if user and user.is_verified:
        return True
    return False

# Оновлення URL аватара користувача
def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    """
    Оновлює URL аватара користувача.

    :param db: Сесія бази даних.
    :param user_id: Ідентифікатор користувача.
    :param avatar_url: Новий URL аватара.
    :return: Оновлений об'єкт користувача або None, якщо не знайдено.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
    return user
