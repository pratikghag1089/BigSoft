"""Self-Learning Module - Learns from past performance and improves decision-making."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import Opportunity, OpportunityStatus, Agent, Task, TaskStatus, Metric
from ..core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class SelfLearningEngine:
    """
    Self-learning engine that analyzes past performance and learns patterns.
    Uses feedback loops to improve decision-making over time.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.llm = ollama_client
        self.knowledge_base: Dict[str, Any] = {}
        self.learning_history: List[Dict[str, Any]] = []

    def analyze_past_opportunities(self) -> Dict[str, Any]:
        """
        Analyze all past opportunities to learn success patterns.

        Returns:
            Analysis results with learned patterns
        """
        logger.info("Analyzing past opportunities for learning...")

        # Get completed opportunities
        opportunities = self.db_session.query(Opportunity).filter(
            Opportunity.status.in_([OpportunityStatus.COMPLETED, OpportunityStatus.FAILED])
        ).all()

        if not opportunities:
            return {"message": "No completed opportunities to learn from"}

        # Separate successful and failed
        successful = [o for o in opportunities if o.status == OpportunityStatus.COMPLETED and o.actual_profit > 0]
        failed = [o for o in opportunities if o.status == OpportunityStatus.FAILED or o.actual_profit <= 0]

        # Extract patterns
        analysis = {
            "total_analyzed": len(opportunities),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "success_rate": len(successful) / len(opportunities) if opportunities else 0,
            "patterns": {}
        }

        # Analyze successful patterns
        if successful:
            analysis["patterns"]["successful"] = self._extract_patterns(successful, "successful")

        # Analyze failure patterns
        if failed:
            analysis["patterns"]["failed"] = self._extract_patterns(failed, "failed")

        # Use LLM to derive insights
        insights = self._generate_insights(analysis)
        analysis["insights"] = insights

        # Store learned patterns in knowledge base
        self.knowledge_base["opportunity_patterns"] = analysis
        self.knowledge_base["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"Learning complete: {len(successful)} successes, {len(failed)} failures")

        return analysis

    def _extract_patterns(self, opportunities: List[Opportunity], outcome: str) -> Dict[str, Any]:
        """Extract patterns from a set of opportunities."""
        if not opportunities:
            return {}

        # Calculate averages and patterns
        avg_revenue = sum(o.actual_revenue for o in opportunities) / len(opportunities)
        avg_cost = sum(o.actual_cost for o in opportunities) / len(opportunities)
        avg_profit = sum(o.actual_profit for o in opportunities) / len(opportunities)
        avg_risk = sum(o.risk_score for o in opportunities) / len(opportunities)
        avg_confidence = sum(o.confidence_score for o in opportunities) / len(opportunities)

        # Category distribution
        categories = {}
        for opp in opportunities:
            cat = opp.category or "unknown"
            categories[cat] = categories.get(cat, 0) + 1

        # Most common category
        most_common_category = max(categories.items(), key=lambda x: x[1])[0] if categories else None

        return {
            "count": len(opportunities),
            "avg_revenue": avg_revenue,
            "avg_cost": avg_cost,
            "avg_profit": avg_profit,
            "avg_risk_score": avg_risk,
            "avg_confidence": avg_confidence,
            "category_distribution": categories,
            "most_common_category": most_common_category
        }

    def _generate_insights(self, analysis: Dict[str, Any]) -> str:
        """Use LLM to generate insights from analysis."""
        prompt = f"""
Analyze the following business performance data and provide actionable insights:

{json.dumps(analysis, indent=2)}

Based on this data, provide:
1. Key patterns that lead to success
2. Common factors in failures
3. Recommendations for future opportunity selection
4. Risk management strategies
5. Suggested improvements to decision-making

Be specific and actionable. Focus on what works and what doesn't.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "")

    def learn_from_agent_performance(self) -> Dict[str, Any]:
        """Learn which types of agents perform best."""
        logger.info("Learning from agent performance...")

        agents = self.db_session.query(Agent).all()

        if not agents:
            return {"message": "No agents to learn from"}

        # Analyze by agent type
        performance_by_type = {}

        for agent in agents:
            agent_type = agent.agent_type

            if agent_type not in performance_by_type:
                performance_by_type[agent_type] = {
                    "count": 0,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "avg_success_rate": 0
                }

            stats = performance_by_type[agent_type]
            stats["count"] += 1

            # Get tasks for this agent
            tasks = self.db_session.query(Task).filter(Task.agent_id == agent.id).all()
            total_tasks = len(tasks)
            completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

            stats["total_tasks"] += total_tasks
            stats["completed_tasks"] += completed
            stats["failed_tasks"] += failed

        # Calculate success rates
        for agent_type, stats in performance_by_type.items():
            if stats["total_tasks"] > 0:
                stats["avg_success_rate"] = stats["completed_tasks"] / stats["total_tasks"]

        # Rank agent types
        ranked_types = sorted(
            performance_by_type.items(),
            key=lambda x: x[1]["avg_success_rate"],
            reverse=True
        )

        learning = {
            "agent_performance": performance_by_type,
            "best_agent_types": [t[0] for t in ranked_types[:3]],
            "worst_agent_types": [t[0] for t in ranked_types[-3:]],
            "recommendations": self._generate_agent_recommendations(performance_by_type)
        }

        self.knowledge_base["agent_performance"] = learning
        logger.info("Agent performance learning complete")

        return learning

    def _generate_agent_recommendations(self, performance: Dict[str, Any]) -> str:
        """Generate recommendations based on agent performance."""
        prompt = f"""
Analyze agent performance data and provide recommendations:

{json.dumps(performance, indent=2)}

Provide:
1. Which agent types should be used more
2. Which agent types should be avoided
3. How to improve underperforming agent types
4. Optimal agent allocation strategies

Be specific and actionable.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "")

    def learn_from_task_execution(self) -> Dict[str, Any]:
        """Learn from task execution patterns."""
        logger.info("Learning from task execution...")

        tasks = self.db_session.query(Task).all()

        if not tasks:
            return {"message": "No tasks to learn from"}

        # Analyze task patterns
        total_tasks = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

        # Analyze completion times for completed tasks
        completion_times = []
        for task in tasks:
            if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                completion_times.append(duration)

        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0

        learning = {
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_tasks if total_tasks > 0 else 0,
            "avg_completion_time_seconds": avg_completion_time,
            "insights": self._generate_task_insights(tasks)
        }

        self.knowledge_base["task_execution"] = learning
        logger.info("Task execution learning complete")

        return learning

    def _generate_task_insights(self, tasks: List[Task]) -> str:
        """Generate insights from task execution data."""
        # Sample some failed tasks for analysis
        failed_tasks = [t for t in tasks if t.status == TaskStatus.FAILED][:5]

        failed_examples = [
            {
                "title": t.title,
                "error": t.error_message
            }
            for t in failed_tasks
        ]

        prompt = f"""
Analyze task execution patterns and failures:

Total tasks: {len(tasks)}
Failed tasks: {len(failed_tasks)}
Failed task examples:
{json.dumps(failed_examples, indent=2)}

Provide:
1. Common reasons for task failures
2. How to improve task success rates
3. Task assignment strategies
4. Process improvements

Be specific and actionable.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "")

    def get_learning_recommendations(self) -> Dict[str, Any]:
        """Get overall recommendations based on all learning."""
        if not self.knowledge_base:
            self.analyze_past_opportunities()
            self.learn_from_agent_performance()
            self.learn_from_task_execution()

        prompt = f"""
