import uuid

from fastapi import APIRouter, Depends, Body, HTTPException, status
from fastapi import FastAPI
from sqlalchemy import select, insert, exists, update
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
        select(models.User).options(joinedload(models.User.languages)).options(joinedload(models.User.role)).where(
            models.User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No user with id: {user_id} found')
    if profile.languages_levels:
        for note in profile.languages_levels:
            flag = await db.scalar(
                select(models.Language).where(models.Language.title == note.language))
            if not flag:
                user.languages.append(models.UserLanguage(level=note.level,
                                                          language=models.Language(title=note.language)))
            else:
                user.languages.append(models.UserLanguage(level=note.level, language_id=flag.id))

    await db.execute(
        update(models.User).where(models.User.id == user_id).values(
            **dict((filter(lambda t: t[1] is not None and t[0] != "languages_levels",
                           profile.dict().items())))))
    await db.commit()
    await db.refresh(user)
    languages_levels = await db.scalars(
        select(models.UserLanguage).options(joinedload(models.UserLanguage.language)).where(
            models.User.id == user_id))
    languages_levels_list = [LanguageLevel(language=lv.language.title, level=lv.level) for lv in languages_levels]
    return ProfileRead(**user.__dict__, languages_levels=languages_levels_list)

# def create_language_level(language_level: LanguageLevelCreate,
#                                 db: AsyncSession = Depends(get_async_session)):
#     db.add(models.LanguageLevel(**language_level.__dict__))
#     await db.commit()
# user = await db.execute(
#     select(models.User).options(joinedload(models.User.languages_level)).where(models.User.id == user_id))
# user.scalars().first().__dict__["languages_level"].append(models.LanguageLevel(language="asss", level="D3"))
# for a in user.scalars().first().__dict__["languages_level"]:
#     print(a.__dict__)
