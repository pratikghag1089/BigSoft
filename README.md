# AI Entrepreneur Agent System

A self-sustaining AI system that acts as an entrepreneur, creating and managing AI agents to build profitable businesses.

## 🎯 Overview

This system uses a local LLM (via Ollama) to create an autonomous AI entrepreneur that:

- **Identifies business opportunities** using AI-powered market analysis
- **Creates and manages specialized AI agents** (researchers, analysts, developers, marketers)
- **Makes strategic business decisions** based on profitability and risk
- **Tracks financial performance** and works towards profitability
- **Operates autonomously** with minimal human intervention

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Master Entrepreneur Agent                   │
│         (Strategic Decision Making & Orchestration)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────────┐
                              │                             │
                              ▼                             ▼
                    ┌──────────────────┐        ┌──────────────────┐
                    │  Agent Factory   │        │ Opportunity       │
                    │  (Create/Delete  │        │ Engine            │
                    │   Sub-Agents)    │        │ (Identify/Eval)   │
                    └──────────────────┘        └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Research   │  │   Analyst    │  │  Developer   │
    │    Agent     │  │    Agent     │  │    Agent     │
    └──────────────┘  └──────────────┘  └──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Task Manager   │
                    │   & Execution    │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    Database      │
                    │  (State/Metrics) │
                    └──────────────────┘
```

## 🚀 Features

### Core Capabilities

- **Autonomous Operation**: Runs independently, making business decisions
- **Multi-Agent System**: Creates specialized agents for different tasks
- **Opportunity Identification**: AI-powered business opportunity scanning
- **Risk Management**: Evaluates opportunities based on risk and profitability
- **Financial Tracking**: Monitors capital, profit/loss, and ROI
- **Task Management**: Distributes work across agents
- **Web Dashboard**: Real-time monitoring interface

### Agent Types

1. **Master Entrepreneur Agent**
   - High-level strategic decision making
   - Resource allocation
   - Opportunity evaluation
   - Agent creation and management

2. **Research Agent**
   - Market research
   - Trend analysis
   - Competitive intelligence

3. **Analyst Agent**
   - Data analysis
   - Financial modeling
   - ROI evaluation

4. **Developer Agent**
   - Software development
   - Automation scripts
   - API integration

5. **Marketing Agent**
   - Marketing strategy
   - Content creation
   - Campaign optimization

## 📋 Prerequisites

- **Ubuntu** (or other Linux distribution)
- **Python 3.8+**
- **Ollama** (for local LLM)
- **gpt-oss:latest model** (or your preferred model)

## 🔧 Installation

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull the Model

```bash
ollama pull gpt-oss:latest
```

### 3. Clone and Setup

```bash
# Clone the repository
cd BigSoft

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 4. Configure

Edit `.env` file to customize settings:

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:latest

# Business Parameters
INITIAL_CAPITAL=1000
RISK_TOLERANCE=0.7
MIN_PROFIT_MARGIN=0.15
```

## 🎮 Usage

### Start Ollama (if not already running)

```bash
ollama serve
```

### Run the Entrepreneur Agent

```bash
# Activate virtual environment
source venv/bin/activate

# Run the agent
python main.py run
```

### Run the Monitoring Dashboard

```bash
python main.py dashboard
```

Then open http://localhost:8000 in your browser.

### Run Both (Agent + Dashboard)

```bash
python main.py both
```

## 📊 Monitoring

The system provides a RESTful API and web dashboard for monitoring:

### API Endpoints

- `GET /api/status` - System status
- `GET /api/agents` - List all agents
- `GET /api/tasks` - List all tasks
- `GET /api/opportunities` - List opportunities
- `GET /api/metrics` - Financial and performance metrics
- `GET /api/dashboard` - Comprehensive dashboard data

### Example Usage

```bash
# Get system status
curl http://localhost:8000/api/status

# Get all opportunities
curl http://localhost:8000/api/opportunities

