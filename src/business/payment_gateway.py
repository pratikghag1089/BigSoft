"""Real Payment Gateway - Razorpay Integration."""

import logging
import razorpay
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.config import settings

logger = logging.getLogger(__name__)


class RazorpayGateway:
    """
    Real payment processing with Razorpay.
    Handles product creation, subscriptions, and payment processing.
    """

    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )
        self.enabled = settings.razorpay_enabled

    def create_payment_link(
        self,
        amount: float,
        description: str,
        customer_email: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment link for a product/service.

        Args:
            amount: Amount in USD (will be converted to INR)
            description: Product/service description
            customer_email: Optional customer email
            reference_id: Optional reference ID (e.g., opportunity_id)

        Returns:
            Payment link details
        """
        if not self.enabled:
            logger.warning("Razorpay not enabled - simulating payment link")
            return {
                "id": f"sim_link_{reference_id}",
                "short_url": f"https://simulated.razorpay.com/{reference_id}",
                "amount": amount,
                "status": "simulated"
            }

        try:
            # Convert USD to INR (approximate rate: 1 USD = 83 INR)
            amount_paise = int(amount * 83 * 100)  # Razorpay uses paise (1 INR = 100 paise)

            link_data = {
                "amount": amount_paise,
                "currency": "INR",
                "description": description,
                "reference_id": reference_id or f"venture_{int(datetime.utcnow().timestamp())}",
                "callback_url": settings.razorpay_callback_url,
                "callback_method": "get"
            }

            if customer_email:
                link_data["customer"] = {"email": customer_email}

            payment_link = self.client.payment_link.create(link_data)

            logger.info(f"Created payment link: {payment_link['short_url']} for ${amount}")

            return {
                "id": payment_link["id"],
                "short_url": payment_link["short_url"],
                "amount_usd": amount,
                "amount_inr": amount * 83,
                "status": payment_link["status"],
                "reference_id": reference_id
            }

        except Exception as e:
            logger.error(f"Error creating payment link: {e}")
            return {"error": str(e), "status": "failed"}

    def create_subscription_plan(
        self,
        plan_name: str,
        amount_monthly: float,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a subscription plan.

        Args:
            plan_name: Name of the plan
            amount_monthly: Monthly amount in USD
            description: Plan description

        Returns:
            Plan details
        """
        if not self.enabled:
            logger.warning("Razorpay not enabled - simulating subscription plan")
            return {
                "id": f"sim_plan_{plan_name.lower().replace(' ', '_')}",
                "name": plan_name,
                "amount": amount_monthly,
                "status": "simulated"
            }

        try:
            amount_paise = int(amount_monthly * 83 * 100)

            plan = self.client.plan.create({
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": plan_name,
                    "description": description,
                    "amount": amount_paise,
                    "currency": "INR"
                }
            })

            logger.info(f"Created subscription plan: {plan_name} - ${amount_monthly}/month")

            return {
                "id": plan["id"],
                "name": plan_name,
                "amount_usd": amount_monthly,
                "amount_inr": amount_monthly * 83,
                "period": "monthly",
                "status": "active"
            }

        except Exception as e:
            logger.error(f"Error creating subscription plan: {e}")
            return {"error": str(e), "status": "failed"}

    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Verify a payment was successful.

        Args:
            payment_id: Razorpay payment ID

        Returns:
            Payment verification details
        """
        if not self.enabled:
            return {"verified": True, "status": "simulated"}

        try:
            payment = self.client.payment.fetch(payment_id)

            verified = payment["status"] == "captured"

            logger.info(f"Payment {payment_id} verification: {verified}")

            return {
                "verified": verified,
                "status": payment["status"],
                "amount_inr": payment["amount"] / 100,
                "amount_usd": (payment["amount"] / 100) / 83,
                "method": payment.get("method", "unknown"),
                "email": payment.get("email", None)
            }

        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            return {"verified": False, "error": str(e)}

    def get_payment_status(self, payment_link_id: str) -> Dict[str, Any]:
        """
        Get status of a payment link.

        Args:
            payment_link_id: Payment link ID

        Returns:
            Status details
        """
        if not self.enabled:
            return {"status": "simulated", "paid": False}

        try:
            link = self.client.payment_link.fetch(payment_link_id)

            return {
                "id": link["id"],
                "status": link["status"],
                "paid": link["status"] == "paid",
                "amount_paid": (link.get("amount_paid", 0) / 100) / 83 if link.get("amount_paid") else 0,
                "payments_count": link.get("payments", {}).get("count", 0)
            }

        except Exception as e:
            logger.error(f"Error fetching payment link status: {e}")
            return {"error": str(e), "status": "error"}

    def create_payout(
        self,
        amount: float,
        account_number: str,
        ifsc_code: str,
        name: str,
        purpose: str = "payout"
    ) -> Dict[str, Any]:
        """
        Create a payout (withdraw funds).

        Args:
            amount: Amount in USD
            account_number: Bank account number
            ifsc_code: IFSC code
            name: Account holder name
            purpose: Payout purpose

        Returns:
            Payout details
        """
        if not self.enabled:
            logger.warning("Razorpay not enabled - simulating payout")
            return {"id": f"sim_payout_{int(datetime.utcnow().timestamp())}", "status": "simulated"}

        try:
            amount_paise = int(amount * 83 * 100)

            payout = self.client.payout.create({
                "account_number": settings.razorpay_account_number,  # Your Razorpay account
                "amount": amount_paise,
                "currency": "INR",
                "mode": "IMPS",  # Fast transfer in India
                "purpose": purpose,
                "fund_account": {
                    "account_type": "bank_account",
                    "bank_account": {
                        "name": name,
                        "ifsc": ifsc_code,
                        "account_number": account_number
                    },
                    "contact": {
                        "name": name,
                        "type": "self"
                    }
                },
                "queue_if_low_balance": True
            })

            logger.info(f"Created payout: ${amount} to {account_number}")

            return {
                "id": payout["id"],
                "status": payout["status"],
                "amount_usd": amount,
                "amount_inr": amount * 83
            }

        except Exception as e:
            logger.error(f"Error creating payout: {e}")
            return {"error": str(e), "status": "failed"}

    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance.

        Returns:
            Balance details
        """
        if not self.enabled:
            return {"balance_usd": 0, "balance_inr": 0, "status": "simulated"}

        try:
            balance = self.client.payment.balance()

            balance_inr = balance["balance"] / 100
            balance_usd = balance_inr / 83

            logger.info(f"Current balance: ${balance_usd:.2f} (₹{balance_inr:.2f})")

            return {
                "balance_usd": balance_usd,
                "balance_inr": balance_inr,
                "currency": "INR"
            }

        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {"error": str(e), "balance_usd": 0}


# Global instance
razorpay_gateway = RazorpayGateway()
