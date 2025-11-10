# 🚀 AI Entrepreneur Agent System V2 - Enhanced Edition

**A truly self-sustaining, self-learning, self-fixing, and self-improving AI entrepreneur that runs real businesses.**

## 🎯 What's New in V2

This is not a simulation - this is a **real business system** with:

### 🧠 **Self-Learning**
- Analyzes past opportunities to learn success patterns
- Studies agent performance to optimize team composition
- Learns from task execution to improve processes
- Builds a knowledge base that grows over time
- Makes data-driven decisions based on historical performance

### 🔨 **Self-Fixing**
- Automatically detects and fixes errors
- Maintains a library of error patterns and solutions
- Uses AI to generate fixes for unknown errors
- Implements retry strategies, backoff mechanisms
- Recovers from failures without human intervention

### 🔧 **Self-Improvement**
- Continuously optimizes strategies
- Generates better code over time
- Improves decision-making algorithms
- Creates new agent types when needed
- Evolves to become more profitable

### 💼 **Real Business Execution**
- **Services**: Generates actual API code, documentation, deployments
- **Products**: Creates MVPs with real functionality
- **Content**: Produces marketable content
- **Automation**: Builds working automation scripts
- **Data**: Develops data processing pipelines

### 🤖 **Dynamic Agent Management**
- Automatically creates agents when needed
- **Evaluates performance** and terminates useless agents
- Tracks metrics: success rate, tasks completed, efficiency
- Removes agents that are idle, underperforming, or failing
- Optimizes team composition based on performance data

### 📁 **Project Management**
- **Workspace Manager**: Each venture gets its own folder structure
  ```
  venture_1_api_service/
  ├── code/          # Generated code
  ├── docs/          # Documentation
  ├── data/          # Data files
  ├── config/        # Configuration
  ├── output/        # Results
  ├── logs/          # Logs
  ├── assets/        # Media
  ├── tests/         # Tests
  ├── deploy/        # Deployment
  └── research/      # Analysis
  ```

- **Kanban Boards**: Visual project management for each venture
  - Columns: Backlog, Todo, In Progress, Review, Testing, Done, Blocked
  - Real-time task tracking
  - Progress visualization
  - WIP limits
  - Syncs with database tasks

### 📊 **Intelligence Systems**

#### Self-Learning Engine
- `analyze_past_opportunities()` - Learns what works
- `learn_from_agent_performance()` - Optimizes team
- `learn_from_task_execution()` - Improves processes
- `should_pursue_opportunity()` - AI-driven decisions
- Exports/imports knowledge base for continuity

#### Self-Fixing Engine
- Detects patterns in errors
- Applies known fixes automatically
- Uses LLM to generate fixes for new errors
- Tracks fix success rates
- Builds error resolution knowledge

#### Self-Improvement Engine
- Analyzes system performance
- Generates optimization strategies
- Applies optimizations automatically
- Creates new agent types via code generation
- Optimizes master strategy continuously

## 🏗️ Enhanced Architecture

```
MasterEntrepreneurAgentV2
├── Self-Learning Engine
│   ├── Opportunity Pattern Learning
│   ├── Agent Performance Learning
│   └── Task Execution Learning
│
├── Self-Fixing Engine
│   ├── Error Pattern Detection
│   ├── Automatic Fix Application
│   └── LLM-Generated Solutions
│
├── Self-Improvement Engine
│   ├── Performance Analysis
│   ├── Strategy Optimization
│   └── Code Generation
│
├── Agent Management
│   ├── Agent Factory (Create)
│   ├── Agent Evaluator (Monitor & Delete)
│   └── Dynamic Team Optimization
│
├── Business Execution
│   ├── Real Code Generation
│   ├── Service Development
│   ├── Product Creation
│   └── Content Production
│
└── Project Management
    ├── Workspace Manager (Folders/Files)
    ├── Kanban Boards (Visual Tracking)
    └── Task Manager (Execution)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull gpt-oss:latest

# Setup system
./setup.sh
```

### 2. Run Enhanced System

```bash
# Start Ollama
ollama serve &

# Activate environment
source venv/bin/activate

# Run V2 with all features
python main_v2.py run

# OR run with dashboard
python main_v2.py both
```

## 💡 How It Works

### Business Cycle (Enhanced)

