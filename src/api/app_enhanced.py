"""Enhanced FastAPI application with real-time WebSocket support."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session

from ..core.config import settings
from ..database import get_db, Agent, Task, Opportunity, Metric, SystemState
from ..database.models import AgentStatus, TaskStatus, OpportunityStatus
from ..business.workspace_manager import WorkspaceManager
from ..business.kanban_board import KanbanBoard
from .websocket_manager import manager as ws_manager

logger = logging.getLogger(__name__)


def create_enhanced_app() -> FastAPI:
    """Create enhanced FastAPI application with real-time features."""
    app = FastAPI(
        title=f"{settings.app_name} - Live Dashboard",
        description="Real-time monitoring of AI Entrepreneur with full transparency",
        version="2.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    workspace_manager = WorkspaceManager()

    # WebSocket endpoint for real-time updates
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await ws_manager.connect(websocket)
        try:
            while True:
                # Keep connection alive and receive any client messages
                data = await websocket.receive_text()
                # Echo back or handle client messages if needed
                logger.debug(f"Received from client: {data}")
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)

    # Serve static files and UI
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main dashboard UI."""
        html_path = Path(__file__).parent / "static" / "index.html"
        if html_path.exists():
            return FileResponse(html_path)
        return HTMLResponse(content=get_embedded_html(), status_code=200)

    @app.get("/api/status")
    async def get_system_status(db: Session = Depends(get_db)):
        """Get current system status."""
        capital_state = db.query(SystemState).filter_by(key="capital").first()
        capital = capital_state.value.get("amount", 0) if capital_state else settings.initial_capital

        total_agents = db.query(Agent).count()
        active_agents = db.query(Agent).filter(Agent.status == AgentStatus.RUNNING).count()
        total_tasks = db.query(Task).count()
        total_opportunities = db.query(Opportunity).count()

        # Get recent activity
        recent_opps = db.query(Opportunity).order_by(
            Opportunity.identified_at.desc()
        ).limit(5).all()

        return {
            "status": "running",
            "capital": capital,
            "initial_capital": settings.initial_capital,
            "profit": capital - settings.initial_capital,
            "roi_percent": ((capital - settings.initial_capital) / settings.initial_capital * 100) if settings.initial_capital > 0 else 0,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_tasks": total_tasks,
            "total_opportunities": total_opportunities,
            "recent_opportunities": [
                {
                    "id": o.id,
                    "title": o.title,
                    "status": o.status.value,
                    "profit": o.actual_profit
                }
                for o in recent_opps
            ],
            "timestamp": datetime.utcnow().isoformat()
        }

    @app.get("/api/agents/live")
    async def get_agents_live(db: Session = Depends(get_db)):
        """Get live agent information."""
        agents = db.query(Agent).all()

        agent_list = []
        for agent in agents:
            tasks = db.query(Task).filter(Task.agent_id == agent.id).all()
            total_tasks = len(tasks)
            completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

            agent_list.append({
                "id": agent.id,
                "name": agent.name,
                "type": agent.agent_type,
                "status": agent.status.value,
                "role": agent.role,
                "capabilities": agent.capabilities,
                "created_at": agent.created_at.isoformat() if agent.created_at else None,
                "tasks_total": total_tasks,
                "tasks_completed": completed,
                "tasks_failed": failed,
                "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0
            })

        return {"agents": agent_list}

    @app.get("/api/thoughts/stream")
    async def get_thought_stream():
        """Get recent thought stream."""
        return {
            "thoughts": ws_manager.thought_stream[-100:],
            "count": len(ws_manager.thought_stream)
        }

    @app.get("/api/events/stream")
    async def get_event_stream():
        """Get recent event stream."""
        return {
            "events": ws_manager.event_stream[-100:],
            "count": len(ws_manager.event_stream)
        }

    @app.get("/api/opportunities/live")
    async def get_opportunities_live(db: Session = Depends(get_db)):
        """Get live opportunities with details."""
        opportunities = db.query(Opportunity).order_by(
            Opportunity.identified_at.desc()
        ).limit(50).all()

        return {
            "opportunities": [
                {
                    "id": opp.id,
                    "title": opp.title,
                    "description": opp.description,
                    "category": opp.category,
                    "status": opp.status.value,
                    "potential_revenue": opp.potential_revenue,
                    "estimated_cost": opp.estimated_cost,
                    "actual_revenue": opp.actual_revenue,
                    "actual_cost": opp.actual_cost,
                    "actual_profit": opp.actual_profit,
                    "profit_margin": opp.profit_margin,
                    "risk_score": opp.risk_score,
                    "confidence_score": opp.confidence_score,
                    "identified_at": opp.identified_at.isoformat() if opp.identified_at else None,
                    "completed_at": opp.completed_at.isoformat() if opp.completed_at else None
                }
                for opp in opportunities
            ]
        }

    @app.get("/api/workspaces/list")
    async def list_workspaces():
        """List all workspaces."""
        workspaces = workspace_manager.list_all_workspaces()
        return {"workspaces": workspaces}

    @app.get("/api/workspaces/{venture_id}/files")
    async def list_workspace_files(venture_id: int):
        """List files in a workspace."""
        workspace_path = workspace_manager.get_workspace_path(venture_id)
        if not workspace_path:
            raise HTTPException(status_code=404, detail="Workspace not found")

        files = workspace_manager.list_files(workspace_path)
        return {"venture_id": venture_id, "files": files}

    @app.get("/api/workspaces/{venture_id}/file")
    async def get_workspace_file(venture_id: int, path: str = Query(...)):
        """Get content of a file in workspace."""
        workspace_path = workspace_manager.get_workspace_path(venture_id)
        if not workspace_path:
            raise HTTPException(status_code=404, detail="Workspace not found")

        content = workspace_manager.read_file(workspace_path, path)
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")

        return {"venture_id": venture_id, "path": path, "content": content}

    @app.get("/api/kanban/{venture_id}")
    async def get_kanban_board(venture_id: int, db: Session = Depends(get_db)):
        """Get Kanban board for a venture."""
        kanban = KanbanBoard(db, f"board_{venture_id}", venture_id)
        kanban.sync_from_tasks()

        return kanban.get_board_state()

    @app.get("/api/metrics/live")
    async def get_live_metrics(db: Session = Depends(get_db)):
        """Get live system metrics."""
        recent_metrics = db.query(Metric).order_by(
            Metric.recorded_at.desc()
        ).limit(100).all()

        return {
            "metrics": [
                {
                    "id": m.id,
                    "type": m.metric_type,
                    "name": m.metric_name,
                    "value": m.value,
                    "category": m.category,
                    "recorded_at": m.recorded_at.isoformat(),
                    "metadata": m.metadata
                }
                for m in recent_metrics
            ]
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "websocket_connections": len(ws_manager.active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }

    return app


def get_embedded_html() -> str:
    """Get embedded HTML for the dashboard."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Entrepreneur Dashboard - Live View</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f0f1e;
            color: #e0e0e0;
            overflow-x: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header .status {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }

        .status-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-badge {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }

        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .panel {
            background: #1a1a2e;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #2d2d44;
        }

        .panel-title {
            font-size: 20px;
            margin-bottom: 15px;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .thought-stream, .event-stream, .log-stream {
            max-height: 400px;
            overflow-y: auto;
            font-size: 14px;
        }

        .thought-item, .event-item, .log-item {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .thought-item {
            background: #2d2d44;
            border-left-color: #667eea;
        }

        .event-item {
            background: #2d3d2d;
            border-left-color: #48bb78;
        }

        .event-item.decision {
            border-left-color: #ed8936;
        }

        .log-item {
            background: #1f1f2e;
            border-left-color: #4299e1;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }

        .log-item.ERROR {
            border-left-color: #f56565;
            background: #3d1f1f;
        }

        .log-item.WARNING {
            border-left-color: #ed8936;
            background: #3d2f1f;
        }

        .timestamp {
            color: #888;
            font-size: 11px;
            margin-bottom: 5px;
        }

        .agent-grid {
            display: grid;
            gap: 10px;
        }

        .agent-card {
            background: #2d2d44;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .agent-card.running {
            border-left-color: #48bb78;
        }

        .agent-card.terminated {
            border-left-color: #f56565;
            opacity: 0.6;
        }

        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .agent-name {
            font-weight: bold;
            font-size: 16px;
        }

        .agent-status {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }

        .agent-status.running {
            background: #48bb78;
            color: white;
        }

        .agent-status.created {
            background: #4299e1;
            color: white;
        }

        .agent-status.terminated {
            background: #f56565;
            color: white;
        }

        .agent-stats {
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #aaa;
        }

        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }

        .metric-label {
            color: #888;
            font-size: 14px;
        }

        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            z-index: 1000;
        }

        .connection-status.connected {
            background: #48bb78;
            color: white;
        }

        .connection-status.disconnected {
            background: #f56565;
            color: white;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a2e;
        }

        ::-webkit-scrollbar-thumb {
            background: #667eea;
            border-radius: 4px;
        }

        .full-width {
            grid-column: 1 / -1;
        }
    </style>
</head>
<body>
    <div id="connectionStatus" class="connection-status disconnected">⚫ Connecting...</div>

    <div class="header">
        <h1>🤖 AI Entrepreneur - Live Intelligence Dashboard</h1>
        <div class="status" id="headerStatus">
            <div class="status-item">
                <span>💰 Capital:</span>
                <span class="status-badge" id="capital">$0.00</span>
            </div>
            <div class="status-item">
                <span>📈 ROI:</span>
                <span class="status-badge" id="roi">0%</span>
            </div>
            <div class="status-item">
                <span>🤖 Active Agents:</span>
                <span class="status-badge" id="activeAgents">0</span>
            </div>
            <div class="status-item">
                <span>💼 Opportunities:</span>
                <span class="status-badge" id="opportunities">0</span>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- AI Thought Stream -->
        <div class="panel full-width">
            <div class="panel-title">🧠 AI Thought Stream (Real-Time)</div>
            <div class="thought-stream" id="thoughtStream">
                <div style="text-align: center; color: #666; padding: 20px;">
                    Waiting for AI thoughts...
                </div>
            </div>
        </div>

        <!-- Decision Stream -->
        <div class="panel">
            <div class="panel-title">🎯 Decisions & Actions</div>
            <div class="event-stream" id="eventStream">
                <div style="text-align: center; color: #666; padding: 20px;">
                    Waiting for decisions...
                </div>
            </div>
        </div>

        <!-- Live Logs -->
        <div class="panel">
            <div class="panel-title">📋 System Logs (Live)</div>
            <div class="log-stream" id="logStream">
                <div style="text-align: center; color: #666; padding: 20px;">
                    Waiting for logs...
                </div>
            </div>
        </div>

        <!-- Active Agents -->
        <div class="panel full-width">
            <div class="panel-title">🤖 Active Agents</div>
            <div class="agent-grid" id="agentGrid">
                <div style="text-align: center; color: #666; padding: 20px;">
                    Loading agents...
                </div>
            </div>
        </div>

        <!-- Key Metrics -->
        <div class="panel">
            <div class="panel-title">📊 Key Metrics</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <div class="metric-label">Total Profit</div>
                    <div class="metric-value" id="totalProfit">$0</div>
                </div>
                <div>
                    <div class="metric-label">Success Rate</div>
                    <div class="metric-value" id="successRate">0%</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws;
        let reconnectInterval;

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                document.getElementById('connectionStatus').textContent = '🟢 Connected';
                document.getElementById('connectionStatus').className = 'connection-status connected';
                clearInterval(reconnectInterval);
                loadInitialData();
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
                document.getElementById('connectionStatus').className = 'connection-status disconnected';

                // Attempt to reconnect
                reconnectInterval = setInterval(() => {
                    console.log('Attempting to reconnect...');
                    connect();
                }, 3000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }

        function handleMessage(data) {
            switch(data.type) {
                case 'thought':
                    addThought(data);
                    break;
                case 'decision':
                    addDecision(data);
                    break;
                case 'agent_action':
                    addAgentAction(data);
                    break;
                case 'system_event':
                    addSystemEvent(data);
                    break;
                case 'log':
                    addLog(data);
                    break;
                case 'metrics_update':
                    updateMetrics(data.metrics);
                    break;
                case 'history':
                    loadHistory(data.data);
                    break;
            }
        }

        function addThought(data) {
            const container = document.getElementById('thoughtStream');
            if (container.children.length === 1 && container.children[0].textContent.includes('Waiting')) {
                container.innerHTML = '';
            }

            const item = document.createElement('div');
            item.className = 'thought-item';
            item.innerHTML = `
                <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
                <div><strong>💭 Thinking:</strong> ${data.thought}</div>
                ${data.context ? `<div style="margin-top: 5px; color: #888; font-size: 12px;">${JSON.stringify(data.context)}</div>` : ''}
            `;
            container.insertBefore(item, container.firstChild);

            // Keep max 50 items
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        function addDecision(data) {
            const container = document.getElementById('eventStream');
            if (container.children.length === 1 && container.children[0].textContent.includes('Waiting')) {
                container.innerHTML = '';
            }

            const item = document.createElement('div');
            item.className = 'event-item decision';
            item.innerHTML = `
                <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
                <div><strong>🎯 Decision:</strong> ${data.decision}</div>
                <div style="margin-top: 5px; color: #aaa;">${data.reasoning}</div>
            `;
            container.insertBefore(item, container.firstChild);

            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        function addAgentAction(data) {
            const container = document.getElementById('eventStream');
            if (container.children.length === 1 && container.children[0].textContent.includes('Waiting')) {
                container.innerHTML = '';
            }

            const item = document.createElement('div');
            item.className = 'event-item';
            item.innerHTML = `
                <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
                <div><strong>🤖 ${data.agent_name}:</strong> ${data.action}</div>
            `;
            container.insertBefore(item, container.firstChild);

            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        function addSystemEvent(data) {
            const container = document.getElementById('eventStream');
            if (container.children.length === 1 && container.children[0].textContent.includes('Waiting')) {
                container.innerHTML = '';
            }

            const item = document.createElement('div');
            item.className = 'event-item';
            item.innerHTML = `
                <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
                <div><strong>⚡ ${data.event_type}:</strong> ${data.message}</div>
            `;
            container.insertBefore(item, container.firstChild);

            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        function addLog(data) {
            const container = document.getElementById('logStream');
            if (container.children.length === 1 && container.children[0].textContent.includes('Waiting')) {
                container.innerHTML = '';
            }

            const item = document.createElement('div');
            item.className = `log-item ${data.level}`;
            item.innerHTML = `
                <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()} [${data.logger}]</div>
                <div>${data.message}</div>
            `;
            container.insertBefore(item, container.firstChild);

            while (container.children.length > 100) {
                container.removeChild(container.lastChild);
            }
        }

        function loadHistory(data) {
            if (data.thoughts) {
                data.thoughts.forEach(thought => addThought(thought));
            }
            if (data.events) {
                data.events.forEach(event => {
                    if (event.type === 'decision') {
                        addDecision(event);
                    } else if (event.type === 'agent_action') {
                        addAgentAction(event);
                    } else if (event.type === 'system_event') {
                        addSystemEvent(event);
                    }
                });
            }
        }

        async function loadInitialData() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateStatus(data);
            } catch (error) {
                console.error('Error loading initial data:', error);
            }

            loadAgents();
        }

        function updateStatus(data) {
            document.getElementById('capital').textContent = `$${data.capital.toFixed(2)}`;
            document.getElementById('roi').textContent = `${data.roi_percent.toFixed(1)}%`;
            document.getElementById('activeAgents').textContent = data.active_agents;
            document.getElementById('opportunities').textContent = data.total_opportunities;
            document.getElementById('totalProfit').textContent = `$${data.profit.toFixed(2)}`;
        }

        function updateMetrics(metrics) {
            if (metrics.capital) {
                document.getElementById('capital').textContent = `$${metrics.capital.toFixed(2)}`;
            }
            if (metrics.roi_percent) {
                document.getElementById('roi').textContent = `${metrics.roi_percent.toFixed(1)}%`;
            }
        }

        async function loadAgents() {
            try {
                const response = await fetch('/api/agents/live');
                const data = await response.json();
                displayAgents(data.agents);
            } catch (error) {
                console.error('Error loading agents:', error);
            }
        }

        function displayAgents(agents) {
            const container = document.getElementById('agentGrid');

            if (agents.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">No agents yet...</div>';
                return;
            }

            container.innerHTML = agents.map(agent => `
                <div class="agent-card ${agent.status}">
                    <div class="agent-header">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-status ${agent.status}">${agent.status.toUpperCase()}</div>
                    </div>
                    <div style="color: #888; font-size: 13px; margin-bottom: 10px;">${agent.role}</div>
                    <div class="agent-stats">
                        <span>📊 ${agent.tasks_total} tasks</span>
                        <span>✅ ${agent.tasks_completed} done</span>
                        <span>📈 ${agent.success_rate.toFixed(0)}% success</span>
                    </div>
                </div>
            `).join('');
        }

        // Refresh agents periodically
        setInterval(loadAgents, 5000);

        // Refresh status periodically
        setInterval(loadInitialData, 10000);

        // Connect on load
        connect();
    </script>
</body>
</html>
"""
