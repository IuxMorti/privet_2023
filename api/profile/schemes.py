import uuid
import datetime
from typing import Union, Optional

from pydantic import BaseModel


class LanguageLevel(BaseModel):
    language: str
    level: str


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
    languages_levels: Optional[list[LanguageLevel]]
    # ИС
    citizenship: Optional[str]
    gender: Optional[str]
    # Buddy
    study_direction: Optional[str]
    visa_end_date: Optional[datetime.date]
    living_place: Optional[str]
    comment: Optional[str]


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
    languages_levels: Optional[list[LanguageLevel]]
    # ИС
    citizenship: Optional[str]
    gender: Optional[str]
    payment_status: bool
    # Buddy
    study_direction: Optional[str]
    # last_buddy: Optional[str]
    # last_arrival: Optional[datetime.date]
    # last_visa_date_end: Optional[datetime.date]
    living_place: Optional[str]
    comment: Optional[str]
