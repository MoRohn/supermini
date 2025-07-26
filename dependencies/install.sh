#!/bin/bash

echo "🤖 Installing SuperMini - AI Multimedia and Management Assistant"
echo "=========================================================="

# Check if Python 3.9+ is installed
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Python 3.9+ is required but not found. Please install Python first."
    exit 1
fi

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  This application is optimized for macOS"
fi

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "🦙 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
sleep 3

# Pull recommended models
echo "📥 Downloading AI models (this may take a while)..."
ollama pull qwen2.5-coder:7b
ollama pull llama3.2:3b

# Create application directories
echo "📁 Creating application directories..."
mkdir -p ~/SuperMini_Output/data
mkdir -p ~/SuperMini_Output/logs

# Create launch script
echo "📝 Creating launch script..."
cat > ~/SuperMini_Output/launch_aimm.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 aimm.py
EOF

chmod +x ~/SuperMini_Output/launch_aimm.sh

# Copy main application file
cp aimm.py ~/SuperMini_Output/

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To start SuperMini:"
echo "1. cd ~/SuperMini_Output"
echo "2. python3 aimm.py"
echo ""
echo "Or use the launch script:"
echo "~/SuperMini_Output/launch_aimm.sh"
echo ""
echo "📋 Next steps:"
echo "• Configure your Claude API key in Settings (optional but recommended)"
echo "• Check that Ollama is running: ollama list"
echo "• Start creating tasks!"
echo ""

# Makefile
.PHONY: install run clean test package

install:
	@echo "Installing SuperMini..."
	pip3 install -r requirements.txt
	@if ! command -v ollama &> /dev/null; then \
		echo "Installing Ollama..."; \
		curl -fsSL https://ollama.ai/install.sh | sh; \
	fi
	@echo "Pulling AI models..."
	ollama pull qwen2.5-coder:7b
	ollama pull llama3.2:3b
	@echo "Setting up directories..."
	mkdir -p ~/SuperMini_Output/{data,logs}
	@echo "Installation complete!"

run:
	@echo "Starting SuperMini..."
	@if ! pgrep -f "ollama serve" > /dev/null; then \
		echo "Starting Ollama..."; \
		ollama serve & \
		sleep 3; \
	fi
	python3 aimm.py

clean:
	@echo "Cleaning up..."
	rm -rf ~/SuperMini_Output/data/memory/*
	rm -rf ~/SuperMini_Output/logs/*
	@echo "Cleanup complete!"

test:
	@echo "Running basic tests..."
	python3 -c "import PyQt6; print('✅ PyQt6 imported successfully')"
	python3 -c "import anthropic; print('✅ Anthropic imported successfully')" || echo "⚠️ Anthropic not available"
	python3 -c "import chromadb; print('✅ ChromaDB imported successfully')" || echo "⚠️ ChromaDB not available"
	@if command -v ollama &> /dev/null; then \
		echo "✅ Ollama is installed"; \
		ollama list; \
	else \
		echo "❌ Ollama not found"; \
	fi

package:
	@echo "Creating distributable package..."
	mkdir -p dist
	cp aimm.py dist/
	cp requirements.txt dist/
	cp install.sh dist/
	cp Makefile dist/
	cp README.md dist/ || touch dist/README.md
	@echo "Package created in dist/ directory"

# Docker support (optional)
docker-build:
	docker build -t aimm:latest .

docker-run:
	docker run -it -v ~/SuperMini_Output:/app/data aimm:latest