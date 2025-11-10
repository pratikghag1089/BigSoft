"""Custom logging handler that broadcasts to WebSocket clients."""

import logging
import asyncio
from typing import Optional


class WebSocketHandler(logging.Handler):
    """Logging handler that broadcasts logs to WebSocket clients."""

    def __init__(self, connection_manager):
        super().__init__()
        self.connection_manager = connection_manager

    def emit(self, record):
        """Emit a log record to WebSocket clients."""
        try:
            log_entry = self.format(record)

            # Create event loop or get existing one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Send log to WebSocket clients
            if loop.is_running():
                asyncio.create_task(
                    self.connection_manager.send_log(
                        level=record.levelname,
                        message=log_entry,
                        logger_name=record.name
                    )
                )
            else:
                loop.run_until_complete(
                    self.connection_manager.send_log(
                        level=record.levelname,
                        message=log_entry,
                        logger_name=record.name
                    )
                )
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Error broadcasting log: {e}")


def setup_broadcast_logging(connection_manager):
    """Setup logging to broadcast to WebSocket clients."""
    # Get root logger
    root_logger = logging.getLogger()

    # Create and add WebSocket handler
    ws_handler = WebSocketHandler(connection_manager)
    ws_handler.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ws_handler.setFormatter(formatter)

    root_logger.addHandler(ws_handler)

    return ws_handler
