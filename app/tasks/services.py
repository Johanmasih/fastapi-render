from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.tasks import schemas, model as models

async def create_task(db: AsyncSession, task: schemas.TaskCreate):
    new_task = models.Task(**task.dict())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task

async def get_tasks(db: AsyncSession):
    result = await db.execute(select(models.Task))
    return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    return result.scalar_one_or_none()

async def update_task(db: AsyncSession, task_id: int, task_data: schemas.TaskUpdate):
    task = await get_task(db, task_id)
    if not task:
        return None
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task

async def delete_task(db: AsyncSession, task_id: int):
    task = await get_task(db, task_id)
    if not task:
        return None
    await db.delete(task)
    await db.commit()
    return task
