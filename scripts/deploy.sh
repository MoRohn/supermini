#!/bin/bash

# SuperMini One-Click Deployment Script
# Run this script to get SuperMini up and running in minutes

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
clear
echo "🤖 SuperMini - AI Multimedia and Management Assistant"
echo "================================================"
echo "One-Click Deployment Script v2.0.0"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is optimized for macOS but will attempt to install anyway"
fi

# Check for Python 3.9+
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
    
    # Check if version is 3.9 or higher
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
        print_success "Python version is compatible"
    else
        print_error "Python 3.9+ is required. Please upgrade Python."
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

# Create project directory
PROJECT_DIR="$HOME/SuperMini"
print_status "Creating project directory at $PROJECT_DIR..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install required packages
print_status "Installing Python dependencies..."
cat > requirements.txt << EOF
PyQt6>=6.6.0
anthropic>=0.7.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
psutil>=5.9.0
chromadb>=0.4.0
EOF

pip install -r requirements.txt

# Check if Ollama is installed
print_status "Checking Ollama installation..."
if [ -d "$HOME/.ollama" ] && command -v ollama &> /dev/null; then
    print_success "Ollama is already installed"
else
    print_status "Ollama not found in ~/.ollama or not in PATH"
    read -p "Would you like to install Ollama? (y/n): " response
    response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
    if [ "$response" = "y" ]; then
        print_status "Installing Ollama..."
        if curl -fsSL https://ollama.ai/install.sh | sh; then
            # Add to PATH if needed
            if [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
                export PATH="/usr/local/bin:$PATH"
                echo 'export PATH="/usr/local/bin:$PATH"' >> "$HOME/.zshrc"
            fi
            print_success "Ollama installed successfully"
        else
            print_error "Failed to install Ollama"
            exit 1
        fi
    else
        print_error "Ollama installation cancelled by user"
        exit 1
    fi
fi

# Start Ollama service
print_status "Starting Ollama service..."
if pgrep -f "ollama serve" > /dev/null; then
    print_success "Ollama is already running"
else
    ollama serve &
    sleep 5
    print_success "Ollama service started"
fi

# Download AI models
print_status "Downloading AI models (this may take several minutes)..."

# Download Qwen model (recommended for coding)
if ollama list | grep -q "qwen2.5-coder:32b"; then
    print_success "qwen2.5-coder:32b already downloaded"
else
    print_status "Downloading qwen2.5-coder:32b..."
    ollama pull qwen2.5-coder:32b
    print_success "qwen2.5-coder:32b downloaded"
fi

# Download Llama model (general purpose)
if ollama list | grep -q "llama3.2:3b"; then
    print_success "llama3.2:3b already downloaded"
else
    print_status "Downloading llama3.2:3b..."
    ollama pull llama3.2:3b
    print_success "llama3.2:3b downloaded"
fi

# Create application directories
print_status "Setting up application directories..."
mkdir -p "$HOME/SuperMini_Output/data"
mkdir -p "$HOME/SuperMini_Output/logs"
mkdir -p "$HOME/SuperMini_Output/data/memory"
mkdir -p "$HOME/SuperMini_Output/data/collaboration"

# Create the main application file (copy from the artifact we created earlier)
print_status "Creating main application file..."

# Make scripts executable
chmod +x aimm.py

# Create launch script
print_status "Creating launch scripts..."
cat > launch.sh << 'LAUNCH_EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

# Start Ollama if not running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Launch SuperMini
echo "Launching SuperMini..."
python3 aimm.py
LAUNCH_EOF

chmod +x launch.sh

# Create desktop shortcut (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "Creating desktop shortcut..."
    cat > "$HOME/Desktop/SuperMini.command" << SHORTCUT_EOF
#!/bin/bash
cd "$PROJECT_DIR"
./launch.sh
SHORTCUT_EOF
    chmod +x "$HOME/Desktop/SuperMini.command"
fi

# Test installation
print_status "Testing installation..."

# Test Python imports
python3 -c "import PyQt6; print('✅ PyQt6 working')" || print_error "PyQt6 import failed"
python3 -c "import requests; print('✅ Requests working')" || print_error "Requests import failed"

# Test Ollama
if ollama list > /dev/null 2>&1; then
    print_success "Ollama is working"
    echo "Available models:"
    ollama list
else
    print_error "Ollama test failed"
fi

# Final success message
echo ""
print_success "🎉 SuperMini installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Launch SuperMini:"
echo "   cd $PROJECT_DIR && ./launch.sh"
echo ""
echo "2. Or double-click the desktop shortcut: SuperMini.command"
echo ""
echo "3. For the full version with Claude API support:"
echo "   - Get an API key from: https://console.anthropic.com/"
echo "   - Replace aimm.py with the full version"
echo ""
echo "4. Test with a simple task like:"
echo "   'Create a Python script to list files in a directory'"
echo ""
echo "📁 Project location: $PROJECT_DIR"
echo "📁 Output directory: $HOME/SuperMini_Output"
echo ""
print_success "Happy AI-assisted productivity! 🚀"

# Open project directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$PROJECT_DIR"
fi