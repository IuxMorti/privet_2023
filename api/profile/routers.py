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


@profile_api.put("/profile/{user_id}", response_model=ProfileRead)
async def update_profile(user_id: uuid.UUID, profile: ProfileUpdate, db: AsyncSession = Depends(get_async_session)):
    user = await db.scalar(
        select(models.User).options(joinedload(models.User.languages_levels)).options(
            joinedload(models.User.role)).where(
            models.User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No user with id: {user_id} found')
    languages_levels_list = []
    if profile.languages:
        for note in profile.languages:
            lv = models.LanguageLevel(user_id=user.id, language=note.language, level=note.level)
            if not any(x.user_id == user.id and x.language == note.language and x.level == note.level for x in
                       user.languages_levels):
                user.languages_levels.append(lv)
            languages_levels_list.append(LanguageLevel(**lv.__dict__))
    if user.role.title == "student" and profile.city is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user_id} can not edit city field')
    if user.role.title != "student" and profile.citizenship is not None and profile.gender is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user_id} can not edit citizenship and gender fields')
    await db.execute(update(models.User).where(models.User.id == user_id).values(
        **dict(filter(lambda t: t[0] != "languages", profile.dict().items()))))
    await db.commit()
    await db.refresh(user)
    return ProfileRead(**user.__dict__, languages=languages_levels_list)


@profile_api.put("/profile/{student_id}/edit", response_model=ProfileRead)
async def update_student_profile(buddy_id: uuid.UUID, student_id: uuid.UUID, student_profile: ProfileUpdate,
                                 db: AsyncSession = Depends(get_async_session)):
    pass
# def create_language_level(language_level: LanguageLevelCreate,
#                                 db: AsyncSession = Depends(get_async_session)):
#     db.add(models.LanguageLevel(**language_level.__dict__))
#     await db.commit()
# user = await db.execute(
#     select(models.User).options(joinedload(models.User.languages_level)).where(models.User.id == user_id))
# user.scalars().first().__dict__["languages_level"].append(models.LanguageLevel(language="asss", level="D3"))
# for a in user.scalars().first().__dict__["languages_level"]:
#     print(a.__dict__)
