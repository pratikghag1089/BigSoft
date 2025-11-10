"""WebSocket Manager for Real-Time Updates."""

import json
import logging
import asyncio
from typing import Set, Dict, Any, List
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.thought_stream: List[Dict[str, Any]] = []
        self.event_stream: List[Dict[str, Any]] = []
        self.max_stream_size = 1000

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

        # Send recent history to new connection
        await self._send_history(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def _send_history(self, websocket: WebSocket):
        """Send recent history to newly connected client."""
        try:
            # Send recent thoughts
            if self.thought_stream:
                await websocket.send_json({
                    "type": "history",
                    "data": {
                        "thoughts": self.thought_stream[-50:],  # Last 50
                        "events": self.event_stream[-50:]
                    }
                })
        except Exception as e:
            logger.error(f"Error sending history: {e}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def send_thought(self, thought: str, context: Dict[str, Any] = None):
        """Broadcast an AI thought/reasoning."""
        thought_event = {
            "type": "thought",
            "timestamp": datetime.utcnow().isoformat(),
            "thought": thought,
            "context": context or {}
        }

        # Add to stream
        self.thought_stream.append(thought_event)
        if len(self.thought_stream) > self.max_stream_size:
            self.thought_stream = self.thought_stream[-self.max_stream_size:]

        await self.broadcast(thought_event)

    async def send_decision(self, decision: str, reasoning: str, data: Dict[str, Any] = None):
        """Broadcast a decision made by the AI."""
        decision_event = {
            "type": "decision",
            "timestamp": datetime.utcnow().isoformat(),
            "decision": decision,
            "reasoning": reasoning,
            "data": data or {}
        }

        self.event_stream.append(decision_event)
        if len(self.event_stream) > self.max_stream_size:
            self.event_stream = self.event_stream[-self.max_stream_size:]

        await self.broadcast(decision_event)

    async def send_agent_action(self, agent_id: int, agent_name: str, action: str, details: Dict[str, Any] = None):
        """Broadcast an agent action."""
        action_event = {
            "type": "agent_action",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "agent_name": agent_name,
            "action": action,
            "details": details or {}
        }

        self.event_stream.append(action_event)
        await self.broadcast(action_event)

    async def send_system_event(self, event_type: str, message: str, data: Dict[str, Any] = None):
        """Broadcast a system event."""
        system_event = {
            "type": "system_event",
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "data": data or {}
        }

        self.event_stream.append(system_event)
        await self.broadcast(system_event)

    async def send_metrics_update(self, metrics: Dict[str, Any]):
        """Broadcast metrics update."""
        metrics_event = {
            "type": "metrics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }

        await self.broadcast(metrics_event)

    async def send_log(self, level: str, message: str, logger_name: str = "system"):
        """Broadcast a log message."""
        log_event = {
            "type": "log",
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": logger_name,
            "message": message
        }

        await self.broadcast(log_event)


# Global connection manager
manager = ConnectionManager()
