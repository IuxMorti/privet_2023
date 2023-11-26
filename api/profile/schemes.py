import uuid
import datetime
from typing import Union, Optional

from pydantic import BaseModel


class LanguageLevelRead(BaseModel):
    language: str
    level: str


class BuddyRead(BaseModel):
    id: uuid.UUID
    full_name: str


class StudentProfileUpdateByBuddy(BaseModel):
    study_direction: Optional[str]
    last_arrival: Optional[datetime.date]
    visa_end_date: Optional[datetime.date]
    living_place: Optional[str]
    comment: Optional[str]


class ProfileUpdate(BaseModel):
    # Общее
    url_photo: Optional[str]
    full_name: Optional[str]
    birthdate: Optional[datetime.date]
    institute: Optional[str]
    native_language: Optional[str]
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    languages: Optional[list[LanguageLevelRead]]
    # ИС
    citizenship: Optional[str]
    gender: Optional[str]
    # Buddy
    city: Optional[str]


class ProfileRead(BaseModel):
    # Общее
    url_photo: Optional[str]
    full_name: str
    email: str
    birthdate: Optional[datetime.date]
    institute: Optional[str]
    phone: Optional[str]
    telegram: Optional[str]
    whatsapp: Optional[str]
    vk: Optional[str]
    native_language: Optional[str]
    languages: Optional[list[LanguageLevelRead]]
    # ИС
    citizenship: Optional[str]
    gender: Optional[str]
    payment_status: bool
    # Buddy
    city: Optional[str]
    buddy_active: bool
    # Buddy-> ИС
    study_direction: Optional[str]
    last_buddies: Optional[list[BuddyRead]]
    last_arrival: Optional[datetime.date]
    visa_end_date: Optional[datetime.date]
    living_place: Optional[str]
    comment: Optional[str]
