"""Task management and execution framework."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.models import Task, TaskStatus, Agent, AgentStatus
from ..agents.agent_factory import AgentFactory

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages tasks and their execution by agents.
    """

    def __init__(self, db_session: Session, agent_factory: AgentFactory):
        self.db_session = db_session
        self.agent_factory = agent_factory

    def create_task(
        self,
        title: str,
        description: str,
        agent_id: Optional[int] = None,
        opportunity_id: Optional[int] = None,
        priority: int = 5,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Create a new task.

        Args:
            title: Task title
            description: Task description
            agent_id: Optional agent to assign to
            opportunity_id: Optional related opportunity
            priority: Task priority (1-10)
            input_data: Optional input data for the task

        Returns:
            Created Task object
        """
        task = Task(
            title=title,
            description=description,
            agent_id=agent_id,
            opportunity_id=opportunity_id,
            priority=priority,
            status=TaskStatus.PENDING,
            input_data=input_data or {}
        )

        self.db_session.add(task)
        self.db_session.commit()

        logger.info(f"Created task: {title} (ID: {task.id})")
        return task

    def assign_task(self, task_id: int, agent_id: int) -> bool:
        """
        Assign a task to an agent.

        Args:
            task_id: Task ID
            agent_id: Agent ID

        Returns:
            True if successful
        """
        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return False

        agent = self.db_session.query(Agent).filter_by(id=agent_id).first()
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return False

        task.agent_id = agent_id
        self.db_session.commit()

        logger.info(f"Assigned task {task_id} to agent {agent_id}")
        return True

    def execute_task(self, task_id: int) -> Dict[str, Any]:
        """
        Execute a task using its assigned agent.

        Args:
            task_id: Task ID

        Returns:
            Execution result
        """
        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            return {"success": False, "error": "Task not found"}

        if not task.agent_id:
            return {"success": False, "error": "Task not assigned to any agent"}

        # Get agent
        agent = self.agent_factory.get_agent(task.agent_id)
        if not agent:
            return {"success": False, "error": "Agent not found or not active"}

        # Execute
        result = agent.execute_task(task)
        return result

    def get_pending_tasks(self, limit: int = 10) -> List[Task]:
        """
        Get pending tasks ordered by priority.

        Args:
            limit: Maximum number to return

        Returns:
            List of pending tasks
        """
        tasks = self.db_session.query(Task).filter(
            Task.status == TaskStatus.PENDING
        ).order_by(Task.priority.desc(), Task.created_at.asc()).limit(limit).all()

        return tasks

    def get_agent_tasks(
        self,
        agent_id: int,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """
        Get tasks for a specific agent.

        Args:
            agent_id: Agent ID
            status: Optional status filter

        Returns:
            List of tasks
        """
        query = self.db_session.query(Task).filter(Task.agent_id == agent_id)

        if status:
            query = query.filter(Task.status == status)

        return query.all()

    def complete_task(self, task_id: int, result: Dict[str, Any]) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID
            result: Task result data

        Returns:
            True if successful
        """
        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.output_data = result
        task.result = result.get("output", "")

        self.db_session.commit()

        logger.info(f"Task {task_id} marked as completed")
        return True

    def fail_task(self, task_id: int, error: str) -> bool:
        """
        Mark a task as failed.

        Args:
            task_id: Task ID
            error: Error message

        Returns:
            True if successful
        """
        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False

        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        task.error_message = error

        self.db_session.commit()

        logger.info(f"Task {task_id} marked as failed: {error}")
        return True

    def cancel_task(self, task_id: int) -> bool:
        """
        Cancel a task.

        Args:
            task_id: Task ID

        Returns:
            True if successful
        """
        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()

        self.db_session.commit()

        logger.info(f"Task {task_id} cancelled")
        return True

    def get_task_stats(self) -> Dict[str, Any]:
        """
        Get task statistics.

        Returns:
            Statistics dictionary
        """
        total = self.db_session.query(Task).count()
        pending = self.db_session.query(Task).filter(Task.status == TaskStatus.PENDING).count()
        in_progress = self.db_session.query(Task).filter(Task.status == TaskStatus.IN_PROGRESS).count()
        completed = self.db_session.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
        failed = self.db_session.query(Task).filter(Task.status == TaskStatus.FAILED).count()

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }
