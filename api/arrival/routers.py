from privet_2023.api.auth.routers import fastapi_users
from privet_2023.api.arrival.schemes import *
from privet_2023.api.functions import *

arrival_api = APIRouter(
    prefix="/arrival",
    tags=["Arrival"]
)


@arrival_api.post("/my/create", status_code=status.HTTP_201_CREATED)
async def create_arrival(arrival_info: ArrivalCreate,
                         user: models.User = Depends(fastapi_users.current_user(active=True)),
                         db: AsyncSession = Depends(get_async_session)):
    not_found_check(user.payment_status, f'User with id:{user.id} must pay to get access')
    arrival = models.Arrival(**dict(filter(lambda t: t[0] != "students", arrival_info.dict().items())))
    print(type(arrival.users))
    db.add(arrival)
    await db.commit()
    await db.refresh(arrival)
    print(arrival.id)
    user_arrival = models.UserArrival(user_id=user.id, arrival_id=arrival.id)
    db.add(user_arrival)
    await db.commit()
    # db.add(models.UserArrival(user_id=user.id, arrival_id=arrival.id))
    # await db.commit()
    # СДЕЛАТЬ ПРИГЛАШЕНИЯ
    # await db.flush()
    # for student_id in arrival_info.students:
    #     put = await db.execute(update(models.User)
    #                            .where(models.User.id == student_id,
    #                                   models.User.payment_status)
    #                            .values(student_arrival_id=arrival.id))
    #     if put.rowcount == 0:
    #         not_found_check(None, f'User with id: {student_id} not found or did not pay')
    print(arrival.__dict__)
    # await db.refresh(arrival)

# @arrival_api.put("/edit/{user_id}", response_model=ProfileRead)
