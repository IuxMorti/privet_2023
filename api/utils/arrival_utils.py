from privet_2023.api.arrival.schemes import *
from privet_2023.api.profile.schemes import *


def make_arrival_read(arrival):
    user_list = []
    citizenship_list = set()
    for user in arrival.users:
        user_list.append(UserRead(**user.__dict__))
        if user.role.value == models.Role.student.value:
            citizenship_list.add(user.citizenship)
    return ArrivalRead(**arrival.__dict__,
                       arrival_users=user_list,
                       citizenship=citizenship_list)
