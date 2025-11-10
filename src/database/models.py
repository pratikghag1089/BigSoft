"""Database models for the AI Entrepreneur Agent System."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class AgentStatus(str, enum.Enum):
    """Agent status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class TaskStatus(str, enum.Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OpportunityStatus(str, enum.Enum):
    """Business opportunity status."""
    IDENTIFIED = "identified"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Agent(Base):
    """Agent model representing AI agents in the system."""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    agent_type = Column(String(100), nullable=False)  # e.g., "master", "researcher", "developer"
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.CREATED)

    # Configuration
    role = Column(Text, nullable=False)
    capabilities = Column(JSON, default=list)
    configuration = Column(JSON, default=dict)

    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Parent-child relationship
    parent_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)

    # Metrics
    tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    total_runtime_seconds = Column(Float, default=0.0)

    # Additional data
    extra_data = Column(JSON, default=dict)

    # Relationships
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    children = relationship("Agent", remote_side=[id])


class Task(Base):
    """Task model for work items assigned to agents."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Integer, default=5)  # 1-10, higher is more important

    # Assignment
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True)

    # Execution
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Lifecycle
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Metrics
    iterations = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)

    # Metadata
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)

    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    opportunity = relationship("Opportunity", back_populates="tasks")


class Opportunity(Base):
    """Business opportunity identified by the system."""

    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(OpportunityStatus), default=OpportunityStatus.IDENTIFIED)

    # Evaluation
    potential_revenue = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.5)  # 0-1
    confidence_score = Column(Float, default=0.5)  # 0-1

    # Execution
    actual_revenue = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    actual_profit = Column(Float, default=0.0)

    # Lifecycle
    identified_at = Column(DateTime, default=datetime.utcnow)
    evaluated_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Strategy
    strategy = Column(Text, nullable=True)
    action_plan = Column(JSON, default=list)

    # Additional fields
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    extra_data = Column(JSON, default=dict)

    # Relationships
    tasks = relationship("Task", back_populates="opportunity", cascade="all, delete-orphan")


class Metric(Base):
    """System and business metrics."""

    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(100), nullable=False)  # e.g., "revenue", "cost", "profit"
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)

    # Context
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=dict)

    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Additional data
    extra_data = Column(JSON, default=dict)


class SystemState(Base):
    """Global system state and configuration."""

    __tablename__ = "system_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    extra_data = Column(JSON, default=dict)
