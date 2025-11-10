"""Self-Fixing Module - Detects and automatically fixes errors."""

import logging
import traceback
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.models import Task, TaskStatus, Agent, AgentStatus, Metric
from ..core.ollama_client import ollama_client

logger = logging.getLogger(__name__)


class ErrorPattern:
    """Represents a known error pattern and its fix."""

    def __init__(
        self,
        pattern_id: str,
        error_signature: str,
        fix_strategy: str,
        fix_function: Optional[Callable] = None,
        confidence: float = 0.8
    ):
        self.pattern_id = pattern_id
        self.error_signature = error_signature
        self.fix_strategy = fix_strategy
        self.fix_function = fix_function
        self.confidence = confidence
        self.times_seen = 0
        self.times_fixed = 0


class SelfFixingEngine:
    """
    Self-fixing engine that detects errors and automatically fixes them.
    Learns from errors and builds a knowledge base of fixes.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.llm = ollama_client
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.error_history: List[Dict[str, Any]] = []

        # Initialize common error patterns
        self._initialize_error_patterns()

    def _initialize_error_patterns(self):
        """Initialize common error patterns."""
        # Database connection errors
        self.register_error_pattern(
            pattern_id="db_connection_error",
            error_signature="database.*connection",
            fix_strategy="Reconnect to database and retry",
            fix_function=self._fix_db_connection
        )

        # Timeout errors
        self.register_error_pattern(
            pattern_id="timeout_error",
            error_signature="timeout|timed out",
            fix_strategy="Retry with increased timeout",
            fix_function=self._fix_timeout
        )

        # Resource exhaustion
        self.register_error_pattern(
            pattern_id="resource_exhausted",
            error_signature="out of memory|resource exhausted",
            fix_strategy="Free resources and optimize",
            fix_function=self._fix_resource_exhaustion
        )

        # API errors
        self.register_error_pattern(
            pattern_id="api_error",
            error_signature="api.*error|http.*[45][0-9][0-9]",
            fix_strategy="Retry with exponential backoff",
            fix_function=self._fix_api_error
        )

    def register_error_pattern(
        self,
        pattern_id: str,
        error_signature: str,
        fix_strategy: str,
        fix_function: Optional[Callable] = None,
        confidence: float = 0.8
    ):
        """Register a new error pattern."""
        pattern = ErrorPattern(
            pattern_id=pattern_id,
            error_signature=error_signature,
            fix_strategy=fix_strategy,
            fix_function=fix_function,
            confidence=confidence
        )

        self.error_patterns[pattern_id] = pattern
        logger.info(f"Registered error pattern: {pattern_id}")

    def detect_and_fix_task_error(self, task_id: int) -> Dict[str, Any]:
        """
        Detect and fix errors in a failed task.

        Args:
            task_id: Task ID

        Returns:
            Fix result
        """
        task = self.db_session.query(Task).filter_by(id=task_id).first()
        if not task:
            return {"success": False, "error": "Task not found"}

        if task.status != TaskStatus.FAILED:
            return {"success": False, "error": "Task did not fail"}

        error_message = task.error_message or ""

        logger.info(f"Attempting to fix task {task_id}: {task.title}")
        logger.debug(f"Error message: {error_message}")

        # Try to match against known patterns
        for pattern in self.error_patterns.values():
            if self._matches_pattern(error_message, pattern.error_signature):
                logger.info(f"Matched error pattern: {pattern.pattern_id}")
                pattern.times_seen += 1

                # Attempt fix
                fix_result = self._apply_fix(task, pattern)

                if fix_result.get("success"):
                    pattern.times_fixed += 1
                    self._log_successful_fix(task, pattern, fix_result)
                    return fix_result

        # If no pattern matched, use LLM to generate a fix
        logger.info("No pattern matched, using LLM to generate fix")
        return self._llm_generate_fix(task)

    def _matches_pattern(self, error_message: str, pattern: str) -> bool:
        """Check if error message matches a pattern."""
        import re
        try:
            return bool(re.search(pattern, error_message, re.IGNORECASE))
        except re.error:
            return pattern.lower() in error_message.lower()

    def _apply_fix(self, task: Task, pattern: ErrorPattern) -> Dict[str, Any]:
        """Apply a fix for a known error pattern."""
        if pattern.fix_function:
            try:
                result = pattern.fix_function(task)
                return result
            except Exception as e:
                logger.error(f"Fix function failed: {e}")
                return {"success": False, "error": str(e)}

        # Generic retry strategy
        return self._generic_retry(task, pattern.fix_strategy)

    def _generic_retry(self, task: Task, strategy: str) -> Dict[str, Any]:
        """Generic retry strategy."""
        logger.info(f"Applying generic retry: {strategy}")

        # Reset task to pending
        task.status = TaskStatus.PENDING
        task.error_message = None
        task.iterations = (task.iterations or 0) + 1

        self.db_session.commit()

        return {
            "success": True,
            "action": "retry",
            "strategy": strategy,
            "message": f"Task reset for retry with strategy: {strategy}"
        }

    def _fix_db_connection(self, task: Task) -> Dict[str, Any]:
        """Fix database connection errors."""
        logger.info("Fixing database connection error")

        try:
            # Reconnect database
            self.db_session.rollback()
            self.db_session.close()

            # Task will be retried automatically
            return {
                "success": True,
                "action": "db_reconnect",
                "message": "Database reconnected, task ready for retry"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _fix_timeout(self, task: Task) -> Dict[str, Any]:
        """Fix timeout errors."""
        logger.info("Fixing timeout error")

        # Increase timeout in task metadata
        if not task.metadata:
            task.metadata = {}

        current_timeout = task.metadata.get("timeout", 300)
        new_timeout = min(current_timeout * 2, 1800)  # Max 30 minutes

        task.metadata["timeout"] = new_timeout
        task.status = TaskStatus.PENDING
        task.error_message = None

        self.db_session.commit()

        return {
            "success": True,
            "action": "increase_timeout",
            "old_timeout": current_timeout,
            "new_timeout": new_timeout,
            "message": f"Timeout increased from {current_timeout}s to {new_timeout}s"
        }

    def _fix_resource_exhaustion(self, task: Task) -> Dict[str, Any]:
        """Fix resource exhaustion errors."""
        logger.info("Fixing resource exhaustion error")

        # Could implement memory cleanup, garbage collection, etc.
        import gc
        gc.collect()

        task.status = TaskStatus.PENDING
        task.error_message = None

        self.db_session.commit()

        return {
            "success": True,
            "action": "resource_cleanup",
            "message": "Resources cleaned up, task ready for retry"
        }

    def _fix_api_error(self, task: Task) -> Dict[str, Any]:
        """Fix API errors."""
        logger.info("Fixing API error")

        # Implement exponential backoff
        if not task.metadata:
            task.metadata = {}

        retry_count = task.metadata.get("retry_count", 0)
        backoff_seconds = min(2 ** retry_count, 60)  # Max 60 seconds

        task.metadata["retry_count"] = retry_count + 1
        task.metadata["backoff_seconds"] = backoff_seconds
        task.status = TaskStatus.PENDING
        task.error_message = None

        self.db_session.commit()

        return {
            "success": True,
            "action": "exponential_backoff",
            "retry_count": retry_count + 1,
            "backoff_seconds": backoff_seconds,
            "message": f"Will retry after {backoff_seconds}s backoff"
        }

    def _llm_generate_fix(self, task: Task) -> Dict[str, Any]:
        """Use LLM to generate a fix for unknown errors."""
        prompt = f"""
