"""Factory for creating and managing AI agents."""

import logging
from typing import Dict, Any, Optional, Type, List
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from .specialized_agents import ResearchAgent, AnalystAgent, DeveloperAgent, MarketingAgent
from ..database.models import Agent as AgentModel, AgentStatus

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating and managing AI agents.
    Handles agent lifecycle, creation, and deletion.
    """

    # Registry of available agent types
    AGENT_TYPES: Dict[str, Type[BaseAgent]] = {
        "researcher": ResearchAgent,
        "analyst": AnalystAgent,
        "developer": DeveloperAgent,
        "marketing": MarketingAgent,
    }

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.active_agents: Dict[int, BaseAgent] = {}

    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
        parent_agent_id: Optional[int] = None,
        **kwargs
    ) -> Optional[BaseAgent]:
        """
        Create a new agent of the specified type.

        Args:
            agent_type: Type of agent to create
            name: Optional custom name
            parent_agent_id: ID of parent agent if any
            **kwargs: Additional arguments for agent initialization

        Returns:
            The created agent instance or None if failed
        """
        if agent_type not in self.AGENT_TYPES:
            logger.error(f"Unknown agent type: {agent_type}")
            return None

        try:
            agent_class = self.AGENT_TYPES[agent_type]
            agent = agent_class(
                name=name,
                parent_agent_id=parent_agent_id,
                db_session=self.db_session,
                **kwargs
            )

            # Save to database
            agent.save_to_db()

            # Track active agent
            self.active_agents[agent.agent_id] = agent

            logger.info(f"Created agent: {agent.name} (ID: {agent.agent_id}, Type: {agent_type})")
            return agent

        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            return None

    def get_agent(self, agent_id: int) -> Optional[BaseAgent]:
        """
        Get an active agent by ID.

        Args:
            agent_id: The agent ID

        Returns:
            The agent instance or None if not found
        """
        return self.active_agents.get(agent_id)

    def delete_agent(self, agent_id: int) -> bool:
        """
        Delete an agent and clean up resources.

        Args:
            agent_id: The agent ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get agent from active agents
            agent = self.active_agents.get(agent_id)
            if agent:
                agent.terminate()
                del self.active_agents[agent_id]

            # Update database
            if self.db_session:
                db_agent = self.db_session.query(AgentModel).filter_by(id=agent_id).first()
                if db_agent:
                    db_agent.status = AgentStatus.TERMINATED
                    self.db_session.commit()

            logger.info(f"Deleted agent ID: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            return False

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[Dict[str, Any]]:
        """
        List all agents, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of agent information dictionaries
        """
        if not self.db_session:
            return []

        query = self.db_session.query(AgentModel)
        if status:
            query = query.filter_by(status=status)

        agents = query.all()

        return [
            {
                "id": agent.id,
                "name": agent.name,
                "type": agent.agent_type,
                "status": agent.status.value,
                "created_at": agent.created_at.isoformat() if agent.created_at else None,
                "tasks_completed": agent.tasks_completed,
            }
            for agent in agents
        ]

    def get_agent_count(self, status: Optional[AgentStatus] = None) -> int:
        """
        Get count of agents, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            Number of agents
        """
        if not self.db_session:
            return 0

        query = self.db_session.query(AgentModel)
        if status:
            query = query.filter_by(status=status)

        return query.count()

    def cleanup_inactive_agents(self) -> int:
        """
        Clean up inactive agents from memory.

        Returns:
            Number of agents cleaned up
        """
        cleaned = 0
        inactive_ids = []

        for agent_id, agent in self.active_agents.items():
            if agent.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.TERMINATED]:
                inactive_ids.append(agent_id)

        for agent_id in inactive_ids:
            del self.active_agents[agent_id]
            cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} inactive agents")

        return cleaned

    @classmethod
    def register_agent_type(cls, agent_type: str, agent_class: Type[BaseAgent]):
        """
        Register a new agent type.

        Args:
            agent_type: The type identifier
            agent_class: The agent class
        """
        cls.AGENT_TYPES[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")

    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available agent types."""
        return list(cls.AGENT_TYPES.keys())
