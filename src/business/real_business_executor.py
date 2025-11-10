"""Real Business Executor - Extends base executor with actual payment and deployment."""

import logging
from typing import Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session

from .business_executor import BusinessExecutor
from .payment_gateway import razorpay_gateway
from ..deployment.digitalocean_deployer import digitalocean_deployer
from ..database.models import Opportunity
from .kanban_board import KanbanBoard, KanbanColumn
from ..core.config import settings

logger = logging.getLogger(__name__)


class RealBusinessExecutor(BusinessExecutor):
    """
    Enhanced business executor that:
    - Actually deploys services to DigitalOcean
    - Creates real payment links with Razorpay
    - Tracks real revenue and costs
    - Manages real infrastructure
    """

    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.payment_gateway = razorpay_gateway
        self.deployer = digitalocean_deployer
        self.real_mode = settings.real_business_mode

    def _execute_service_business(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """
        Execute service business with REAL deployment and payments.
        """
        logger.info(f"Executing service business in {'REAL' if self.real_mode else 'SIMULATION'} mode")

        # First, do the base execution (generate code, docs, etc.)
        result = super()._execute_service_business(opportunity, workspace_path, kanban)

        if not self.real_mode:
            return result

        # ===== REAL BUSINESS MODE =====

        # Step 1: Deploy to DigitalOcean
        deployment_result = self._deploy_to_cloud(opportunity, workspace_path, kanban)
        result.update(deployment_result)

        # Step 2: Create payment links/subscriptions
        payment_result = self._setup_payments(opportunity, deployment_result.get("deployment_url"), kanban)
        result.update(payment_result)

        # Step 3: Track real costs
        cost_result = self._track_real_costs(opportunity, deployment_result, kanban)
        result.update(cost_result)

        # Step 4: Update opportunity with real data
        opportunity.extra_data = opportunity.extra_data or {}
        opportunity.extra_data.update({
            "deployment_url": deployment_result.get("deployment_url"),
            "payment_link": payment_result.get("payment_link"),
            "droplet_id": deployment_result.get("droplet_id"),
            "real_deployment_cost": cost_result.get("deployment_cost", 0),
            "deployed_at": result.get("deployed_at"),
            "real_mode": True
        })
        self.db_session.commit()

        return result

    def _deploy_to_cloud(
        self,
        opportunity: Opportunity,
        workspace_path: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Deploy service to DigitalOcean."""
        logger.info("Deploying to DigitalOcean...")

        if not settings.use_real_deployment:
            logger.info("Real deployment disabled in config")
            return {
                "deployed": False,
                "deployment_url": "http://simulated.example.com",
                "reason": "real_deployment_disabled"
            }

        try:
            # Add Kanban card
            card_id = kanban.add_card(
                title="Deploy to DigitalOcean",
                description="Creating droplet and deploying service",
                column=KanbanColumn.IN_PROGRESS,
                priority=10
            )

            # Create droplet
            app_name = f"venture_{opportunity.id}_{opportunity.title.lower().replace(' ', '-')[:30]}"

            droplet_result = self.deployer.create_droplet(
                name=app_name,
                region=settings.digitalocean_default_region,
                size="s-1vcpu-1gb"  # $6/month
            )

            if "error" in droplet_result:
                logger.error(f"Droplet creation failed: {droplet_result['error']}")
                kanban.move_card(card_id, KanbanColumn.BACKLOG)
                kanban.add_comment(card_id, f"Failed: {droplet_result['error']}")
                return {
                    "deployed": False,
                    "error": droplet_result['error']
                }

            # Deploy application
            deploy_result = self.deployer.deploy_app(
                droplet_id=droplet_result["id"],
                workspace_path=Path(workspace_path),
                app_name=app_name,
                port=8000
            )

            if "error" in deploy_result:
                logger.error(f"Deployment failed: {deploy_result['error']}")
                kanban.move_card(card_id, KanbanColumn.BACKLOG)
                return {
                    "deployed": False,
                    "droplet_created": True,
                    "droplet_id": droplet_result["id"],
                    "error": deploy_result['error']
                }

            # Success!
            kanban.move_card(card_id, KanbanColumn.DONE)
            kanban.add_comment(card_id, f"✅ Deployed to {deploy_result['url']}")

            logger.info(f"✅ Service deployed to: {deploy_result['url']}")

            return {
                "deployed": True,
                "deployment_url": deploy_result["url"],
                "droplet_id": droplet_result["id"],
                "ip_address": droplet_result["ip_address"],
                "region": settings.digitalocean_default_region,
                "deployed_at": kanban._get_timestamp()
            }

        except Exception as e:
            logger.error(f"Deployment error: {e}", exc_info=True)
            return {
                "deployed": False,
                "error": str(e)
            }

    def _setup_payments(
        self,
        opportunity: Opportunity,
        service_url: str,
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Setup payment processing with Razorpay."""
        logger.info("Setting up payment gateway...")

        if not settings.use_real_payments:
            logger.info("Real payments disabled in config")
            return {
                "payment_setup": False,
                "payment_link": "https://simulated-payment.example.com",
                "reason": "real_payments_disabled"
            }

        try:
            # Add Kanban card
            card_id = kanban.add_card(
                title="Setup Payment Gateway",
                description="Creating Razorpay payment links",
                column=KanbanColumn.IN_PROGRESS,
                priority=9
            )

            # Determine pricing model
            if "subscription" in opportunity.description.lower() or "monthly" in opportunity.description.lower():
                # Create subscription plan
                monthly_price = opportunity.potential_revenue / 12  # Estimate monthly price

                plan_result = self.payment_gateway.create_subscription_plan(
                    plan_name=opportunity.title,
                    amount_monthly=monthly_price,
                    description=opportunity.description[:200]
                )

                if "error" in plan_result:
                    logger.error(f"Subscription plan creation failed: {plan_result['error']}")
                    kanban.move_card(card_id, KanbanColumn.BACKLOG)
                    return {
                        "payment_setup": False,
                        "error": plan_result['error']
                    }

                kanban.move_card(card_id, KanbanColumn.DONE)
                kanban.add_comment(card_id, f"✅ Subscription plan created: ${monthly_price}/month")

                return {
                    "payment_setup": True,
                    "payment_type": "subscription",
                    "plan_id": plan_result["id"],
                    "monthly_price_usd": monthly_price,
                    "monthly_price_inr": plan_result["amount_inr"]
                }

            else:
                # Create one-time payment link
                payment_link_result = self.payment_gateway.create_payment_link(
                    amount=opportunity.potential_revenue,
                    description=f"{opportunity.title} - {opportunity.description[:100]}",
                    reference_id=f"opp_{opportunity.id}"
                )

                if "error" in payment_link_result:
                    logger.error(f"Payment link creation failed: {payment_link_result['error']}")
                    kanban.move_card(card_id, KanbanColumn.BACKLOG)
                    return {
                        "payment_setup": False,
                        "error": payment_link_result['error']
                    }

                kanban.move_card(card_id, KanbanColumn.DONE)
                kanban.add_comment(card_id, f"✅ Payment link created: {payment_link_result['short_url']}")

                logger.info(f"✅ Payment link created: {payment_link_result['short_url']}")

                return {
                    "payment_setup": True,
                    "payment_type": "one_time",
                    "payment_link": payment_link_result["short_url"],
                    "payment_link_id": payment_link_result["id"],
                    "amount_usd": opportunity.potential_revenue,
                    "amount_inr": payment_link_result["amount_inr"]
                }

        except Exception as e:
            logger.error(f"Payment setup error: {e}", exc_info=True)
            return {
                "payment_setup": False,
                "error": str(e)
            }

    def _track_real_costs(
        self,
        opportunity: Opportunity,
        deployment_result: Dict[str, Any],
        kanban: KanbanBoard
    ) -> Dict[str, Any]:
        """Track actual costs from deployment and services."""
        logger.info("Tracking real costs...")

        costs = {
            "deployment_cost": 0,
            "monthly_cost": 0,
            "breakdown": {}
        }

        # DigitalOcean costs
        if deployment_result.get("deployed"):
            # Droplet: $6/month
            costs["deployment_cost"] = 6.0
            costs["monthly_cost"] += 6.0
            costs["breakdown"]["droplet"] = 6.0

        # Domain costs (if registered)
        if deployment_result.get("domain"):
            # Typical domain: $12/year = $1/month
            costs["monthly_cost"] += 1.0
            costs["breakdown"]["domain"] = 1.0

        # Update opportunity actual cost
        if opportunity.actual_cost:
            opportunity.actual_cost += costs["deployment_cost"]
        else:
            opportunity.actual_cost = costs["deployment_cost"]

        self.db_session.commit()

        logger.info(f"Real costs tracked: ${costs['monthly_cost']}/month")

        return costs

    def check_real_revenue(self, opportunity: Opportunity) -> Dict[str, Any]:
        """Check if we've received actual payments."""
        if not self.real_mode or not settings.use_real_payments:
            return {"real_revenue": 0, "checked": False}

        try:
            opportunity_data = opportunity.extra_data or {}

            # Check payment link status
            payment_link_id = opportunity_data.get("payment_link_id")
            if payment_link_id:
                status = self.payment_gateway.get_payment_status(payment_link_id)

                if status.get("paid"):
                    real_revenue = status.get("amount_paid", 0)

                    # Update opportunity
                    if opportunity.actual_profit is None:
                        opportunity.actual_profit = 0
                    opportunity.actual_profit += real_revenue - (opportunity.actual_cost or 0)

                    self.db_session.commit()

                    logger.info(f"✅ Real revenue received: ${real_revenue}")

                    return {
                        "real_revenue": real_revenue,
                        "payments_count": status.get("payments_count", 0),
                        "checked": True,
                        "profitable": opportunity.actual_profit > 0
                    }

            return {"real_revenue": 0, "checked": True, "paid": False}

        except Exception as e:
            logger.error(f"Error checking real revenue: {e}")
            return {"real_revenue": 0, "checked": False, "error": str(e)}

    def get_real_balance(self) -> float:
        """Get real balance from Razorpay account."""
        if not self.real_mode or not settings.use_real_payments:
            return 0.0

        try:
            balance_data = self.payment_gateway.get_balance()
            return balance_data.get("balance_usd", 0.0)
        except Exception as e:
            logger.error(f"Error getting real balance: {e}")
            return 0.0


# Factory function to get the right executor
def get_business_executor(db_session: Session) -> BusinessExecutor:
    """Get business executor based on settings."""
    if settings.real_business_mode:
        logger.info("Creating REAL business executor")
        return RealBusinessExecutor(db_session)
    else:
        logger.info("Creating simulated business executor")
        return BusinessExecutor(db_session)
