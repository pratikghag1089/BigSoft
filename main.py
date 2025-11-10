#!/usr/bin/env python3
"""
AI Entrepreneur Agent System - Main Entry Point

This is a self-sustaining AI system that acts as an entrepreneur,
creating and managing AI agents to build profitable businesses.
"""

import sys
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logging
from src.core.config import settings
from src.core.ollama_client import ollama_client
from src.database.database import init_db, db_manager
from src.agents.master_agent import MasterEntrepreneurAgent

logger = logging.getLogger(__name__)


def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    logger.info("Checking Ollama connection...")
    if not ollama_client.check_connection():
        logger.error(f"Cannot connect to Ollama at {settings.ollama_host}")
        logger.error("Please ensure Ollama is running: ollama serve")
        return False

    logger.info("✓ Ollama connection successful")

    # Check if model is available
    models = ollama_client.list_models()
    logger.info(f"Available models: {', '.join(models)}")

    if settings.ollama_model not in models:
        logger.warning(f"Model {settings.ollama_model} not found")
        logger.info(f"Pulling model: ollama pull {settings.ollama_model}")
        # In production, you'd call: ollama pull {model}
        logger.warning("Please run: ollama pull " + settings.ollama_model)
        return False

    logger.info(f"✓ Model {settings.ollama_model} is available")
    return True


def run_entrepreneur():
    """Run the master entrepreneur agent."""
    logger.info("="*80)
    logger.info("AI ENTREPRENEUR AGENT SYSTEM")
    logger.info("="*80)
    logger.info(f"Initial Capital: ${settings.initial_capital:.2f}")
    logger.info(f"Risk Tolerance: {settings.risk_tolerance}")
    logger.info(f"Min Profit Margin: {settings.min_profit_margin}")
    logger.info("="*80)
    logger.info("")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Create database session
    with db_manager.session_scope() as session:
        # Create master entrepreneur agent
        logger.info("Creating Master Entrepreneur Agent...")
        master_agent = MasterEntrepreneurAgent(db_session=session)

        # Run the agent
        logger.info("Starting autonomous operation...")
        logger.info("")

        try:
            result = master_agent.run()

            logger.info("")
            logger.info("="*80)
            logger.info("EXECUTION COMPLETE")
            logger.info("="*80)

            if result.get("success"):
                logger.info(f"✓ Cycles Completed: {result.get('cycles_completed', 0)}")
                logger.info(f"✓ Final Capital: ${result.get('final_capital', 0):.2f}")
                logger.info(f"✓ Total Profit: ${result.get('profit', 0):+.2f}")
                logger.info("")
                logger.info("Final Report:")
                logger.info(result.get('report', 'No report available'))
            else:
                logger.error(f"✗ Execution failed: {result.get('error')}")

        except KeyboardInterrupt:
            logger.info("\n\nExecution interrupted by user")
            master_agent.terminate()
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)


def run_dashboard():
    """Run the monitoring dashboard."""
    import uvicorn
    from src.api.app import create_app

    logger.info("Starting monitoring dashboard...")
    logger.info(f"Dashboard will be available at: http://{settings.dashboard_host}:{settings.dashboard_port}")

    # Initialize database
    init_db()

    # Create and run app
    app = create_app()
    uvicorn.run(
        app,
        host=settings.dashboard_host,
        port=settings.dashboard_port,
        log_level="info"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Entrepreneur Agent System - A self-sustaining AI entrepreneur"
    )
    parser.add_argument(
        "command",
        choices=["run", "dashboard", "both"],
        help="Command to execute: run (agent), dashboard (monitoring), both"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check connections, don't run"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)

    logger.info("Initializing AI Entrepreneur Agent System...")

    # Check Ollama connection
    if not check_ollama_connection():
        logger.error("Ollama connection check failed. Exiting.")
        sys.exit(1)

    if args.check_only:
        logger.info("Connection check complete. Exiting.")
        sys.exit(0)

    # Execute command
    if args.command == "run":
        run_entrepreneur()
    elif args.command == "dashboard":
        run_dashboard()
    elif args.command == "both":
        import threading
        import time

        # Run dashboard in background thread
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()

        # Wait a bit for dashboard to start
        time.sleep(2)

        # Run entrepreneur in main thread
        run_entrepreneur()


if __name__ == "__main__":
    main()
