#!/usr/bin/env python3
from pydantic import BaseModel, Field, BaseSettings
from uuid import UUID
from datetime import date


class Settings(BaseSettings):
    app_name: str = "Habitap API"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    # User's email
    email: str = Field(
        default="test@example.com", description="The email this user registered with"
    )


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID
    is_active: bool

    class Config:
        orm_mode = True


class HabitBase(BaseModel):
    name: str
    description: str
    goal: int
    start_date: date
    is_counted: bool


class Habit(HabitBase):
    id: UUID
    owner_id: UUID

    class Config:
        orm_mode = True


class HabitCreate(HabitBase):
    pass


class EntryBase(BaseModel):
    date: date
    value: int
    habit_id: UUID

    class Config:
        orm_mode = True


class Entry(EntryBase):
    id: UUID


class EntryCreate(EntryBase):
    pass
