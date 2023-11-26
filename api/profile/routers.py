import uuid

from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi import FastAPI
from sqlalchemy import select, insert, exists, update, delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from privet_2023.db import models
from privet_2023.db.session import *
from privet_2023.api.profile.schemes import *

profile_api = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@profile_api.put("/edit/{user_id}", response_model=ProfileRead)
async def update_profile(user_id: uuid.UUID, profile: ProfileUpdate, db: AsyncSession = Depends(get_async_session)):
    user = await db.scalar(select(models.User)
                           .options(joinedload(models.User.languages_levels))
                           .options(joinedload(models.User.role))
                           .options(joinedload(models.User.student_arrival))
                           .where(models.User.id == user_id))
    not_found_check(user, f'No user with id: {user_id} found')
    if user.role.title == "student" and profile.city is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user_id} can not edit city field')
    if user.role.title != "student" and profile.citizenship is not None and profile.gender is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user_id} can not edit citizenship and gender fields')
    languages_levels_list = fill_languages_levels_list(user, profile)
    for lv in [LanguageLevelRead(**el.__dict__) for el in user.languages_levels]:
        if lv not in languages_levels_list:
            await db.execute(delete(models.LanguageLevel).where(models.LanguageLevel.user_id == user.id,
                                                                models.LanguageLevel.language == lv.language,
                                                                models.LanguageLevel.level == lv.level))
    await db.execute(update(models.User).where(models.User.id == user_id).values(
        **dict(filter(lambda t: t[0] != "languages", profile.dict().items()))))
    await db.commit()
    await db.refresh(user)
    if len(languages_levels_list) == 0:
        languages_levels_list = None
    arrival = await db.scalar(select(models.Arrival).options(joinedload(models.Arrival.buddies)).where(
        models.Arrival.id == user.student_arrival_id))
    return ProfileRead(**user.__dict__, languages=languages_levels_list, last_arrival=fill_last_student_arrival(user),
                       last_buddies=fill_last_student_buddies(arrival))


@profile_api.get("/{user_id}", response_model=ProfileRead)
async def get_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    user = await db.scalar(select(models.User)
                           .options(joinedload(models.User.languages_levels))
                           .options(joinedload(models.User.student_arrival))
                           .options(joinedload(models.User.role))
                           .where(models.User.id == user_id))
    not_found_check(user, f'No user with id: {user_id} found')
    arrival = await db.scalar(select(models.Arrival).options(joinedload(models.Arrival.buddies)).where(
        models.Arrival.id == user.student_arrival_id))
    return ProfileRead(**user.__dict__, languages=fill_languages_levels_list(user),
                       last_arrival=fill_last_student_arrival(user),
                       last_buddies=fill_last_student_buddies(arrival))


@profile_api.put("/{student_id}/edit", response_model=ProfileRead)
async def update_student_profile_by_buddy(buddy_id: uuid.UUID, student_id: uuid.UUID,
                                          student_profile: StudentProfileUpdateByBuddy,
                                          db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .options(joinedload(models.Arrival.students))
                              .options(joinedload(models.Arrival.buddies))
                              .where(models.Arrival.students.any(models.User.id == student_id),
                                     models.Arrival.buddies.any(models.User.id == buddy_id)))
    not_found_check(arrival, f'No student with id: {student_id} with buddy id: {buddy_id} found')
    await db.execute(update(models.User).where(models.User.id == student_id).values(
        **dict(filter(lambda t: t[0] != "last_arrival", student_profile.dict().items()))))
    await db.commit()
    user = await db.scalar(select(models.User)
                           .options(joinedload(models.User.languages_levels))
                           .where(models.User.id == student_id))
    if student_profile.last_arrival:
        pass  # создам новый прилет
    return ProfileRead(**user.__dict__, languages=fill_languages_levels_list(user), last_arrival=arrival.date_time,
                       last_buddies=fill_last_student_buddies(arrival))


def not_found_check(essence, comment: str):
    if not essence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=comment)


def fill_last_student_arrival(user):
    if user.student_arrival:
        return user.student_arrival.date_time
    return None


def fill_last_student_buddies(arrival):
    if arrival:
        return [BuddyRead(**b.__dict__) for b in arrival.buddies]
    return None


def fill_languages_levels_list(user, profile=None):
    if not profile:
        if user.languages_levels:
            return [LanguageLevelRead(**lv.__dict__) for lv in user.languages_levels]
        return None
    languages_levels_list = []
    if profile.languages:
        for note in profile.languages:
            lv = models.LanguageLevel(user_id=user.id, language=note.language, level=note.level)
            if not any(x.user_id == user.id and x.language == note.language and x.level == note.level for x in
                       user.languages_levels):
                user.languages_levels.append(lv)
            languages_levels_list.append(LanguageLevelRead(**lv.__dict__))
    return languages_levels_list
