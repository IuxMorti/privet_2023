from privet_2023.db import models
from privet_2023.api.arrival.schemes import *
from privet_2023.api.profile.schemes import *


def fill_last_student_arrival(user, arrival):
    if arrival and user.role.value == models.Role.student.value:
        return arrival.date_time
    return None


def fill_last_student_buddies(user, arrival):
    if arrival and user.role.value == models.Role.student.value:
        return [BuddyRead(**b.__dict__) for b in arrival.buddies]
    return None


def fill_languages_levels_list(user):
    if user.languages_levels:
        return [LanguageLevelRead(**lv.__dict__) for lv in user.languages_levels]
    return None
