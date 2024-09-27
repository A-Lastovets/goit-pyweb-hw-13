from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi_ratelimiter import FastAPIRateLimiter
import crud, models, schemas, auth
from config import engine, get_db
from datetime import datetime, timedelta
from email_utils import send_verification_email
from token_utils import create_email_verification_token, verify_email_token
from cloudinary import uploader

# Налаштування CORS
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ініціалізація FastAPI Rate Limiter
FastAPIRateLimiter.init(app)

# Ініціалізація бази даних
models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функція для отримання користувача з токена
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Отримати користувача з токена.

    :param token: JWT токен для аутентифікації.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо токен недійсний або користувач не знайдений.
    :return: Об'єкт користувача.
    """
    email = auth.verify_token(token, HTTPException(status_code=401, detail="Invalid token"))
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Функція для оновлення аватара
@app.post("/users/me/avatar")
@FastAPIRateLimiter.limit("10/minute")
async def update_avatar(file: UploadFile = File(...), user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Оновити аватар користувача.

    :param file: Файл з аватаром для завантаження.
    :param user: Об'єкт користувача, отриманий з токена.
    :param db: Сесія бази даних.
    :return: Підтвердження про успішне оновлення аватара та URL нового аватара.
    """
    result = uploader.upload(file.file, folder="avatars")
    user.avatar_url = result['secure_url']
    db.commit()
    
    return {"msg": "Avatar updated successfully", "avatar_url": user.avatar_url}

# Маршрут для створення контакту
@app.post("/contacts/", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    """
    Створити новий контакт.

    :param contact: Дані нового контакту.
    :param db: Сесія бази даних.
    :return: Створений контакт.
    """
    return crud.create_contact(db, contact)

# Отримання одного контакту за ID
@app.get("/contacts/{contact_id}", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Отримати контакт за його ID.

    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо контакт не знайдено.
    :return: Контакт.
    """
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Отримання контактів користувача (з аутентифікацією)
@app.get("/contacts/", response_model=List[schemas.ContactInDB])
@FastAPIRateLimiter.limit("10/minute")
async def read_contacts(skip: int = 0, limit: int = 10, user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Отримати список контактів користувача.

    :param skip: Кількість пропущених контактів.
    :param limit: Максимальна кількість контактів для повернення.
    :param user: Об'єкт користувача, отриманий з токена.
    :param db: Сесія бази даних.
    :return: Список контактів.
    """
    return crud.get_contacts_by_user(db, user_id=user.id, skip=skip, limit=limit)

# Оновлення контакту
@app.put("/contacts/{contact_id}", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    """
    Оновити контакт за його ID.

    :param contact_id: ID контакту для оновлення.
    :param contact: Дані для оновлення контакту.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо контакт не знайдено.
    :return: Оновлений контакт.
    """
    db_contact = crud.update_contact(db, contact_id, contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Видалення контакту
@app.delete("/contacts/{contact_id}", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Видалити контакт за його ID.

    :param contact_id: ID контакту для видалення.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо контакт не знайдено.
    :return: Видалений контакт.
    """
    db_contact = crud.delete_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Пошук контактів
@app.get("/contacts/search/", response_model=List[schemas.ContactInDB])
@FastAPIRateLimiter.limit("10/minute")
async def search_contacts(query: str, db: Session = Depends(get_db)):
    """
    Пошук контактів за запитом.

    :param query: Запит для пошуку (частина імені або електронної пошти).
    :param db: Сесія бази даних.
    :return: Список контактів, що відповідають запиту.
    """
    contacts = db.query(models.Contact).filter(
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%"))
    ).all()
    return contacts

# Отримання контактів з найближчими днями народження
@app.get("/contacts/upcoming-birthdays/", response_model=List[schemas.ContactInDB])
@FastAPIRateLimiter.limit("10/minute")
async def upcoming_birthdays(db: Session = Depends(get_db)):
    """
    Отримати контакти з найближчими днями народження.

    :param db: Сесія бази даних.
    :return: Список контактів з днями народження в найближчі 7 днів.
    """
    today = datetime.now().date()
    upcoming = today + timedelta(days=7)
    contacts = db.query(models.Contact).filter(
        models.Contact.birthday.between(today, upcoming)
    ).all()
    return contacts

# Реєстрація користувача з верифікацією email
@app.post("/register", response_model=schemas.User)
@FastAPIRateLimiter.limit("10/minute")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    """
    Зареєструвати нового користувача з верифікацією електронної пошти.

    :param user: Дані користувача для реєстрації.
    :param db: Сесія бази даних.
    :param background_tasks: Завдання для фонової обробки (для надсилання листа).
    :raises HTTPException: Якщо електронна пошта вже зареєстрована.
    :return: Дані зареєстрованого користувача з повідомленням про успішну реєстрацію.
    """
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.create_user(db, user)
    
    token = create_email_verification_token(db_user.email)
    send_verification_email(db_user.email, db_user.email.split('@')[0], token, background_tasks)
    
    return {
        "id": db_user.id,
        "email": db_user.email,
        "is_active": db_user.is_active,
        "message": "User registered successfully. Please check your email to verify."
    }

# Верифікація email
@app.get("/verify-email")
@FastAPIRateLimiter.limit("10/minute")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Верифікувати електронну пошту за допомогою токена.

    :param token: Токен для верифікації електронної пошти.
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо токен недійсний або верифікація не вдалася.
    :return: Підтвердження про успішну верифікацію електронної пошти.
    """
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    db_user = crud.get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = True
    db.commit()
    
    return {"msg": "Email verified successfully"}

# Вхід і отримання токену
@app.post("/token", response_model=schemas.Token)
@FastAPIRateLimiter.limit("10/minute")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Увійти в систему, отримати JWT токен.

    :param form_data: Дані для аутентифікації (електронна пошта та пароль).
    :param db: Сесія бази даних.
    :raises HTTPException: Якщо аутентифікація не вдалася.
    :return: JWT токен та дані користувача.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please verify your email before logging in.")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
