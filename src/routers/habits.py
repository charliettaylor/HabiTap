from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import src.crud as crud
import src.dependencies as deps
import src.schemas as schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/habits",
    tags=["Habits"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[schemas.Habit])
async def get_user_habits(
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(deps.get_current_active_user),
):
    habits = crud.get_habits_by_user(db, user.id)

    if not habits:
        raise HTTPException(status_code=404, detail=f"No habits for this user")

    print("here", habits)
    return habits


@router.get("/{name}", response_model=schemas.Habit)
async def get_habit_by_name(
    name: str,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(deps.get_current_active_user),
):
    habit = crud.get_habit_by_name(db, user.id, name)
    if not habit:
        raise HTTPException(status_code=404, detail=f"No habit with name {name}")
    return habit


@router.post("/", response_model=schemas.Habit)
async def create_habit(
    habit: schemas.HabitCreate,
    db: Session = Depends(deps.get_db),
    user: schemas.User = Depends(deps.get_current_active_user),
):
    db_habit = crud.get_habit_by_name(db, user.id, habit.name)
    if db_habit:
        raise HTTPException(
            status_code=400, detail="Habit with that name already exists"
        )
    return crud.create_habit(db=db, habit=habit, user_id=user.id)
