import json

from dateutil.relativedelta import relativedelta
from sqlalchemy import select
import holidays

from db.models import *
from db.session import *
from api.tasks.schemes import *


async def create_tasks_for_user(arrival_id: uuid.UUID,
                                user_id: uuid.UUID,
                                db: AsyncSession):
    query = select(Arrival).where(Arrival.id == arrival_id)
    arrival = await db.scalar(query)
    query = select(User).where(User.id == user_id)
    user = await db.scalar(query)

    f = open('tasks.json', encoding='utf-8')
    tasks = json.load(f)
    date_visa = None
    for task in tasks['tasks']:
        new_task = task
        new_task['student_id'] = user_id
        new_task['arrival_id'] = arrival_id

        if task['title'] == 'Встреча в аэропорту':
            new_task['deadline'] = arrival.date_time

        elif task['title'] == 'Продление визы':
            if user.last_visa_expiration:
                deadline = user.last_visa_expiration - relativedelta(days=40)
                while deadline in holidays.Russia() or deadline.weekday() >= 5:
                    deadline -= relativedelta(days=1)
                date_visa = deadline
                new_task['deadline'] = deadline

        elif task['title'] == 'Прохождение медосвидетельствования':
            if date_visa:
                deadline = date_visa
                working_days = 0
                while working_days < 3:
                    if deadline.weekday() < 5:
                        working_days += 1
                        deadline -= relativedelta(days=1)
                new_task['deadline'] = deadline

        elif task['title'] == 'Прохождение дактилоскопии':
            if user.student_arrivals:
                student_arrivals = list(sorted(user.student_arrivals, key=lambda a: a.date_time))
                last_arrival = student_arrivals[-1]
                new_task['deadline'] = last_arrival.date_time + relativedelta(months=3)

        res_task = Task(**new_task)
        db.add(res_task)
        await db.commit()
        await db.refresh(res_task)
    f.close()
