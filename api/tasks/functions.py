from sqlalchemy import select
from api.auth.routers import fastapi_users

from db.models import *
from db.session import *
from api.tasks.schemes import *


async def create_tasks_for_arrival_user(id_arrival: uuid.UUID,
                                        tasks_users: TaskCreate,
                                        db: AsyncSession = Depends(get_async_session),
                                        user: User = Depends(fastapi_users.current_user(active=True))):
    if user.role == Role.student:
        return False
    query = select(User).where(User.arrivals == id_arrival)
    users = (await db.execute(query)).scalars().all()
    for task in tasks_users.tasks:
        old_task = task.__dict__
        for user in users:
            old_task['student_id'] = user.id
            res_task = Task(**old_task)
            db.add(res_task)
            await db.commit()
            await db.refresh(res_task)
    return True
