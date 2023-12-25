from db import models
from api.user import schemes
from api.utils.exceptions import is_valid_role


def fill_last_student_arrival(user):
    if is_valid_role(user, models.Role.student) and user.student_arrivals:
        return user.student_arrivals[0].date_time
    return None


def fill_last_student_buddies(user, arrival):
    if arrival and is_valid_role(user, models.Role.student):
        return [schemes.UserRead(**b.__dict__, user_role=b.role.value) for b in arrival.buddies]
    return None


def fill_languages_levels_list(user):
    if user.languages_levels:
        return [schemes.LanguageLevelRead(**lv.__dict__) for lv in user.languages_levels]
    return None
