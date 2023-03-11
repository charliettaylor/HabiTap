from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

import src.dependencies as deps
import src.schemas as schemas
import src.crud as crud

# router = APIRouter()

# TODO: Figure out how to make OAuth and get_current_active_user global deps