Based on comprehensive learning data, provide strategic recommendations:

{json.dumps(self.knowledge_base, indent=2)}

Provide a comprehensive strategy document covering:
1. Opportunity selection strategy (what to pursue, what to avoid)
2. Agent management strategy (which agents to use, how many)
3. Risk management approach
4. Capital allocation strategy
5. Process improvements
6. Success metrics to track

Make it actionable and specific.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)

        return {
            "recommendations": response.get("response", ""),
            "knowledge_base": self.knowledge_base,
            "generated_at": datetime.utcnow().isoformat()
        }

    def should_pursue_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use learned patterns to decide if an opportunity should be pursued.

        Args:
            opportunity_data: Opportunity details

        Returns:
            Decision with reasoning
        """
        if "opportunity_patterns" not in self.knowledge_base:
            self.analyze_past_opportunities()

        patterns = self.knowledge_base.get("opportunity_patterns", {})

        prompt = f"""
Based on learned patterns from past opportunities, evaluate this new opportunity:

New Opportunity:
{json.dumps(opportunity_data, indent=2)}

Learned Patterns:
{json.dumps(patterns, indent=2)}

Provide:
1. Should we pursue this opportunity? (YES/NO)
2. Confidence level (0-1)
3. Key reasons for the decision
4. Recommended adjustments
5. Expected success probability

Respond in JSON format with keys: decision, confidence, reasons, adjustments, success_probability
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)

        try:
            decision = json.loads(response.get("response", "{}"))
        except json.JSONDecodeError:
            decision = {
                "decision": "UNCERTAIN",
                "confidence": 0.5,
                "reasons": response.get("response", "")
            }

        return decision

    def export_knowledge_base(self, file_path: str):
        """Export learned knowledge to file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, indent=2)

        logger.info(f"Exported knowledge base to {file_path}")

    def import_knowledge_base(self, file_path: str):
        """Import previously learned knowledge."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)

            logger.info(f"Imported knowledge base from {file_path}")
        except Exception as e:
            logger.error(f"Error importing knowledge base: {e}")
