from api.auth.routers import fastapi_users
from api.functions import *
from api.profile.schemes import *
from db import models
from db.session import *
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update, delete


profile_api = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@profile_api.put("/edit/my", response_model=ProfileRead)
async def update_profile(profile: ProfileUpdate,
                         current_user: models.User = Depends(fastapi_users.current_user(active=True)),
                         db: AsyncSession = Depends(get_async_session)):
    user = await db.scalar(select(models.User).where(models.User.id == current_user.id))
    if user.role.value == models.Role.student.value and profile.city is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} can not edit city field')
    if user.role.value != models.Role.student.value and profile.citizenship is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} can not edit citizenship field')
    languages_levels_list = fill_languages_levels_list(user, profile)
    for lv in [LanguageLevelRead(**el.__dict__) for el in user.languages_levels]:
        if lv not in languages_levels_list:
            await db.execute(delete(models.LanguageLevel)
                             .where(models.LanguageLevel.user_id == user.id,
                                    models.LanguageLevel.language == lv.language,
                                    models.LanguageLevel.level == lv.level))
    await db.execute(update(models.User).where(models.User.id == user.id).values(
        **dict(filter(lambda t: t[0] != "languages", profile.dict().items()))))
    await db.commit()
    await db.refresh(user)
    if len(languages_levels_list) == 0:
        languages_levels_list = None
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.users.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    return ProfileRead(**user.__dict__,
                       languages=languages_levels_list,
                       last_arrival=fill_last_student_arrival(user, arrival),
                       last_buddies=fill_last_student_buddies(user, arrival))


@profile_api.get("/my", response_model=ProfileRead)
async def get_profile(user: models.User = Depends(fastapi_users.current_user(active=True)),
                      db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.users.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    return ProfileRead(**user.__dict__,
                       languages=fill_languages_levels_list(user),
                       last_arrival=fill_last_student_arrival(user, arrival),
                       last_buddies=fill_last_student_buddies(user, arrival))


@profile_api.put("/edit/{student_id}", response_model=ProfileRead)
async def update_student_profile_by_buddy(student_id: uuid.UUID,
                                          student_profile: StudentProfileUpdateByBuddy,
                                          buddy: models.User = Depends(fastapi_users.current_user(active=True)),
                                          db: AsyncSession = Depends(get_async_session)):
    not_found_check(buddy.role.value != models.Role.student.value, f'User with id: {buddy.id} is not buddy')
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.users.any(models.User.id == student_id))
                              .order_by(models.Arrival.date_time.desc()))
    buddy_found = False
    if arrival:
        for user in arrival.users:
            if user.role.value != models.Role.student.value and user.id == buddy.id and user.id != student_id:
                buddy_found = True
    not_found_check(buddy_found, f'User with id: {buddy.id} is not last buddy of user with id: {student_id}')
    await db.execute(update(models.User).where(models.User.id == student_id).values(**student_profile.__dict__))
    await db.commit()
    user = await db.scalar(select(models.User)
                           .where(models.User.id == student_id))
    return ProfileRead(**user.__dict__,
                       languages=fill_languages_levels_list(user),
                       last_arrival=fill_last_student_arrival(user, arrival),
                       last_buddies=fill_last_student_buddies(user, arrival))
