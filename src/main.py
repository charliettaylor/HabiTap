#!/usr/bin/env python3
from datetime import timedelta
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext


import src.crud as crud
import src.models as models
import src.schemas as schemas
import src.auth as auth
import src.config as config
import src.dependencies as deps

from src.db import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="HabiTap API",
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


# Auth


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(deps.get_db),
    settings: config.Settings = Depends(deps.get_settings),
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
    user = crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Routes


@app.get("/")
async def root():
    return "Welcome to the HabiTap API"


@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, pwd_context=pwd_context, user=user)


@app.post("/token", response_model=schemas.Token, tags=["Users"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
    settings: config.Settings = Depends(deps.get_settings),
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


@app.get("/users/me/", response_model=schemas.User, tags=["Users"])
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.get("/habits/{name}", response_model=schemas.Habit, tags=["Habits"])
async def get_habit_by_name(
    name: str,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    habit = crud.get_habit_by_name(db, user.id, name)
    if not habit:
        raise HTTPException(status_code=404, detail=f"No habit with name {name}")
    return habit


@app.post("/habits/", response_model=schemas.Habit, tags=["Habits"])
async def create_habit(
    habit: schemas.HabitCreate,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    db_habit = crud.get_habit_by_name(db, user.id, habit.name)
    if db_habit:
        raise HTTPException(
            status_code=400, detail="Habit with that name already exists"
        )
    return crud.create_habit(db=db, habit=habit, user_id=user.id)


@app.get("/entries/{habit_id}", response_model=list[schemas.Entry], tags=["Entries"])
def get_entries_by_habit(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    entries = crud.get_entries_by_habit(db, user.id, habit_id)
    if not entries:
        raise HTTPException(status_code=404, detail=f"No entries for habit {habit_id}")
    return entries


@app.post("/entries/", response_model=schemas.EntryCreate, tags=["Entries"])
def create_entry(
    entry: schemas.EntryCreate,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(get_current_active_user),
):
    db_entry = crud.get_entry(db, user.id, entry)
    if db_entry is not None:
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

    return crud.create_entry(db=db, user_id=user.id, entry=entry)
