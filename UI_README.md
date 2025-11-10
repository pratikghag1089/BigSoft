

# 🌐 Live UI Dashboard - See AI Think in Real-Time!

**Full transparency into every thought, decision, and action the AI makes.**

## 🎯 What You Get

A beautiful, real-time web interface that shows:

### 🧠 **AI Thought Stream**
- Every reasoning process the AI goes through
- Context and data for each thought
- Live updates as thoughts happen
- Full transparency into decision-making

### 🎯 **Decision & Action Stream**
- Every decision the AI makes
- Reasoning behind each decision
- Agent actions in real-time
- System events

### 🤖 **Live Agent Monitor**
- All active agents displayed
- Real-time status updates (Running, Created, Terminated)
- Performance metrics per agent
- Task completion rates
- Success rates

### 📋 **Live System Logs**
- All system logs in real-time
- Color-coded by severity (INFO, WARNING, ERROR)
- Timestamped entries
- Filterable by logger

### 📊 **Key Metrics**
- Current capital
- Total profit/loss
- ROI percentage
- Active agents count
- Opportunities tracked
- Success rates

## 🚀 Quick Start

### 1. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Ollama

```bash
ollama serve
```

### 3. Run with UI

```bash
# This starts BOTH the UI dashboard AND the AI agent
python main_ui.py

# Or explicitly:
python main_ui.py both
```

### 4. Open Your Browser

```
http://localhost:8000
```

You'll immediately see:
- 🟢 **Connected** status indicator
- Live thought stream starting
- Agent activity as they're created
- All decisions and reasoning
- Real-time logs

## 🎨 UI Features

### Real-Time Updates via WebSockets

The UI uses WebSockets for **instant** updates with **zero** page refresh:

- **Thoughts** appear instantly as AI thinks
- **Decisions** show up with reasoning
- **Agent actions** broadcast immediately
- **Logs** stream in real-time
- **Metrics** update live

### Beautiful Dark Theme

- Easy on the eyes for long monitoring sessions
- Color-coded information:
  - 🟣 Purple: Thoughts
  - 🟢 Green: Actions
  - 🟠 Orange: Decisions
  - 🔵 Blue: Logs
  - 🔴 Red: Errors

### Automatic Scrolling

- New items appear at the top
- Old items fade out
- No manual scrolling needed
- Focus on latest activity

### Connection Status

Top-right indicator shows:
- 🟢 **Connected**: Receiving live updates
- 🔴 **Disconnected**: Lost connection
- **Automatic reconnection** attempts

## 📡 How It Works

### Architecture

```
┌─────────────────┐
│  Your Browser   │
│   (Web UI)      │
└────────┬────────┘
         │ WebSocket
         │ (Real-time)
         ▼
┌─────────────────┐
│   FastAPI       │
│   Server        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Observer    │◄──────┐
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│ Master Agent    │       │
│  + Sub-Agents   │───────┘
└─────────────────┘
    Broadcasts all
    thoughts & actions
```

### What Gets Broadcast

**1. Thoughts** (`broadcast_thought`)
```python
observer.broadcast_thought_sync(
    "Analyzing opportunity: AI Content API",
    {
        "revenue": 5000,
        "cost": 500,
        "risk": 0.3
    }
)
```

**2. Decisions** (`broadcast_decision`)
```python
observer.broadcast_decision_sync(
    "PURSUE opportunity",
    "High profit margin (90%) and low risk (0.3)",
    {"opportunity_id": 5, "confidence": 0.85}
)
```

**3. Agent Actions** (`broadcast_agent_action`)
```python
observer.broadcast_agent_action_sync(
    agent_id=3,
    agent_name="Researcher",
    action="Completed market research",
    {"findings": "High demand for API services"}
)
```

**4. System Events** (`broadcast_system_event`)
```python
observer.broadcast_system_event_sync(
    "agent_terminated",
    "Agent #7 (Developer) terminated due to low performance",
    {"agent_id": 7, "reason": "success_rate_below_threshold"}
)
```

**5. Logs** (automatic)
All logging output is automatically broadcast to UI

## 🎮 Usage Examples

### See AI Make Decisions

Watch in real-time as the AI:

1. **Scans for opportunities**
   ```
   🧠 Thinking: Scanning market for profitable opportunities...
   🧠 Thinking: Found 5 potential opportunities
   🧠 Thinking: Evaluating opportunity #1: AI Content API
   ```

2. **Evaluates with learned patterns**
   ```
   🧠 Thinking: Comparing against historical success patterns
   🧠 Thinking: Similar opportunities had 80% success rate
   🎯 Decision: PURSUE this opportunity
       Reasoning: Matches successful pattern, low risk, high margin
   ```

3. **Creates agents**
   ```
   🤖 Master Agent: Creating specialized agents for execution
   🤖 Researcher: Starting market research
   🤖 Developer: Beginning code generation
   ```

4. **Executes and reports**
   ```
   ⚡ workspace_created: Created venture_5_ai_content_api/
   ⚡ code_generated: Generated service.py (250 lines)
   🎯 Decision: Opportunity execution SUCCESSFUL
       Reasoning: All artifacts generated, tests passed
   ```

### Monitor Agent Performance

See agents get evaluated and terminated:

```
🧠 Thinking: Evaluating agent performance (Cycle 3)
🤖 Agent #2 (Researcher): KEPT - 90% success rate ✓
🤖 Agent #4 (Developer): TERMINATED - 30% success rate ✗
⚡ agent_terminated: Agent removed due to underperformance
```

### Watch Self-Fixing in Action

See the AI fix its own errors:

