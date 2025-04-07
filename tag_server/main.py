from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Task Tag Service",
    description="Service for generating tags for tasks based on due date and priority",
    version="1.0.0",
)


class TaskTagRequest(BaseModel):

    due_date: datetime = Field(..., description="Due date of the task")
    priority: str = Field(
        ..., description="Priority level of the task (Low, Medium, High)"
    )


class TaskTagResponse(BaseModel):

    tag: str = Field(..., description="Generated tag for the task")


def calculate_time_difference(due_date: datetime) -> int:

    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    due = due_date.replace(hour=0, minute=0, second=0, microsecond=0)

    days_remaining = (due - now).days

    return days_remaining


def generate_tag(due_date: datetime, priority: str) -> str:

    if priority not in ["Low", "Medium", "High"]:
        raise ValueError(
            f"Invalid priority: {priority}. Must be one of: Low, Medium, High"
        )

    days_remaining = calculate_time_difference(due_date)

    if days_remaining < 0:

        base_tag = "Overdue"
    elif days_remaining < 1:

        base_tag = "Urgent"
    elif days_remaining <= 7:

        base_tag = "High priority"
    elif days_remaining <= 28:

        base_tag = "Medium"
    else:

        base_tag = "Low priority"

    final_tag = base_tag

    if base_tag == "Overdue":

        final_tag = "Overdue"
    elif priority == "High" and (base_tag == "Medium" or base_tag == "Low priority"):

        final_tag = "High priority"
    elif priority == "Low" and base_tag == "High priority" and days_remaining > 3:

        final_tag = "Medium"

    return final_tag


@app.get("/", tags=["Root"])
async def root():

    return {"message": "Welcome to the Task Tag Service!"}


@app.post("/tag", response_model=TaskTagResponse, tags=["Tags"])
async def get_task_tag(request: TaskTagRequest):

    try:

        tag = generate_tag(request.due_date, request.priority)

        return TaskTagResponse(tag=tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
