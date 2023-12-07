from privet_2023.api.utils.arrival_utils import *
from privet_2023.api.auth.routers import fastapi_users
from privet_2023.api.utils.error_check import *
from privet_2023.db.session import *

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import select, insert, exists, update, delete

arrival_api = APIRouter(
    prefix="/arrival",
    tags=["Arrival"]
)


@arrival_api.post("/my", status_code=status.HTTP_201_CREATED)
async def create_arrival(arrival_info: ArrivalCreate,
                         student: models.User = Depends(fastapi_users.current_user(active=True)),
                         db: AsyncSession = Depends(get_async_session)):
    check(not student.payment_status, status.HTTP_403_FORBIDDEN, f'User with id:{student.id} must pay to get access')
    arrival = models.Arrival(**dict(filter(lambda t: t[0] != "students", arrival_info.dict().items())))
    arrival.number = str(arrival_info.date_time.date()).replace("-", "")
    db.add(arrival)
    await db.flush()
    db.add(models.UserArrival(user_id=student.id, arrival_id=arrival.id))
    if arrival_info.students:
        for student_id in arrival_info.students:
            st = await db.scalar(select(models.User).where(models.User.id == student_id))
            check(not st.payment_status, status.HTTP_403_FORBIDDEN,
                  f'User with id:{student_id} must pay to get access')
            db.add(models.UserArrival(user_id=student_id, arrival_id=arrival.id))
    await db.commit()


@arrival_api.put("/join/{arrival_id}", status_code=status.HTTP_200_OK)
async def join_buddy_to_arrival(arrival_id: uuid.UUID,
                                buddy: models.User = Depends(fastapi_users.current_user(active=True)),
                                db: AsyncSession = Depends(get_async_session)):
    check(buddy.role.value == models.Role.student.value, status.HTTP_403_FORBIDDEN,
          f'User with id:{buddy.id} must be buddy')
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    check(arrival.status.value != models.ArrivalStatus.awaiting_approval.value, status.HTTP_403_FORBIDDEN,
          f'Arrival with id:{arrival.id} must be with status: awaiting_approval, but was: {arrival.status}')
    buddy_count = 0
    student_count = 0
    for user in arrival.users:
        if user.role.value == models.Role.student.value:
            student_count += 1
        else:
            buddy_count += 1
    check((buddy_count == 2) or (buddy_count == 1 and student_count < 3), status.HTTP_403_FORBIDDEN, "arrival is full")
    db.add(models.UserArrival(user_id=buddy.id, arrival_id=arrival.id))
    await db.commit()


@arrival_api.put("/add_buddies/{arrival_id}/", status_code=status.HTTP_200_OK)
async def add_buddies_to_arrival_by_team_leader(arrival_id: uuid.UUID,
                                                buddies: list[uuid.UUID],
                                                team_leader: models.User = Depends(
                                                    fastapi_users.current_user(active=True)),
                                                db: AsyncSession = Depends(get_async_session)):
    check(team_leader.role.value != models.Role.team_leader.value, status.HTTP_403_FORBIDDEN,
          f'User with id:{team_leader.id} must be team_leader')
    for buddy_id in buddies:
        bu = await db.scalar(select(models.User).where(models.User.id == buddy_id))
        check(bu.role.value == models.Role.student.value, status.HTTP_403_FORBIDDEN,
              f'User with id:{team_leader.id} must be buddy')
        db.add(models.UserArrival(user_id=buddy_id, arrival_id=arrival_id))
    await db.commit()


@arrival_api.put("/activate/{arrival_id}", status_code=status.HTTP_200_OK)
async def make_arrival_status_active(arrival_id: uuid.UUID,
                                     team_leader: models.User = Depends(fastapi_users.current_user(active=True)),
                                     db: AsyncSession = Depends(get_async_session)):
    check(team_leader.role.value != models.Role.team_leader.value, status.HTTP_403_FORBIDDEN,
          f'User with id:{team_leader.id} must be team_leader')
    await db.execute(
        update(models.Arrival).where(models.Arrival.id == arrival_id).values(status=models.ArrivalStatus.active))
    await db.commit()


@arrival_api.get("/{arrival_id}", response_model=ArrivalRead)
async def get_arrival(arrival_id: uuid.UUID,
                      db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.id == arrival_id))
    check(not arrival, status.HTTP_404_NOT_FOUND, f'arrival with id:{arrival_id} not found')
    return make_arrival_read(arrival)


@arrival_api.get("", response_model=list[ArrivalRead])
async def get_all_arrivals(db: AsyncSession = Depends(get_async_session)):
    arrivals = await db.scalars(select(models.Arrival))
    return [make_arrival_read(arrival) for arrival in arrivals]
