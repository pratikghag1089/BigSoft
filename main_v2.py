#!/usr/bin/env python3
"""
AI Entrepreneur Agent System V2 - Enhanced with Self-Learning, Self-Fixing, Self-Improvement

Main entry point for the enhanced system with:
- Self-learning from past performance
- Self-fixing when errors occur
- Self-improvement through continuous optimization
- Real business execution
- Dynamic agent management (auto-delete useless agents)
- Project management with Kanban boards
- Workspace management for each venture
"""

import sys
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logging
from src.core.config import settings
from src.core.ollama_client import ollama_client
from src.database.database import init_db, db_manager
from src.agents.master_agent_v2 import MasterEntrepreneurAgentV2

logger = logging.getLogger(__name__)


def check_ollama_connection():
    """Check if Ollama is running and accessible."""
    logger.info("Checking Ollama connection...")
    if not ollama_client.check_connection():
        logger.error(f"Cannot connect to Ollama at {settings.ollama_host}")
        logger.error("Please ensure Ollama is running: ollama serve")
        return False

    logger.info("✓ Ollama connection successful")

    models = ollama_client.list_models()
    logger.info(f"Available models: {', '.join(models)}")

    if settings.ollama_model not in models:
        logger.warning(f"Model {settings.ollama_model} not found")
        logger.warning("Please run: ollama pull " + settings.ollama_model)
        return False

    logger.info(f"✓ Model {settings.ollama_model} is available")
    return True


def run_entrepreneur_v2():
    """Run the enhanced V2 master entrepreneur agent."""
    logger.info("="*80)
    logger.info("AI ENTREPRENEUR AGENT SYSTEM V2 - ENHANCED EDITION")
    logger.info("="*80)
    logger.info("Features:")
    logger.info("  🧠 Self-Learning from past performance")
    logger.info("  🔨 Self-Fixing when errors occur")
    logger.info("  🔧 Self-Improvement through optimization")
    logger.info("  💼 Real business execution (code, content, services)")
    logger.info("  🤖 Dynamic agent management (auto-cleanup)")
    logger.info("  📋 Kanban boards for project management")
    logger.info("  📁 Workspace management for each venture")
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
        # Create enhanced master entrepreneur agent
        logger.info("Creating Enhanced Master Entrepreneur Agent V2...")
        master_agent = MasterEntrepreneurAgentV2(db_session=session)

        # Run the agent
        logger.info("Starting autonomous operation with enhanced capabilities...")
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
                logger.info(f"✓ ROI: {result.get('roi_percent', 0):.2f}%")
                logger.info(f"✓ Workspaces Created: {result.get('workspaces_created', 0)}")
                logger.info("")
                logger.info("Final Report:")
                logger.info(result.get('report', 'No report available'))
                logger.info("")
                logger.info("💡 Check agent_data/workspaces/ for all generated files and projects")
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

    init_db()

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
        description="AI Entrepreneur Agent System V2 - Self-learning, self-fixing, self-improving AI entrepreneur"
    )
    parser.add_argument(
        "command",
        choices=["run", "dashboard", "both"],
        help="Command: run (V2 agent), dashboard (monitoring), both"
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

    setup_logging(args.log_level)

    logger.info("Initializing AI Entrepreneur Agent System V2...")

    if not check_ollama_connection():
        logger.error("Ollama connection check failed. Exiting.")
        sys.exit(1)

    if args.check_only:
        logger.info("Connection check complete. Exiting.")
        sys.exit(0)

    if args.command == "run":
        run_entrepreneur_v2()
    elif args.command == "dashboard":
        run_dashboard()
    elif args.command == "both":
        import threading
        import time

        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()

        time.sleep(2)

        run_entrepreneur_v2()


if __name__ == "__main__":
    main()
