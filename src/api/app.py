"""FastAPI application for monitoring dashboard."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.config import settings
from ..database import get_db, Agent, Task, Opportunity, Metric, SystemState
from ..database.models import AgentStatus, TaskStatus, OpportunityStatus

logger = logging.getLogger(__name__)


# Pydantic models for API
class SystemStatusResponse(BaseModel):
    """System status response."""
    status: str
    capital: float
    total_agents: int
    active_agents: int
    total_tasks: int
    total_opportunities: int
    uptime: str


class AgentResponse(BaseModel):
    """Agent response model."""
    id: int
    name: str
    agent_type: str
    status: str
    role: str
    created_at: Optional[str]
    tasks_completed: int


class TaskResponse(BaseModel):
    """Task response model."""
    id: int
    title: str
    description: str
    status: str
    priority: int
    agent_id: Optional[int]
    created_at: Optional[str]


class OpportunityResponse(BaseModel):
    """Opportunity response model."""
    id: int
    title: str
    description: str
    status: str
    potential_revenue: float
    estimated_cost: float
    profit_margin: float
    risk_score: float
    confidence_score: float


class MetricResponse(BaseModel):
    """Metric response model."""
    id: int
    metric_type: str
    metric_name: str
    value: float
    recorded_at: str


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI Entrepreneur Agent System - Monitoring Dashboard",
        version="1.0.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.app_name,
            "version": "1.0.0",
            "status": "running"
        }

    @app.get("/api/status", response_model=SystemStatusResponse)
    async def get_system_status(db: Session = Depends(get_db)):
        """Get system status."""
        # Get capital
        capital_state = db.query(SystemState).filter_by(key="capital").first()
        capital = capital_state.value.get("amount", 0) if capital_state else settings.initial_capital

        # Get counts
        total_agents = db.query(Agent).count()
        active_agents = db.query(Agent).filter(Agent.status == AgentStatus.RUNNING).count()
        total_tasks = db.query(Task).count()
        total_opportunities = db.query(Opportunity).count()

        return {
            "status": "running",
            "capital": capital,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_tasks": total_tasks,
            "total_opportunities": total_opportunities,
            "uptime": "N/A"
        }

    @app.get("/api/agents", response_model=List[AgentResponse])
    async def list_agents(
        status: Optional[str] = Query(None),
        limit: int = Query(100, le=1000),
        db: Session = Depends(get_db)
    ):
        """List all agents."""
        query = db.query(Agent)

        if status:
            try:
                status_enum = AgentStatus(status)
                query = query.filter(Agent.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        agents = query.limit(limit).all()

        return [
            {
                "id": agent.id,
                "name": agent.name,
                "agent_type": agent.agent_type,
                "status": agent.status.value,
                "role": agent.role,
                "created_at": agent.created_at.isoformat() if agent.created_at else None,
                "tasks_completed": agent.tasks_completed
            }
            for agent in agents
        ]

    @app.get("/api/agents/{agent_id}", response_model=AgentResponse)
    async def get_agent(agent_id: int, db: Session = Depends(get_db)):
        """Get specific agent details."""
        agent = db.query(Agent).filter_by(id=agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "id": agent.id,
            "name": agent.name,
            "agent_type": agent.agent_type,
            "status": agent.status.value,
            "role": agent.role,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "tasks_completed": agent.tasks_completed
        }

    @app.get("/api/tasks", response_model=List[TaskResponse])
    async def list_tasks(
        status: Optional[str] = Query(None),
        limit: int = Query(100, le=1000),
        db: Session = Depends(get_db)
    ):
        """List all tasks."""
        query = db.query(Task)

        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter(Task.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        tasks = query.order_by(Task.created_at.desc()).limit(limit).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority,
                "agent_id": task.agent_id,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            for task in tasks
        ]

    @app.get("/api/opportunities", response_model=List[OpportunityResponse])
    async def list_opportunities(
        status: Optional[str] = Query(None),
        limit: int = Query(100, le=1000),
        db: Session = Depends(get_db)
    ):
        """List all opportunities."""
        query = db.query(Opportunity)

        if status:
            try:
                status_enum = OpportunityStatus(status)
                query = query.filter(Opportunity.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        opportunities = query.order_by(Opportunity.identified_at.desc()).limit(limit).all()

        return [
            {
                "id": opp.id,
                "title": opp.title,
                "description": opp.description,
                "status": opp.status.value,
                "potential_revenue": opp.potential_revenue,
                "estimated_cost": opp.estimated_cost,
                "profit_margin": opp.profit_margin,
                "risk_score": opp.risk_score,
                "confidence_score": opp.confidence_score
            }
            for opp in opportunities
        ]

    @app.get("/api/metrics", response_model=List[MetricResponse])
    async def list_metrics(
        metric_type: Optional[str] = Query(None),
        limit: int = Query(100, le=1000),
        db: Session = Depends(get_db)
    ):
        """List metrics."""
        query = db.query(Metric)

        if metric_type:
            query = query.filter(Metric.metric_type == metric_type)

        metrics = query.order_by(Metric.recorded_at.desc()).limit(limit).all()

        return [
            {
                "id": metric.id,
                "metric_type": metric.metric_type,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "recorded_at": metric.recorded_at.isoformat()
            }
            for metric in metrics
        ]

    @app.get("/api/dashboard")
    async def get_dashboard_data(db: Session = Depends(get_db)):
        """Get comprehensive dashboard data."""
        # Capital
        capital_state = db.query(SystemState).filter_by(key="capital").first()
        capital = capital_state.value.get("amount", 0) if capital_state else settings.initial_capital

        # Agent stats
        total_agents = db.query(Agent).count()
        active_agents = db.query(Agent).filter(Agent.status == AgentStatus.RUNNING).count()

        # Task stats
        total_tasks = db.query(Task).count()
        completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
        failed_tasks = db.query(Task).filter(Task.status == TaskStatus.FAILED).count()

        # Opportunity stats
        total_opps = db.query(Opportunity).count()
        completed_opps = db.query(Opportunity).filter(Opportunity.status == OpportunityStatus.COMPLETED).count()

        # Recent metrics
        recent_metrics = db.query(Metric).order_by(Metric.recorded_at.desc()).limit(10).all()

        # Calculate profit
        profit = capital - settings.initial_capital
        roi = (profit / settings.initial_capital * 100) if settings.initial_capital > 0 else 0

        return {
            "financials": {
                "initial_capital": settings.initial_capital,
                "current_capital": capital,
                "profit": profit,
                "roi_percent": roi
            },
            "agents": {
                "total": total_agents,
                "active": active_agents,
                "inactive": total_agents - active_agents
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "opportunities": {
                "total": total_opps,
                "completed": completed_opps
            },
            "recent_metrics": [
                {
                    "type": m.metric_type,
                    "name": m.metric_name,
                    "value": m.value,
                    "timestamp": m.recorded_at.isoformat()
                }
                for m in recent_metrics
            ]
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

    return app