1. **Learning Phase**
   - Analyzes all past opportunities
   - Studies agent performance patterns
   - Reviews task execution history
   - Builds knowledge base

2. **Agent Management** (Every 3 cycles)
   - Evaluates all active agents
   - Measures: success rate, tasks completed, efficiency, idle time
   - **Terminates** underperforming agents
   - Optimizes team composition

3. **Self-Fixing** (Continuous)
   - Monitors for failed tasks
   - Detects error patterns
   - Applies fixes automatically
   - Logs successful fixes

4. **Self-Improvement** (Every 5 cycles)
   - Analyzes system performance
   - Generates optimization strategy
   - Applies optimizations
   - Updates decision algorithms

5. **Opportunity Scanning**
   - Identifies business opportunities
   - Uses learned patterns to evaluate
   - AI decides: pursue or reject
   - Confidence-based selection

6. **Real Execution**
   - Creates workspace with full folder structure
   - Sets up Kanban board
   - Generates actual code/content/services
   - Saves all artifacts to workspace
   - Tracks progress on Kanban

7. **Financial Update**
   - Records actual revenue/costs
   - Updates capital
   - Saves to database

8. **Performance Review**
   - Calculates ROI
   - Reviews metrics
   - Decides whether to continue

## 📈 Agent Lifecycle

### Creation
```python
# Automatically created when needed
agent = agent_factory.create_agent("researcher", name="Market Analyst")
```

### Performance Tracking
- Tasks completed
- Success rate
- Average task time
- Tasks per hour
- Idle time

### Evaluation Criteria
- **Success Rate**: Must be > 40%
- **Task Count**: Need minimum 3 tasks to evaluate
- **Idle Time**: Max 60 minutes without tasks
- **Productivity**: Minimum 0.5 tasks/hour

### Automatic Termination
Agents are terminated if:
- Success rate < 40%
- Idle for > 60 minutes
- Failure ratio > 70%
- Very low productivity

```
🤖 AGENT MANAGEMENT: Evaluating agent performance...
  Agent 5 (Data Analyst): KEPT - Good performance: 85.0% success rate
  Agent 7 (Developer): TERMINATED - Low success rate: 25.0% < 40.0%
  Agent 9 (Researcher): TERMINATED - Idle for 75 minutes
Agents evaluated: 8, terminated: 2
```

## 🗂️ Workspace Management

Each venture gets its own isolated workspace:

### Automatic Structure
```
venture_1_ai_api_service/
├── code/
│   ├── service.py          # Generated service code
│   └── automation_1.py     # Automation scripts
├── docs/
│   ├── API.md              # API documentation
│   └── business_plan.md    # Business plan
├── config/
│   └── requirements.txt    # Dependencies
├── output/
│   └── content.md          # Generated content
├── logs/
│   └── venture.log         # Venture-specific logs
├── workspace.json          # Metadata
└── README.md               # Workspace readme
```

### Workspace Operations
```python
# Create workspace
workspace = workspace_manager.create_workspace(
    venture_id=1,
    venture_name="AI API Service"
)

# Write files
workspace_manager.write_file(workspace, "code/service.py", code)

# Read files
content = workspace_manager.read_file(workspace, "docs/API.md")

# List files
files = workspace_manager.list_files(workspace, folder="code")

# Archive when done
archive = workspace_manager.archive_workspace(venture_id=1)
```

## 📋 Kanban Board System

### Visual Project Management
```
┌─────────────┬──────────┬─────────────┬────────┬─────────┬──────┬─────────┐
│   Backlog   │   Todo   │ In Progress │ Review │ Testing │ Done │ Blocked │
├─────────────┼──────────┼─────────────┼────────┼─────────┼──────┼─────────┤
│  Task 1     │  Task 2  │   Task 3    │ Task 4 │         │Task 5│         │
│  Task 6     │          │             │        │         │Task 7│         │
└─────────────┴──────────┴─────────────┴────────┴─────────┴──────┴─────────┘
```

### Features
- Drag cards between columns
- Priority ordering
- Assignee tracking
- Tags and labels
- Automatic task sync
- Progress statistics
- WIP limits
- Export to JSON

