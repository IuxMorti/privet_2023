import uuid

from fastapi_users import FastAPIUsers, exceptions
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_users.router import ErrorCode
from starlette import status
from db.models import User
from .strategy import auth_backend
from .manager import get_user_manager, UserManager

from .schemes import UserRead, UserCreate, UserUpdate

auth_api = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

auth_api.include_router(fastapi_users.get_verify_router(UserRead))
auth_api.include_router(fastapi_users.get_reset_password_router())
auth_api.include_router(fastapi_users.get_auth_router(auth_backend))
auth_api.include_router(fastapi_users.get_register_router(UserRead, UserCreate))


@auth_api.post("/check-code")
async def reset_password(
        token: str = Body(..., embed=True),
        user_manager: UserManager = Depends(get_user_manager), ):
    try:
        await user_manager.check_code(token, "password_fgpt")
        return "Код валиден"
    except (
            exceptions.InvalidResetPasswordToken,
            exceptions.UserNotExists,
            exceptions.UserInactive,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
