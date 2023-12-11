import time
import uuid
from typing import Optional

import jwt
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions, models
from fastapi_users.jwt import decode_jwt, generate_jwt

import config
from api.utils.generate_code_email import get_random_code
from api.utils.message_utils import send_verify_message, send_reset_message
from db.models import User
from db.session import get_user_db, redis_session

SECRET = config.SECRET


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def request_verify(self,
                             user: models.UP,
                             request: Optional[Request] = None):
        if not user.is_active:
            raise exceptions.UserInactive()
        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )
        await redis_session.set(name=token, value=get_random_code(), exat=int(time.time() + 300))
        await self.on_after_request_verify(user, token, request)
        return token

    async def verify(self,
                     token: str,
                     request: Optional[Request] = None
                     ) -> models.UP:
        try:
            data = decode_jwt(
                token,
                self.verification_token_secret,
                [self.verification_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidVerifyToken()

        try:
            user_id = data["sub"]
            email = data["email"]
        except KeyError:
            raise exceptions.InvalidVerifyToken()

        try:
            user = await self.get_by_email(email)
        except exceptions.UserNotExists:
            raise exceptions.InvalidVerifyToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidVerifyToken()

        if parsed_id != user.id:
            raise exceptions.InvalidVerifyToken()

        if user.is_verified:
            raise exceptions.UserAlreadyVerified()

        verified_user = await self._update(user, {"is_verified": True})

        await self.on_after_verify(verified_user, request)
        await redis_session.delete(token)
        return verified_user

    async def forgot_password(self,
                              user: models.UP,
                              request: Optional[Request] = None):
        if not user.is_active:
            raise exceptions.UserInactive()

        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.hashed_password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        await redis_session.set(name=token, value=get_random_code(), exat=int(time.time() + 300))
        await self.on_after_forgot_password(user, token, request)
        return token

    async def reset_password(self,
                             token: str,
                             password: str,
                             request: Optional[Request] = None) -> User:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidResetPasswordToken()

        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.hashed_password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise exceptions.InvalidResetPasswordToken()

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        await redis_session.delete(token)
        return updated_user

    async def on_after_forgot_password(self,
                                       user: User,
                                       token: str,
                                       request: Optional[Request] = None):
        code = await redis_session.get(token)
        send_reset_message(code, user.email)

    async def on_after_request_verify(self,
                                      user: User,
                                      token: str,
                                      request: Optional[Request] = None):
        code = await redis_session.get(token)
        send_verify_message(code, user.email)

    @staticmethod
    async def check_code(token: str, code: str):
        code_redis = await redis_session.get(f'{token}')
        return code_redis == code
