import uuid

from fastapi_users import FastAPIUsers, exceptions
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr
from db.models import User
from .strategy import auth_backend
from .manager import get_user_manager, UserManager

from .schemes import UserRead, UserCreate

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


@auth_api.post("/request-verify-token-with-code",
               status_code=status.HTTP_202_ACCEPTED,
               name="verify:request-token",)
async def request_verify_token(request: Request,
                               email: EmailStr = Body(..., embed=True),
                               user_manager: UserManager = Depends(get_user_manager)):
    try:
        user = await user_manager.get_by_email(email)
        token = await user_manager.request_verify(user, request)
        return {"token": token}
    except (exceptions.UserNotExists,
            exceptions.UserInactive,
            exceptions.UserAlreadyVerified):
        pass
    return None


@auth_api.post("/forgot-password-with-code",
               status_code=status.HTTP_202_ACCEPTED,
               name="reset:forgot_password",)
async def forgot_password(request: Request,
                          email: EmailStr = Body(..., embed=True),
                          user_manager: UserManager = Depends(get_user_manager),):
    try:
        user = await user_manager.get_by_email(email)
    except exceptions.UserNotExists:
        return None

    try:
        token = await user_manager.forgot_password(user, request)
        return {"token": token}
    except exceptions.UserInactive:
        pass
    return None


@auth_api.post("/check-code")
async def check_user_code(token: str = Body(..., embed=True),
                          code: str = Body(..., embed=True),
                          user_manager: UserManager = Depends(get_user_manager)):
    res = await user_manager.check_code(token, code)
    if not res:
        raise HTTPException(detail="Incorrect code", status_code=status.HTTP_400_BAD_REQUEST)
    return "Code is correct"
