from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import src.dependencies as deps
import src.schemas as schemas
import src.crud as crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/entries",
    tags=["Entries"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{habit_id}", response_model=list[schemas.Entry])
def get_entries_by_habit(
    habit_id: UUID,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(deps.get_current_active_user),
):
    entries = crud.get_entries_by_habit(db, user.id, habit_id)
    if not entries:
        raise HTTPException(status_code=404, detail=f"No entries for habit {habit_id}")
    return entries


@router.post("/", response_model=schemas.EntryCreate)
def create_entry(
    entry: schemas.EntryCreate,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(deps.get_current_active_user),
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