# Get dashboard data
curl http://localhost:8000/api/dashboard
```

## 🎯 How It Works

### Business Cycle

1. **Analysis Phase**
   - Evaluate current capital and resources
   - Review active agents and opportunities
   - Assess overall performance

2. **Opportunity Scanning**
   - Use AI to identify potential business opportunities
   - Consider market trends, automation potential, and profitability

3. **Evaluation & Selection**
   - Score opportunities based on:
     - Revenue potential
     - Cost efficiency
     - Risk level
     - Confidence score
     - Profit margin
   - Select the best opportunity within available capital

4. **Execution**
   - Create specialized agents as needed
   - Allocate tasks
   - Execute the business opportunity
   - Track progress and results

5. **Financial Update**
   - Update capital based on profit/loss
   - Record metrics
   - Evaluate performance

6. **Decision Loop**
   - Decide whether to continue or stop
   - Repeat cycle if conditions are met

### Success Criteria

The system aims to:
- Achieve positive ROI
- Double initial capital (100% ROI target)
- Maintain risk-adjusted profitability
- Avoid bankruptcy

## 🧪 Development

### Project Structure

```
BigSoft/
├── src/
│   ├── core/           # Core components (config, Ollama client)
│   ├── agents/         # Agent implementations
│   ├── business/       # Business logic (opportunities, tasks)
│   ├── database/       # Database models and management
│   ├── api/            # FastAPI dashboard
│   └── utils/          # Utilities (logging, etc.)
├── logs/               # Log files
├── agent_data/         # Agent persistent data
├── main.py             # Main entry point
├── requirements.txt    # Python dependencies
├── setup.sh            # Setup script
└── README.md           # This file
```

### Adding New Agent Types

1. Create a new agent class in `src/agents/specialized_agents.py`:

```python
class MyCustomAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            agent_type="custom",
            role="Custom Role",
            capabilities=["capability1", "capability2"],
            **kwargs
        )

    def _execute_task_impl(self, task):
        # Implementation
        pass

    def run(self):
        # Implementation
        pass
```

2. Register it in `AgentFactory`:

```python
AgentFactory.register_agent_type("custom", MyCustomAgent)
```

## 🔐 Security Considerations

- The system operates autonomously - monitor it carefully
- Set reasonable capital limits in configuration
- Review opportunities before execution (in production)
- Use API authentication for the dashboard
- Keep logs for audit trails

## ⚙️ Configuration Options

Key configuration parameters in `.env`:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `INITIAL_CAPITAL` | Starting capital | 1000 |
| `RISK_TOLERANCE` | Risk acceptance (0-1) | 0.7 |
| `MIN_PROFIT_MARGIN` | Minimum profit margin | 0.15 |
| `MAX_CONCURRENT_AGENTS` | Max active agents | 10 |
| `OPPORTUNITY_SCAN_INTERVAL_MINUTES` | Scan frequency | 30 |

## 🐛 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### Database Issues

```bash
# Reset database
rm entrepreneur_agent.db
python main.py run
```

### Model Not Found

```bash
# Pull the model
ollama pull gpt-oss:latest

# List available models
ollama list
```

## 📈 Performance Tuning

- **Adjust temperature**: Lower for more conservative decisions (0.3-0.5)
- **Modify risk tolerance**: Higher for more aggressive strategies
- **Increase capital**: More capital = more opportunities
- **Fine-tune profit margins**: Balance between selectivity and action

## 🤝 Contributing

This is an experimental system. Contributions are welcome!

Areas for improvement:
- More sophisticated opportunity evaluation
- Integration with real APIs and services
- Advanced multi-agent coordination
- Better risk management
- Machine learning for strategy optimization

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This is an experimental AI system for educational and research purposes. It does not actually conduct real business transactions or generate real revenue. Any business opportunities are simulated within the system.

## 🎓 Learn More

- [Ollama Documentation](https://ollama.ai/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Built with ❤️ using local AI models and autonomous agents**