### Usage
```python
# Create board
kanban = KanbanBoard(db, "board_venture_1", venture_id=1)

# Add card
card = kanban.add_card(
    title="Build API endpoint",
    description="Create POST /api/data endpoint",
    column=KanbanColumn.TODO,
    priority=8,
    assignee="Developer Agent",
    tags=["api", "backend"]
)

# Move card
kanban.move_card(card.card_id, KanbanColumn.IN_PROGRESS)

# Get board state
state = kanban.get_board_state()

# Export
kanban.export_board("venture_1/kanban_board.json")
```

## 🧠 Self-Learning Examples

### Learning from Opportunities
```python
# Analyze past performance
analysis = learning_engine.analyze_past_opportunities()
# Returns: success patterns, failure patterns, insights

# Make AI-driven decision
decision = learning_engine.should_pursue_opportunity({
    "title": "SaaS Dashboard",
    "category": "product",
    "potential_revenue": 5000,
    "estimated_cost": 500,
    "risk_score": 0.3
})
# Returns: decision (YES/NO), confidence, reasons
```

### Learning from Agents
```python
# Learn which agent types work best
performance = learning_engine.learn_from_agent_performance()
# Returns: best_agent_types, worst_agent_types, recommendations
```

## 🔨 Self-Fixing Examples

### Automatic Error Recovery
```python
# Detect and fix failed task
result = fixing_engine.detect_and_fix_task_error(task_id=123)
# Automatically:
# - Detects error pattern
# - Applies known fix
# - Or generates new fix with AI
# - Retries task
```

### Error Patterns
The system learns to fix:
- Database connection errors → Reconnect automatically
- Timeout errors → Increase timeout and retry
- API errors → Exponential backoff
- Resource exhaustion → Cleanup and retry
- Unknown errors → AI generates fix

## 🔧 Self-Improvement Examples

### Continuous Optimization
```python
# Run full improvement cycle
result = improvement_engine.continuous_improvement_cycle()
# Automatically:
# 1. Analyzes performance
# 2. Generates optimization strategy
# 3. Applies top optimizations
# 4. Updates master strategy
```

### Code Generation
```python
# Generate new agent type
code = improvement_engine.create_new_agent_type({
    "name": "SEO Specialist",
    "capabilities": ["keyword research", "content optimization"],
    "role": "SEO expert"
})
# Generates complete Python class, saves to file
```

## 📊 Enhanced Metrics

### System Metrics
- Capital and ROI
- Opportunity success rate
- Agent performance scores
- Task completion rates
- Workspace count
- Code artifacts generated
- Self-fixes applied
- Optimizations completed

### Agent Metrics (Per Agent)
- Total tasks
- Completed tasks
- Failed tasks
- Success rate
- Average task time
- Tasks per hour
- Uptime
- Termination reason (if terminated)

### Opportunity Metrics
- Revenue (projected vs actual)
- Costs (projected vs actual)
- Profit margin
- Risk score
- Confidence score
- Execution time
- Files generated

## 🎯 Configuration

### Enhanced Settings (.env)

```bash
# Business Parameters
INITIAL_CAPITAL=1000
RISK_TOLERANCE=0.7
MIN_PROFIT_MARGIN=0.15

# Agent Management
MAX_CONCURRENT_AGENTS=10
AGENT_MIN_SUCCESS_RATE=0.4      # 40% minimum
AGENT_MAX_IDLE_MINUTES=60
AGENT_MIN_TASKS_TO_EVAL=3

# Self-Improvement
IMPROVEMENT_CYCLE_INTERVAL=5     # Every 5 cycles
AGENT_EVAL_INTERVAL=3            # Every 3 cycles

# Workspaces
WORKSPACE_BASE_PATH=agent_data/workspaces
ARCHIVE_OLD_WORKSPACES=true
```

## 🔥 Real Business Execution

### Service Business
Generates:
- Complete FastAPI service code
- API documentation
- Requirements.txt
- Deployment configuration
- Test files

### Product Business
Creates:
- Product specification
- MVP code
- User documentation
- Feature roadmap

### Content Business
Produces:
- High-quality content
- SEO optimization
- Content strategy
- Distribution plan

### Automation Business
Builds:
- Working automation scripts
- Scheduling configuration
- Error handling
- Logging

### Data Business
Develops:
- Data pipelines
- ETL processes
- Data analysis scripts
- Visualization code

## 📈 Dashboard Enhancements

New API endpoints:

