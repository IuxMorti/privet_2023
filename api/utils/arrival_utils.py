from api.arrival.schemes import *
from api.profile.schemes import *


def make_arrival_read(arrival):
    students_list = []
    citizenship_list = set()
    for user in arrival.students:
        students_list.append(UserRead(**user.__dict__))
        citizenship_list.add(user.citizenship)
    return ArrivalRead(**arrival.__dict__,
                       arrival_students=students_list,
                       arrival_buddies=[UserRead(**user.__dict__) for user in arrival.buddies],
                       citizenship=citizenship_list)
