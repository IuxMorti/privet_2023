# import uuid
#
# from fastapi import APIRouter, Depends, Body, HTTPException, status
# from fastapi import FastAPI
# from sqlalchemy import select, insert, exists, update, delete
# from sqlalchemy.orm import joinedload, selectinload
# from sqlalchemy.exc import IntegrityError
# from starlette.responses import JSONResponse
#
# from privet_2023.api.arrival.schemes import *
# from privet_2023.db import models
# from privet_2023.db.session import *
# from privet_2023.api.profile.schemes import *
#
#
# def check(verification_condition: bool, status_code, detail):
#     if verification_condition:
#         raise HTTPException(status_code=status_code,
#                             detail=detail)
#
#
# def fill_last_student_arrival(user, arrival):
#     if arrival and user.role.value == models.Role.student.value:
#         return arrival.date_time
#     return None
#
#
# def fill_last_student_buddies(user, arrival):
#     if arrival and user.role.value == models.Role.student.value:
#         return [BuddyRead(**b.__dict__) for b in arrival.users if b.role.value != models.Role.student.value]
#     return None
#
#
# def fill_languages_levels_list(user, profile=None):
#     if not profile:
#         if user.languages_levels:
#             return [LanguageLevelRead(**lv.__dict__) for lv in user.languages_levels]
#         return None
#     languages_levels_list = []
#     if profile.languages:
#         for note in profile.languages:
#             lv = models.LanguageLevel(user_id=user.id, language=note.language, level=note.level)
#             if not any(x.user_id == user.id and x.language == note.language and x.level == note.level for x in
#                        user.languages_levels):
#                 user.languages_levels.append(lv)
#             languages_levels_list.append(LanguageLevelRead(**lv.__dict__))
#     return languages_levels_list
#
#
# def make_arrival_read(arrival):
#     user_list = []
#     citizenship_list = set()
#     for user in arrival.users:
#         user_list.append(UserRead(**user.__dict__))
#         if user.role.value == models.Role.student.value:
#             citizenship_list.add(user.citizenship)
#     return ArrivalRead(**arrival.__dict__,
#                        arrival_users=user_list,
#                        citizenships=citizenship_list)
