from datetime import datetime
from typing import List, Optional

from app.models import Priority, Task, TaskManager
from app.utils import get_tag_for_task, compare_and_update_priority


def get_all_tasks(task_manager: TaskManager) -> List[Task]:

    return task_manager.list_tasks()


def get_task_by_id(task_manager: TaskManager, task_id: int) -> Optional[Task]:

    return task_manager.get_task(task_id)


def create_task(
    task_manager: TaskManager,
    title: str,
    description: str,
    due_date: datetime,
    priority: Priority,
    completed: bool = False,
    get_tag: bool = True,
) -> Task:

    task = task_manager.add_task(
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        completed=completed,
        tag=None,
    )

    if get_tag:
        tag = get_tag_for_task(
            task_id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
        )
        task.tag = tag

    return task


def update_task(
    task_manager: TaskManager,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    priority: Optional[Priority] = None,
    completed: Optional[bool] = None,
    get_tag: bool = True,
) -> Optional[Task]:

    task = task_manager.get_task(task_id)
    if not task:
        return None

    task_manager.update_task(
        task_id=task_id,
        title=title,
        description=description,
        due_date=due_date,
        priority=priority,
        completed=completed,
    )

    if get_tag and due_date is not None:
        updated_title = title if title is not None else task.title
        updated_desc = description if description is not None else task.description
        updated_date = due_date if due_date is not None else task.due_date
        updated_prio = priority if priority is not None else task.priority

        tag = get_tag_for_task(
            task_id=task_id,
            title=updated_title,
            description=updated_desc,
            due_date=updated_date,
            priority=updated_prio,
        )

        task.tag = tag

    return task


def delete_task(task_manager: TaskManager, task_id: int) -> bool:

    return task_manager.delete_task(task_id)


def mark_tasks_as_complete(
    task_manager: TaskManager, task_ids: List[int]
) -> List[Task]:

    return task_manager.mark_tasks_complete(task_ids)


def mark_tasks_as_incomplete(
    task_manager: TaskManager, task_ids: List[int]
) -> List[Task]:

    return task_manager.mark_tasks_incomplete(task_ids)


def delete_multiple_tasks(task_manager: TaskManager, task_ids: List[int]) -> int:

    return task_manager.delete_tasks(task_ids)


def filter_tasks(
    task_manager: TaskManager,
    completed: Optional[bool] = None,
    priority: Optional[Priority] = None,
) -> List[Task]:

    return task_manager.filter_tasks(completed=completed, priority=priority)


def update_priorities_by_due_date(
    task_manager: TaskManager, reference_date: datetime, new_priority: Priority
) -> List[Task]:

    return compare_and_update_priority(task_manager, reference_date, new_priority)
