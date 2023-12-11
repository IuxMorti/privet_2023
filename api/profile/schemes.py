import uuid
import datetime
from typing import Union, Optional
from db import models
from pydantic import BaseModel


class LanguageLevelRead(BaseModel):
    language: str
    level: str


class BuddyRead(BaseModel):
    id: uuid.UUID
    full_name: str


class StudentProfileUpdateByBuddy(BaseModel):
    study_program: Optional[str]
    last_visa_expiration: Optional[datetime.date]
    accommodation: Optional[str]
    comment: Optional[str]
    # last_arrival: Optional[datetime.date]


class ProfileUpdate(BaseModel):
    # Общее
    url_photo: Optional[str]
    full_name: Optional[str]
    sex: Optional[str]
    birthdate: Optional[datetime.date]
    university: Optional[str]
    native_language: Optional[str]
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    languages: Optional[list[LanguageLevelRead]]
    # ИС
    citizenship: Optional[str]
    # Buddy
    city: Optional[str]


class ProfileRead(BaseModel):
    # Общее
    url_photo: Optional[str]
    full_name: str
    user_role: models.Role
    email: str
    sex: Optional[str]
    birthdate: Optional[datetime.date]
    university: Optional[str]
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    native_language: Optional[str]
    languages: Optional[list[LanguageLevelRead]]
    # ИС
    citizenship: Optional[str]
    is_escort_paid: bool
    # Buddy
    city: Optional[str]
    is_confirmed_buddy: bool
    # Buddy-> ИС
    study_program: Optional[str]
    last_buddies: Optional[list[BuddyRead]]
    last_arrival: Optional[datetime.date]
    last_visa_expiration: Optional[datetime.date]
    accommodation: Optional[str]
    comment: Optional[str]
