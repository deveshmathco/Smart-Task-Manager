from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union


class Priority(str, Enum):

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Task:

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str,
        due_date: datetime,
        priority: Priority,
        completed: bool = False,
        tag: Optional[str] = None,
    ):

        self.id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = completed
        self.tag = tag

    def mark_complete(self) -> None:

        self.completed = True

    def mark_incomplete(self) -> None:

        self.completed = False

    def update(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[Priority] = None,
        completed: Optional[bool] = None,
        tag: Optional[str] = None,
    ) -> None:

        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if due_date is not None:
            self.due_date = due_date
        if priority is not None:
            self.priority = priority
        if completed is not None:
            self.completed = completed
        if tag is not None:
            self.tag = tag

    def to_dict(self) -> Dict[str, Union[int, str, bool]]:

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),
            "priority": self.priority.value,
            "completed": self.completed,
            "tag": self.tag,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[int, str, bool]]) -> "Task":

        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data["description"],
            due_date=datetime.fromisoformat(data["due_date"]),
            priority=Priority(data["priority"]),
            completed=data["completed"],
            tag=data.get("tag"),
        )


class TaskManager:

    def __init__(self):

        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1

    def add_task(
        self,
        title: str,
        description: str,
        due_date: datetime,
        priority: Priority,
        completed: bool = False,
        tag: Optional[str] = None,
    ) -> Task:

        task = Task(
            task_id=self.next_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            completed=completed,
            tag=tag,
        )
        self.tasks[task.id] = task
        self.next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:

        return self.tasks.get(task_id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[Priority] = None,
        completed: Optional[bool] = None,
        tag: Optional[str] = None,
    ) -> Optional[Task]:

        task = self.get_task(task_id)
        if task:
            task.update(
                title=title,
                description=description,
                due_date=due_date,
                priority=priority,
                completed=completed,
                tag=tag,
            )
        return task

    def delete_task(self, task_id: int) -> bool:

        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

    def list_tasks(self) -> List[Task]:

        return list(self.tasks.values())

    def mark_tasks_complete(self, task_ids: List[int]) -> List[Task]:

        updated_tasks = []
        for task_id in task_ids:
            task = self.get_task(task_id)
            if task:
                task.mark_complete()
                updated_tasks.append(task)
        return updated_tasks

    def mark_tasks_incomplete(self, task_ids: List[int]) -> List[Task]:

        updated_tasks = []
        for task_id in task_ids:
            task = self.get_task(task_id)
            if task:
                task.mark_incomplete()
                updated_tasks.append(task)
        return updated_tasks

    def delete_tasks(self, task_ids: List[int]) -> int:

        deleted_count = 0
        for task_id in task_ids:
            if self.delete_task(task_id):
                deleted_count += 1
        return deleted_count

    def filter_tasks(
        self, completed: Optional[bool] = None, priority: Optional[Priority] = None
    ) -> List[Task]:

        filtered_tasks = self.list_tasks()

        if completed is not None:
            filtered_tasks = [
                task for task in filtered_tasks if task.completed == completed
            ]

        if priority is not None:
            filtered_tasks = [
                task for task in filtered_tasks if task.priority == priority
            ]

        return filtered_tasks
