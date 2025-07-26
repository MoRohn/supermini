#!/bin/bash
# SuperMini Linux Launcher
# Cross-platform launcher optimized for Linux systems

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}🐧 SuperMini - Autonomous Mac Mini AI Agent (Linux)${NC}"
echo -e "${BLUE}================================================================${NC}"

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if universal launcher exists
if [ -f "universal_launcher.py" ]; then
    echo -e "${GREEN}🚀 Using Universal SuperMini Launcher${NC}"
    python3 universal_launcher.py
    exit $?
fi

# Fallback method
echo -e "${YELLOW}⚠️  Universal launcher not found, using fallback method${NC}"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo -e "${CYAN}   Install with your package manager:${NC}"
    echo -e "${CYAN}   Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv${NC}"
    echo -e "${CYAN}   Fedora: sudo dnf install python3 python3-pip${NC}"
    echo -e "${CYAN}   Arch: sudo pacman -S python python-pip${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}🐍 Python version: $PYTHON_VERSION${NC}"

# Check if version is 3.9+
if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
    echo -e "${GREEN}✅ Python version is compatible${NC}"
else
    echo -e "${RED}❌ Python 3.9+ is required. Please upgrade Python.${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}🐍 Activating Python virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found${NC}"
    echo -e "${BLUE}🔧 Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Virtual environment created${NC}"
        source venv/bin/activate
    else
        echo -e "${RED}❌ Failed to create virtual environment${NC}"
        echo -e "${YELLOW}   Continuing with system Python...${NC}"
    fi
fi

# Install/update dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦 Installing/updating Python dependencies...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "${RED}❌ Some dependencies failed to install${NC}"
        echo -e "${YELLOW}   SuperMini may have limited functionality${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Create output directory
OUTPUT_DIR="$HOME/SuperMini_Output"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${BLUE}📁 Creating output directory: $OUTPUT_DIR${NC}"
    mkdir -p "$OUTPUT_DIR"/{data,logs,data/memory,data/collaboration,autonomous}
    echo -e "${GREEN}✅ Output directories created${NC}"
fi

# Check for Ollama
echo -e "${BLUE}🧠 Checking Ollama AI service...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama found${NC}"
    
    # Check if Ollama service is running
    if ! pgrep -f "ollama serve" > /dev/null; then
        echo -e "${YELLOW}⚡ Starting Ollama service...${NC}"
        ollama serve &
        sleep 3
        
        if pgrep -f "ollama serve" > /dev/null; then
            echo -e "${GREEN}✅ Ollama service started${NC}"
        else
            echo -e "${RED}❌ Failed to start Ollama service${NC}"
        fi
    else
        echo -e "${GREEN}✅ Ollama service already running${NC}"
    fi
    
    # Check for AI models
    if ollama list 2>/dev/null | grep -q "qwen2.5-coder\|llama"; then
        echo -e "${GREEN}🧠 AI models available${NC}"
    else
        echo -e "${YELLOW}⚠️  No AI models found${NC}"
        echo -e "${CYAN}   Install models with: ollama pull qwen2.5-coder:7b${NC}"
    fi
else
    echo -e "${RED}❌ Ollama not found${NC}"
    echo -e "${CYAN}   Install with: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
    echo -e "${CYAN}   Or visit: https://ollama.ai/download/linux${NC}"
    echo -e "${YELLOW}   SuperMini will work with limited AI functionality${NC}"
fi

# Check for GUI libraries (important for PyQt6 on Linux)
echo -e "${BLUE}🖥️  Checking GUI libraries...${NC}"
python3 -c "import PyQt6; print('✅ PyQt6 available')" 2>/dev/null || {
    echo -e "${RED}❌ PyQt6 not available${NC}"
    echo -e "${CYAN}   Install with: pip install PyQt6${NC}"
    echo -e "${CYAN}   Or system package: sudo apt install python3-pyqt6 (Ubuntu/Debian)${NC}"
}

# Check if main script exists
if [ ! -f "aimm.py" ]; then
    echo -e "${RED}❌ aimm.py not found in current directory${NC}"
    echo -e "${BLUE}Current directory: $(pwd)${NC}"
    echo -e "${BLUE}Directory contents:${NC}"
    ls -la
    read -p "Press Enter to exit..."
    exit 1
fi

# Set up desktop integration if desired
if [ ! -f "$HOME/.local/share/applications/supermini.desktop" ]; then
    echo -e "${BLUE}🖥️  Desktop integration available${NC}"
    read -p "Install desktop shortcut? (y/n): " install_desktop
    if [[ "$install_desktop" == "y" || "$install_desktop" == "Y" ]]; then
        if [ -f "icons_generated/desktop/linux/install_linux_icons.sh" ]; then
            echo -e "${BLUE}🔧 Installing desktop integration...${NC}"
            cd icons_generated/desktop/linux && ./install_linux_icons.sh && cd "$SCRIPT_DIR"
        else
            echo -e "${YELLOW}⚠️  Desktop integration files not found${NC}"
        fi
    fi
fi

# Launch SuperMini
echo -e "${BLUE}================================================================${NC}"
echo -e "${GREEN}🚀 Launching SuperMini...${NC}"
echo -e "${BLUE}================================================================${NC}"

# Launch with proper error handling
python3 aimm.py 2>&1

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo -e "${RED}❌ SuperMini exited with error code: $exit_code${NC}"
    echo -e "${BLUE}Check the log file for details: $OUTPUT_DIR/logs/supermini.log${NC}"
    read -p "Press Enter to exit..."
fi

echo -e "${GREEN}👋 SuperMini session ended${NC}"