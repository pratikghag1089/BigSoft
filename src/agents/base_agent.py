"""Base agent class for all AI agents in the system."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from ..core.ollama_client import ollama_client
from ..database.models import Agent as AgentModel, AgentStatus, Task, TaskStatus

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Provides common functionality for agent lifecycle and task execution.
    """

    def __init__(
        self,
        agent_id: Optional[int] = None,
        name: Optional[str] = None,
        agent_type: str = "base",
        role: str = "Generic Agent",
        capabilities: Optional[List[str]] = None,
        parent_agent_id: Optional[int] = None,
        db_session: Optional[Session] = None,
    ):
        self.agent_id = agent_id
        self.name = name or f"{agent_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.agent_type = agent_type
        self.role = role
        self.capabilities = capabilities or []
        self.parent_agent_id = parent_agent_id
        self.db_session = db_session
        self.status = AgentStatus.CREATED
        self.llm_client = ollama_client

        # Runtime state
        self.memory: List[Dict[str, str]] = []
        self.context: Dict[str, Any] = {}

    def save_to_db(self):
        """Persist agent to database."""
        if not self.db_session:
            logger.warning("No database session available")
            return

        if self.agent_id:
            # Update existing
            agent = self.db_session.query(AgentModel).filter_by(id=self.agent_id).first()
            if agent:
                agent.status = self.status
                agent.metadata = self.context
        else:
            # Create new
            agent = AgentModel(
                name=self.name,
                agent_type=self.agent_type,
                status=self.status,
                role=self.role,
                capabilities=self.capabilities,
                parent_agent_id=self.parent_agent_id,
                metadata=self.context,
            )
            self.db_session.add(agent)
            self.db_session.flush()
            self.agent_id = agent.id

        self.db_session.commit()

    def update_status(self, status: AgentStatus):
        """Update agent status."""
        self.status = status
        if self.db_session and self.agent_id:
            agent = self.db_session.query(AgentModel).filter_by(id=self.agent_id).first()
            if agent:
                agent.status = status
                if status == AgentStatus.RUNNING and not agent.started_at:
                    agent.started_at = datetime.utcnow()
                elif status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.TERMINATED]:
                    agent.completed_at = datetime.utcnow()
                self.db_session.commit()

    def think(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Use LLM to think and generate a response.

        Args:
            prompt: The prompt to send to the LLM
            system_prompt: Optional system prompt

        Returns:
            The LLM's response
        """
        if not system_prompt:
            system_prompt = f"You are {self.name}, a {self.role}. {' '.join([f'You can {cap}.' for cap in self.capabilities])}"

        # Add to memory
        self.memory.append({"role": "user", "content": prompt})

        # Get response from LLM
        response = self.llm_client.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                *self.memory
            ],
            temperature=0.7,
        )

        response_text = response.get("response", "")

        # Add to memory
        self.memory.append({"role": "assistant", "content": response_text})

        # Keep memory from growing too large
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]

        return response_text

    def execute_task(self, task: Task) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.

        Args:
            task: The task to execute

        Returns:
            Result dictionary with status and output
        """
        logger.info(f"Agent {self.name} executing task: {task.title}")

        try:
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            if self.db_session:
                self.db_session.commit()

            # Execute the task (implemented by subclasses)
            result = self._execute_task_impl(task)

            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result.get("output", "")
            task.output_data = result

            if self.db_session:
                self.db_session.commit()

            return {"success": True, "result": result}

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()

            if self.db_session:
                self.db_session.commit()

            return {"success": False, "error": str(e)}

    @abstractmethod
    def _execute_task_impl(self, task: Task) -> Dict[str, Any]:
        """
        Implementation of task execution (to be overridden by subclasses).

        Args:
            task: The task to execute

        Returns:
            Result dictionary
        """
        pass

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Main execution method for the agent (to be overridden by subclasses).

        Returns:
            Execution result
        """
        pass

    def terminate(self):
        """Terminate the agent."""
        logger.info(f"Terminating agent: {self.name}")
        self.update_status(AgentStatus.TERMINATED)
        self.memory.clear()
        self.context.clear()