Analyze this task failure and suggest a fix:

Task: {task.title}
Description: {task.description}
Error: {task.error_message}
Iterations: {task.iterations}

Provide:
1. Root cause analysis
2. Specific fix strategy
3. Whether the task should be retried or cancelled
4. Any adjustments needed to task parameters

Respond in JSON format with keys: root_cause, fix_strategy, action (retry/cancel/modify), adjustments
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)

        try:
            import json
            fix_plan = json.loads(response.get("response", "{}"))

            action = fix_plan.get("action", "retry").lower()

            if action == "cancel":
                task.status = TaskStatus.CANCELLED
                self.db_session.commit()
                return {
                    "success": True,
                    "action": "cancel",
                    "reason": fix_plan.get("root_cause", "Unfixable error"),
                    "llm_analysis": fix_plan
                }

            elif action == "modify":
                # Apply suggested modifications
                adjustments = fix_plan.get("adjustments", {})
                if not task.metadata:
                    task.metadata = {}

                task.metadata["llm_adjustments"] = adjustments
                task.status = TaskStatus.PENDING
                task.error_message = None

                self.db_session.commit()

                return {
                    "success": True,
                    "action": "modify_and_retry",
                    "adjustments": adjustments,
                    "llm_analysis": fix_plan
                }

            else:  # retry
                task.status = TaskStatus.PENDING
                task.error_message = None
                self.db_session.commit()

                return {
                    "success": True,
                    "action": "retry",
                    "llm_analysis": fix_plan
                }

        except Exception as e:
            logger.error(f"LLM fix generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "llm_response": response.get("response", "")
            }

    def _log_successful_fix(self, task: Task, pattern: ErrorPattern, result: Dict[str, Any]):
        """Log a successful fix."""
        fix_record = {
            "task_id": task.id,
            "task_title": task.title,
            "error_pattern": pattern.pattern_id,
            "fix_strategy": pattern.fix_strategy,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.error_history.append(fix_record)

        # Record metric
        metric = Metric(
            metric_type="self_fixing",
            metric_name="successful_fix",
            value=1,
            category="error_recovery",
            metadata=fix_record
        )
        self.db_session.add(metric)
        self.db_session.commit()

        logger.info(f"Successfully fixed task {task.id} using pattern {pattern.pattern_id}")

    def analyze_error_trends(self) -> Dict[str, Any]:
        """Analyze error trends and patterns."""
        # Get all failed tasks
        failed_tasks = self.db_session.query(Task).filter(
            Task.status == TaskStatus.FAILED
        ).all()

        if not failed_tasks:
            return {"message": "No failed tasks to analyze"}

        # Categorize errors
        error_categories = {}
        for task in failed_tasks:
            error_msg = task.error_message or "Unknown error"

            # Try to match patterns
            matched_pattern = None
            for pattern in self.error_patterns.values():
                if self._matches_pattern(error_msg, pattern.error_signature):
                    matched_pattern = pattern.pattern_id
                    break

            category = matched_pattern or "uncategorized"
            if category not in error_categories:
                error_categories[category] = {
                    "count": 0,
                    "examples": []
                }

            error_categories[category]["count"] += 1
            if len(error_categories[category]["examples"]) < 3:
                error_categories[category]["examples"].append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "error": error_msg[:200]  # First 200 chars
                })

        # Pattern statistics
        pattern_stats = {
            pattern_id: {
                "times_seen": pattern.times_seen,
                "times_fixed": pattern.times_fixed,
                "success_rate": pattern.times_fixed / pattern.times_seen if pattern.times_seen > 0 else 0
            }
            for pattern_id, pattern in self.error_patterns.items()
        }

        return {
            "total_failed_tasks": len(failed_tasks),
            "error_categories": error_categories,
            "pattern_statistics": pattern_stats,
            "fix_history_count": len(self.error_history)
        }

    def get_fix_recommendations(self) -> str:
        """Get recommendations for improving error handling."""
        trends = self.analyze_error_trends()

        prompt = f"""
Analyze error trends and provide recommendations:

{json.dumps(trends, indent=2)}

Provide:
1. Most critical error patterns to address
2. Suggested improvements to error handling
3. New error patterns to add
4. Process improvements to reduce errors

Be specific and actionable.
"""

        response = self.llm.generate(prompt=prompt, temperature=0.7)
        return response.get("response", "")
