import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, update
from api.auth.routers import fastapi_users
from db.models import Task, Role, User
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_async_session
from api.task.schemes import TaskRead, TaskChange

task_api = APIRouter(
    prefix="/task",
    tags=["Tasks"]
)


@task_api.get("/my", response_model=List[TaskRead])
async def get_my_tasks(db: AsyncSession = Depends(get_async_session),
                       user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    query = select(Task).where(Task.student_id == user.id and Task.is_active)
    result = await db.scalars(query)
    return [TaskRead(**task.__dict__) for task in result]


@task_api.get("", response_model=List[TaskRead], response_model_exclude_none=True)
async def get_user_tasks(id_user: uuid.UUID,
                         db: AsyncSession = Depends(get_async_session),
                         user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    if user.role == Role.student:
        raise HTTPException(detail="User must have role 'maintainer' или 'user'.",
                            status_code=status.HTTP_403_FORBIDDEN)
    query = select(Task).where(Task.student_id == id_user and Task.is_active)
    result = await db.scalars(query)
    return [TaskRead(**task.__dict__) for task in result]


@task_api.put("/{id_task}", response_model=TaskRead, response_model_exclude_none=True)
async def change_task(id_task: uuid.UUID,
                      task: TaskChange,
                      db: AsyncSession = Depends(get_async_session),
                      user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    if user.role == Role.student:
        raise HTTPException(detail="User must have role 'maintainer' или 'user'.",
                            status_code=status.HTTP_403_FORBIDDEN)
    query = update(Task).where(Task.id == id_task).values(task.dict(exclude_unset=True))
    await db.execute(query)
    await db.commit()
    query = select(Task).where(Task.id == id_task)
    result = await db.scalar(query)
    return TaskRead(**result.__dict__)
