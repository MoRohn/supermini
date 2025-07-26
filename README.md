# 🤖 SuperMini - AI on Mini Mac Assistant

A powerful desktop AI assistant that combines Claude API and local Ollama models for task automation, autonomous exploration, and intelligent enhancement capabilities.

![SuperMini Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)

## ✨ Features

### 🔧 Task Automation
- **Code Generation**: Write, debug, and optimize code in multiple programming languages
- **Script Creation**: Generate automation scripts for system tasks and workflows
- **File Processing**: Batch process files with intelligent operations

### 🎨 Multimedia Processing
- **Image Analysis**: Describe, analyze, and extract information from images
- **Audio Processing**: Transcribe and analyze audio files (planned)
- **Video Enhancement**: Process and enhance video content (planned)

### 📊 Data Analytics
- **CSV Analysis**: Analyze data files and generate insights
- **Visualization**: Create charts and graphs from data
- **Statistical Analysis**: Perform advanced data analysis

### 📄 Document Intelligence
- **RAG Processing**: Summarize and analyze documents with retrieval-augmented generation
- **Q&A Systems**: Answer questions based on document content
- **Content Extraction**: Extract key information from various file formats

### 🧠 Memory System
- **Context Awareness**: Remember previous tasks and conversations
- **Learning**: Improve responses based on interaction history
- **Personalization**: Adapt to user preferences and patterns

## 🚀 Quick Start

### Prerequisites
- macOS 10.15+ (optimized for macOS, but works on other platforms)
- Python 3.9 or higher
- 8GB+ RAM recommended
- Internet connection for Claude API (optional)

### Installation

#### Option 1: Automated Installation
```bash
# Clone the repository
git clone https://github.com/your-username/supermini.git
cd supermini

# Run automated setup
chmod +x dependencies/install.sh
./dependencies/install.sh
```

#### Option 2: Manual Installation
```bash
# Install Python dependencies
pip3 install PyQt6 anthropic requests pandas numpy psutil chromadb

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve &

# Pull recommended models
ollama pull qwen2.5-coder:7b
ollama pull llama3.2:3b

# Create directories
mkdir -p ~/SuperMini_Output/data ~/SuperMini_Output/logs

# Run the application
python3 supermini.py
```

### First Run Setup

