#!/usr/bin/env python3
"""
Task Lifecycle Management
Handles task creation, assignment, status updates, and completion.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from threading import Lock


class TaskState(Enum):
    """Task state enumeration."""
    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskError(Exception):
    """Base exception for task errors."""
    pass


class TaskNotFoundError(TaskError):
    """Raised when task ID doesn't exist."""
    pass


class InvalidTaskStateError(TaskError):
    """Raised when task state transition is invalid."""
    pass


@dataclass
class Task:
    """Represents a task."""
    id: str
    task_type: str
    title: str
    description: str
    payload: Dict[str, Any]
    state: TaskState = TaskState.CREATED
    created_at: str = ""
    updated_at: str = ""

    # Assignment
    assigned_to: Optional[str] = None
    assigned_at: Optional[str] = None

    # Completion
    result: Optional[Dict[str, Any]] = None
    completed_at: Optional[str] = None

    # Progress
    progress: float = 0.0
    status_message: Optional[str] = None

    # Metadata
    priority: str = "medium"
    deadline: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Error handling
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "task_type": self.task_type,
            "title": self.title,
            "description": self.description,
            "payload": self.payload,
            "state": self.state.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "assigned_to": self.assigned_to,
            "assigned_at": self.assigned_at,
            "result": self.result,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "status_message": self.status_message,
            "priority": self.priority,
            "deadline": self.deadline,
            "metadata": self.metadata,
            "error": self.error,
            "error_details": self.error_details
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            task_type=data["task_type"],
            title=data["title"],
            description=data["description"],
            payload=data.get("payload", {}),
            state=TaskState(data.get("state", "created")),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            assigned_to=data.get("assigned_to"),
            assigned_at=data.get("assigned_at"),
            result=data.get("result"),
            completed_at=data.get("completed_at"),
            progress=data.get("progress", 0.0),
            status_message=data.get("status_message"),
            priority=data.get("priority", "medium"),
            deadline=data.get("deadline"),
            metadata=data.get("metadata", {}),
            error=data.get("error"),
            error_details=data.get("error_details")
        )


