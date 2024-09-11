from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas, auth
from config import engine, get_db
from datetime import datetime, timedelta

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Маршрут для створення контакту
@app.post("/contacts/", response_model=schemas.ContactInDB)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

# Отримання одного контакту за ID
@app.get("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Отримання контактів користувача (з аутентифікацією)
@app.get("/contacts/", response_model=List[schemas.ContactInDB])
def read_contacts(token: str = Depends(oauth2_scheme), skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    email = auth.verify_token(token, HTTPException(status_code=401, detail="Invalid token"))
    user = crud.get_user_by_email(db, email)
    return crud.get_contacts_by_user(db, user_id=user.id, skip=skip, limit=limit)

# Оновлення контакту
@app.put("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = crud.update_contact(db, contact_id, contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Видалення контакту
@app.delete("/contacts/{contact_id}", response_model=schemas.ContactInDB)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.delete_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Пошук контактів
@app.get("/contacts/search/", response_model=List[schemas.ContactInDB])
def search_contacts(query: str, db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).filter(
        (models.Contact.first_name.ilike(f"%{query}%")) |
        (models.Contact.last_name.ilike(f"%{query}%")) |
        (models.Contact.email.ilike(f"%{query}%"))
    ).all()
    return contacts

# Отримання контактів з найближчими днями народження
@app.get("/contacts/upcoming-birthdays/", response_model=List[schemas.ContactInDB])
def upcoming_birthdays(db: Session = Depends(get_db)):
    today = datetime.now().date()
    upcoming = today + timedelta(days=7)
    contacts = db.query(models.Contact).filter(
        models.Contact.birthday.between(today, upcoming)
    ).all()
    return contacts

# Реєстрація користувача
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=409, detail="Email already registered")
    return db_user

# Вхід і отримання токену
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
