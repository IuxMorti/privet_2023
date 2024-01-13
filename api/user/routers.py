import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.routers import fastapi_users
from api.auth.schemes import UserRead, UserUpdate
from api.utils.exceptions import is_valid_role, is_found_check, is_confirmed_buddy_check, is_right_role_check
from api.user import schemes
from api.user.functions import fill_last_student_arrival, fill_last_student_buddies, fill_languages_levels_list
from db import models
from db.session import get_async_session

user_api = APIRouter(
    prefix="/user",
    tags=["user"]
)
user_api.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))


@user_api.get("/profile/my", response_model=schemes.ProfileRead)
async def get_current_profile(user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
                              db: AsyncSession = Depends(get_async_session)):
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.students.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    return schemes.ProfileRead(**user.__dict__,
                               user_role=user.role.value,
                               languages=fill_languages_levels_list(user),
                               last_arrival=fill_last_student_arrival(user),
                               last_buddies=fill_last_student_buddies(user, arrival))


@user_api.get("/profile/{user_id}", response_model=schemes.ProfileRead)
async def get_profile(user_id: uuid.UUID, db: AsyncSession = Depends(get_async_session)):
    user = await db.scalar(select(models.User).where(models.User.id == user_id))
    is_found_check(user)
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.students.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    return schemes.ProfileRead(**user.__dict__,
                               user_role=user.role.value,
                               languages=fill_languages_levels_list(user),
                               last_arrival=fill_last_student_arrival(user),
                               last_buddies=fill_last_student_buddies(user, arrival))


@user_api.get("/list/{full_name}", response_model=list[schemes.UserRead])
async def get_users_by_full_name(full_name: str,
                                 db: AsyncSession = Depends(get_async_session)):
    users = await db.scalars(select(models.User).where(models.User.full_name == full_name))
    return [schemes.UserRead(**user.__dict__, user_role=user.role.value) for user in users]


@user_api.put("/profile/my", response_model=schemes.ProfileRead)
async def update_current_profile(profile: schemes.ProfileUpdate,
                                 user: models.User = Depends(fastapi_users.current_user(active=True, verified=True)),
                                 db: AsyncSession = Depends(get_async_session)):
    if user.role.value == models.Role.student.value and profile.city is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} can not edit city field')
    if not user.role.value == models.Role.student.value and profile.citizenship is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} can not edit citizenship field')
    if profile.languages:
        for note in profile.languages:
            lv = models.LanguageLevel(user_id=user.id, language=note.language, level=note.level)
            if not any(x.user_id == user.id and x.language == note.language and x.level == note.level for x in
                       user.languages_levels):
                db.add(lv)
    for lv in [schemes.LanguageLevelRead(**el.__dict__) for el in user.languages_levels]:
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
    return schemes.ProfileRead(**user.__dict__,
                               user_role=user.role.value,
                               last_arrival=fill_last_student_arrival(user),
                               last_buddies=fill_last_student_buddies(user, arrival))


@user_api.put("/profile/{student_id}", response_model=schemes.ProfileRead)
async def update_student_profile_by_buddy(student_id: uuid.UUID,
                                          student_profile: schemes.StudentProfileUpdateByBuddy,
                                          user: models.User = Depends(
                                              fastapi_users.current_user(active=True, verified=True)),
                                          db: AsyncSession = Depends(get_async_session)):
    student = await db.scalar(select(models.User)
                              .where(models.User.id == student_id))
    is_confirmed_buddy_check(user)
    is_right_role_check(student, models.Role.student)
    arrival = await db.scalar(select(models.Arrival)
                              .where(models.Arrival.students.any(models.User.id == student_id),
                                     models.Arrival.buddies.any(models.User.id == user.id))
                              .order_by(models.Arrival.date_time.desc()))
    is_found_check(arrival)
    student.__dict__.update(student_profile.__dict__)
    await db.execute(update(models.User).where(models.User.id == student_id).values(**student_profile.__dict__))
    await db.commit()
    return schemes.ProfileRead(**student.__dict__,
                               user_role=student.role.value,
                               languages=fill_languages_levels_list(student),
                               last_arrival=fill_last_student_arrival(student),
                               last_buddies=fill_last_student_buddies(student, arrival))


@user_api.put("/confirm/{maintainer_id}", status_code=status.HTTP_200_OK)
async def confirm_maintainer(maintainer_id: uuid.UUID,
                             user: models.User = Depends(
                                 fastapi_users.current_user(active=True, verified=True)),
                             db: AsyncSession = Depends(get_async_session)):
    is_right_role_check(user, models.Role.team_leader)
    maintainer = await db.scalar(select(models.User)
                                 .where(models.User.id == maintainer_id))
    is_right_role_check(maintainer, models.Role.maintainer)
    maintainer.is_confirmed_buddy = True
    await db.commit()


@user_api.post("/upload-profile-image")
async def upload_profile_image(
        file: UploadFile = File(...),
        user: models.User = Depends(
            fastapi_users.current_user(active=True, verified=True)),
        db: AsyncSession = Depends(get_async_session)):
    if file.filename.split('.')[-1] not in ['png', 'jpg', 'jpeg']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'incorrect format image')
    cwd = os.getcwd()
    path_image_dir = "upload_files/user/profile/" + str(user.id) + "/"
    full_image_path = os.path.join(str(cwd), path_image_dir, file.filename)
    # Create directory if not exist
    if not os.path.exists(path_image_dir):
        os.makedirs(path_image_dir)

    # Rename file to 'profile.png'
    file_name = full_image_path.replace(file.filename, "profile.png")

    # Write file
    with open(file_name, 'wb+') as f:
        f.write(file.file.read())
        f.flush()
        f.close()

    await db.execute(update(models.User)
                     .where(models.User.id == user.id)
                     .values({"url_photo": os.path.join(path_image_dir, "profile.png")}))
    await db.commit()

    return {
        "profile_image": os.path.join(path_image_dir, "profile.png")
    }


@user_api.get("/profile/img")
async def get_profile_image(
        user: models.User = Depends(
            fastapi_users.current_user(active=True, verified=True))):
    cwd = os.getcwd()
    full_image_path = os.path.join(str(cwd), user.url_photo)
    return FileResponse(path=full_image_path)