```
🔴 ERROR: Task #12 failed - Timeout connecting to API
🧠 Thinking: Detected timeout error pattern
🎯 Decision: Apply timeout fix - increase timeout and retry
⚡ error_fixed: Task #12 retrying with 600s timeout
✅ Success: Task #12 completed successfully after fix
```

### Observe Self-Improvement

Watch it optimize itself:

```
🧠 Thinking: Running self-improvement cycle (Cycle 5)
🧠 Thinking: Analyzing past 10 opportunities...
🧠 Thinking: Success rate for services: 80%, products: 40%
🎯 Decision: Optimize strategy - prefer service opportunities
⚡ strategy_updated: Updated opportunity selection criteria
```

## 📊 API Endpoints

### REST APIs

```bash
# System status
GET /api/status

# Live agent data
GET /api/agents/live

# Thought stream history
GET /api/thoughts/stream

# Event stream history
GET /api/events/stream

# Live opportunities
GET /api/opportunities/live

# Workspace files
GET /api/workspaces/list
GET /api/workspaces/{id}/files
GET /api/workspaces/{id}/file?path=code/service.py

# Kanban board
GET /api/kanban/{venture_id}

# Live metrics
GET /api/metrics/live

# Health check
GET /health
```

### WebSocket

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Receive messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'thought':
            console.log('AI Thought:', data.thought);
            break;
        case 'decision':
            console.log('AI Decision:', data.decision);
            console.log('Reasoning:', data.reasoning);
            break;
        case 'agent_action':
            console.log('Agent Action:', data.action);
            break;
        case 'log':
            console.log('Log:', data.message);
            break;
    }
};
```

## 🎨 Customization

### Change Colors

Edit the `<style>` section in `app_enhanced.py`:

```css
.thought-item {
    border-left-color: #YOUR_COLOR;
}
```

### Add New Panels

Add new sections to the dashboard:

```html
<div class="panel">
    <div class="panel-title">🆕 Your Custom Panel</div>
    <div id="customContent">...</div>
</div>
```

### Custom WebSocket Messages

Send custom messages from your code:

```python
from src.api.websocket_manager import manager

await manager.broadcast({
    "type": "custom_event",
    "data": {"your": "data"}
})
```

## 🔧 Advanced Features

### Historical Replay

The UI maintains history:
- Last 50 thoughts
- Last 50 events
- Last 100 logs

New connections receive history immediately.

### Multiple Clients

Multiple browsers can connect simultaneously:
- Each gets independent view
- All receive same updates
- No performance impact

### Automatic Reconnection

If connection drops:
- UI shows disconnected status
- Attempts reconnection every 3 seconds
- Resumes from where it left off

## 🎯 What You'll See

### Startup Sequence

```
🟢 Connected
🧠 Thinking: System initialized. Beginning autonomous operations...
⚡ system_start: AI Entrepreneur System starting with $1000.00 capital
🧠 Thinking: Loading past learning data...
🧠 Thinking: Analyzing 10 historical opportunities...
🧠 Thinking: Identified success patterns: Services have 80% success rate
```

### Business Cycle

```
🧠 Thinking: Business Cycle 1 starting
🧠 Thinking: Current capital: $1000.00
🧠 Thinking: Scanning for opportunities...
🧠 Thinking: Found 5 opportunities
🎯 Decision: Selected "AI Content API" - 85% confidence
⚡ opportunity_selected: Executing AI Content API
🤖 Master Agent: Creating workspace venture_5_ai_content_api
🤖 Master Agent: Generating service code...
✅ Success: Service code generated (250 lines)
⚡ workspace_updated: Added 5 files to workspace
🎯 Decision: Opportunity execution SUCCESSFUL - Profit: +$650
💰 Capital updated: $1650.00
```

### Agent Management

```
🧠 Thinking: Agent evaluation cycle (Cycle 3)
🤖 Agent #2 (Researcher): Success rate 90% - KEPT
🤖 Agent #4 (Developer): Success rate 30% - TERMINATED
⚡ agent_terminated: Removed underperforming agent
🧠 Thinking: Active agents: 3, Terminated: 2
```

## 📱 Mobile Support

The UI is responsive and works on:
- ✅ Desktop browsers
- ✅ Tablets
- ✅ Mobile phones (landscape recommended)

## 🔒 Security Note

The UI is for **local development and monitoring**.

For production:
- Add authentication
- Use WSS (secure WebSocket)
- Restrict CORS origins
- Add rate limiting

## 🎓 Learning from the UI

The UI is a great learning tool:

**Understand AI Decision-Making**
- See how it weighs options
- Observe pattern recognition
- Watch learning in action

**Monitor Performance**
- Track which strategies work
- See agent effectiveness
- Identify bottlenecks

**Debug Issues**
- Watch error patterns
- See fix attempts
- Track success/failure

**Study Self-Improvement**
- Observe optimization cycles
- See strategy evolution
- Watch performance gains

## 🚀 Pro Tips

1. **Open UI before starting agent** - Don't miss initial thoughts
2. **Use multiple browser tabs** - Different views simultaneously
3. **Check mobile** - Monitor from anywhere
4. **Save screenshots** - Document interesting decisions
5. **Use browser console** - See raw WebSocket messages

## 🎉 Enjoy Full Transparency!

You now have **complete visibility** into your AI entrepreneur's mind.

Watch it:
- 🧠 Think through problems
- 🎯 Make strategic decisions
- 🤖 Manage its team
- 🔨 Fix its own errors
- 🔧 Improve itself
- 💰 Build profitable businesses

**All in real-time, with full transparency!**

---

**Questions? Issues?**

Check the logs in the UI - they often explain what's happening!

