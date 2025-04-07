import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import crud
from app.models import Priority, TaskManager
from app.schemas import (
    BulkTaskIdsRequest,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
    TaskBatchCreate,
)
from app.utils import load_tasks_from_file, save_tasks_to_file, get_tag_for_task

TASKS_FILE = os.path.join(os.path.dirname(__file__), "data", "tasks.json")
TAG_SERVICE_URL = "http://localhost:8001/tag"

app = FastAPI(
    title="Smart Task Manager API",
    description="API for managing tasks in the Smart Task Manager application. Requires the tagger server running on port 8001.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_task_manager() -> TaskManager:

    return load_tasks_from_file(TASKS_FILE)


def save_tasks(task_manager: TaskManager) -> None:

    save_tasks_to_file(task_manager, TASKS_FILE)


class TaggerRequest(BaseModel):

    task_id: int = Field(..., description="ID of the task to update")


@app.get("/", tags=["Root"])
async def root():

    return {
        "message": "Welcome to the Smart Task Manager API!",
        "note": "This server requires the Tag Server running on port 8001 to function properly.",
    }


@app.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(
    task: TaskCreate, task_manager: TaskManager = Depends(get_task_manager)
):

    created_task = crud.create_task(
        task_manager=task_manager,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        completed=task.completed,
    )

    save_tasks(task_manager)

    tag = created_task.tag if created_task.tag is not None else ""

    return TaskResponse(
        id=created_task.id,
        title=created_task.title,
        description=created_task.description,
        due_date=created_task.due_date,
        priority=created_task.priority,
        completed=created_task.completed,
        tag=tag,
    )


@app.get("/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def get_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority level"),
    task_manager: TaskManager = Depends(get_task_manager),
):

    tasks = crud.filter_tasks(
        task_manager=task_manager, completed=completed, priority=priority
    )

    task_responses = []
    for task in tasks:

        tag = task.tag if task.tag is not None else ""

        task_responses.append(
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                due_date=task.due_date,
                priority=task.priority,
                completed=task.completed,
                tag=tag,
            )
        )

    return TaskListResponse(tasks=task_responses, count=len(task_responses))


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: int = Path(..., description="ID of the task to retrieve"),
    task_manager: TaskManager = Depends(get_task_manager),
):

    task = crud.get_task_by_id(task_manager, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    tag = task.tag if task.tag is not None else ""

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        completed=task.completed,
        tag=tag,
    )


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_update: TaskUpdate,
    task_id: int = Path(..., description="ID of the task to update"),
    task_manager: TaskManager = Depends(get_task_manager),
):

    updated_task = crud.update_task(
        task_manager=task_manager,
        task_id=task_id,
        title=task_update.title,
        description=task_update.description,
        due_date=task_update.due_date,
        priority=task_update.priority,
        completed=task_update.completed,
    )

    if updated_task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    save_tasks(task_manager)

    tag = updated_task.tag if updated_task.tag is not None else ""

    return TaskResponse(
        id=updated_task.id,
        title=updated_task.title,
        description=updated_task.description,
        due_date=updated_task.due_date,
        priority=updated_task.priority,
        completed=updated_task.completed,
        tag=tag,
    )


@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(
    task_id: int = Path(..., description="ID of the task to delete"),
    task_manager: TaskManager = Depends(get_task_manager),
):

    success = crud.delete_task(task_manager, task_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

    save_tasks(task_manager)

    return {"message": f"Task with ID {task_id} deleted successfully"}


@app.post(
    "/tasks/complete", response_model=List[TaskResponse], tags=["Bulk Operations"]
)
async def complete_tasks(
    request: BulkTaskIdsRequest, task_manager: TaskManager = Depends(get_task_manager)
):

    updated_tasks = crud.mark_tasks_as_complete(task_manager, request.task_ids)

    save_tasks(task_manager)

    response_tasks = []
    for task in updated_tasks:

        tag = task.tag if task.tag is not None else ""

        response_tasks.append(
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                due_date=task.due_date,
                priority=task.priority,
                completed=task.completed,
                tag=tag,
            )
        )

    return response_tasks


@app.post(
    "/tasks/incomplete", response_model=List[TaskResponse], tags=["Bulk Operations"]
)
async def incomplete_tasks(
    request: BulkTaskIdsRequest, task_manager: TaskManager = Depends(get_task_manager)
):

    updated_tasks = crud.mark_tasks_as_incomplete(task_manager, request.task_ids)

    save_tasks(task_manager)

    response_tasks = []
    for task in updated_tasks:

        tag = task.tag if task.tag is not None else ""

        response_tasks.append(
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                due_date=task.due_date,
                priority=task.priority,
                completed=task.completed,
                tag=tag,
            )
        )

    return response_tasks


@app.post("/tasks/delete", tags=["Bulk Operations"])
async def delete_tasks(
    request: BulkTaskIdsRequest, task_manager: TaskManager = Depends(get_task_manager)
):

    deleted_count = crud.delete_multiple_tasks(task_manager, request.task_ids)

    save_tasks(task_manager)

    return {"message": f"Deleted {deleted_count} tasks"}


@app.post("/tagger", response_model=TaskResponse, tags=["Tagger"])
async def update_task_tag(
    tagger_request: TaggerRequest, task_manager: TaskManager = Depends(get_task_manager)
):

    print(f"DEBUG: update_task_tag called with task_id={tagger_request.task_id}")

    task = crud.get_task_by_id(task_manager, tagger_request.task_id)
    if task is None:
        raise HTTPException(
            status_code=404, detail=f"Task with ID {tagger_request.task_id} not found"
        )

    tag = get_tag_for_task(
        task_id=task.id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
    )

    task.tag = tag
    print(f"DEBUG: Updated task (id={task.id}) tag to '{tag}'")

    save_tasks(task_manager)

    tag = task.tag if task.tag is not None else ""

    response_task = TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        priority=task.priority,
        completed=task.completed,
        tag=tag,
    )

    print(f"DEBUG: Returning updated task with tag '{response_task.tag}'")
    return response_task


@app.post("/tasks/batch", response_model=List[TaskResponse], tags=["Bulk Operations"])
async def create_batch_tasks(
    batch_request: TaskBatchCreate,
    task_manager: TaskManager = Depends(get_task_manager),
):

    created_tasks = []

    for task_data in batch_request.tasks:
        created_task = crud.create_task(
            task_manager=task_manager,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority,
            completed=task_data.completed,
        )
        created_tasks.append(created_task)

    save_tasks(task_manager)

    response_tasks = []
    for task in created_tasks:

        tag = task.tag if task.tag is not None else ""

        response_tasks.append(
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                due_date=task.due_date,
                priority=task.priority,
                completed=task.completed,
                tag=tag,
            )
        )

    return response_tasks


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
