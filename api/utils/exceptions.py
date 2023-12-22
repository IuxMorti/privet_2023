from fastapi import HTTPException, status
from db import models


def is_valid_role(user: models.User, role: models.Role):
    is_found_check(user)
    return user.role.value == role.value


def check(verification_condition: bool, status_code, detail):
    if verification_condition:
        raise HTTPException(status_code=status_code,
                            detail=detail)


def is_found_check(model):
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


def is_right_role_check(user: models.User, role: models.Role):
    is_found_check(user)
    if not user.role.value == role.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} was {user.role.value} but must be {role.value}')


def is_confirmed_buddy_check(user: models.User):
    is_found_check(user)
    if not user.is_confirmed_buddy:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} is not confirmed buddy')


def can_create_arrival_check(user: models.User):
    is_found_check(user)
    if not user.is_escort_paid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'User with id:{user.id} must pay to get access')
    if user.student_arrivals and user.student_arrivals[0].status.value != models.ArrivalStatus.completed.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'user with id: {user.id} already has an active arrival')