class TaskManager:
    """Manages task lifecycle."""

    # Valid state transitions
    VALID_TRANSITIONS = {
        TaskState.CREATED: [TaskState.ASSIGNED, TaskState.CANCELLED],
        TaskState.ASSIGNED: [TaskState.IN_PROGRESS, TaskState.CANCELLED, TaskState.FAILED],
        TaskState.IN_PROGRESS: [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED],
        TaskState.COMPLETED: [],  # Terminal state
        TaskState.FAILED: [],     # Terminal state
        TaskState.CANCELLED: []   # Terminal state
    }

    def __init__(self):
        """Initialize task manager."""
        self.tasks: Dict[str, Task] = {}
        self.lock = Lock()

    def create_task(self,
                   task_type: str,
                   title: str,
                   description: str,
                   payload: Dict[str, Any],
                   priority: str = "medium",
                   deadline: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Task:
        """
        Create a new task.

        Args:
            task_type: Type of task
            title: Task title
            description: Task description
            payload: Task payload data
            priority: Task priority (low, medium, high, urgent)
            deadline: Optional deadline (ISO8601)
            metadata: Optional metadata

        Returns:
            Created task
        """
        task = Task(
            id=str(uuid.uuid4()),
            task_type=task_type,
            title=title,
            description=description,
            payload=payload,
            priority=priority,
            deadline=deadline,
            metadata=metadata or {}
        )

        with self.lock:
            self.tasks[task.id] = task

        return task

    def assign_task(self, task_id: str, agent_id: str) -> Task:
        """
        Assign a task to an agent.

        Args:
            task_id: Task ID
            agent_id: Agent ID to assign to

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            InvalidTaskStateError: If task state doesn't allow assignment
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if task.state != TaskState.CREATED:
                raise InvalidTaskStateError(
                    f"Cannot assign task in state {task.state.value}"
                )

            task.state = TaskState.ASSIGNED
            task.assigned_to = agent_id
            task.assigned_at = datetime.utcnow().isoformat() + "Z"
            task.updated_at = datetime.utcnow().isoformat() + "Z"

        return task

    def update_task_status(self,
                          task_id: str,
                          new_state: str,
                          progress: Optional[float] = None,
                          message: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Task:
        """
        Update task status.

        Args:
            task_id: Task ID
            new_state: New task state
            progress: Optional progress value (0.0-1.0)
            message: Optional status message
            metadata: Optional metadata to update

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            InvalidTaskStateError: If state transition is invalid
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")

            try:
                new_task_state = TaskState(new_state)
            except ValueError:
                raise InvalidTaskStateError(f"Invalid task state: {new_state}")

            # Validate state transition
            valid_transitions = self.VALID_TRANSITIONS.get(task.state, [])
            if new_task_state not in valid_transitions:
                raise InvalidTaskStateError(
                    f"Invalid state transition: {task.state.value} -> {new_state}"
                )

            # Update task
            task.state = new_task_state
            task.updated_at = datetime.utcnow().isoformat() + "Z"

            if progress is not None:
                task.progress = max(0.0, min(1.0, progress))

            if message is not None:
                task.status_message = message

            if metadata is not None:
                task.metadata.update(metadata)

        return task

    def complete_task(self,
                     task_id: str,
                     result: Dict[str, Any],
                     execution_time_ms: Optional[int] = None) -> Task:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID
            result: Task result data
            execution_time_ms: Optional execution time in milliseconds

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            InvalidTaskStateError: If task state doesn't allow completion
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")

            if task.state not in [TaskState.ASSIGNED, TaskState.IN_PROGRESS]:
                raise InvalidTaskStateError(
                    f"Cannot complete task in state {task.state.value}"
                )

            task.state = TaskState.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow().isoformat() + "Z"
            task.updated_at = datetime.utcnow().isoformat() + "Z"

            if execution_time_ms:
                task.metadata["execution_time_ms"] = execution_time_ms

        return task

    def cancel_task(self, task_id: str, reason: str) -> Task:
        """
        Cancel a task.

        Args:
            task_id: Task ID
            reason: Cancellation reason

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            InvalidTaskStateError: If task state doesn't allow cancellation
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")

            terminal_states = [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
            if task.state in terminal_states:
                raise InvalidTaskStateError(
                    f"Cannot cancel task in state {task.state.value}"
                )

            task.state = TaskState.CANCELLED
            task.status_message = f"Cancelled: {reason}"
            task.updated_at = datetime.utcnow().isoformat() + "Z"

        return task

    def fail_task(self,
                  task_id: str,
                  error: str,
                  error_details: Optional[Dict[str, Any]] = None) -> Task:
        """
        Mark a task as failed.

        Args:
            task_id: Task ID
            error: Error message
            error_details: Optional error details

        Returns:
            Updated task

        Raises:
            TaskNotFoundError: If task doesn't exist
            InvalidTaskStateError: If task state doesn't allow failure
        """
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                raise TaskNotFoundError(f"Task {task_id} not found")

            terminal_states = [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
            if task.state in terminal_states:
                raise InvalidTaskStateError(
                    f"Cannot fail task in state {task.state.value}"
                )

            task.state = TaskState.FAILED
            task.error = error
            task.error_details = error_details or {}
            task.updated_at = datetime.utcnow().isoformat() + "Z"

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task or None if not found
        """
        return self.tasks.get(task_id)

    def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """
        Get all tasks assigned to an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of tasks
        """
        return [
            task for task in self.tasks.values()
            if task.assigned_to == agent_id
        ]

    def get_tasks_by_state(self, state: str) -> List[Task]:
        """
        Get all tasks in a specific state.

        Args:
            state: Task state

        Returns:
            List of tasks
        """
        try:
            task_state = TaskState(state)
        except ValueError:
            return []

        return [
            task for task in self.tasks.values()
            if task.state == task_state
        ]

    def get_active_tasks(self) -> List[Task]:
        """
        Get all active (non-terminal) tasks.

        Returns:
            List of active tasks
        """
        terminal_states = [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
        return [
            task for task in self.tasks.values()
            if task.state not in terminal_states
        ]

    def list_tasks(self) -> List[Task]:
        """
        List all tasks.

        Returns:
            List of all tasks
        """
        return list(self.tasks.values())

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
        return False


def main():
    """CLI interface for task lifecycle operations."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Task Lifecycle CLI")
    parser.add_argument("command",
                       choices=["create", "assign", "update", "complete", "cancel", "list"],
                       help="Command to run")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--type", help="Task type")
    parser.add_argument("--title", help="Task title")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--payload", help="Task payload (JSON)")
    parser.add_argument("--agent", help="Agent ID for assignment")
    parser.add_argument("--status", help="New task status")
    parser.add_argument("--progress", type=float, help="Progress (0.0-1.0)")
    parser.add_argument("--message", help="Status message")
    parser.add_argument("--result", help="Task result (JSON)")
    parser.add_argument("--reason", help="Cancellation reason")
    parser.add_argument("--priority", default="medium", help="Task priority")
    parser.add_argument("--state-filter", help="Filter by state")
    parser.add_argument("--agent-filter", help="Filter by assigned agent")

    args = parser.parse_args()

    manager = TaskManager()

    if args.command == "create":
        if not args.type or not args.title:
            print("Error: --type and --title required for create command")
            sys.exit(1)

        payload = json.loads(args.payload) if args.payload else {}

        task = manager.create_task(
            task_type=args.type,
            title=args.title,
            description=args.description or "",
            payload=payload,
            priority=args.priority
        )

        print(f"Created task: {task.id}")
        print(json.dumps(task.to_dict(), indent=2))

    elif args.command == "assign":
        if not args.task_id or not args.agent:
            print("Error: --task-id and --agent required for assign command")
            sys.exit(1)

        try:
            task = manager.assign_task(args.task_id, args.agent)
            print(f"Assigned task {task.id} to {args.agent}")
            print(json.dumps(task.to_dict(), indent=2))
        except (TaskNotFoundError, InvalidTaskStateError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "update":
        if not args.task_id or not args.status:
            print("Error: --task-id and --status required for update command")
            sys.exit(1)

        try:
            task = manager.update_task_status(
                args.task_id,
                args.status,
                progress=args.progress,
                message=args.message
            )
            print(f"Updated task {task.id} to {args.status}")
            print(json.dumps(task.to_dict(), indent=2))
        except (TaskNotFoundError, InvalidTaskStateError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "complete":
        if not args.task_id or not args.result:
            print("Error: --task-id and --result required for complete command")
            sys.exit(1)

        try:
            result = json.loads(args.result)
            task = manager.complete_task(args.task_id, result)
            print(f"Completed task {task.id}")
            print(json.dumps(task.to_dict(), indent=2))
        except (TaskNotFoundError, InvalidTaskStateError, json.JSONDecodeError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "cancel":
        if not args.task_id or not args.reason:
            print("Error: --task-id and --reason required for cancel command")
            sys.exit(1)

        try:
            task = manager.cancel_task(args.task_id, args.reason)
            print(f"Cancelled task {task.id}: {args.reason}")
            print(json.dumps(task.to_dict(), indent=2))
        except (TaskNotFoundError, InvalidTaskStateError) as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "list":
        tasks = manager.list_tasks()

        if args.state_filter:
            tasks = manager.get_tasks_by_state(args.state_filter)
        elif args.agent_filter:
            tasks = manager.get_tasks_by_agent(args.agent_filter)

        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"  - {task.id}")
            print(f"    Type: {task.task_type}")
            print(f"    Title: {task.title}")
            print(f"    State: {task.state.value}")
            print(f"    Assigned to: {task.assigned_to or 'None'}")


if __name__ == "__main__":
    main()
