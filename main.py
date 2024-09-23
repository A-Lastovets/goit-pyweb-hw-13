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
    email = auth.verify_token(token, HTTPException(status_code=401, detail="Invalid token"))
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Функція для оновлення аватара
@app.post("/users/me/avatar")
@FastAPIRateLimiter.limit("10/minute")
async def update_avatar(file: UploadFile = File(...), user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = uploader.upload(file.file, folder="avatars")
    user.avatar_url = result['secure_url']
    db.commit()
    
    return {"msg": "Avatar updated successfully", "avatar_url": user.avatar_url}

# Маршрут для створення контакту
@app.post("/contacts/", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

# Отримання одного контакту за ID
@app.get("/contacts/{contact_id}", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Отримання контактів користувача (з аутентифікацією)
@app.get("/contacts/", response_model=List[schemas.ContactInDB])
@FastAPIRateLimiter.limit("10/minute")
async def read_contacts(skip: int = 0, limit: int = 10, user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_contacts_by_user(db, user_id=user.id, skip=skip, limit=limit)

# Оновлення контакту
@app.put("/contacts/{contact_id}", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = crud.update_contact(db, contact_id, contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Видалення контакту
@app.delete("/contacts/{contact_id}", response_model=schemas.ContactInDB)
@FastAPIRateLimiter.limit("10/minute")
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.delete_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Пошук контактів
@app.get("/contacts/search/", response_model=List[schemas.ContactInDB])
@FastAPIRateLimiter.limit("10/minute")
async def search_contacts(query: str, db: Session = Depends(get_db)):
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
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please verify your email before logging in.")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