```bash
# Workspaces
GET /api/workspaces              # List all workspaces
GET /api/workspaces/{id}         # Get workspace details
GET /api/workspaces/{id}/files   # List files in workspace

# Kanban boards
GET /api/kanban/{venture_id}     # Get Kanban board state
POST /api/kanban/{venture_id}/cards  # Add card
PUT /api/kanban/{venture_id}/cards/{id}  # Move card

# Intelligence
GET /api/learning/insights       # Get learned insights
GET /api/learning/recommendations  # Get recommendations
GET /api/improvements/history    # Improvement history
GET /api/fixes/history           # Fix history

# Agents
GET /api/agents/performance      # Agent performance stats
GET /api/agents/{id}/metrics     # Detailed agent metrics
DELETE /api/agents/{id}          # Terminate agent
```

## 🎓 Example Output

```
============================================================
ENHANCED MASTER ENTREPRENEUR AGENT V2 STARTING
============================================================

🧠 LEARNING PHASE: Analyzing past performance...
  Identified 5 opportunities
  Learning from 3 successful patterns
  Insights: Services with <$500 cost have 80% success rate

============================================================
BUSINESS CYCLE 1
Current Capital: $1000.00
============================================================

📈 Analyzing current state...
  Active agents: 2, Total: 4
  Active opportunities: 1
  Workspaces: 3

📊 Evaluating 5 opportunities with learned patterns...
  ✓ AI Content API: 85.0% confidence
  ✓ Automation Service: 72.0% confidence
  ✗ Complex SaaS: Rejected - High risk pattern detected
  ✗ E-commerce Store: Rejected - Low success probability

💼 EXECUTING: AI Content API
  Creating workspace: venture_5_ai_content_api/
  Setting up Kanban board...
  Generating service code...
  Creating API documentation...
  Saving artifacts...

✅ SUCCESS: Revenue: $850.00, Cost: $200.00, Profit: +$650.00
💰 New Capital: $1650.00

============================================================
BUSINESS CYCLE 3
============================================================

🤖 AGENT MANAGEMENT: Evaluating agent performance...
  Agent 2 (Researcher): KEPT - Good performance: 90.0% success rate
  Agent 4 (Developer): TERMINATED - Low success rate: 30.0%
  Agent 6 (Analyst): TERMINATED - Idle for 75 minutes
Agents evaluated: 5, terminated: 2

🔨 SELF-FIXING: Attempting to fix 2 failed tasks...
  ✓ Fixed task 12: Timeout error - increased timeout
  ✓ Fixed task 18: API error - applied exponential backoff

============================================================
BUSINESS CYCLE 5
============================================================

🔧 SELF-IMPROVEMENT: Running optimization cycle...
  Analyzing performance...
  Generating optimization strategy...
  Applying 3 optimizations...
    ✓ Optimized opportunity selection criteria
    ✓ Updated agent creation strategy
    ✓ Improved capital allocation
Optimizations applied: 3

============================================================
EXECUTION COMPLETE
============================================================

✓ Cycles Completed: 15
✓ Final Capital: $3,250.00
✓ Total Profit: +$2,250.00
✓ ROI: 225.0%
✓ Workspaces Created: 8
✓ Agents Terminated: 5 (performance-based)
✓ Errors Fixed: 12
✓ Optimizations Applied: 6

🎓 FINAL LEARNING: Generating comprehensive insights...
  [Detailed AI-generated report with learned patterns]
```

## 🔒 Safety & Ethics

- All operations are logged
- Workspaces are isolated
- No destructive operations without confirmation
- Agent limits prevent resource exhaustion
- Human oversight recommended for deployment
- Built for ethical, legal business only

## 🤝 Contributing

Areas for enhancement:
- Real payment integrations
- Cloud deployment automation
- More agent types
- Advanced learning algorithms
- Integration with real APIs
- Better ROI tracking

## 📝 License

MIT License - See LICENSE file

## ⚠️ Disclaimer

This system generates real code and artifacts. While it aims to create profitable businesses, success depends on:
- Market conditions
- Execution quality
- Domain expertise
- Human oversight for critical decisions
- Legal and regulatory compliance

Use responsibly and validate all generated outputs.

---

**Built with 🧠 by autonomous AI - Now with real self-learning, self-fixing, and self-improvement capabilities!**

