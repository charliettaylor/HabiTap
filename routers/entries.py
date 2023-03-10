from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from ..main import get_db
import schemas, crud

router = APIRouter()

@router.get("/entries/{habit_id}", response_model=list[schemas.Entry], tags=["Entries"])
def get_entries_by_habit(habit_id: UUID, db: Session = Depends(get_db)):
    entries = crud.get_entries_by_habit(db, habit_id)
    if not entries:
        raise HTTPException(status_code=404, detail=f"No entries for habit {habit_id}")
    return entries.all()


@router.post("/entries/", response_model=schemas.EntryCreate, tags=["Entries"])
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