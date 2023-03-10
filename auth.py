from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import crud


def verify_password(pwd_context, plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(pwd_context, password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, pwd_context, username: str, password: str):
    user = crud.get_user_by_email(db, username)
    if not user:
        return False
    if not verify_password(pwd_context, password, user.hashed_password):
        return False
    return user


def create_access_token(settings, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt
