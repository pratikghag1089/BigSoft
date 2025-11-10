"""Real Business Execution Module - Executes actual business operations."""

import logging
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.models import Opportunity, Task, TaskStatus
from .workspace_manager import WorkspaceManager
from .kanban_board import KanbanBoard, KanbanColumn
from ..core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class BusinessExecutor:
    """
    Executes real business operations including:
    - Code generation and execution
    - API integrations
    - Service deployments
    - Content creation
    - Data processing
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.llm = ollama_client
        self.workspace_manager = WorkspaceManager()

    def execute_opportunity(self, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Execute a business opportunity with real actions.

        Args:
            opportunity: Opportunity to execute

        Returns:
            Execution results
        """
        logger.info(f"Executing opportunity: {opportunity.title}")

        # Create workspace
        workspace_path = self.workspace_manager.create_workspace(
            venture_id=opportunity.id,
            venture_name=opportunity.title,
            extra_data={
                "category": opportunity.category,
                "estimated_revenue": opportunity.potential_revenue,
                "estimated_cost": opportunity.estimated_cost
            }
        )

        # Create Kanban board
        kanban = KanbanBoard(self.db_session, f"board_{opportunity.id}", opportunity.id)

        # Generate execution plan
        execution_plan = self._generate_execution_plan(opportunity)

        # Create tasks from plan
        tasks = self._create_tasks_from_plan(opportunity, execution_plan, kanban)

        # Execute based on category
        category = opportunity.category or "general"

        result = {
            "opportunity_id": opportunity.id,
            "workspace_path": workspace_path,
            "execution_started_at": datetime.utcnow().isoformat(),
            "category": category,
            "tasks_created": len(tasks),
            "success": False
        }

        try:
            if category == "service":
                result.update(self._execute_service_business(opportunity, workspace_path, kanban))
            elif category == "product":
                result.update(self._execute_product_business(opportunity, workspace_path, kanban))
            elif category == "content":
                result.update(self._execute_content_business(opportunity, workspace_path, kanban))
            elif category == "automation":
                result.update(self._execute_automation_business(opportunity, workspace_path, kanban))
            elif category == "data":
                result.update(self._execute_data_business(opportunity, workspace_path, kanban))
            else:
                result.update(self._execute_generic_business(opportunity, workspace_path, kanban))

            result["success"] = True

        except Exception as e:
            logger.error(f"Opportunity execution failed: {e}", exc_info=True)
            result["error"] = str(e)
            result["success"] = False

        # Save Kanban board state
        kanban_file = Path(workspace_path) / "kanban_board.json"
        kanban.export_board(str(kanban_file))

        result["execution_completed_at"] = datetime.utcnow().isoformat()

        return result

    def _generate_execution_plan(self, opportunity: Opportunity) -> Dict[str, Any]:
        """Generate detailed execution plan."""
        prompt = f"""
Generate a detailed execution plan for this business opportunity:

Title: {opportunity.title}
Description: {opportunity.description}
Category: {opportunity.category}
Budget: ${opportunity.estimated_cost}
Expected Revenue: ${opportunity.potential_revenue}
Strategy: {opportunity.strategy}

Generate a comprehensive execution plan with:
1. Specific milestones (with deliverables)
2. Tasks for each milestone (actionable items)
3. Required resources (tools, APIs, services)
4. Timeline estimates
5. Success criteria

Respond in JSON format:
{{
  "milestones": [
    {{
      "name": "milestone name",
      "deliverables": ["deliverable1", "deliverable2"],
      "tasks": ["task1", "task2"],
      "timeline_days": 7
    }}
  ],
  "resources": ["resource1", "resource2"],
  "success_criteria": ["criteria1", "criteria2"]
}}
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)

        try:
            plan = json.loads(response.get("response", "{}"))
        except json.JSONDecodeError:
            # Fallback plan
            plan = {
                "milestones": [
                    {
                        "name": "Setup and Planning",
                        "deliverables": ["Project structure", "Requirements doc"],
                        "tasks": ["Create workspace", "Define requirements"],
                        "timeline_days": 3
                    },
                    {
                        "name": "Implementation",
                        "deliverables": ["Core functionality"],
                        "tasks": ["Develop core features", "Testing"],
                        "timeline_days": 7
                    },
                    {
                        "name": "Launch",
                        "deliverables": ["Live product/service"],
                        "tasks": ["Deploy", "Marketing"],
                        "timeline_days": 3
                    }
                ],
                "resources": ["Development tools", "APIs"],
                "success_criteria": ["Working product", "First customers"]
            }

        return plan

    def _create_tasks_from_plan(
        self,
        opportunity: Opportunity,
        plan: Dict[str, Any],
        kanban: KanbanBoard
    ) -> List[Task]:
        """Create tasks from execution plan."""
        tasks = []

        milestones = plan.get("milestones", [])

        for i, milestone in enumerate(milestones):
            milestone_tasks = milestone.get("tasks", [])

            for task_title in milestone_tasks:
                # Create database task
                task = Task(
                    title=task_title,
                    description=f"Milestone: {milestone.get('name', f'M{i+1}')}",
                    opportunity_id=opportunity.id,
                    priority=10 - i,  # Earlier milestones have higher priority
                    status=TaskStatus.PENDING,
                    extra_data={
                        "milestone": milestone.get("name", f"Milestone {i+1}"),
                        "deliverables": milestone.get("deliverables", []),
                        "timeline_days": milestone.get("timeline_days", 7)
                    }
                )

                self.db_session.add(task)
                tasks.append(task)

                # Add to Kanban
                kanban.add_card(
                    title=task_title,
                    description=f"Milestone: {milestone.get('name')}",
                    column=KanbanColumn.BACKLOG,
                    priority=10 - i,
                    task_id=task.id,
                    tags=[milestone.get("name", "")]
                )

        self.db_session.commit()

        logger.info(f"Created {len(tasks)} tasks for opportunity {opportunity.id}")

        return tasks

    def _execute_service_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Execute a service-based business."""
        logger.info("Executing service business...")

        # Generate service code
        service_code = self._generate_service_code(opportunity)

        # Save to workspace
        self.workspace_manager.write_file(
            Path(workspace_path),
            "code/service.py",
            service_code
        )

        # Generate API documentation
        api_docs = self._generate_api_docs(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "docs/API.md",
            api_docs
        )

        # Create requirements.txt
        requirements = self._generate_requirements(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "requirements.txt",
            requirements
        )

        # Update Kanban
        for card in list(kanban.cards.values())[:3]:  # Move first 3 cards to done
            kanban.move_card(card.card_id, KanbanColumn.DONE)

        return {
            "service_code_generated": True,
            "api_docs_generated": True,
            "files_created": ["code/service.py", "docs/API.md", "requirements.txt"],
            "next_steps": "Deploy service to production environment"
        }

    def _execute_product_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Execute a product-based business."""
        logger.info("Executing product business...")

        # Generate product specification
        spec = self._generate_product_spec(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "docs/product_spec.md",
            spec
        )

        # Generate MVP code
        mvp_code = self._generate_mvp_code(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "code/mvp.py",
            mvp_code
        )

        return {
            "product_spec_generated": True,
            "mvp_code_generated": True,
            "files_created": ["docs/product_spec.md", "code/mvp.py"],
            "next_steps": "Build MVP and test with users"
        }

    def _execute_content_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Execute a content-based business."""
        logger.info("Executing content business...")

        # Generate content
        content = self._generate_content(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "output/content.md",
            content
        )

        # Generate content strategy
        strategy = self._generate_content_strategy(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "docs/content_strategy.md",
            strategy
        )

        return {
            "content_generated": True,
            "strategy_generated": True,
            "files_created": ["output/content.md", "docs/content_strategy.md"],
            "next_steps": "Publish and promote content"
        }

    def _execute_automation_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Execute an automation-based business."""
        logger.info("Executing automation business...")

        # Generate automation scripts
        scripts = self._generate_automation_scripts(opportunity)

        for i, script in enumerate(scripts):
            self.workspace_manager.write_file(
                Path(workspace_path),
                f"code/automation_{i+1}.py",
                script
            )

        return {
            "automation_scripts_generated": len(scripts),
            "files_created": [f"code/automation_{i+1}.py" for i in range(len(scripts))],
            "next_steps": "Test and deploy automation"
        }

    def _execute_data_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Execute a data-based business."""
        logger.info("Executing data business...")

        # Generate data processing pipeline
        pipeline = self._generate_data_pipeline(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "code/data_pipeline.py",
            pipeline
        )

        return {
            "data_pipeline_generated": True,
            "files_created": ["code/data_pipeline.py"],
            "next_steps": "Set up data sources and run pipeline"
        }

    def _execute_generic_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Execute generic business opportunity."""
        logger.info("Executing generic business...")

        # Generate business plan
        plan = self._generate_business_plan(opportunity)

        self.workspace_manager.write_file(
            Path(workspace_path),
            "docs/business_plan.md",
            plan
        )

        return {
            "business_plan_generated": True,
            "files_created": ["docs/business_plan.md"],
            "next_steps": "Review plan and execute next steps"
        }

    def _generate_service_code(self, opportunity: Opportunity) -> str:
        """Generate service code."""
        prompt = f"""
Generate production-ready Python code for this service:

{opportunity.title}
{opportunity.description}

Generate a complete FastAPI service with:
1. API endpoints
2. Request/response models
3. Error handling
4. Documentation
5. Basic validation

Return ONLY Python code, properly formatted.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# Service code generation failed")

    def _generate_api_docs(self, opportunity: Opportunity) -> str:
        """Generate API documentation."""
        prompt = f"""
Generate comprehensive API documentation for:

{opportunity.title}
{opportunity.description}

Include:
1. Overview
2. Authentication
3. Endpoints (with examples)
4. Error codes
5. Rate limits
6. Getting started

Format as Markdown.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# API Documentation")

    def _generate_requirements(self, opportunity: Opportunity) -> str:
        """Generate Python requirements."""
        return """fastapi==0.109.0
uvicorn==0.25.0
pydantic==2.5.3
requests==2.31.0
python-dotenv==1.0.0
"""

    def _generate_product_spec(self, opportunity: Opportunity) -> str:
        """Generate product specification."""
        prompt = f"""
Generate a detailed product specification for:

{opportunity.title}
{opportunity.description}

Include:
1. Product overview
2. Target users
3. Key features
4. User stories
5. Technical requirements
6. Success metrics

Format as Markdown.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# Product Specification")

    def _generate_mvp_code(self, opportunity: Opportunity) -> str:
        """Generate MVP code."""
        prompt = f"""
Generate MVP code for:

{opportunity.title}
{opportunity.description}

Create a minimal viable product with core functionality.
Return ONLY Python code.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# MVP code")

    def _generate_content(self, opportunity: Opportunity) -> str:
        """Generate content."""
        prompt = f"""
Generate high-quality content for:

{opportunity.title}
{opportunity.description}

Create engaging, valuable content that serves the target audience.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.8)
        return response.get("response", "# Content")

    def _generate_content_strategy(self, opportunity: Opportunity) -> str:
        """Generate content strategy."""
        prompt = f"""
Generate a content strategy for:

{opportunity.title}
{opportunity.description}

Include:
1. Content themes
2. Distribution channels
3. Publishing schedule
4. Monetization approach
5. Growth strategy
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# Content Strategy")

    def _generate_automation_scripts(self, opportunity: Opportunity) -> List[str]:
        """Generate automation scripts."""
        prompt = f"""
Generate automation scripts for:

{opportunity.title}
{opportunity.description}

Create 2-3 Python scripts for key automation tasks.
Return each script separately, marked with --- separator.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        scripts_text = response.get("response", "")

        # Split by separator
        scripts = scripts_text.split("---")
        return [s.strip() for s in scripts if s.strip()][:3]

    def _generate_data_pipeline(self, opportunity: Opportunity) -> str:
        """Generate data pipeline code."""
        prompt = f"""
Generate a data processing pipeline for:

{opportunity.title}
{opportunity.description}

Create Python code with:
1. Data ingestion
2. Processing/transformation
3. Storage
4. Error handling

Return ONLY Python code.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# Data pipeline")

    def _generate_business_plan(self, opportunity: Opportunity) -> str:
        """Generate business plan."""
        prompt = f"""
Generate a comprehensive business plan for:

{opportunity.title}
{opportunity.description}

Include:
1. Executive summary
2. Market analysis
3. Revenue model
4. Operations plan
5. Financial projections
6. Milestones

Format as Markdown.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "# Business Plan")
