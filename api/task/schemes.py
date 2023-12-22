from typing import Optional, List

from pydantic import BaseModel
from datetime import date


class TaskRead(BaseModel):
    title: str
    description: Optional[str]
    is_active: bool
    deadline: date


class TaskCreate(BaseModel):
    tasks: List[TaskRead]


class TaskChange(BaseModel):
    is_active: Optional[bool]
    deadline: Optional[date]
