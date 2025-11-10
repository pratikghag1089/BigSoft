"""Enhanced Master Entrepreneur Agent V2 - With self-learning, self-fixing, and self-improvement."""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from .agent_factory import AgentFactory
from .agent_evaluator import AgentEvaluator
from ..database.models import (
    AgentStatus, Task, TaskStatus, Opportunity,
    OpportunityStatus, Metric, SystemState
)
from ..business.workspace_manager import WorkspaceManager
from ..business.kanban_board import KanbanBoard
from ..business.business_executor import BusinessExecutor
from ..business.opportunity_engine import OpportunityEngine
from ..business.task_manager import TaskManager
from ..intelligence.self_learning import SelfLearningEngine
from ..intelligence.self_fixing import SelfFixingEngine
from ..intelligence.self_improvement import SelfImprovementEngine
from ..core.config import settings

logger = logging.getLogger(__name__)


class MasterEntrepreneurAgentV2(BaseAgent):
    """
    Enhanced Master Entrepreneur Agent with:
    - Self-learning from past performance
    - Self-fixing when errors occur
    - Self-improvement through optimization
    - Real business execution
    - Dynamic agent management
    - Project management with Kanban
    - Workspace management for each venture
    """

    def __init__(self, db_session: Session):
        super().__init__(
            name="MasterEntrepreneurV2",
            agent_type="master",
            role="Self-Improving AI Entrepreneur",
            capabilities=[
                "identify business opportunities",
                "evaluate market potential",
                "make strategic decisions",
                "create and manage specialized agents",
                "allocate resources",
                "track profitability",
                "learn from experience",
                "fix errors automatically",
                "improve strategies continuously",
                "execute real business operations"
            ],
            db_session=db_session
        )

        self.capital = settings.initial_capital
        self.risk_tolerance = settings.risk_tolerance
        self.min_profit_margin = settings.min_profit_margin

        # Initialize all subsystems
        self.agent_factory = AgentFactory(db_session)
        self.agent_evaluator = AgentEvaluator(db_session, self.agent_factory)
        self.workspace_manager = WorkspaceManager()
        self.business_executor = BusinessExecutor(db_session)
        self.opportunity_engine = OpportunityEngine(db_session)
        self.task_manager = TaskManager(db_session, self.agent_factory)

        # Intelligence subsystems
        self.learning_engine = SelfLearningEngine(db_session)
        self.fixing_engine = SelfFixingEngine(db_session)
        self.improvement_engine = SelfImprovementEngine(db_session)

        # Load system state
        self._load_system_state()

        logger.info("Master Entrepreneur Agent V2 initialized with enhanced capabilities")

    def _load_system_state(self):
        """Load system state from database."""
        if not self.db_session:
            return

        state = self.db_session.query(SystemState).filter_by(key="capital").first()
        if state:
            self.capital = state.value.get("amount", self.capital)
        else:
            state = SystemState(
                key="capital",
                value={"amount": self.capital, "currency": "USD"},
                metadata={"initialized_at": datetime.utcnow().isoformat()}
            )
            self.db_session.add(state)
            self.db_session.commit()

    def _save_system_state(self):
        """Save system state to database."""
        if not self.db_session:
            return

        state = self.db_session.query(SystemState).filter_by(key="capital").first()
        if state:
            state.value = {"amount": self.capital, "currency": "USD"}
            state.updated_at = datetime.utcnow()
            self.db_session.commit()

    def run(self) -> Dict[str, Any]:
        """
        Main execution loop with self-learning, self-fixing, and self-improvement.

        Returns:
            Execution summary
        """
        logger.info("="*80)
        logger.info("ENHANCED MASTER ENTREPRENEUR AGENT V2 STARTING")
        logger.info("="*80)

        self.update_status(AgentStatus.RUNNING)
        self.save_to_db()

        try:
            # Initial learning phase
            logger.info("\n🧠 LEARNING PHASE: Analyzing past performance...")
            self.learning_engine.analyze_past_opportunities()
            self.learning_engine.learn_from_agent_performance()

            cycle_count = 0
            max_cycles = 100

            while cycle_count < max_cycles and self.status == AgentStatus.RUNNING:
                cycle_count += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"BUSINESS CYCLE {cycle_count}")
                logger.info(f"Current Capital: ${self.capital:.2f}")
                logger.info(f"{'='*80}\n")

                # Step 1: Self-improvement (every 5 cycles)
                if cycle_count % 5 == 0:
                    logger.info("🔧 SELF-IMPROVEMENT: Running optimization cycle...")
                    improvement_result = self.improvement_engine.continuous_improvement_cycle()
                    logger.info(f"Optimizations applied: {len(improvement_result.get('steps', []))}")

                # Step 2: Agent evaluation and cleanup (every 3 cycles)
                if cycle_count % 3 == 0:
                    logger.info("🤖 AGENT MANAGEMENT: Evaluating agent performance...")
                    eval_result = self.agent_evaluator.evaluate_all_agents()
                    logger.info(f"Agents evaluated: {eval_result['evaluated']}, terminated: {eval_result['terminated']}")

                # Step 3: Self-fixing - check for failed tasks
                failed_tasks = self.db_session.query(Task).filter(
                    Task.status == TaskStatus.FAILED
                ).limit(5).all()

                if failed_tasks:
                    logger.info(f"🔨 SELF-FIXING: Attempting to fix {len(failed_tasks)} failed tasks...")
                    for task in failed_tasks:
                        fix_result = self.fixing_engine.detect_and_fix_task_error(task.id)
                        if fix_result.get("success"):
                            logger.info(f"  ✓ Fixed task {task.id}: {fix_result.get('action')}")

                # Step 4: Analyze current state
                state_analysis = self._analyze_current_state()

                # Step 5: Identify opportunities (use learning to guide)
                opportunities = self.opportunity_engine.identify_opportunities(
                    context=state_analysis,
                    count=5
                )

                # Step 6: Use learning engine to evaluate opportunities
                if opportunities:
                    logger.info(f"📊 Evaluating {len(opportunities)} opportunities with learned patterns...")

                    scored_opportunities = []
                    for opp in opportunities:
                        # Get AI decision based on learned patterns
                        decision = self.learning_engine.should_pursue_opportunity({
                            "title": opp.title,
                            "category": opp.category,
                            "potential_revenue": opp.potential_revenue,
                            "estimated_cost": opp.estimated_cost,
                            "risk_score": opp.risk_score
                        })

                        if decision.get("decision") == "YES":
                            score = decision.get("confidence", 0.5)
                            scored_opportunities.append((score, opp))
                            logger.info(f"  ✓ {opp.title}: {score:.1%} confidence")
                        else:
                            logger.info(f"  ✗ {opp.title}: Rejected - {decision.get('reasons', 'Low confidence')}")

                    # Select best opportunity
                    if scored_opportunities:
                        scored_opportunities.sort(reverse=True, key=lambda x: x[0])
                        _, best_opportunity = scored_opportunities[0]

                        # Check if we can afford it
                        if best_opportunity.estimated_cost <= self.capital:
                            logger.info(f"\n💼 EXECUTING: {best_opportunity.title}")

                            # Execute with real business operations
                            result = self.business_executor.execute_opportunity(best_opportunity)

                            # Update financials (in real version, this would be actual revenue)
                            # For now, simulate based on execution success
                            if result.get("success"):
                                # Calculate actual profit (simulated based on confidence)
                                confidence = scored_opportunities[0][0]
                                actual_revenue = best_opportunity.potential_revenue * confidence
                                actual_cost = best_opportunity.estimated_cost
                                actual_profit = actual_revenue - actual_cost

                                best_opportunity.actual_revenue = actual_revenue
                                best_opportunity.actual_cost = actual_cost
                                best_opportunity.actual_profit = actual_profit
                                best_opportunity.status = OpportunityStatus.COMPLETED
                                best_opportunity.completed_at = datetime.utcnow()

                                self.capital += actual_profit
                                self._save_system_state()

                                logger.info(f"✅ SUCCESS: Revenue: ${actual_revenue:.2f}, Cost: ${actual_cost:.2f}, Profit: ${actual_profit:+.2f}")
                                logger.info(f"💰 New Capital: ${self.capital:.2f}")
                            else:
                                best_opportunity.status = OpportunityStatus.FAILED
                                best_opportunity.completed_at = datetime.utcnow()
                                logger.warning(f"❌ FAILED: {result.get('error', 'Unknown error')}")

                            self.db_session.commit()

                # Step 7: Review performance
                performance = self._review_performance()

                # Step 8: Decide whether to continue
                if not self._should_continue(performance):
                    break

                # Record metrics
                self._record_metrics(cycle_count, performance)

            # Final learning and reporting
            logger.info("\n🎓 FINAL LEARNING: Generating comprehensive insights...")
            final_recommendations = self.learning_engine.get_learning_recommendations()

            # Generate final report
            self.update_status(AgentStatus.COMPLETED)
            final_report = self._generate_enhanced_final_report(final_recommendations)

            return {
                "success": True,
                "cycles_completed": cycle_count,
                "final_capital": self.capital,
                "profit": self.capital - settings.initial_capital,
                "roi_percent": ((self.capital - settings.initial_capital) / settings.initial_capital * 100),
                "report": final_report,
                "workspaces_created": len(self.workspace_manager.list_all_workspaces()),
                "learning_insights": final_recommendations
            }

        except Exception as e:
            logger.error(f"Master agent execution failed: {e}", exc_info=True)
            self.update_status(AgentStatus.FAILED)
            return {
                "success": False,
                "error": str(e)
            }

    def _execute_task_impl(self, task: Task) -> Dict[str, Any]:
        """Execute a specific task."""
        prompt = f"""
Task: {task.title}
Description: {task.description}

As a self-improving AI entrepreneur, provide a detailed execution plan.
Consider past learnings and optimize for success.

Respond in JSON format with keys: plan, actions, expected_outcome, risk_mitigation
"""

        response = self.think(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError:
            result = {"output": response, "raw": True}

        return result

    def _analyze_current_state(self) -> Dict[str, Any]:
        """Analyze current business state with enhanced metrics."""
        logger.info("📈 Analyzing current state...")

        active_agents = self.agent_factory.get_agent_count(AgentStatus.RUNNING)
        total_agents = self.agent_factory.get_agent_count()

        active_opportunities = self.db_session.query(Opportunity).filter(
            Opportunity.status.in_([OpportunityStatus.IN_PROGRESS, OpportunityStatus.EVALUATING])
        ).count()

        completed_opportunities = self.db_session.query(Opportunity).filter(
            Opportunity.status == OpportunityStatus.COMPLETED
        ).count()

        # Get workspace count
        workspaces = self.workspace_manager.list_all_workspaces()

        analysis = {
            "capital": self.capital,
            "active_agents": active_agents,
            "total_agents": total_agents,
            "active_opportunities": active_opportunities,
            "completed_opportunities": completed_opportunities,
            "active_workspaces": len(workspaces),
            "timestamp": datetime.utcnow().isoformat()
        }

        return analysis

    def _review_performance(self) -> Dict[str, Any]:
        """Review overall performance."""
        initial_capital = settings.initial_capital
        current_capital = self.capital
        profit = current_capital - initial_capital
        roi = (profit / initial_capital * 100) if initial_capital > 0 else 0

        # Get agent stats
        agent_stats = self.agent_evaluator.get_system_agent_stats()

        # Get task stats
        task_stats = self.task_manager.get_task_stats()

        performance = {
            "initial_capital": initial_capital,
            "current_capital": current_capital,
            "total_profit": profit,
            "roi_percent": roi,
            "is_profitable": profit > 0,
            "agent_stats": agent_stats,
            "task_stats": task_stats
        }

        return performance

    def _should_continue(self, performance: Dict[str, Any]) -> bool:
        """Decide whether to continue with enhanced logic."""
        if self.capital <= 0:
            logger.warning("🚫 Bankrupt! Stopping operations.")
            return False

        roi = performance.get("roi_percent", 0)
        if roi > 100:
            logger.info("🎉 Mission accomplished! Doubled capital!")
            return False

        return True

    def _record_metrics(self, cycle: int, performance: Dict[str, Any]):
        """Record performance metrics."""
        if not self.db_session:
            return

        metric = Metric(
            metric_type="performance",
            metric_name="cycle_performance",
            value=performance.get("roi_percent", 0),
            category="business_cycle",
            metadata={
                "cycle": cycle,
                **performance
            }
        )
        self.db_session.add(metric)
        self.db_session.commit()

    def _generate_enhanced_final_report(self, recommendations: Dict[str, Any]) -> str:
        """Generate enhanced final report."""
        prompt = f"""
Generate a comprehensive final business report:

Initial Capital: ${settings.initial_capital:.2f}
Final Capital: ${self.capital:.2f}
Total Profit/Loss: ${self.capital - settings.initial_capital:+.2f}
ROI: {((self.capital - settings.initial_capital) / settings.initial_capital * 100):.2f}%

Learned Insights:
{json.dumps(recommendations, indent=2)}

Provide a detailed report with:
1. Executive Summary
2. Financial Performance Analysis
3. Key Achievements
4. Lessons Learned (data-driven insights)
5. What Worked Well
6. What Didn't Work
7. Strategic Recommendations (based on learning)
8. Future Opportunities
9. System Improvements Made
10. Conclusion

Make it comprehensive, data-driven, and actionable.
"""

        report = self.think(prompt)
        return report
