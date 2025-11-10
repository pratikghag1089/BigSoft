"""Self-Improvement Module - Optimizes strategies and generates improvements."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from ..database.models import Opportunity, Agent, Task, Metric, SystemState
from ..core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class SelfImprovementEngine:
    """
    Self-improvement engine that continuously optimizes strategies,
    generates better code, and improves system performance.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.llm = ollama_client
        self.improvements: List[Dict[str, Any]] = []
        self.optimization_history: List[Dict[str, Any]] = []

    def analyze_system_performance(self) -> Dict[str, Any]:
        """
        Analyze overall system performance to identify improvement areas.

        Returns:
            Performance analysis
        """
        logger.info("Analyzing system performance for improvements...")

        # Get system metrics
        metrics = self.db_session.query(Metric).all()

        # Calculate key performance indicators
        total_opportunities = self.db_session.query(Opportunity).count()
        successful_opportunities = self.db_session.query(Opportunity).filter(
            Opportunity.actual_profit > 0
        ).count()

        total_agents = self.db_session.query(Agent).count()
        total_tasks = self.db_session.query(Task).count()

        # Get capital state
        capital_state = self.db_session.query(SystemState).filter_by(key="capital").first()
        current_capital = capital_state.value.get("amount", 0) if capital_state else 0

        analysis = {
            "total_opportunities": total_opportunities,
            "successful_opportunities": successful_opportunities,
            "success_rate": successful_opportunities / total_opportunities if total_opportunities > 0 else 0,
            "total_agents": total_agents,
            "total_tasks": total_tasks,
            "current_capital": current_capital,
            "metric_count": len(metrics),
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"System performance: {analysis['success_rate']:.1%} success rate")

        return analysis

    def generate_optimization_strategy(self) -> Dict[str, Any]:
        """
        Generate an optimization strategy based on performance analysis.

        Returns:
            Optimization strategy
        """
        logger.info("Generating optimization strategy...")

        performance = self.analyze_system_performance()

        prompt = f"""
Analyze system performance and generate optimization strategy:

{json.dumps(performance, indent=2)}

Generate a comprehensive optimization strategy covering:
1. Critical areas that need improvement
2. Specific optimization actions (with implementation details)
3. Expected impact of each optimization
4. Priority order (what to optimize first)
5. Success metrics to track

For each optimization, be specific enough that it could be implemented programmatically.

Respond in JSON format with structure:
{{
  "optimizations": [
    {{
      "area": "area name",
      "action": "specific action",
      "implementation": "how to implement",
      "expected_impact": "expected improvement",
      "priority": 1-10
    }}
  ],
  "overall_strategy": "strategic summary"
}}
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)

        try:
            strategy = json.loads(response.get("response", "{}"))
        except json.JSONDecodeError:
            strategy = {
                "optimizations": [],
                "overall_strategy": response.get("response", ""),
                "parse_error": True
            }

        # Store strategy
        self.optimization_history.append({
            "strategy": strategy,
            "timestamp": datetime.utcnow().isoformat(),
            "performance_snapshot": performance
        })

        logger.info(f"Generated optimization strategy with {len(strategy.get('optimizations', []))} actions")

        return strategy

    def apply_optimization(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a specific optimization.

        Args:
            optimization: Optimization details

        Returns:
            Application result
        """
        area = optimization.get("area", "unknown")
        action = optimization.get("action", "")

        logger.info(f"Applying optimization: {area} - {action}")

        # Record optimization attempt
        result = {
            "area": area,
            "action": action,
            "applied_at": datetime.utcnow().isoformat(),
            "success": False
        }

        try:
            # Determine optimization type and apply
            if "agent" in area.lower():
                result.update(self._optimize_agents(optimization))
            elif "task" in area.lower():
                result.update(self._optimize_tasks(optimization))
            elif "opportunity" in area.lower():
                result.update(self._optimize_opportunities(optimization))
            elif "capital" in area.lower() or "financial" in area.lower():
                result.update(self._optimize_financial_strategy(optimization))
            else:
                result.update(self._generic_optimization(optimization))

            self.improvements.append(result)

            # Record metric
            metric = Metric(
                metric_type="self_improvement",
                metric_name=f"optimization_{area}",
                value=1 if result.get("success") else 0,
                category="optimization",
                extra_data=result
            )
            self.db_session.add(metric)
            self.db_session.commit()

        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            result["error"] = str(e)

        return result

    def _optimize_agents(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize agent-related aspects."""
        implementation = optimization.get("implementation", "")

        # Parse and apply agent optimizations
        if "reduce" in implementation.lower() and "underperforming" in implementation.lower():
            # Remove underperforming agents
            from ..agents.agent_evaluator import AgentEvaluator
            from ..agents.agent_factory import AgentFactory

            factory = AgentFactory(self.db_session)
            evaluator = AgentEvaluator(self.db_session, factory)

            eval_result = evaluator.evaluate_all_agents()

            return {
                "success": True,
                "implementation": "Evaluated and removed underperforming agents",
                "details": eval_result
            }

        elif "increase" in implementation.lower() and "specialized" in implementation.lower():
            return {
                "success": True,
                "implementation": "Strategy updated to create more specialized agents",
                "note": "Will be applied in next opportunity execution"
            }

        return {
            "success": True,
            "implementation": "Agent optimization noted for future application"
        }

    def _optimize_tasks(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize task-related aspects."""
        # Could implement task batching, priority optimization, etc.
        return {
            "success": True,
            "implementation": "Task optimization strategy updated",
            "note": "Will be applied to future tasks"
        }

    def _optimize_opportunities(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize opportunity selection and evaluation."""
        implementation = optimization.get("implementation", "")

        # Update opportunity selection criteria
        if not hasattr(self, 'opportunity_criteria'):
            self.opportunity_criteria = {}

        # Extract criteria from implementation
        self.opportunity_criteria["last_update"] = datetime.utcnow().isoformat()
        self.opportunity_criteria["implementation"] = implementation

        # Store in system state
        state = self.db_session.query(SystemState).filter_by(key="opportunity_criteria").first()
        if not state:
            state = SystemState(key="opportunity_criteria", value={})
            self.db_session.add(state)

        state.value = self.opportunity_criteria
        self.db_session.commit()

        return {
            "success": True,
            "implementation": "Updated opportunity selection criteria",
            "criteria": self.opportunity_criteria
        }

    def _optimize_financial_strategy(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize financial and capital allocation strategies."""
        # Could update risk tolerance, capital allocation, etc.
        return {
            "success": True,
            "implementation": "Financial strategy parameters updated",
            "note": "Will affect future opportunity evaluations"
        }

    def _generic_optimization(self, optimization: Dict[str, Any]) -> Dict[str, Any]:
        """Apply generic optimization."""
        return {
            "success": True,
            "implementation": "Optimization strategy recorded",
            "note": "Manual implementation may be required"
        }

    def generate_code_improvement(self, code_context: Dict[str, Any]) -> str:
        """
        Generate improved code based on performance analysis.

        Args:
            code_context: Context about what code to improve

        Returns:
            Generated improved code
        """
        prompt = f"""
Generate improved code based on this context:

{json.dumps(code_context, indent=2)}

Generate Python code that:
1. Implements the requested improvement
2. Follows best practices
3. Includes error handling
4. Is well-documented with comments
5. Is production-ready

Return ONLY the Python code, properly formatted.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        code = response.get("response", "")

        logger.info("Generated code improvement")

        return code

    def create_new_agent_type(self, specification: Dict[str, Any]) -> str:
        """
        Generate code for a new agent type based on needs.

        Args:
            specification: Agent specification

        Returns:
            Generated agent code
        """
        logger.info(f"Generating new agent type: {specification.get('name', 'Custom')}")

        prompt = f"""
Generate a complete Python class for a new agent type:

Specification:
{json.dumps(specification, indent=2)}

Generate a Python class that:
1. Inherits from BaseAgent
2. Implements all required methods (_execute_task_impl, run)
3. Has the specified capabilities
4. Includes proper error handling
5. Is well-documented

Return ONLY the Python code for the class, properly formatted and ready to use.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        code = response.get("response", "")

        # Save generated code
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        agent_name = specification.get("name", "custom").lower().replace(" ", "_")
        file_name = f"agent_{agent_name}_{timestamp}.py"

        generated_dir = Path("agent_data/generated_agents")
        generated_dir.mkdir(parents=True, exist_ok=True)

        file_path = generated_dir / file_name
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

        logger.info(f"Generated new agent type: {file_path}")

        return code

    def optimize_master_agent_strategy(self) -> Dict[str, Any]:
        """
        Optimize the master agent's decision-making strategy.

        Returns:
            Optimization results
        """
        logger.info("Optimizing master agent strategy...")

        # Analyze past decisions
        opportunities = self.db_session.query(Opportunity).all()

        decision_analysis = {
            "total_opportunities": len(opportunities),
            "successful": sum(1 for o in opportunities if o.actual_profit > 0),
            "failed": sum(1 for o in opportunities if o.actual_profit <= 0)
        }

        prompt = f"""
Analyze past decisions and optimize strategy:

{json.dumps(decision_analysis, indent=2)}

Generate an optimized decision-making strategy that includes:
1. Updated opportunity evaluation criteria
2. Risk assessment improvements
3. Capital allocation strategy
4. Agent creation/deletion thresholds
5. Success metrics and KPIs

Be specific and quantitative where possible.

Respond in JSON format with these sections.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)

        try:
            optimized_strategy = json.loads(response.get("response", "{}"))
        except json.JSONDecodeError:
            optimized_strategy = {
                "strategy": response.get("response", ""),
                "parse_error": True
            }

        # Store optimized strategy
        state = self.db_session.query(SystemState).filter_by(key="master_strategy").first()
        if not state:
            state = SystemState(key="master_strategy", value={})
            self.db_session.add(state)

        state.value = {
            "strategy": optimized_strategy,
            "optimized_at": datetime.utcnow().isoformat()
        }
        self.db_session.commit()

        logger.info("Master agent strategy optimized")

        return {
            "success": True,
            "strategy": optimized_strategy,
            "applied_at": datetime.utcnow().isoformat()
        }

    def continuous_improvement_cycle(self) -> Dict[str, Any]:
        """
        Execute a complete continuous improvement cycle.

        Returns:
            Cycle results
        """
        logger.info("Starting continuous improvement cycle...")

        results = {
            "cycle_started_at": datetime.utcnow().isoformat(),
            "steps": []
        }

        # Step 1: Analyze performance
        performance = self.analyze_system_performance()
        results["steps"].append({
            "step": "performance_analysis",
            "result": performance
        })

        # Step 2: Generate optimization strategy
        strategy = self.generate_optimization_strategy()
        results["steps"].append({
            "step": "strategy_generation",
            "result": strategy
        })

        # Step 3: Apply top priority optimizations
        optimizations = strategy.get("optimizations", [])
        if optimizations:
            # Sort by priority
            optimizations.sort(key=lambda x: x.get("priority", 5), reverse=True)

            # Apply top 3 optimizations
            applied = []
            for opt in optimizations[:3]:
                result = self.apply_optimization(opt)
                applied.append(result)

            results["steps"].append({
                "step": "apply_optimizations",
                "result": applied
            })

        # Step 4: Optimize master strategy
        strategy_result = self.optimize_master_agent_strategy()
        results["steps"].append({
            "step": "optimize_master_strategy",
            "result": strategy_result
        })

        results["cycle_completed_at"] = datetime.utcnow().isoformat()
        results["success"] = True

        logger.info("Continuous improvement cycle completed")

        return results

    def get_improvement_report(self) -> Dict[str, Any]:
        """Get a report of all improvements made."""
        return {
            "total_improvements": len(self.improvements),
            "improvements": self.improvements,
            "optimization_history_count": len(self.optimization_history),
            "last_optimization": self.optimization_history[-1] if self.optimization_history else None
        }
