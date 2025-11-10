"""Business opportunity identification and evaluation engine."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.models import Opportunity, OpportunityStatus
from ..core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class OpportunityEngine:
    """
    Engine for identifying, evaluating, and managing business opportunities.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.llm = ollama_client

    def identify_opportunities(
        self,
        context: Optional[Dict[str, Any]] = None,
        count: int = 5
    ) -> List[Opportunity]:
        """
        Identify new business opportunities.

        Args:
            context: Optional context about current business state
            count: Number of opportunities to generate

        Returns:
            List of Opportunity objects
        """
        logger.info(f"Identifying {count} business opportunities...")

        prompt = f"""
You are an AI business opportunity analyst. Identify {count} profitable business opportunities
that can be automated using AI and software.

Context:
{self._format_context(context)}

For each opportunity, provide:
1. title: Short descriptive name
2. description: What the opportunity involves
3. category: Type (e.g., "service", "product", "content", "automation")
4. potential_revenue: Realistic monthly revenue estimate (number only)
5. estimated_cost: Initial and monthly costs (number only)
6. risk_score: 0-1 scale (0=very low risk, 1=very high risk)
7. confidence_score: 0-1 scale (0=uncertain, 1=very confident)
8. strategy: How to execute this opportunity
9. requirements: What's needed to succeed

Focus on:
- Digital/online opportunities
- Automation and AI-driven solutions
- Low initial investment
- Scalable business models
- Ethical and legal businesses

Respond with ONLY a valid JSON array. No other text.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.8)
        response_text = response.get("response", "")

        try:
            import json
            opportunities_data = json.loads(response_text)

            if not isinstance(opportunities_data, list):
                opportunities_data = [opportunities_data]

            opportunities = []
            for opp_data in opportunities_data:
                opportunity = Opportunity(
                    title=opp_data.get("title", "Untitled Opportunity"),
                    description=opp_data.get("description", ""),
                    category=opp_data.get("category", "general"),
                    potential_revenue=float(opp_data.get("potential_revenue", 0)),
                    estimated_cost=float(opp_data.get("estimated_cost", 0)),
                    risk_score=float(opp_data.get("risk_score", 0.5)),
                    confidence_score=float(opp_data.get("confidence_score", 0.5)),
                    strategy=opp_data.get("strategy", ""),
                    status=OpportunityStatus.IDENTIFIED,
                    metadata={
                        "requirements": opp_data.get("requirements", []),
                        "identified_by": "opportunity_engine"
                    }
                )

                # Calculate profit margin
                if opportunity.potential_revenue > 0:
                    opportunity.profit_margin = (
                        (opportunity.potential_revenue - opportunity.estimated_cost) /
                        opportunity.potential_revenue
                    )

                self.db_session.add(opportunity)
                opportunities.append(opportunity)

            self.db_session.commit()
            logger.info(f"Identified {len(opportunities)} opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Failed to identify opportunities: {e}")
            return []

    def evaluate_opportunity(self, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Evaluate a specific opportunity in detail.

        Args:
            opportunity: The opportunity to evaluate

        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating opportunity: {opportunity.title}")

        prompt = f"""
You are a business analyst. Evaluate this opportunity in detail:

Title: {opportunity.title}
Description: {opportunity.description}
Category: {opportunity.category}
Potential Revenue: ${opportunity.potential_revenue}
Estimated Cost: ${opportunity.estimated_cost}
Current Risk Score: {opportunity.risk_score}

Provide a detailed evaluation covering:
1. Market analysis
2. Competition
3. Technical feasibility
4. Financial projections
5. Key risks and mitigation strategies
6. Success probability (0-1)
7. Recommended action (approve/reject/revise)

Respond in JSON format with these keys.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        response_text = response.get("response", "")

        try:
            import json
            evaluation = json.loads(response_text)

            # Update opportunity status
            opportunity.status = OpportunityStatus.EVALUATING
            opportunity.evaluated_at = datetime.utcnow()

            # Store evaluation in metadata
            if not opportunity.metadata:
                opportunity.metadata = {}
            opportunity.metadata["evaluation"] = evaluation

            self.db_session.commit()

            logger.info(f"Evaluation complete for: {opportunity.title}")
            return evaluation

        except Exception as e:
            logger.error(f"Failed to evaluate opportunity: {e}")
            return {
                "success_probability": 0.5,
                "recommended_action": "revise",
                "error": str(e)
            }

    def get_top_opportunities(
        self,
        limit: int = 5,
        status: Optional[OpportunityStatus] = None
    ) -> List[Opportunity]:
        """
        Get top opportunities ranked by score.

        Args:
            limit: Maximum number to return
            status: Optional status filter

        Returns:
            List of top opportunities
        """
        query = self.db_session.query(Opportunity)

        if status:
            query = query.filter(Opportunity.status == status)

        # Sort by a combination of factors
        opportunities = query.all()

        # Score and rank
        scored = []
        for opp in opportunities:
            score = self._calculate_opportunity_score(opp)
            scored.append((score, opp))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [opp for _, opp in scored[:limit]]

    def _calculate_opportunity_score(self, opportunity: Opportunity) -> float:
        """Calculate a score for an opportunity."""
        # Revenue potential (normalized to 0-1, assuming max 10000)
        revenue_score = min(opportunity.potential_revenue / 10000, 1.0)

        # Cost efficiency (lower cost is better)
        cost_score = 1.0 - min(opportunity.estimated_cost / 1000, 1.0)

        # Risk-adjusted (lower risk is better)
        risk_score = 1.0 - opportunity.risk_score

        # Confidence
        confidence_score = opportunity.confidence_score

        # Profit margin
        margin_score = opportunity.profit_margin if opportunity.profit_margin else 0

        # Weighted combination
        score = (
            revenue_score * 0.25 +
            cost_score * 0.20 +
            risk_score * 0.20 +
            confidence_score * 0.20 +
            margin_score * 0.15
        )

        return score

    def _format_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Format context for prompt."""
        if not context:
            return "No specific context provided."

        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)
