#!/usr/bin/env python3
"""
AI Entrepreneur Agent System - With Live UI Dashboard

Main entry point with real-time Web UI for full transparency.
See everything the AI thinks and does in real-time!
"""

import sys
import logging
import argparse
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logging
from src.core.config import settings
from src.core.ollama_client import ollama_client
from src.core.ai_observer import observer
from src.database.database import init_db, db_manager
from src.agents.master_agent_v2 import MasterEntrepreneurAgentV2
from src.api.websocket_manager import manager as ws_manager
from src.utils.broadcast_logger import setup_broadcast_logging

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


def run_entrepreneur_with_ui():
    """Run the entrepreneur agent with UI broadcasting."""
    logger.info("="*80)
    logger.info("AI ENTREPRENEUR AGENT SYSTEM - LIVE UI DASHBOARD")
    logger.info("="*80)
    logger.info("🌐 Open http://localhost:8000 to see AI thoughts in real-time!")
    logger.info("="*80)
    logger.info("")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Setup WebSocket broadcasting for AI thoughts
    observer.set_websocket_manager(ws_manager)

    # Create database session
    with db_manager.session_scope() as session:
        logger.info("Creating Enhanced Master Entrepreneur Agent V2...")

        # Broadcast system start
        observer.broadcast_system_event_sync(
            "system_start",
            f"AI Entrepreneur System starting with ${settings.initial_capital:.2f} capital"
        )

        master_agent = MasterEntrepreneurAgentV2(db_session=session)

        # Inject observer into agent for broadcasting
        master_agent.observer = observer

        logger.info("Starting autonomous operation with LIVE UI monitoring...")
        logger.info("")

        try:
            # Broadcast that agent is starting
            observer.broadcast_thought_sync(
                "System initialized. Beginning autonomous business operations...",
                {"capital": settings.initial_capital, "risk_tolerance": settings.risk_tolerance}
            )

            result = master_agent.run()

            logger.info("")
            logger.info("="*80)
            logger.info("EXECUTION COMPLETE")
            logger.info("="*80)

            if result.get("success"):
                observer.broadcast_system_event_sync(
                    "execution_complete",
                    f"Mission complete! Final capital: ${result.get('final_capital', 0):.2f}",
                    result
                )

                logger.info(f"✓ Cycles Completed: {result.get('cycles_completed', 0)}")
                logger.info(f"✓ Final Capital: ${result.get('final_capital', 0):.2f}")
                logger.info(f"✓ Total Profit: ${result.get('profit', 0):+.2f}")
                logger.info(f"✓ ROI: {result.get('roi_percent', 0):.2f}%")
            else:
                logger.error(f"✗ Execution failed: {result.get('error')}")

        except KeyboardInterrupt:
            logger.info("\n\nExecution interrupted by user")
            observer.broadcast_system_event_sync("user_interrupt", "Execution stopped by user")
            master_agent.terminate()
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            observer.broadcast_system_event_sync("error", f"System error: {str(e)}")


def run_dashboard():
    """Run the enhanced dashboard with WebSocket support."""
    import uvicorn
    from src.api.app_enhanced import create_enhanced_app

    logger.info("Starting Live Dashboard with WebSocket support...")
    logger.info(f"Dashboard will be available at: http://{settings.dashboard_host}:{settings.dashboard_port}")

    init_db()

    # Setup broadcast logging
    setup_broadcast_logging(ws_manager)

    app = create_enhanced_app()

    uvicorn.run(
        app,
        host=settings.dashboard_host,
        port=settings.dashboard_port,
        log_level="info"
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Entrepreneur with Live UI - See AI thoughts in real-time!"
    )
    parser.add_argument(
        "command",
        choices=["run", "dashboard", "both"],
        default="both",
        nargs="?",
        help="Command: run (agent only), dashboard (UI only), both (default)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    logger.info("Initializing AI Entrepreneur Agent System with Live UI...")

    if not check_ollama_connection():
        logger.error("Ollama connection check failed. Exiting.")
        sys.exit(1)

    if args.command == "run":
        # Run agent only (no dashboard)
        run_entrepreneur_with_ui()

    elif args.command == "dashboard":
        # Run dashboard only
        run_dashboard()

    else:  # both
        # Run both dashboard and agent
        logger.info("="*80)
        logger.info("🚀 STARTING FULL SYSTEM")
        logger.info("="*80)
        logger.info("1. Dashboard will start on http://localhost:8000")
        logger.info("2. Open it in your browser to see AI thoughts in real-time")
        logger.info("3. AI agent will start after dashboard is ready")
        logger.info("="*80)
        logger.info("")

        # Start dashboard in background thread
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()

        # Wait for dashboard to start
        logger.info("Waiting for dashboard to start...")
        time.sleep(5)

        logger.info("✓ Dashboard ready!")
        logger.info("")
        logger.info("🌐 OPEN YOUR BROWSER NOW:")
        logger.info(f"   👉 http://localhost:{settings.dashboard_port}")
        logger.info("")
        logger.info("You'll see:")
        logger.info("  🧠 Every thought the AI has")
        logger.info("  🎯 Every decision it makes")
        logger.info("  🤖 All agent activities")
        logger.info("  📋 Live system logs")
        logger.info("  📊 Real-time metrics")
        logger.info("")
        time.sleep(3)

        # Run entrepreneur in main thread
        run_entrepreneur_with_ui()


if __name__ == "__main__":
    main()
