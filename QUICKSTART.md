# Quick Start Guide

Get your AI Entrepreneur Agent System running in 5 minutes!

## Prerequisites Check

```bash
# Check Python
python3 --version  # Should be 3.8+

# Check Ollama
ollama --version
```

## Installation (3 steps)

### 1. Install Ollama (if needed)

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull the AI Model

```bash
ollama pull gpt-oss:latest
```

### 3. Setup the System

```bash
./setup.sh
```

## Running (2 ways)

### Option A: Agent Only

```bash
# Start Ollama (in terminal 1)
ollama serve

# Run the agent (in terminal 2)
source venv/bin/activate
python main.py run
```

### Option B: Agent + Dashboard

```bash
# Start Ollama (in terminal 1)
ollama serve

# Run both agent and dashboard (in terminal 2)
source venv/bin/activate
python main.py both
```

Then open http://localhost:8000 in your browser!

## First Run

The system will:
1. ✅ Check Ollama connection
2. ✅ Initialize database
3. ✅ Create the Master Entrepreneur Agent
4. ✅ Start scanning for business opportunities
5. ✅ Execute profitable opportunities
6. ✅ Track financial performance

## Monitoring

Watch the logs to see:
- Opportunities identified
- Agents created/managed
- Financial updates
- Performance metrics

## Configuration

Edit `.env` to customize:

```bash
# Change starting capital
INITIAL_CAPITAL=5000

# Adjust risk tolerance (0-1)
RISK_TOLERANCE=0.5

# Set minimum profit margin
MIN_PROFIT_MARGIN=0.20
```

## Dashboard API

```bash
# System status
curl http://localhost:8000/api/status

# All opportunities
curl http://localhost:8000/api/opportunities

# Full dashboard data
curl http://localhost:8000/api/dashboard
```

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Start Ollama in a separate terminal
ollama serve
```

### "Model not found"
```bash
ollama pull gpt-oss:latest
```

### "Database error"
```bash
# Reset database
rm entrepreneur_agent.db
```

## What's Next?

- Monitor the logs to see your AI entrepreneur in action
- Check the dashboard to track performance
- Adjust configuration for different strategies
- Review generated opportunities and decisions

## Example Output

```
=========================================================
AI ENTREPRENEUR AGENT SYSTEM
=========================================================
Initial Capital: $1000.00
Risk Tolerance: 0.7
Min Profit Margin: 0.15
=========================================================

2025-11-10 10:00:00 - INFO - Master Entrepreneur Agent starting...
2025-11-10 10:00:05 - INFO - Business Cycle 1
2025-11-10 10:00:05 - INFO - Current Capital: $1000.00
2025-11-10 10:00:10 - INFO - Scanning for business opportunities...
2025-11-10 10:00:15 - INFO - Identified 5 opportunities
2025-11-10 10:00:16 - INFO - Selected opportunity: AI Content Generation Service
2025-11-10 10:00:20 - INFO - Executing opportunity...
2025-11-10 10:00:25 - INFO - Opportunity execution result: SUCCESS
2025-11-10 10:00:25 - INFO - Capital updated: $1250.00 (change: +$250.00)
```

## Need Help?

- Check the full README.md for detailed documentation
- Review logs in `logs/entrepreneur_agent.log`
- Monitor the dashboard at http://localhost:8000

---

**Ready to build an AI-powered business empire? Run `python main.py run` and let's go! 🚀**
