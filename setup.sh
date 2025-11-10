#!/bin/bash
# Setup script for AI Entrepreneur Agent System

set -e

echo "========================================"
echo "AI Entrepreneur Agent System - Setup"
echo "========================================"
echo ""

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠ Ollama is not installed"
    echo ""
    echo "Please install Ollama:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ Ollama is installed"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ Pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠ Please edit .env file to configure your settings"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create necessary directories
mkdir -p logs agent_data

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Ensure Ollama is running: ollama serve"
echo "2. Pull the model: ollama pull gpt-oss:latest"
echo "3. Activate environment: source venv/bin/activate"
echo "4. Run the system: python main.py run"
echo ""
echo "For monitoring dashboard:"
echo "  python main.py dashboard"
echo ""
echo "For both:"
echo "  python main.py both"
echo ""
