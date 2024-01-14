from api.arrival import schemes
from db import models


def make_arrival_read(arrival: models.Arrival):
    students_list = []
    citizenship_list = set()
    for user in arrival.students:
        students_list.append(schemes.UserRead(**user.__dict__))
        citizenship_list.add(user.citizenship)
    citizenship_list = list(citizenship_list)
    if citizenship_list:
        if not citizenship_list[0]:
            citizenship_list = None
    return schemes.ArrivalRead(**arrival.__dict__,
                               arrival_students=students_list,
                               arrival_buddies=[schemes.UserRead(**user.__dict__) for user in arrival.buddies],
                               citizenship=citizenship_list)
