import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

import requests
from requests.exceptions import RequestException

from app.models import Priority, Task, TaskManager

DEFAULT_TAG_SERVICE_URL = "http://localhost:8001/tag"


def load_tasks_from_file(file_path: str) -> TaskManager:

    task_manager = TaskManager()

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

                if data.get("tasks"):
                    task_ids = [task["id"] for task in data["tasks"]]
                    task_manager.next_id = max(task_ids) + 1 if task_ids else 1

                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    task_manager.tasks[task.id] = task
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading tasks from {file_path}: {e}")

    return task_manager


def save_tasks_to_file(task_manager: TaskManager, file_path: str) -> bool:

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        tasks_data = {
            "tasks": [task.to_dict() for task in task_manager.list_tasks()],
            "next_id": task_manager.next_id,
        }

        with open(file_path, "w") as f:
            json.dump(tasks_data, f, indent=2)

        return True
    except (IOError, TypeError) as e:
        print(f"Error saving tasks to {file_path}: {e}")
        return False


def get_tag_for_task(
    task_id: int,
    title: str,
    description: str,
    due_date: datetime,
    priority: Priority,
    tag_service_url: str = DEFAULT_TAG_SERVICE_URL,
) -> Optional[str]:

    payload = {"due_date": due_date.isoformat(), "priority": priority.value}

    print(f"DEBUG: Calling tag service with payload: {payload}")

    try:
        response = requests.post(tag_service_url, json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            tag = result.get("tag")
            print(f"DEBUG: Tag service returned tag: {tag}")
            return tag
        else:
            print(f"ERROR: Tag service returned status code {response.status_code}")
            print(f"ERROR: Response text: {response.text}")
            return "Default Tag"

    except RequestException as e:
        print(f"ERROR: Error calling tag service: {e}")
        return "Default Tag"
    except Exception as e:
        print(f"ERROR: Unexpected error in get_tag_for_task: {e}")
        return "Default Tag"


def compare_and_update_priority(
    task_manager: TaskManager, reference_date: datetime, new_priority: Priority
) -> List[Task]:

    updated_tasks = []
    ref_date = reference_date.date()

    print(
        f"DEBUG: compare_and_update_priority called with reference_date={ref_date}, new_priority={new_priority.value}"
    )

    for task in task_manager.list_tasks():
        task_date = task.due_date.date()
        print(f"DEBUG: Checking task (id={task.id}) with due_date={task_date}")

        if task_date == ref_date:
            print(f"DEBUG: Found matching task with id={task.id}")

            task.priority = new_priority

            tag = get_tag_for_task(
                task_id=task.id,
                title=task.title,
                description=task.description,
                due_date=task.due_date,
                priority=new_priority,
            )

            if tag:
                task.tag = tag
                print(f"DEBUG: Updated task (id={task.id}) with tag={tag}")
            else:
                print(f"ERROR: Failed to get tag for task (id={task.id})")

            updated_tasks.append(task)

    print(f"DEBUG: Updated {len(updated_tasks)} tasks")
    return updated_tasks
