from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import Priority


class TaskBase(BaseModel):

    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Detailed description of the task")
    due_date: datetime = Field(..., description="Deadline for the task")
    priority: Priority = Field(..., description="Priority level (Low, Medium, High)")


class TaskCreate(TaskBase):

    completed: bool = Field(False, description="Whether the task is completed")


class TaskUpdate(BaseModel):

    title: Optional[str] = Field(None, description="New title for the task")
    description: Optional[str] = Field(None, description="New description for the task")
    due_date: Optional[datetime] = Field(None, description="New deadline for the task")
    priority: Optional[Priority] = Field(None, description="New priority level")
    completed: Optional[bool] = Field(None, description="New completion status")
    tag: Optional[str] = Field(None, description="New tag for the task")


class TaskResponse(TaskBase):

    id: int = Field(..., description="Unique identifier for the task")
    completed: bool = Field(..., description="Whether the task is completed")
    tag: Optional[str] = Field(None, description="Tag associated with the task")

    class Config:

        orm_mode = True


class TaskListResponse(BaseModel):

    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    count: int = Field(..., description="Total number of tasks")


class BulkTaskIdsRequest(BaseModel):

    task_ids: List[int] = Field(..., description="List of task IDs to operate on")


class TaskBatchCreate(BaseModel):

    tasks: List[TaskCreate] = Field(..., description="List of tasks to create")
