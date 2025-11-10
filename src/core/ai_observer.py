"""AI Observer - Broadcasts AI thoughts and actions to UI."""

import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AIObserver:
    """
    Observes and broadcasts AI thoughts, decisions, and actions.
    This provides full transparency into what the AI is thinking and doing.
    """

    def __init__(self, websocket_manager=None):
        self.ws_manager = websocket_manager
        self._enabled = websocket_manager is not None

    def set_websocket_manager(self, ws_manager):
        """Set the WebSocket manager for broadcasting."""
        self.ws_manager = ws_manager
        self._enabled = True

    async def broadcast_thought(self, thought: str, context: Dict[str, Any] = None):
        """Broadcast an AI thought process."""
        if not self._enabled:
            return

        try:
            await self.ws_manager.send_thought(thought, context or {})
        except Exception as e:
            logger.error(f"Error broadcasting thought: {e}")

    def broadcast_thought_sync(self, thought: str, context: Dict[str, Any] = None):
        """Synchronous version of broadcast_thought."""
        if not self._enabled:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast_thought(thought, context))
            else:
                loop.run_until_complete(self.broadcast_thought(thought, context))
        except Exception as e:
            logger.error(f"Error broadcasting thought sync: {e}")

    async def broadcast_decision(self, decision: str, reasoning: str, data: Dict[str, Any] = None):
        """Broadcast a decision made by the AI."""
        if not self._enabled:
            return

        try:
            await self.ws_manager.send_decision(decision, reasoning, data or {})
        except Exception as e:
            logger.error(f"Error broadcasting decision: {e}")

    def broadcast_decision_sync(self, decision: str, reasoning: str, data: Dict[str, Any] = None):
        """Synchronous version of broadcast_decision."""
        if not self._enabled:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast_decision(decision, reasoning, data))
            else:
                loop.run_until_complete(self.broadcast_decision(decision, reasoning, data))
        except Exception as e:
            logger.error(f"Error broadcasting decision sync: {e}")

    async def broadcast_agent_action(self, agent_id: int, agent_name: str, action: str, details: Dict[str, Any] = None):
        """Broadcast an agent action."""
        if not self._enabled:
            return

        try:
            await self.ws_manager.send_agent_action(agent_id, agent_name, action, details or {})
        except Exception as e:
            logger.error(f"Error broadcasting agent action: {e}")

    def broadcast_agent_action_sync(self, agent_id: int, agent_name: str, action: str, details: Dict[str, Any] = None):
        """Synchronous version of broadcast_agent_action."""
        if not self._enabled:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast_agent_action(agent_id, agent_name, action, details))
            else:
                loop.run_until_complete(self.broadcast_agent_action(agent_id, agent_name, action, details))
        except Exception as e:
            logger.error(f"Error broadcasting agent action sync: {e}")

    async def broadcast_system_event(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Broadcast a system event."""
        if not self._enabled:
            return

        try:
            await self.ws_manager.send_system_event(event_type, message, data or {})
        except Exception as e:
            logger.error(f"Error broadcasting system event: {e}")

    def broadcast_system_event_sync(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Synchronous version of broadcast_system_event."""
        if not self._enabled:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broadcast_system_event(event_type, message, data))
            else:
                loop.run_until_complete(self.broadcast_system_event(event_type, message, data))
        except Exception as e:
            logger.error(f"Error broadcasting system event sync: {e}")


# Global observer instance
observer = AIObserver()
