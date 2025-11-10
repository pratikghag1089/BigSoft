"""Master Entrepreneur Agent - The main decision-making agent."""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from ..database.models import (
    AgentStatus, Task, TaskStatus, Opportunity,
    OpportunityStatus, Metric, SystemState
)
from ..core.config import settings

logger = logging.getLogger(__name__)


class MasterEntrepreneurAgent(BaseAgent):
    """
    The Master Entrepreneur Agent is the top-level decision maker.
    It identifies opportunities, creates specialized agents, and manages the business.
    """

    def __init__(self, db_session: Session):
        super().__init__(
            name="MasterEntrepreneur",
            agent_type="master",
            role="Entrepreneur and Business Strategist",
            capabilities=[
                "identify business opportunities",
                "evaluate market potential",
                "make strategic decisions",
                "create and manage specialized agents",
                "allocate resources",
                "track profitability"
            ],
            db_session=db_session
        )

        self.capital = settings.initial_capital
        self.risk_tolerance = settings.risk_tolerance
        self.min_profit_margin = settings.min_profit_margin

        # Load or initialize system state
        self._load_system_state()

    def _load_system_state(self):
        """Load system state from database."""
        if not self.db_session:
            return

        state = self.db_session.query(SystemState).filter_by(key="capital").first()
        if state:
            self.capital = state.value.get("amount", self.capital)
        else:
            # Initialize state
            state = SystemState(
                key="capital",
                value={"amount": self.capital, "currency": "USD"},
                extra_data={"initialized_at": datetime.utcnow().isoformat()}
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
        Main execution loop for the Master Entrepreneur Agent.

        Returns:
            Execution summary
        """
        logger.info("Master Entrepreneur Agent starting...")
        self.update_status(AgentStatus.RUNNING)
        self.save_to_db()

        try:
            # Main business cycle
            cycle_count = 0
            max_cycles = 100  # Prevent infinite loops in initial version

            while cycle_count < max_cycles and self.status == AgentStatus.RUNNING:
                cycle_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"Business Cycle {cycle_count}")
                logger.info(f"Current Capital: ${self.capital:.2f}")
                logger.info(f"{'='*60}\n")

                # Step 1: Analyze current state
                state_analysis = self._analyze_current_state()

                # Step 2: Scan for opportunities
                opportunities = self._scan_opportunities()

                # Step 3: Evaluate and select best opportunity
                if opportunities:
                    selected_opportunity = self._select_best_opportunity(opportunities)

                    if selected_opportunity:
                        # Step 4: Execute opportunity
                        result = self._execute_opportunity(selected_opportunity)

                        # Step 5: Update financial state
                        self._update_financials(result)

                # Step 6: Review performance
                performance = self._review_performance()

                # Step 7: Decide whether to continue
                if not self._should_continue(performance):
                    break

                # Record metrics
                self._record_metrics(cycle_count, performance)

            # Finalize
            self.update_status(AgentStatus.COMPLETED)
            final_report = self._generate_final_report()

            return {
                "success": True,
                "cycles_completed": cycle_count,
                "final_capital": self.capital,
                "profit": self.capital - settings.initial_capital,
                "report": final_report
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

As an entrepreneur, provide a detailed plan and execution strategy for this task.
Consider:
1. Resources needed
2. Potential challenges
3. Success metrics
4. Step-by-step action plan

Respond in JSON format with keys: plan, resources, challenges, metrics, actions
"""

        response = self.think(prompt)

        try:
            # Try to parse JSON response
            result = json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, return as plain text
            result = {"output": response, "raw": True}

        return result

    def _analyze_current_state(self) -> Dict[str, Any]:
        """Analyze the current business state."""
        logger.info("Analyzing current business state...")

        # Get metrics from database
        active_agents = 0
        active_opportunities = 0
        completed_opportunities = 0

        if self.db_session:
            from ..database.models import Agent, Opportunity

            active_agents = self.db_session.query(Agent).filter(
                Agent.status == AgentStatus.RUNNING
            ).count()

            active_opportunities = self.db_session.query(Opportunity).filter(
                Opportunity.status.in_([OpportunityStatus.IN_PROGRESS, OpportunityStatus.EVALUATING])
            ).count()

            completed_opportunities = self.db_session.query(Opportunity).filter(
                Opportunity.status == OpportunityStatus.COMPLETED
            ).count()

        analysis = {
            "capital": self.capital,
            "active_agents": active_agents,
            "active_opportunities": active_opportunities,
            "completed_opportunities": completed_opportunities,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"State Analysis: {json.dumps(analysis, indent=2)}")
        return analysis

    def _scan_opportunities(self) -> List[Dict[str, Any]]:
        """Scan for business opportunities using AI."""
        logger.info("Scanning for business opportunities...")

        prompt = f"""
You are an AI entrepreneur with ${self.capital:.2f} in capital.
Your goal is to identify profitable business opportunities that can be automated or executed by AI agents.

Generate 3-5 potential business opportunities. For each opportunity, provide:
1. Title: A concise name
2. Description: What the opportunity is
3. Potential Revenue: Estimated revenue (realistic, conservative estimate)
4. Estimated Cost: What it would cost to execute
5. Risk Score: 0-1 (0=low risk, 1=high risk)
6. Confidence: 0-1 (how confident you are this will work)
7. Category: Type of business (e.g., "service", "product", "content", "data")
8. Strategy: High-level approach
9. Action Plan: 3-5 concrete steps

Focus on opportunities that:
- Can be executed with AI and automation
- Have low initial costs
- Can generate revenue quickly
- Are ethical and legal
- Match your available capital

Respond ONLY with a valid JSON array of opportunities.
"""

        response = self.think(prompt)

        try:
            # Extract JSON from response
            opportunities = json.loads(response)

            if not isinstance(opportunities, list):
                opportunities = [opportunities]

            logger.info(f"Identified {len(opportunities)} opportunities")
            return opportunities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse opportunities: {e}")
            return []

    def _select_best_opportunity(self, opportunities: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best opportunity based on criteria."""
        logger.info("Evaluating and selecting best opportunity...")

        if not opportunities:
            return None

        # Score each opportunity
        scored_opportunities = []

        for opp in opportunities:
            try:
                revenue = float(opp.get("potential_revenue", 0))
                cost = float(opp.get("estimated_cost", 0))
                risk = float(opp.get("risk_score", 0.5))
                confidence = float(opp.get("confidence", 0.5))

                # Check if we can afford it
                if cost > self.capital:
                    continue

                # Calculate profit margin
                profit_margin = (revenue - cost) / revenue if revenue > 0 else 0

                # Skip if below minimum profit margin
                if profit_margin < self.min_profit_margin:
                    continue

                # Calculate score
                # Higher revenue, lower cost, lower risk, higher confidence = better
                score = (
                    (revenue / 1000) * 0.3 +  # Revenue factor
                    (1 - cost / self.capital) * 0.2 +  # Capital efficiency
                    (1 - risk) * 0.2 +  # Risk-adjusted
                    confidence * 0.3  # Confidence factor
                )

                # Adjust for risk tolerance
                score = score * (1 - (risk * (1 - self.risk_tolerance)))

                scored_opportunities.append((score, opp))

            except (ValueError, TypeError) as e:
                logger.warning(f"Error scoring opportunity: {e}")
                continue

        if not scored_opportunities:
            logger.warning("No suitable opportunities found")
            return None

        # Select best opportunity
        scored_opportunities.sort(reverse=True, key=lambda x: x[0])
        best_score, best_opp = scored_opportunities[0]

        logger.info(f"Selected opportunity: {best_opp.get('title')} (score: {best_score:.3f})")
        return best_opp

    def _execute_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a business opportunity."""
        logger.info(f"Executing opportunity: {opportunity.get('title')}")

        # Save opportunity to database
        if self.db_session:
            opp_model = Opportunity(
                title=opportunity.get("title", "Untitled"),
                description=opportunity.get("description", ""),
                status=OpportunityStatus.IN_PROGRESS,
                potential_revenue=float(opportunity.get("potential_revenue", 0)),
                estimated_cost=float(opportunity.get("estimated_cost", 0)),
                risk_score=float(opportunity.get("risk_score", 0.5)),
                confidence_score=float(opportunity.get("confidence", 0.5)),
                strategy=opportunity.get("strategy", ""),
                action_plan=opportunity.get("action_plan", []),
                category=opportunity.get("category", "general"),
                started_at=datetime.utcnow()
            )
            self.db_session.add(opp_model)
            self.db_session.commit()

            opportunity_id = opp_model.id
        else:
            opportunity_id = None

        # Simulate execution (in a real system, this would create agents and tasks)
        cost = float(opportunity.get("estimated_cost", 0))
        revenue = float(opportunity.get("potential_revenue", 0))
        confidence = float(opportunity.get("confidence", 0.5))
        risk = float(opportunity.get("risk_score", 0.5))

        # Simulate success/failure based on confidence and risk
        import random
        success_probability = confidence * (1 - risk * 0.5)
        success = random.random() < success_probability

        actual_revenue = revenue * confidence if success else revenue * 0.1
        actual_cost = cost

        # Update opportunity
        if self.db_session and opportunity_id:
            opp_model = self.db_session.query(Opportunity).filter_by(id=opportunity_id).first()
            if opp_model:
                opp_model.actual_revenue = actual_revenue
                opp_model.actual_cost = actual_cost
                opp_model.actual_profit = actual_revenue - actual_cost
                opp_model.status = OpportunityStatus.COMPLETED if success else OpportunityStatus.FAILED
                opp_model.completed_at = datetime.utcnow()
                self.db_session.commit()

        result = {
            "success": success,
            "revenue": actual_revenue,
            "cost": actual_cost,
            "profit": actual_revenue - actual_cost,
            "opportunity_id": opportunity_id
        }

        logger.info(f"Opportunity execution result: {json.dumps(result, indent=2)}")
        return result

    def _update_financials(self, result: Dict[str, Any]):
        """Update financial state based on execution result."""
        profit = result.get("profit", 0)
        self.capital += profit

        logger.info(f"Capital updated: ${self.capital:.2f} (change: ${profit:+.2f})")

        self._save_system_state()

        # Record metric
        if self.db_session:
            metric = Metric(
                metric_type="financial",
                metric_name="capital",
                value=self.capital,
                category="business"
            )
            self.db_session.add(metric)

            profit_metric = Metric(
                metric_type="financial",
                metric_name="profit",
                value=profit,
                category="business"
            )
            self.db_session.add(profit_metric)

            self.db_session.commit()

    def _review_performance(self) -> Dict[str, Any]:
        """Review overall performance."""
        initial_capital = settings.initial_capital
        current_capital = self.capital
        profit = current_capital - initial_capital
        roi = (profit / initial_capital * 100) if initial_capital > 0 else 0

        performance = {
            "initial_capital": initial_capital,
            "current_capital": current_capital,
            "total_profit": profit,
            "roi_percent": roi,
            "is_profitable": profit > 0
        }

        logger.info(f"Performance Review: ROI = {roi:.2f}%, Profit = ${profit:.2f}")
        return performance

    def _should_continue(self, performance: Dict[str, Any]) -> bool:
        """Decide whether to continue running."""
        # Stop if bankrupt
        if self.capital <= 0:
            logger.warning("Bankrupt! Stopping operations.")
            return False

        # Stop if very profitable (achieved goal)
        roi = performance.get("roi_percent", 0)
        if roi > 100:  # Doubled money
            logger.info("Achieved significant profitability! Mission accomplished.")
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
            extra_data={
                "cycle": cycle,
                **performance
            }
        )
        self.db_session.add(metric)
        self.db_session.commit()

    def _generate_final_report(self) -> str:
        """Generate a final report of business performance."""
        prompt = f"""
Generate a comprehensive business report based on the following data:

Initial Capital: ${settings.initial_capital:.2f}
Final Capital: ${self.capital:.2f}
Total Profit/Loss: ${self.capital - settings.initial_capital:+.2f}
ROI: {((self.capital - settings.initial_capital) / settings.initial_capital * 100):.2f}%

Provide:
1. Executive Summary
2. Key Achievements
3. Challenges Faced
4. Financial Performance
5. Lessons Learned
6. Recommendations for Future

Keep it concise but insightful.
"""

        report = self.think(prompt)
        return report
