import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import RequestException


class TaskManagerClient:

    def __init__(self, base_url: str = "http://localhost:8000"):

        self.base_url = base_url

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url)
            else:
                raise ValueError(f"Invalid HTTP method: {method}")

            response.raise_for_status()

            return response.json()

        except RequestException as e:
            print(f"Error making request to {url}: {e}")

            try:
                error_detail = e.response.json().get("detail", str(e))
                print(f"Error details: {error_detail}")
            except:
                pass

            raise

    def create_task(
        self,
        title: str,
        description: str,
        due_date: Union[str, datetime],
        priority: str,
        completed: bool = False,
    ) -> Dict[str, Any]:

        if isinstance(due_date, datetime):
            due_date = due_date.isoformat()

        task_data = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "completed": completed,
        }

        return self._make_request("POST", "/tasks", data=task_data)

    def get_tasks(
        self, completed: Optional[bool] = None, priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        params = {}
        if completed is not None:
            params["completed"] = completed
        if priority is not None:
            params["priority"] = priority

        response = self._make_request("GET", "/tasks", params=params)

        return response.get("tasks", [])

    def get_task(self, task_id: int) -> Dict[str, Any]:

        return self._make_request("GET", f"/tasks/{task_id}")

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[Union[str, datetime]] = None,
        priority: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Dict[str, Any]:

        if isinstance(due_date, datetime):
            due_date = due_date.isoformat()

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if due_date is not None:
            update_data["due_date"] = due_date
        if priority is not None:
            update_data["priority"] = priority
        if completed is not None:
            update_data["completed"] = completed

        return self._make_request("PUT", f"/tasks/{task_id}", data=update_data)

    def delete_task(self, task_id: int) -> Dict[str, Any]:

        return self._make_request("DELETE", f"/tasks/{task_id}")

    def mark_tasks_complete(self, task_ids: List[int]) -> List[Dict[str, Any]]:

        data = {"task_ids": task_ids}
        return self._make_request("POST", "/tasks/complete", data=data)

    def mark_tasks_incomplete(self, task_ids: List[int]) -> List[Dict[str, Any]]:

        data = {"task_ids": task_ids}
        return self._make_request("POST", "/tasks/incomplete", data=data)

    def delete_tasks(self, task_ids: List[int]) -> Dict[str, Any]:

        data = {"task_ids": task_ids}
        return self._make_request("POST", "/tasks/delete", data=data)

    def create_batch(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        processed_tasks = []
        for task in tasks:
            processed_task = task.copy()
            if isinstance(processed_task.get("due_date"), datetime):
                processed_task["due_date"] = processed_task["due_date"].isoformat()
            processed_tasks.append(processed_task)

        batch_data = {"tasks": processed_tasks}

        return self._make_request("POST", "/tasks/batch", data=batch_data)

    def update_priorities_by_due_date(
        self, due_date: Union[str, datetime], priority: str
    ) -> List[Dict[str, Any]]:

        if isinstance(due_date, datetime):
            due_date = due_date.isoformat()

        tagger_data = {"due_date": due_date, "priority": priority}

        return self._make_request("POST", "/tagger", data=tagger_data)

    def update_task_tag(self, task_id: int) -> Dict[str, Any]:

        data = {"task_id": task_id}
        return self._make_request("POST", "/tagger", data=data)


def print_task(task: Dict[str, Any]) -> None:

    print(f"ID: {task['id']}")
    print(f"Title: {task['title']}")
    print(f"Description: {task['description']}")
    print(f"Due Date: {task['due_date']}")
    print(f"Priority: {task['priority']}")
    print(f"Completed: {task['completed']}")
    if task.get("tag"):
        print(f"Tag: {task['tag']}")
    print()


def main():

    parser = argparse.ArgumentParser(description="Smart Task Manager Client")

    parser.add_argument(
        "--url", default="http://localhost:8000", help="Base URL of the API"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument("--title", required=True, help="Task title")
    create_parser.add_argument("--description", required=True, help="Task description")
    create_parser.add_argument(
        "--due-date", required=True, help="Task due date (YYYY-MM-DD)"
    )
    create_parser.add_argument(
        "--priority",
        required=True,
        choices=["Low", "Medium", "High"],
        help="Task priority level",
    )
    create_parser.add_argument(
        "--completed", action="store_true", help="Mark task as completed"
    )

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--completed",
        choices=["true", "false"],
        help="Filter for completed/incomplete tasks",
    )
    list_parser.add_argument(
        "--priority",
        choices=["Low", "Medium", "High"],
        help="Filter for tasks with specific priority",
    )

    get_parser = subparsers.add_parser("get", help="Get a task by ID")
    get_parser.add_argument("id", type=int, help="Task ID")

    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("id", type=int, help="Task ID")
    update_parser.add_argument("--title", help="New task title")
    update_parser.add_argument("--description", help="New task description")
    update_parser.add_argument("--due-date", help="New task due date (YYYY-MM-DD)")
    update_parser.add_argument(
        "--priority", choices=["Low", "Medium", "High"], help="New task priority level"
    )
    update_parser.add_argument(
        "--completed", choices=["true", "false"], help="New task completion status"
    )

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")

    complete_parser = subparsers.add_parser("complete", help="Mark tasks as complete")
    complete_parser.add_argument("ids", type=int, nargs="+", help="Task IDs")

    incomplete_parser = subparsers.add_parser(
        "incomplete", help="Mark tasks as incomplete"
    )
    incomplete_parser.add_argument("ids", type=int, nargs="+", help="Task IDs")

    delete_multiple_parser = subparsers.add_parser(
        "delete-multiple", help="Delete multiple tasks"
    )
    delete_multiple_parser.add_argument("ids", type=int, nargs="+", help="Task IDs")

    tagger_parser = subparsers.add_parser(
        "update-priorities",
        help="Update priorities of tasks with due dates matching a reference date",
    )
    tagger_parser.add_argument(
        "--due-date", required=True, help="Reference due date (YYYY-MM-DD)"
    )
    tagger_parser.add_argument(
        "--priority",
        required=True,
        choices=["Low", "Medium", "High"],
        help="New priority to assign to matching tasks",
    )

    update_tag_parser = subparsers.add_parser(
        "update-tag", help="Update a task's tag based on its due date"
    )
    update_tag_parser.add_argument("id", type=int, help="Task ID")

    args = parser.parse_args()

    client = TaskManagerClient(args.url)

    try:
        if args.command == "create":

            due_date = datetime.strptime(args.due_date, "%Y-%m-%d")

            task = client.create_task(
                title=args.title,
                description=args.description,
                due_date=due_date,
                priority=args.priority,
                completed=args.completed,
            )

            print("Task created successfully:")
            print_task(task)

        elif args.command == "list":

            completed = None
            if args.completed == "true":
                completed = True
            elif args.completed == "false":
                completed = False

            tasks = client.get_tasks(completed=completed, priority=args.priority)

            print(f"Found {len(tasks)} tasks:")
            for task in tasks:
                print_task(task)

        elif args.command == "get":

            task = client.get_task(args.id)

            print("Task details:")
            print_task(task)

        elif args.command == "update":

            due_date = None
            if args.due_date:
                due_date = datetime.strptime(args.due_date, "%Y-%m-%d")

            completed = None
            if args.completed == "true":
                completed = True
            elif args.completed == "false":
                completed = False

            task = client.update_task(
                task_id=args.id,
                title=args.title,
                description=args.description,
                due_date=due_date,
                priority=args.priority,
                completed=completed,
            )

            print("Task updated successfully:")
            print_task(task)

        elif args.command == "delete":

            result = client.delete_task(args.id)

            print(result["message"])

        elif args.command == "complete":

            tasks = client.mark_tasks_complete(args.ids)

            print(f"Marked {len(tasks)} tasks as complete:")
            for task in tasks:
                print_task(task)

        elif args.command == "incomplete":

            tasks = client.mark_tasks_incomplete(args.ids)

            print(f"Marked {len(tasks)} tasks as incomplete:")
            for task in tasks:
                print_task(task)

        elif args.command == "delete-multiple":

            result = client.delete_tasks(args.ids)

            print(result["message"])

        elif args.command == "update-priorities":

            due_date = datetime.strptime(args.due_date, "%Y-%m-%d")

            tasks = client.update_priorities_by_due_date(due_date, args.priority)

            print(
                f"Updated {len(tasks)} tasks with due date {args.due_date} to priority {args.priority}:"
            )
            for task in tasks:
                print_task(task)

        elif args.command == "update-tag":

            task = client.update_task_tag(args.id)

            print("Task updated successfully:")
            print_task(task)

        else:
            print("Please specify a command.")
            parser.print_help()
            sys.exit(1)

    except RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
