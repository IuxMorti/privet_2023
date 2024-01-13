# from api.utils.arrival_utils import *
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from api.arrival import schemes
from api.arrival.functions import make_arrival_read
from api.auth.routers import fastapi_users
from api.utils.exceptions import is_confirmed_buddy_check, is_right_role_check, can_create_arrival_check, is_found_check
from api.utils.generate_code_email import get_random_code
from api.task.functions import create_tasks_for_user
from db import models
from db.session import get_async_session

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import select, insert, exists, update, delete

arrival_api = APIRouter(
    prefix="/arrival",
    tags=["Arrival"]
)


@arrival_api.post("/pay", status_code=status.HTTP_200_OK)
async def pay_for_arrival(
        user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
        db: AsyncSession = Depends(get_async_session)
):
    query = update(models.User).where(models.User.id == user.id).values(is_escort_paid=True)
    await db.execute(query)
    await db.commit()


@arrival_api.post("/my", status_code=status.HTTP_201_CREATED)
async def create_arrival(arrival_info: schemes.ArrivalCreate,
                         user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
                         db: AsyncSession = Depends(get_async_session)):
    can_create_arrival_check(user)
    arrival = models.Arrival(**dict(filter(lambda t: t[0] != "students", arrival_info.dict().items())))
    arrival.number = str(arrival_info.date_time.date()).replace("-", "")[2:] + get_random_code()
    db.add(arrival)
    await db.flush()
    db.add(models.StudentArrival(student_id=user.id, arrival_id=arrival.id))
    if arrival_info.students:
        for student_id in arrival_info.students:
            st = await db.scalar(select(models.User).where(models.User.id == student_id))
            can_create_arrival_check(st)
            db.add(models.StudentArrival(student_id=student_id, arrival_id=arrival.id))
            await create_tasks_for_user(arrival.id, student_id, db)
    await create_tasks_for_user(arrival.id, user.id, db)
    await db.commit()


@arrival_api.get("/{arrival_id}", response_model=schemes.ArrivalRead)
async def get_arrival(arrival_id: uuid.UUID,
                      db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    is_found_check(arrival)
    return make_arrival_read(arrival)


@arrival_api.get("", response_model=schemes.ArrivalRead)
async def get_arrival_by_number(arrival_number: str, db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.number == arrival_number))
    is_found_check(arrival)
    return make_arrival_read(arrival)


@arrival_api.put("/join/{arrival_id}", status_code=status.HTTP_200_OK)
async def join_buddy_to_arrival(arrival_id: uuid.UUID,
                                user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
                                db: AsyncSession = Depends(get_async_session)):
    is_confirmed_buddy_check(user)
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    if arrival.status.value != models.ArrivalStatus.awaiting_approval.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Arrival with id:{arrival.id} must be with status: awaiting_approval, but was: {arrival.status}')
    buddy_count = len(arrival.buddies)
    student_count = len(arrival.students)
    if (buddy_count == 2) or (buddy_count == 1 and student_count < 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'arrival with id: {arrival.id} is full')
    db.add(models.BuddyArrival(buddy_id=user.id, arrival_id=arrival.id))
    await db.commit()


@arrival_api.put("/add_buddies/{arrival_id}/", status_code=status.HTTP_200_OK)
async def add_buddies_to_arrival_by_team_leader(arrival_id: uuid.UUID,
                                                buddies: list[uuid.UUID],
                                                user: models.User = Depends(
                                                    fastapi_users.current_user(active=True, verified=True)),
                                                db: AsyncSession = Depends(get_async_session)):
    is_right_role_check(user, models.Role.team_leader)
    for buddy_id in buddies:
        bu = await db.scalar(select(models.User).where(models.User.id == buddy_id))
        is_confirmed_buddy_check(bu)
        db.add(models.BuddyArrival(buddy_id=buddy_id, arrival_id=arrival_id))
    await db.commit()


@arrival_api.put("/activate/{arrival_id}", status_code=status.HTTP_200_OK)
async def make_arrival_status_active(arrival_id: uuid.UUID,
                                     user: models.User = Depends(
                                         fastapi_users.current_user(active=True, verified=True)),
                                     db: AsyncSession = Depends(get_async_session)):
    is_right_role_check(user, models.Role.team_leader)
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    is_found_check(arrival)
    if arrival.status.value != models.ArrivalStatus.awaiting_approval.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            f'Arrival with id:{arrival.id} must be with status: {models.ArrivalStatus.awaiting_approval}')
    arrival.status = models.ArrivalStatus.active
    await db.commit()


@arrival_api.get("s", response_model=list[schemes.ArrivalRead])
async def get_all_arrivals(db: AsyncSession = Depends(get_async_session)):
    arrivals = await db.scalars(select(models.Arrival))
    return [make_arrival_read(arrival) for arrival in arrivals]


@arrival_api.delete("/{arrival_id}", status_code=status.HTTP_200_OK)
async def leave_arrival(arrival_id: uuid.UUID,
                        user: models.User = Depends(
                            fastapi_users.current_user(active=True, verified=True)),
                        db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    is_found_check(arrival)
    if arrival.status.value != models.ArrivalStatus.awaiting_approval.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'to leave from arrival status must be {models.ArrivalStatus.awaiting_approval.value}')
    if user.is_confirmed_buddy:
        await db.execute(delete(models.BuddyArrival)
                         .where(models.BuddyArrival.arrival_id == arrival_id,
                                models.BuddyArrival.buddy_id == user.id))
    else:
        await db.execute(delete(models.StudentArrival)
                         .where(models.StudentArrival.arrival_id == arrival_id,
                                models.StudentArrival.student_id == user.id))
        await db.execute(
            delete(models.Task).where(models.Task.student_id == user.id, models.Task.arrival_id == arrival_id))
        if len(arrival.students) == 1:
            await db.execute(delete(models.Arrival).where(models.Arrival.id == arrival_id))
    await db.commit()


@arrival_api.delete("/{arrival_id}/{buddy_id}", status_code=status.HTTP_200_OK)
async def delete_buddy_from_arrival(arrival_id: uuid.UUID,
                                    buddy_id: uuid.UUID,
                                    user: models.User = Depends(
                                        fastapi_users.current_user(active=True, verified=True)),
                                    db: AsyncSession = Depends(get_async_session)):
    is_right_role_check(user, models.Role.team_leader)
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    is_found_check(arrival)
    buddy = await db.scalar(select(models.User).where(models.User.id == buddy_id))
    is_confirmed_buddy_check(buddy)
    await db.execute(delete(models.BuddyArrival)
                     .where(models.BuddyArrival.arrival_id == arrival_id,
                            models.BuddyArrival.buddy_id == buddy.id))
    await db.commit()
