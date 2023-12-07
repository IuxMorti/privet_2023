from privet_2023.db import models
from privet_2023.api.arrival.schemes import *
from privet_2023.api.profile.schemes import *


def fill_last_student_arrival(user, arrival):
    if arrival and user.role.value == models.Role.student.value:
        return arrival.date_time
    return None


def fill_last_student_buddies(user, arrival):
    if arrival and user.role.value == models.Role.student.value:
        return [BuddyRead(**b.__dict__) for b in arrival.users if b.role.value != models.Role.student.value]
    return None


def fill_languages_levels_list(user, profile=None):
    if not profile:
        if user.languages_levels:
            return [LanguageLevelRead(**lv.__dict__) for lv in user.languages_levels]
        return None
    languages_levels_list = []
    if profile.languages:
        for note in profile.languages:
            lv = models.LanguageLevel(user_id=user.id, language=note.language, level=note.level)
            if not any(x.user_id == user.id and x.language == note.language and x.level == note.level for x in
                       user.languages_levels):
                user.languages_levels.append(lv)
            languages_levels_list.append(LanguageLevelRead(**lv.__dict__))
    return languages_levels_list
