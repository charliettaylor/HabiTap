#!/usr/bin/env python3
from typing import List
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid

from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Habit(Base):
    __tablename__ = "habits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(String, index=True)
    is_counted = Column(Boolean)
    goal = Column(Integer)
    start_date = Column(Date)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    entries = relationship("Entry", back_populates="habit")


class Entry(Base):
    __tablename__ = "entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date(), unique=True, index=True)
    value = Column(Integer(), unique=False)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id"))

    habit = relationship("Habit", back_populates="entries")
