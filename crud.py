#!/usr/bin/env python3
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
import models, schemas
import auth


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, pwd_context, user: schemas.UserCreate) -> schemas.User:
    id = uuid4()
    hashed_password = auth.get_password_hash(pwd_context, user.password)
    db_user = models.User(
        id=id, email=user.email, hashed_password=hashed_password, is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_habit(db: Session, id: UUID):
    return db.query(models.Habit).filter(models.Habit.id == id).first()


def get_habit_by_name(db: Session, name: str):
    return db.query(models.Habit).filter(models.Habit.name == name).first()


def create_habit(
    db: Session, habit: schemas.HabitCreate, user_id: UUID
) -> schemas.Habit:
    id = uuid4()

    db_habit = models.Habit(
        id=id,
        name=habit.name,
        description=habit.description,
        goal=habit.goal,
        start_date=habit.start_date,
        owner_id=user_id,
    )

    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


def get_entries_by_habit(db: Session, habit_id: UUID):
    return db.query(models.Entry).filter_by(habit_id=habit_id)


def get_entry(db: Session, entry: schemas.EntryBase):
    return db.query(models.Entry).filter_by(date=entry.date, habit_id=entry.habit_id)


def create_entry(db: Session, entry: schemas.EntryCreate):
    id = uuid4()

    db_entry = models.Entry(
        id=id,
        date=entry.date,
        value=entry.value,
        habit_id=entry.habit_id,
    )

    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry
