#!/usr/bin/env python3
from datetime import timedelta
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from uuid import UUID

import crud, models, schemas, auth, config

from db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Habitap API",
        version="1.0.0",
        description="A habit tracking app with a good API",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings():
    return config.Settings()


# Auth


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: config.Settings = Depends(get_settings),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Routes


@app.get("/")
async def root(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/test/{num}")
async def num(num: int):
    return {"message": f"Your number is {num}"}


@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, pwd_context=pwd_context, user=user)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    settings: config.Settings = Depends(get_settings),
):
    user = auth.authenticate_user(
        db, pwd_context, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        settings, data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/habits/{name}", response_model=schemas.Habit, tags=["Habits"])
def get_habit_by_name(name: str, db: Session = Depends(get_db)):
    habit = crud.get_habit_by_name(db, name)
    if not habit:
        raise HTTPException(status_code=404, detail=f"No habit with name {name}")
    return habit


@app.post("/habits/{user_id}", response_model=schemas.Habit, tags=["Habits"])
def create_habit(
    user_id: UUID, habit: schemas.HabitCreate, db: Session = Depends(get_db)
):
    db_habit = crud.get_habit_by_name(db, habit.name)
    if db_habit:
        raise HTTPException(
            status_code=400, detail="Habit with that name already exists"
        )
    return crud.create_habit(db=db, habit=habit, user_id=user_id)


@app.get("/entries/{habit_id}", response_model=list[schemas.Entry], tags=["Entries"])
def get_entries_by_habit(habit_id: UUID, db: Session = Depends(get_db)):
    entries = crud.get_entries_by_habit(db, habit_id)
    if not entries:
        raise HTTPException(status_code=404, detail=f"No entries for habit {habit_id}")
    return entries.all()


@app.post("/entries/", response_model=schemas.EntryCreate, tags=["Entries"])
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db)):
    db_entry = crud.get_entry(db, entry)
    if db_entry.count() > 0:
        raise HTTPException(status_code=400, detail="Entry already exists")

    habit = crud.get_habit(db, entry.habit_id)
    if not habit:
        raise HTTPException(status_code=400, detail="Habit does not exist")

    if entry.date < habit.start_date:
        raise HTTPException(
            status_code=400, detail="Can not make entry before habit start date"
        )

    if not habit.is_counted and entry.value not in [0, 1]:
        raise HTTPException(
            status_code=400,
            detail="Non-counted habits must be 1 or 0 for true or false",
        )

    return crud.create_entry(db=db, entry=entry)