1. **Launch SuperMini**: Run `python3 supermini.py`
2. **Configure API Key** (optional but recommended):
   - Click "⚙️ Settings"
   - Enter your Claude API key from [Anthropic Console](https://console.anthropic.com/)
   - Save settings
3. **Verify Ollama**: Ensure local models are downloaded and running
4. **Start Creating**: Enter your first task and click "🚀 Process Task"

## 💡 Usage Examples

### Code Generation
```
Task: "Create a Python script to sort a CSV file by date column"
Files: data.csv
Result: Complete Python script with error handling
```

### Image Analysis
```
Task: "Analyze this screenshot and describe the UI elements"
Files: screenshot.png
Result: Detailed description of interface components
```

### Data Analysis
```
Task: "Analyze sales data and create visualizations"
Files: sales_data.csv
Result: Statistical analysis + Python visualization code
```

### Document Summarization
```
Task: "Summarize the key points from these research papers"
Files: paper1.pdf, paper2.pdf
Result: Comprehensive summary with key insights
```

### Automation Scripts
```
Task: "Create a backup script for my Documents folder"
Result: Bash script with scheduling options
```

## 🔧 Configuration

### AI Models
- **Claude API**: Primary model for complex reasoning (requires API key)
- **Ollama Local**: Fallback models that run locally
  - `qwen2.5-coder:7b` - Best for coding tasks
  - `llama3.2:3b` - General purpose, faster responses

### Settings Options
- **Max Tokens**: Control response length (512-8192)
- **Temperature**: Creativity level (0.0-1.0)
- **Memory**: Enable/disable context awareness
- **Task Types**: Auto-detection or manual selection

## 📁 File Structure

```
~/SuperMini_Output/
├── data/
│   ├── memory/          # ChromaDB memory database
│   ├── collaboration/   # Task sharing data
│   └── generated_*      # Your generated files
└── logs/
    └── supermini.log        # Application logs
```

## 🎯 Task Types

### 🔹 Code
- **Description**: Programming, scripting, debugging
- **Input**: Code requirements, existing files
- **Output**: Complete scripts, functions, or applications
- **Examples**: "Fix this Python script", "Create a web scraper"

### 🔹 Multimedia
- **Description**: Image, audio, and video processing
- **Input**: Media files, processing requirements
- **Output**: Analysis, enhanced files, descriptions
- **Examples**: "Describe this image", "Enhance video quality"

### 🔹 RAG (Retrieval Augmented Generation)
- **Description**: Document analysis and question answering
- **Input**: Documents, questions
- **Output**: Summaries, answers, insights
- **Examples**: "Summarize these PDFs", "Answer questions about this document"

### 🔹 Automation
- **Description**: System tasks and workflow automation
- **Input**: Task requirements, file operations
- **Output**: Scripts, shortcuts, automation workflows
- **Examples**: "Backup my files", "Organize downloads folder"

### 🔹 Analytics
- **Description**: Data analysis and visualization
- **Input**: Data files (CSV, JSON), analysis requirements
- **Output**: Statistical analysis, charts, insights
- **Examples**: "Analyze sales trends", "Create data dashboard"

## 🛠️ Advanced Features

### Memory System
SuperMini remembers your previous tasks and uses them for context:
- **Automatic Learning**: Improves responses based on your preferences
- **Context Awareness**: References previous tasks when relevant
- **Pattern Recognition**: Learns your common workflows

### System Monitoring
Track resource usage in real-time:
- **CPU Usage**: Monitor processing load
- **Memory Usage**: Track RAM consumption
- **Performance Metrics**: Optimize for your system

### Collaboration Features
- **Local Storage**: All data stored securely on your machine
- **Task History**: Complete record of all interactions
- **Export Options**: Share results and generated files

## 🔍 Troubleshooting

### Common Issues

#### "No AI models available"
```bash
# Check Ollama status
ollama list

# Restart Ollama service
pkill ollama
ollama serve &

# Re-download models
ollama pull qwen2.5-coder:7b
```

#### "Claude API errors"
- Verify API key in Settings
- Check internet connection
- Ensure sufficient API credits

#### "Memory errors"
```bash
# Clear memory database
rm -rf ~/SuperMini_Output/data/memory/*
# Restart application
```

#### "Installation issues"
```bash
# Update pip and dependencies
pip3 install --upgrade pip
pip3 install --upgrade -r requirements.txt
```

### Performance Optimization

#### For Better Speed:
- Use smaller Ollama models: `llama3.2:1b`
- Reduce max tokens in settings
- Disable memory for simple tasks

#### For Better Quality:
- Use Claude API for complex tasks
- Enable memory for context
- Use larger models: `qwen2.5-coder:14b`

## 🔐 Privacy & Security

- **Local First**: All processing can be done locally with Ollama
- **No Data Collection**: Your tasks and files stay on your machine
- **Optional Cloud**: Claude API only used when configured
- **Secure Storage**: All data encrypted and stored locally

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your improvements
4. **Test Thoroughly**: Ensure everything works
5. **Submit Pull Request**: Describe your changes

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-repo/supermini.git
cd supermini

# Install development dependencies
pip3 install -r requirements-dev.txt

# Run in development mode
python3 supermini.py --debug
```

## 📋 Roadmap

### Version 2.1 (Next Release)
- [ ] Voice input/output support
- [ ] Plugin system for custom tools
- [ ] Web interface option
- [ ] Enhanced video processing

### Version 2.2 (Future)
- [ ] Multi-language support
- [ ] Advanced automation workflows
- [ ] Team collaboration features
- [ ] Cloud synchronization option

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for the Claude API
- **Ollama** for local AI model hosting
- **Qt/PyQt** for the user interface framework
- **ChromaDB** for vector memory storage

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-repo/supermini/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-repo/supermini/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/supermini/discussions)
- **Email**: support@supermini.app

---

**Made with ❤️ for the AI community**

*SuperMini - Where AI meets productivity*