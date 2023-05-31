#!/usr/bin/env python3
from datetime import date
from pydantic import BaseModel, Field, BaseSettings, EmailStr
from uuid import UUID


class Settings(BaseSettings):
    app_name: str = "Habitap API"
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    sqlalchemy_database_url: str

    class Config:
        env_file = ".env"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    # User's email
    email: EmailStr = Field(
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
    name: str = Field(default="", description="The name for this habit")
    description: str = Field(default="", description="The description for this habit")
    goal: int = Field(default=1, description="The goal for this habit")
    start_date: date = Field(
        default=date.today(), description="The date this habit started"
    )
    is_counted: bool = Field(
        default=False,
        description="Is this habit counted? Counted habits should be something that can be tracked (e.g. pushups, situps, etc.) Non-counted habits should be something that is either done or not done (e.g. read a book, meditate, etc.)",
    )


class Habit(HabitBase):
    id: UUID
    owner_id: UUID

    class Config:
        orm_mode = True


class HabitCreate(HabitBase):
    pass


class EntryBase(BaseModel):
    date = Field(default=date.today(), description="The date this entry was created")
    value: int = Field(
        default=0,
        description="The value for this entry. Counted habits will take any non-negative number as a value. Non-counted habits will take either 0 or 1. 0 means the habit was not completed that day, while 1 means it was.",
    )
    habit_id: UUID = Field(default="", description="The habit ID this entry belongs to")

    class Config:
        orm_mode = True


class Entry(EntryBase):
    id: UUID
    owner_id: UUID = Field(default="", description="The user this entry belongs to")


class EntryCreate(EntryBase):
    pass
