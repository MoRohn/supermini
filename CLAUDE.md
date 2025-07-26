# CLAUDE.md

## Plan & Review

### Before starting work
- Always in plan mode to. make a plan
- After get the paln, make sure you write the plan to .claude/tasks/TASK_NAME.md
- The plan should be a detailed implementation plan and the reasoning behind them, as well as tasks broken down
- If the task require external knowledge or certain packages, also research to get latest knowledge (Use Task tool for research)
- Don't over plan it, alway think MVP and then enhance from there
- Once you write the plan, firstly display the plan and allow user to review plan.

### While implementing
- You should update the plan as you work.
- After you complete tasks in the plan, you should update and append detailed descriptions of the changes you made, so following tasks can be easily hand over to other AI engineers.


Contents below provides guidance when working with code in this repository:

## Project Overview

SuperMini (AI on Mini Mac) is a desktop AI assistant built with PyQt6 that combines Claude API and local Ollama models for task automation, multimedia processing, and intelligent document analysis. The application processes five main task types: code generation, multimedia analysis, RAG (document processing), automation scripts, and data analytics.

## Architecture

### Core Components

- **aimm.py**: Main application file containing the PyQt6 GUI and task processing engine
- **Task Processing Engine**: Handles five task types with auto-classification and memory context
- **AI Integration**: Dual AI system using Claude API (primary) and Ollama models (fallback)
- **Memory System**: ChromaDB-based vector storage for context awareness and learning
- **Output Management**: Structured file generation in `~/SuperMini_Output/` directory

### Key Classes and Systems

- `TaskProcessor`: Main processing engine with methods for each task type
- `MemoryManager`: ChromaDB integration for context storage and retrieval
- `AIProvider`: Handles Claude API and Ollama model interactions
- `SystemMonitor`: Real-time performance monitoring (CPU, memory, task metrics)
- Task types: code, multimedia, rag, automation, analytics

### Data Flow

1. User input → Task classification (auto or manual)
2. Memory context retrieval → Task-specific processing
3. AI model querying (Claude → Ollama fallback)
4. File generation and output management
5. Memory storage for future context

## Development Commands

### Running the Application
```bash
# Main application
python3 aimm.py

# Debug mode (if implemented)
python3 aimm.py --debug
```

### Dependencies Management
```bash
# Install dependencies
pip3 install -r requirements.txt

# Alternative setup
python3 dependencies/setup.py install
```

### Ollama Setup (Required for local AI)
```bash
# Start Ollama service
ollama serve &

# Install required models
ollama pull qwen2.5-coder:7b
ollama pull llama3.2:3b

# Check model status
ollama list
```

### Testing
```bash
# No test framework detected - tests directory is empty
# Add test framework setup if implementing tests
```

## File Structure

```
~/SuperMini_Output/
├── data/
│   ├── memory/          # ChromaDB vector database
│   ├── collaboration/   # Task sharing data
│   └── generated_*      # Generated output files
└── logs/
    └── supermini.log        # Application logs
```

## Task Types and Processing

### Code Tasks
- Input: Programming requirements, existing files
- Processing: Code generation with syntax-specific file extensions
- Output: Complete scripts/applications with proper file naming

### Multimedia Tasks
- Input: Image files (PNG, JPG, etc.)
- Processing: Base64 encoding and AI vision analysis
- Output: Analysis reports and descriptions

### RAG Tasks
- Input: Documents (PDF, text files)
- Processing: Document analysis with retrieval-augmented generation
- Output: Summaries, Q&A responses, insights

### Automation Tasks
- Input: System task requirements
- Processing: Shell script generation with executable permissions
- Output: Bash scripts (automation_script_*.sh)

### Analytics Tasks
- Input: CSV data files
- Processing: Pandas-based data analysis with visualization code
- Output: Analysis reports and Python visualization scripts

## Key Configuration

### Required Environment
- Python 3.9+
- PyQt6 for GUI
- Claude API key (optional, configured in GUI settings)
- Ollama service running locally
- ChromaDB for memory functionality

### Important Paths
- Output directory: `~/SuperMini_Output/`
- Log file: `~/SuperMini_Output/logs/supermini.log`
- Memory database: `~/SuperMini_Output/data/memory/`

## Memory and Context System

The application uses ChromaDB to maintain context awareness:
- Task history storage with embeddings
- Context retrieval based on prompt similarity
- Learning from user patterns and preferences
- Memory can be enabled/disabled per task

## Auto-Continue Feature

Tasks can automatically continue based on AI response patterns:
- Detects questions or continuation cues in responses
- Supports up to 10 continuation iterations
- Accumulates results and generated files across continuations
- Useful for complex multi-step tasks

## Autonomous Capabilities (NEW)

Enhanced with Simular AI Agent-S framework for autonomous computer interaction:

### Core Features
- **Autonomous Task Execution**: AI agents can directly interact with the computer interface
- **Screenshot-based Observation**: Takes screenshots to understand current state
- **Safety Management**: Built-in validation and confirmation for high-risk actions
- **Workflow Management**: Create and execute multi-step autonomous workflows

### Key Components
- `AutonomousAgent`: Main agent class using Agent-S framework
- `SafetyManager`: Validates actions and restricts dangerous operations
- `AutonomousWorkflowManager`: Orchestrates complex multi-task workflows

### GUI Integration
- Autonomous mode checkbox in task interface
- Autonomous suggestions button shows recommended actions
- Status indicator shows availability of autonomous features
- Screenshot capture and workflow visualization

### Installation for Full Autonomous Features
```bash
pip install gui-agents>=0.1.2 pyautogui>=0.9.54
```

### Safety Features
- Command validation against restricted operations
- Safe directory enforcement for file operations
- User confirmation prompts for high-risk actions
- Execution timeouts and step limits

### Usage Patterns
1. Enable "Autonomous Mode" checkbox for AI-driven computer interaction
2. Use "Show Autonomous Suggestions" to preview recommended actions
3. Autonomous agents work with all existing task types (code, multimedia, etc.)
4. Screenshots and execution logs saved to `~/SuperMini_Output/autonomous/`

## Enhanced Stop Functionality (NEW)

Comprehensive stop button implementation for all operation modes:

### Stop Buttons Available
- **⏹️ Stop Task**: Halts regular task execution and auto-continuation
- **⏹️ Stop Exploration**: Terminates autonomous exploration mode
- **⏹️ Stop Enhancement**: Stops self-enhancement processes

### Stop Behavior
- **Immediate Response**: Stop flags are checked during auto-continuation loops
- **Graceful Shutdown**: Threads are given 2-3 seconds to stop naturally  
- **Force Termination**: Unresponsive threads are force-terminated as fallback
- **GUI State Management**: Buttons automatically update enabled/disabled states
- **Activity Logging**: All stop actions are logged for transparency

### Technical Implementation
- `TaskProcessor.stop_requested` flag interrupts long-running operations
- Thread classes (`TaskThread`, `ExploreThread`, `EnhanceThread`) respond to stop signals
- Auto-continuation loops check stop flag between iterations
- Proper cleanup and resource management on termination

### Usage
1. Click any stop button to immediately halt the corresponding operation
2. Progress bars disappear and status updates to "stopped"
3. Start buttons re-enable for new operations
4. All stop actions are logged in Activity Monitor