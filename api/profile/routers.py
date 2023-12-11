from api.auth.routers import fastapi_users
from api.utils.profile_utils import *
from api.utils.error_check import *

from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy import select, insert, exists, update, delete

from db.session import *
from api.profile.schemes import *

profile_api = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@profile_api.put("/my", response_model=ProfileRead)
async def update_profile(profile: ProfileUpdate,
                         user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
                         db: AsyncSession = Depends(get_async_session)):
    check(user.role.value == models.Role.student.value and profile.city is not None, status.HTTP_403_FORBIDDEN,
          f'user with id: {user.id} can not edit city field')
    check(user.role.value != models.Role.student.value and profile.citizenship is not None, status.HTTP_403_FORBIDDEN,
          f'user with id: {user.id} can not edit citizenship field')
    if profile.languages:
        for note in profile.languages:
            lv = models.LanguageLevel(user_id=user.id, language=note.language, level=note.level)
            if not any(x.user_id == user.id and x.language == note.language and x.level == note.level for x in
                       user.languages_levels):
                db.add(lv)
    for lv in [LanguageLevelRead(**el.__dict__) for el in user.languages_levels]:
        if not profile.languages or lv not in profile.languages:
            await db.execute(delete(models.LanguageLevel)
                             .where(models.LanguageLevel.user_id == user.id,
                                    models.LanguageLevel.language == lv.language,
                                    models.LanguageLevel.level == lv.level))
    await db.execute(update(models.User).where(models.User.id == user.id).values(
        **dict(filter(lambda t: t[0] != "languages", profile.dict().items()))))
    await db.commit()
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.students.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    user.__dict__.update(profile.__dict__)
    return ProfileRead(**user.__dict__,
                       user_role=user.role.value,
                       last_arrival=fill_last_student_arrival(user, arrival),
                       last_buddies=fill_last_student_buddies(user, arrival))


@profile_api.get("/my", response_model=ProfileRead)
async def get_profile(user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
                      db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.students.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    return ProfileRead(**user.__dict__,
                       user_role=user.role.value,
                       languages=fill_languages_levels_list(user),
                       last_arrival=fill_last_student_arrival(user, arrival),
                       last_buddies=fill_last_student_buddies(user, arrival))


@profile_api.put("/{student_id}", response_model=ProfileRead)
async def update_student_profile_by_buddy(student_id: uuid.UUID,
                                          student_profile: StudentProfileUpdateByBuddy,
                                          buddy: models.User = Depends(
                                              fastapi_users.current_user(active=True, verified=True)),
                                          db: AsyncSession = Depends(get_async_session)):
    student = await db.scalar(select(models.User)
                              .where(models.User.id == student_id))
    check(buddy.role.value == models.Role.student.value
          or (buddy.role.value == models.Role.student.maintainer and not buddy.is_confirmed_buddy)
          or student.role.value != models.Role.student.value,
          status.HTTP_403_FORBIDDEN,
          f'User with id: {buddy.id} is not confirmed buddy or user wit id {student_id} is not student')
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.students.any(models.User.id == student_id),
                                     models.Arrival.buddies.any(models.User.id == buddy.id))
                              .order_by(models.Arrival.date_time.desc()))
    check(not arrival, status.HTTP_403_FORBIDDEN,
          f'User with id: {buddy.id} is not last buddy of user with id: {student_id}')
    student.__dict__.update(student_profile.__dict__)
    await db.execute(update(models.User).where(models.User.id == student_id).values(**student_profile.__dict__))
    await db.commit()
    await db.refresh(student)
    return ProfileRead(**student.__dict__,
                       user_role=student.role.value,
                       languages=fill_languages_levels_list(student),
                       last_arrival=fill_last_student_arrival(student, arrival),
                       last_buddies=fill_last_student_buddies(student, arrival))


@profile_api.put("/activate/{maintainer_id}", status_code=status.HTTP_200_OK)
async def confirm_maintainer(maintainer_id: uuid.UUID,
                             team_leader: models.User = Depends(
                                 fastapi_users.current_user(active=True, verified=True)),
                             db: AsyncSession = Depends(get_async_session)):
    maintainer = await db.scalar(select(models.User)
                                 .where(models.User.id == maintainer_id))
    check(
        team_leader.role.value != models.Role.team_leader.value or maintainer.role.value != models.Role.maintainer.value,
        status.HTTP_403_FORBIDDEN,
        f'user with id: {maintainer_id} is mot maintainer or user with id: {team_leader.id} is not team_leader')
    maintainer.is_confirmed_buddy = True
    await db.commit()
