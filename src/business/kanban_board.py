"""Kanban Board System for Project Management."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from enum import Enum

from ..database.models import Task, TaskStatus, Opportunity

logger = logging.getLogger(__name__)


class KanbanColumn(str, Enum):
    """Kanban board columns."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"


class KanbanCard:
    """Represents a card on the Kanban board."""

    def __init__(
        self,
        card_id: str,
        title: str,
        description: str,
        column: KanbanColumn,
        priority: int = 5,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.card_id = card_id
        self.title = title
        self.description = description
        self.column = column
        self.priority = priority
        self.assignee = assignee
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "card_id": self.card_id,
            "title": self.title,
            "description": self.description,
            "column": self.column.value,
            "priority": self.priority,
            "assignee": self.assignee,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class KanbanBoard:
    """
    Kanban board for project management.
    Tracks tasks, visualizes workflow, and manages project progress.
    """

    def __init__(self, db_session: Session, board_id: str, venture_id: Optional[int] = None):
        self.db_session = db_session
        self.board_id = board_id
        self.venture_id = venture_id
        self.cards: Dict[str, KanbanCard] = {}
        self.columns = list(KanbanColumn)

    def add_card(
        self,
        title: str,
        description: str,
        column: KanbanColumn = KanbanColumn.BACKLOG,
        priority: int = 5,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None,
        task_id: Optional[int] = None
    ) -> KanbanCard:
        """
        Add a new card to the board.

        Args:
            title: Card title
            description: Card description
            column: Initial column
            priority: Priority (1-10)
            assignee: Assigned agent/person
            tags: Tags for categorization
            task_id: Optional linked task ID

        Returns:
            Created card
        """
        card_id = f"card_{len(self.cards) + 1}_{datetime.utcnow().timestamp()}"

        metadata = {}
        if task_id:
            metadata["task_id"] = task_id

        card = KanbanCard(
            card_id=card_id,
            title=title,
            description=description,
            column=column,
            priority=priority,
            assignee=assignee,
            tags=tags,
            metadata=metadata
        )

        self.cards[card_id] = card
        logger.info(f"Added card to Kanban: {title} -> {column.value}")

        return card

    def move_card(self, card_id: str, new_column: KanbanColumn) -> bool:
        """
        Move a card to a different column.

        Args:
            card_id: Card ID
            new_column: Target column

        Returns:
            True if moved successfully
        """
        if card_id not in self.cards:
            logger.error(f"Card {card_id} not found")
            return False

        card = self.cards[card_id]
        old_column = card.column

        card.column = new_column
        card.updated_at = datetime.utcnow()

        logger.info(f"Moved card {card_id}: {old_column.value} -> {new_column.value}")

        # Update linked task if exists
        if "task_id" in card.metadata:
            self._sync_task_status(card)

        return True

    def update_card(
        self,
        card_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        assignee: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Update card details."""
        if card_id not in self.cards:
            return False

        card = self.cards[card_id]

        if title:
            card.title = title
        if description:
            card.description = description
        if priority is not None:
            card.priority = priority
        if assignee:
            card.assignee = assignee
        if tags is not None:
            card.tags = tags

        card.updated_at = datetime.utcnow()

        logger.debug(f"Updated card {card_id}")
        return True

    def delete_card(self, card_id: str) -> bool:
        """Delete a card."""
        if card_id in self.cards:
            del self.cards[card_id]
            logger.info(f"Deleted card {card_id}")
            return True
        return False

    def get_column_cards(self, column: KanbanColumn) -> List[KanbanCard]:
        """Get all cards in a specific column."""
        cards = [card for card in self.cards.values() if card.column == column]
        # Sort by priority (higher first)
        cards.sort(key=lambda c: c.priority, reverse=True)
        return cards

    def get_board_state(self) -> Dict[str, Any]:
        """
        Get complete board state.

        Returns:
            Board state with all columns and cards
        """
        board_state = {
            "board_id": self.board_id,
            "venture_id": self.venture_id,
            "columns": {}
        }

        for column in self.columns:
            cards = self.get_column_cards(column)
            board_state["columns"][column.value] = {
                "name": column.value.replace('_', ' ').title(),
                "count": len(cards),
                "cards": [card.to_dict() for card in cards]
            }

        # Add statistics
        board_state["stats"] = self._calculate_stats()

        return board_state

    def sync_from_tasks(self):
        """Sync Kanban board with database tasks."""
        if not self.venture_id:
            return

        # Get tasks for this venture
        tasks = self.db_session.query(Task).filter(
            Task.opportunity_id == self.venture_id
        ).all()

        for task in tasks:
            # Check if card already exists
            existing_card = None
            for card in self.cards.values():
                if card.metadata.get("task_id") == task.id:
                    existing_card = card
                    break

            if existing_card:
                # Update existing card
                column = self._task_status_to_column(task.status)
                if existing_card.column != column:
                    self.move_card(existing_card.card_id, column)
            else:
                # Create new card
                column = self._task_status_to_column(task.status)
                assignee = f"Agent {task.agent_id}" if task.agent_id else None

                self.add_card(
                    title=task.title,
                    description=task.description,
                    column=column,
                    priority=task.priority,
                    assignee=assignee,
                    task_id=task.id
                )

        logger.info(f"Synced {len(tasks)} tasks to Kanban board")

    def _task_status_to_column(self, status: TaskStatus) -> KanbanColumn:
        """Convert task status to Kanban column."""
        mapping = {
            TaskStatus.PENDING: KanbanColumn.TODO,
            TaskStatus.IN_PROGRESS: KanbanColumn.IN_PROGRESS,
            TaskStatus.COMPLETED: KanbanColumn.DONE,
            TaskStatus.FAILED: KanbanColumn.BLOCKED,
            TaskStatus.CANCELLED: KanbanColumn.BLOCKED
        }
        return mapping.get(status, KanbanColumn.BACKLOG)

    def _sync_task_status(self, card: KanbanCard):
        """Sync card column change back to task."""
        task_id = card.metadata.get("task_id")
        if not task_id:
            return

        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            return

        # Update task status based on column
        status_mapping = {
            KanbanColumn.BACKLOG: TaskStatus.PENDING,
            KanbanColumn.TODO: TaskStatus.PENDING,
            KanbanColumn.IN_PROGRESS: TaskStatus.IN_PROGRESS,
            KanbanColumn.REVIEW: TaskStatus.IN_PROGRESS,
            KanbanColumn.TESTING: TaskStatus.IN_PROGRESS,
            KanbanColumn.DONE: TaskStatus.COMPLETED,
            KanbanColumn.BLOCKED: TaskStatus.FAILED
        }

        new_status = status_mapping.get(card.column)
        if new_status and task.status != new_status:
            task.status = new_status
            if new_status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.utcnow()
            elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.utcnow()

            self.db_session.commit()

    def _calculate_stats(self) -> Dict[str, Any]:
        """Calculate board statistics."""
        total_cards = len(self.cards)

        if total_cards == 0:
            return {
                "total_cards": 0,
                "completion_rate": 0,
                "in_progress": 0,
                "blocked": 0
            }

        done_count = len(self.get_column_cards(KanbanColumn.DONE))
        in_progress = len(self.get_column_cards(KanbanColumn.IN_PROGRESS))
        blocked = len(self.get_column_cards(KanbanColumn.BLOCKED))

        return {
            "total_cards": total_cards,
            "completion_rate": (done_count / total_cards) * 100,
            "in_progress": in_progress,
            "blocked": blocked,
            "remaining": total_cards - done_count
        }

    def export_board(self, file_path: str):
        """Export board state to JSON file."""
        board_state = self.get_board_state()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(board_state, f, indent=2)

        logger.info(f"Exported Kanban board to {file_path}")

    def get_wip_limit_status(self, column: KanbanColumn, limit: int = 5) -> Dict[str, Any]:
        """
        Check Work In Progress (WIP) limit for a column.

        Args:
            column: Column to check
            limit: WIP limit

        Returns:
            Status information
        """
        cards = self.get_column_cards(column)
        count = len(cards)

        return {
            "column": column.value,
            "current": count,
            "limit": limit,
            "exceeded": count > limit,
            "available": max(0, limit - count)
        }
