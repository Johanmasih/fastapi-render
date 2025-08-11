from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.tasks import schemas, services
from ..database.db import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=schemas.TaskRead)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    return await services.create_task(db, task)

@router.get("/", response_model=List[schemas.TaskRead])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    return await services.get_tasks(db)

@router.get("/{task_id}", response_model=schemas.TaskRead)
async def read_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await services.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.TaskRead)
async def update_task(task_id: int, task: schemas.TaskUpdate, db: AsyncSession = Depends(get_db)):
    updated_task = await services.update_task(db, task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    deleted_task = await services.delete_task(db, task_id)
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
