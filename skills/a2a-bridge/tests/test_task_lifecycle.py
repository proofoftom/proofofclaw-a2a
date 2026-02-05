#!/usr/bin/env python3
"""
Unit tests for Task Lifecycle module.
"""

import unittest
import sys
import uuid
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, '/home/node/.openclaw/workspace/skills/a2a-bridge/scripts')

from task_lifecycle import Task, TaskManager, TaskState, TaskNotFoundError, InvalidTaskStateError


class TestTask(unittest.TestCase):
    """Test Task dataclass."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            id="task-001",
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.assertEqual(task.id, "task-001")
        self.assertEqual(task.task_type, "research")
        self.assertEqual(task.state, TaskState.CREATED)
        self.assertEqual(task.progress, 0.0)
        self.assertIsInstance(task.metadata, dict)

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            id="task-001",
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        result = task.to_dict()

        self.assertEqual(result["id"], "task-001")
        self.assertEqual(result["task_type"], "research")
        self.assertEqual(result["state"], "created")
        self.assertIn("created_at", result)

    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        data = {
            "id": "task-001",
            "task_type": "research",
            "title": "Research Task",
            "description": "Test research",
            "payload": {"query": "test"},
            "state": "in_progress",
            "progress": 0.5
        }

        task = Task.from_dict(data)

        self.assertEqual(task.id, "task-001")
        self.assertEqual(task.state, TaskState.IN_PROGRESS)
        self.assertEqual(task.progress, 0.5)


class TestTaskManager(unittest.TestCase):
    """Test TaskManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskManager()

    def test_create_task(self):
        """Test creating a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.assertIsNotNone(task.id)
        self.assertEqual(task.task_type, "research")
        self.assertEqual(task.state, TaskState.CREATED)
        self.assertIn(task.id, self.manager.tasks)

    def test_create_task_with_metadata(self):
        """Test creating a task with all parameters."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"},
            priority="high",
            deadline="2024-12-31T23:59:59Z",
            metadata={"source": "user_request"}
        )

        self.assertEqual(task.priority, "high")
        self.assertEqual(task.deadline, "2024-12-31T23:59:59Z")
        self.assertEqual(task.metadata["source"], "user_request")

    def test_assign_task(self):
        """Test assigning a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        assigned_task = self.manager.assign_task(task.id, "agent-001")

        self.assertEqual(assigned_task.state, TaskState.ASSIGNED)
        self.assertEqual(assigned_task.assigned_to, "agent-001")
        self.assertIsNotNone(assigned_task.assigned_at)

    def test_assign_task_not_found(self):
        """Test assigning non-existent task."""
        with self.assertRaises(TaskNotFoundError):
            self.manager.assign_task("task-999", "agent-001")

    def test_assign_task_already_assigned(self):
        """Test assigning task that's already assigned."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")

        with self.assertRaises(InvalidTaskStateError):
            self.manager.assign_task(task.id, "agent-002")

    def test_update_task_status(self):
        """Test updating task status."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")

        updated = self.manager.update_task_status(
            task.id,
            "in_progress",
            progress=0.5,
            message="Working on it"
        )

        self.assertEqual(updated.state, TaskState.IN_PROGRESS)
        self.assertEqual(updated.progress, 0.5)
        self.assertEqual(updated.status_message, "Working on it")

    def test_update_task_with_metadata(self):
        """Test updating task status with metadata."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        updated = self.manager.update_task_status(
            task.id,
            "assigned",
            metadata={"agent": "agent-001"}
        )

        self.assertEqual(updated.metadata["agent"], "agent-001")

    def test_update_task_invalid_transition(self):
        """Test invalid state transition."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        # Can't go from CREATED to COMPLETED
        with self.assertRaises(InvalidTaskStateError):
            self.manager.update_task_status(task.id, "completed")

    def test_complete_task(self):
        """Test completing a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")
        self.manager.update_task_status(task.id, "in_progress")

        completed = self.manager.complete_task(
            task.id,
            result={"summary": "Done"}
        )

        self.assertEqual(completed.state, TaskState.COMPLETED)
        self.assertEqual(completed.result["summary"], "Done")
        self.assertIsNotNone(completed.completed_at)

    def test_complete_task_with_execution_time(self):
        """Test completing task with execution time."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")

        completed = self.manager.complete_task(
            task.id,
            result={"summary": "Done"},
            execution_time_ms=5000
        )

        self.assertEqual(completed.metadata["execution_time_ms"], 5000)

    def test_complete_task_not_found(self):
        """Test completing non-existent task."""
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete_task("task-999", result={"summary": "Done"})

    def test_complete_task_invalid_state(self):
        """Test completing task in invalid state."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        # Can't complete task that's not assigned/in_progress
        with self.assertRaises(InvalidTaskStateError):
            self.manager.complete_task(task.id, result={"summary": "Done"})

    def test_cancel_task(self):
        """Test canceling a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        cancelled = self.manager.cancel_task(task.id, "No longer needed")

        self.assertEqual(cancelled.state, TaskState.CANCELLED)
        self.assertIn("Cancelled: No longer needed", cancelled.status_message)

    def test_cancel_task_already_completed(self):
        """Test canceling already completed task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")
        self.manager.complete_task(task.id, result={"summary": "Done"})

        with self.assertRaises(InvalidTaskStateError):
            self.manager.cancel_task(task.id, "Cancel")

    def test_fail_task(self):
        """Test failing a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")

        failed = self.manager.fail_task(
            task.id,
            error="API error",
            error_details={"code": 500}
        )

        self.assertEqual(failed.state, TaskState.FAILED)
        self.assertEqual(failed.error, "API error")
        self.assertEqual(failed.error_details["code"], 500)

    def test_fail_task_already_completed(self):
        """Test failing already completed task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        self.manager.assign_task(task.id, "agent-001")
        self.manager.complete_task(task.id, result={"summary": "Done"})

        with self.assertRaises(InvalidTaskStateError):
            self.manager.fail_task(task.id, error="Error")

    def test_get_task(self):
        """Test getting a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Research Task",
            description="Test research",
            payload={"query": "test"}
        )

        result = self.manager.get_task(task.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, task.id)

    def test_get_task_not_found(self):
        """Test getting non-existent task."""
        result = self.manager.get_task("task-999")
        self.assertIsNone(result)

    def test_get_tasks_by_agent(self):
        """Test getting tasks by agent."""
        task1 = self.manager.create_task(
            task_type="research",
            title="Task 1",
            description="Test",
            payload={}
        )
        self.manager.assign_task(task1.id, "agent-001")

        task2 = self.manager.create_task(
            task_type="research",
            title="Task 2",
            description="Test",
            payload={}
        )
        self.manager.assign_task(task2.id, "agent-002")

        task3 = self.manager.create_task(
            task_type="research",
            title="Task 3",
            description="Test",
            payload={}
        )
        self.manager.assign_task(task3.id, "agent-001")

        results = self.manager.get_tasks_by_agent("agent-001")

        self.assertEqual(len(results), 2)
        self.assertIn(task1.id, [t.id for t in results])
        self.assertIn(task3.id, [t.id for t in results])

    def test_get_tasks_by_state(self):
        """Test getting tasks by state."""
        task1 = self.manager.create_task(
            task_type="research",
            title="Task 1",
            description="Test",
            payload={}
        )

        task2 = self.manager.create_task(
            task_type="research",
            title="Task 2",
            description="Test",
            payload={}
        )
        self.manager.assign_task(task2.id, "agent-001")

        task3 = self.manager.create_task(
            task_type="research",
            title="Task 3",
            description="Test",
            payload={}
        )

        results = self.manager.get_tasks_by_state("created")

        self.assertEqual(len(results), 2)

    def test_get_active_tasks(self):
        """Test getting active tasks."""
        task1 = self.manager.create_task(
            task_type="research",
            title="Task 1",
            description="Test",
            payload={}
        )

        task2 = self.manager.create_task(
            task_type="research",
            title="Task 2",
            description="Test",
            payload={}
        )
        self.manager.assign_task(task2.id, "agent-001")

        task3 = self.manager.create_task(
            task_type="research",
            title="Task 3",
            description="Test",
            payload={}
        )
        self.manager.complete_task(task3.id, result={"summary": "Done"})

        active = self.manager.get_active_tasks()

        self.assertEqual(len(active), 2)
        self.assertIn(task1.id, [t.id for t in active])
        self.assertIn(task2.id, [t.id for t in active])

    def test_list_tasks(self):
        """Test listing all tasks."""
        self.manager.create_task(
            task_type="research",
            title="Task 1",
            description="Test",
            payload={}
        )

        self.manager.create_task(
            task_type="research",
            title="Task 2",
            description="Test",
            payload={}
        )

        tasks = self.manager.list_tasks()

        self.assertEqual(len(tasks), 2)

    def test_delete_task(self):
        """Test deleting a task."""
        task = self.manager.create_task(
            task_type="research",
            title="Task",
            description="Test",
            payload={}
        )

        result = self.manager.delete_task(task.id)

        self.assertTrue(result)
        self.assertNotIn(task.id, self.manager.tasks)

    def test_delete_task_not_found(self):
        """Test deleting non-existent task."""
        result = self.manager.delete_task("task-999")
        self.assertFalse(result)

    def test_progress_clamping(self):
        """Test that progress is clamped between 0 and 1."""
        task = self.manager.create_task(
            task_type="research",
            title="Task",
            description="Test",
            payload={}
        )

        # Test > 1
        updated = self.manager.update_task_status(task.id, "assigned", progress=1.5)
        self.assertEqual(updated.progress, 1.0)

        # Test < 0
        updated = self.manager.update_task_status(task.id, "assigned", progress=-0.5)
        self.assertEqual(updated.progress, 0.0)


if __name__ == "__main__":
    unittest.main()
