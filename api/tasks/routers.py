from typing import Optional, List

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import select, insert, exists, update, delete
from api.auth.routers import fastapi_users

from db.models import *
from db.session import *
from api.tasks.schemes import *

task_api = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@task_api.get("/my", response_model=List[TaskRead])
async def get_my_tasks(db: AsyncSession = Depends(get_async_session),
                       user: User = Depends(fastapi_users.current_user(active=True))):
    query = select(Task).where(Task.student_id == user.id and Task.is_active)
    result = await db.scalars(query)
    return [TaskRead(**task.__dict__) for task in result]


@task_api.get("", response_model=List[TaskRead], response_model_exclude_none=True)
async def get_user_tasks(id_user: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    # TODO сделать ограничение по роли? и учитывать зарегистрирован ли пользователь
    query = select(Task).where(Task.student_id == id_user and Task.is_active)
    result = await db.execute(query)
    return [TaskRead(**task.__dict__) for task in result.scalars().all()]


@task_api.post("/{id_arrival}")
async def create_tasks_for_arrival_user(id_arrival: uuid.UUID,
                                        tasks_users: TaskCreate,
                                        db: AsyncSession = Depends(get_async_session)):
    # TODO сделать ограничение по роли? и учитывать зарегистрирован ли пользователь
    query = select(User).where(User.student_arrival_id == id_arrival)
    users = (await db.execute(query)).scalars().all()
    for task in tasks_users.tasks:
        old_task = task.__dict__
        for user in users:
            old_task['student_id'] = user.id
            print(old_task)
            res_task = Task(**old_task)
            db.add(res_task)
            await db.commit()
            await db.refresh(res_task)
    return 'OK'


@task_api.put("tasks/edit/{id_task}", response_model=TaskRead, response_model_exclude_none=True)
async def change_task_status(id_task: uuid.UUID,
                             task: TaskChange,
                             db: AsyncSession = Depends(get_async_session)):
    # query = select(Task).where(Task.id == id_task)
    query = update(Task).where(Task.id == id_task).values(task.dict(exclude_unset=True))
    old_task = (await db.execute(query)).scalars().first()
    await db.commit()
    # if old_task == None:
    #     pass
    # old_task = Task(**task.__dict__)
    # print(old_task.deadline)
    # print(old_task.id)
    # await db.commit()
    # await db.refresh(old_task)
    return TaskRead(**old_task.__dict__)