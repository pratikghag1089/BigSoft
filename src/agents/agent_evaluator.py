"""Agent Performance Evaluation and Lifecycle Management."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import Agent, AgentStatus, Task, TaskStatus
from .agent_factory import AgentFactory

logger = logging.getLogger(__name__)


class AgentEvaluator:
    """
    Evaluates agent performance and manages agent lifecycle.
    Automatically removes underperforming or useless agents.
    """

    def __init__(self, db_session: Session, agent_factory: AgentFactory):
        self.db_session = db_session
        self.agent_factory = agent_factory

        # Performance thresholds
        self.min_success_rate = 0.4  # 40% minimum success rate
        self.min_tasks_before_eval = 3  # Need at least 3 tasks to evaluate
        self.max_idle_minutes = 60  # Delete if idle for 60 minutes
        self.max_failed_tasks_ratio = 0.7  # Max 70% failures

    def evaluate_all_agents(self) -> Dict[str, Any]:
        """
        Evaluate all active agents and remove underperformers.

        Returns:
            Evaluation summary
        """
        logger.info("Evaluating all agents...")

        agents = self.db_session.query(Agent).filter(
            Agent.status.in_([AgentStatus.RUNNING, AgentStatus.CREATED, AgentStatus.PAUSED])
        ).all()

        results = {
            "evaluated": 0,
            "kept": 0,
            "terminated": 0,
            "reasons": []
        }

        for agent in agents:
            should_keep, reason = self._evaluate_agent(agent)

            results["evaluated"] += 1

            if should_keep:
                results["kept"] += 1
                logger.debug(f"Agent {agent.id} ({agent.name}): KEPT - {reason}")
            else:
                results["terminated"] += 1
                results["reasons"].append(f"{agent.name}: {reason}")
                self._terminate_agent(agent, reason)
                logger.info(f"Agent {agent.id} ({agent.name}): TERMINATED - {reason}")

        logger.info(f"Evaluation complete: {results['terminated']} agents terminated")
        return results

    def _evaluate_agent(self, agent: Agent) -> tuple[bool, str]:
        """
        Evaluate a single agent's performance.

        Args:
            agent: Agent to evaluate

        Returns:
            (should_keep, reason)
        """
        # Skip master agents
        if agent.agent_type == "master":
            return True, "Master agent - protected"

        # Check if agent has any tasks
        task_count = self.db_session.query(Task).filter(Task.agent_id == agent.id).count()

        if task_count == 0:
            # Check if agent is too old without tasks
            if agent.created_at:
                age_minutes = (datetime.utcnow() - agent.created_at).total_seconds() / 60
                if age_minutes > self.max_idle_minutes:
                    return False, f"No tasks in {age_minutes:.0f} minutes"

            return True, "Too new to evaluate"

        # Not enough tasks to evaluate
        if task_count < self.min_tasks_before_eval:
            return True, f"Only {task_count} tasks - need {self.min_tasks_before_eval}"

        # Check success rate
        completed = self.db_session.query(Task).filter(
            Task.agent_id == agent.id,
            Task.status == TaskStatus.COMPLETED
        ).count()

        failed = self.db_session.query(Task).filter(
            Task.agent_id == agent.id,
            Task.status == TaskStatus.FAILED
        ).count()

        success_rate = completed / task_count if task_count > 0 else 0

        if success_rate < self.min_success_rate:
            return False, f"Low success rate: {success_rate:.1%} < {self.min_success_rate:.1%}"

        # Check failure ratio
        if failed > 0:
            failure_ratio = failed / task_count
            if failure_ratio > self.max_failed_tasks_ratio:
                return False, f"High failure ratio: {failure_ratio:.1%}"

        # Check if agent is idle for too long
        if agent.status == AgentStatus.RUNNING:
            last_task = self.db_session.query(Task).filter(
                Task.agent_id == agent.id
            ).order_by(Task.created_at.desc()).first()

            if last_task and last_task.completed_at:
                idle_minutes = (datetime.utcnow() - last_task.completed_at).total_seconds() / 60
                if idle_minutes > self.max_idle_minutes:
                    return False, f"Idle for {idle_minutes:.0f} minutes"

        # Check agent efficiency (tasks per hour)
        if agent.created_at:
            age_hours = (datetime.utcnow() - agent.created_at).total_seconds() / 3600
            if age_hours > 1:  # At least 1 hour old
                tasks_per_hour = task_count / age_hours
                if tasks_per_hour < 0.5:  # Less than 1 task per 2 hours
                    return False, f"Low productivity: {tasks_per_hour:.2f} tasks/hour"

        return True, f"Good performance: {success_rate:.1%} success rate"

    def _terminate_agent(self, agent: Agent, reason: str):
        """Terminate an agent and log the reason."""
        # Use agent factory to properly terminate
        self.agent_factory.delete_agent(agent.id)

        # Log termination in metadata
        agent.extra_data = agent.extra_data or {}
        agent.extra_data["termination_reason"] = reason
        agent.extra_data["terminated_at"] = datetime.utcnow().isoformat()

        self.db_session.commit()

    def get_agent_performance_report(self, agent_id: int) -> Dict[str, Any]:
        """
        Get detailed performance report for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Performance report
        """
        agent = self.db_session.query(Agent).filter_by(id=agent_id).first()
        if not agent:
            return {"error": "Agent not found"}

        tasks = self.db_session.query(Task).filter(Task.agent_id == agent_id).all()

        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)

        success_rate = completed / total_tasks if total_tasks > 0 else 0

        # Calculate average task time
        completed_tasks = [t for t in tasks if t.completed_at and t.started_at]
        if completed_tasks:
            avg_time = sum(
                (t.completed_at - t.started_at).total_seconds()
                for t in completed_tasks
            ) / len(completed_tasks)
        else:
            avg_time = 0

        # Calculate uptime
        uptime = 0
        if agent.started_at:
            end_time = agent.completed_at or datetime.utcnow()
            uptime = (end_time - agent.started_at).total_seconds()

        return {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "agent_type": agent.agent_type,
            "status": agent.status.value,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "uptime_seconds": uptime,
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "in_progress": in_progress,
            "success_rate": success_rate,
            "avg_task_time_seconds": avg_time,
            "tasks_per_hour": (total_tasks / (uptime / 3600)) if uptime > 0 else 0
        }

    def get_system_agent_stats(self) -> Dict[str, Any]:
        """Get overall system agent statistics."""
        total_agents = self.db_session.query(Agent).count()
        active_agents = self.db_session.query(Agent).filter(
            Agent.status == AgentStatus.RUNNING
        ).count()
        terminated_agents = self.db_session.query(Agent).filter(
            Agent.status == AgentStatus.TERMINATED
        ).count()

        # Get termination reasons
        terminated = self.db_session.query(Agent).filter(
            Agent.status == AgentStatus.TERMINATED
        ).all()

        termination_reasons = {}
        for agent in terminated:
            if agent.extra_data and "termination_reason" in agent.extra_data:
                reason = agent.extra_data["termination_reason"]
                termination_reasons[reason] = termination_reasons.get(reason, 0) + 1

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "terminated_agents": terminated_agents,
            "termination_reasons": termination_reasons
        }
