#!/bin/bash
# SuperMini Enhanced Launcher Script - Unified cross-platform launcher
# Supports both development and app bundle environments

# Use the universal Python launcher for robust cross-platform support
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine if we're in an app bundle or development environment
if [[ "$SCRIPT_DIR" == *".app/Contents/MacOS"* ]]; then
    # We're in an app bundle
    RESOURCES_DIR="$(dirname "$SCRIPT_DIR")/Resources"
    cd "$RESOURCES_DIR"
else
    # We're in development environment
    cd "$SCRIPT_DIR"
fi

# Check if universal launcher exists, use it if available
if [ -f "universal_launcher.py" ]; then
    echo "🚀 Using Universal SuperMini Launcher"
    python3 universal_launcher.py
    exit $?
fi

# Fallback to original launcher logic if universal launcher not found
echo "⚠️  Universal launcher not found, using fallback method"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Starting SuperMini - Autonomous Mac Mini AI Agent${NC}"
echo "=================================================="

# Check for virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}🐍 Activating Python virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found, using system Python${NC}"
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}🐍 Python version: $PYTHON_VERSION${NC}"

# Check if Ollama is installed and running
echo -e "${BLUE}🧠 Checking Ollama service...${NC}"
if command -v ollama &> /dev/null; then
    if ! pgrep -f "ollama serve" > /dev/null; then
        echo -e "${YELLOW}⚡ Starting Ollama service...${NC}"
        ollama serve &
        sleep 3
        
        if pgrep -f "ollama serve" > /dev/null; then
            echo -e "${GREEN}✅ Ollama service started successfully${NC}"
        else
            echo -e "${RED}❌ Failed to start Ollama service${NC}"
        fi
    else
        echo -e "${GREEN}✅ Ollama service is already running${NC}"
    fi
    
    # Check for AI models
    if ollama list | grep -q "qwen2.5-coder"; then
        echo -e "${GREEN}🧠 AI models available${NC}"
    else
        echo -e "${YELLOW}⚠️  No AI models found. Some features may be limited.${NC}"
        echo -e "${BLUE}   Run 'ollama pull qwen2.5-coder:7b' to install models${NC}"
    fi
else
    echo -e "${RED}❌ Ollama not found. Please install from: https://ollama.ai${NC}"
    echo -e "${BLUE}   Or install via Homebrew: brew install ollama${NC}"
fi

# Create output directory if it doesn't exist
OUTPUT_DIR="$HOME/SuperMini_Output"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${BLUE}📁 Creating output directory: $OUTPUT_DIR${NC}"
    mkdir -p "$OUTPUT_DIR"/{data,logs,data/memory,data/collaboration}
fi

# Launch SuperMini
echo -e "${GREEN}🚀 Launching SuperMini...${NC}"
echo "=================================================="

# Check if aimm.py exists
if [ ! -f "aimm.py" ]; then
    echo -e "${RED}❌ aimm.py not found in current directory${NC}"
    echo -e "${BLUE}Current directory: $(pwd)${NC}"
    echo -e "${BLUE}Directory contents:${NC}"
    ls -la
    exit 1
fi

# Launch with error handling
python3 aimm.py 2>&1 || {
    exit_code=$?
    echo -e "${RED}❌ SuperMini exited with error code: $exit_code${NC}"
    echo -e "${BLUE}Press any key to continue...${NC}"
    read -n 1
    exit $exit_code
}
