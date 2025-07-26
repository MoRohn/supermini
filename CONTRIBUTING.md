# Contributing to SuperMini

Thank you for your interest in contributing to SuperMini! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of PyQt6/Qt development
- Familiarity with AI/ML concepts (helpful but not required)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/supermini.git
   cd supermini
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (if available)
   pip install -r requirements-dev.txt
   ```

3. **Set Up Ollama (for local AI models)**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve &
   
   # Pull required models
   ollama pull qwen2.5-coder:7b
   ollama pull llama3.2:3b
   ```

4. **Verify Installation**
   ```bash
   python3 supermini.py
   ```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug Fixes**: Fix issues and improve stability
- **Feature Enhancements**: Add new functionality or improve existing features
- **Documentation**: Improve documentation, examples, and guides
- **Testing**: Add or improve test coverage
- **Performance**: Optimize code performance and resource usage
- **UI/UX**: Improve user interface and user experience
- **AI Models**: Add support for new AI models or providers

### Before You Start

1. **Check existing issues** to see if your idea is already being worked on
2. **Create an issue** to discuss large changes before implementing
3. **Keep changes focused** - one feature or fix per pull request
4. **Follow coding standards** outlined below

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clean, documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run existing tests
python -m pytest tests/

# Test the application manually
python3 supermini.py

# Test with different configurations
# - Different AI models
# - Various task types
# - Edge cases and error conditions
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: Add new feature description"
# or
git commit -m "fix: Fix issue description"
```

Use conventional commit messages:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/examples if applicable
- Testing steps for reviewers

## Coding Standards

### Python Code Style

- Follow **PEP 8** style guidelines
- Use **type hints** for function parameters and return values
- Maximum line length: **88 characters** (Black formatter standard)
- Use **docstrings** for all public functions and classes

### Code Organization

```
supermini/
├── supermini.py              # Main application entry point
├── activity_monitor.py       # Activity monitoring components
├── autonomous_*.py           # Autonomous functionality modules
├── enhanced_*.py            # Enhanced feature modules
├── task_intelligence.py     # Task processing logic
├── assets/                  # Icons, images, and UI assets
├── scripts/                 # Build and deployment scripts
├── tests/                   # Test files
├── docs/                    # Documentation
└── prompts/                 # AI prompt templates
```

### Documentation Standards

- Use **docstrings** for all public APIs
- Include **type hints** in function signatures
- Add **inline comments** for complex logic
- Update **README.md** for user-facing changes
- Update **CHANGELOG.md** for all changes

### Example Code Style

```python
from typing import Optional, List, Dict, Any
import logging

class TaskProcessor:
    """Processes various types of AI tasks with proper error handling.
    
    This class handles the main task processing pipeline including
    AI model interaction, result formatting, and error recovery.
    
    Attributes:
        model_provider: The AI model provider instance
        memory_enabled: Whether to use memory context
    """
    
    def __init__(self, model_provider: str, memory_enabled: bool = True) -> None:
        """Initialize the task processor.
        
        Args:
            model_provider: Name of the AI model provider ('claude' or 'ollama')
            memory_enabled: Whether to enable memory context for tasks
        """
        self.model_provider = model_provider
        self.memory_enabled = memory_enabled
        self.logger = logging.getLogger(__name__)
    
    def process_task(self, 
                    task_description: str, 
                    files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Process a task with the specified parameters.
        
        Args:
            task_description: Human-readable description of the task
            files: Optional list of file paths to include in processing
            
        Returns:
            Dictionary containing:
                - 'result': The processed result
                - 'files_generated': List of generated file paths
                - 'status': 'success' or 'error'
                - 'error_message': Error description if status is 'error'
                
        Raises:
            TaskProcessingError: If task processing fails critically
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            self.logger.error(f"Task processing failed: {e}")
            raise
```

## Testing

### Test Structure

- Place tests in the `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test function names
- Include both unit tests and integration tests

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_task_processing.py

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Guidelines

- **Test all public APIs**
- **Mock external dependencies** (AI APIs, file system when appropriate)
- **Test error conditions** and edge cases
- **Use fixtures** for common test data
- **Keep tests isolated** and independent

## Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include for all function parameters and returns
- **Inline Comments**: Explain complex logic and decisions

### User Documentation

- Update **README.md** for user-facing changes
- Add examples to **docs/** directory
- Update **API documentation** for new features

## Issue Reporting

### Bug Reports

When reporting bugs, include:

- **SuperMini version**
- **Operating system** and version
- **Python version**
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Error messages** and log output
- **Screenshots** if applicable

### Feature Requests

For feature requests, provide:

- **Clear description** of the proposed feature
- **Use case** and motivation
- **Expected behavior** and user experience
- **Implementation ideas** (if any)
- **Alternatives considered**

### Issue Labels

- `bug` - Something isn't working correctly
- `enhancement` - New feature or improvement
- `documentation` - Documentation related
- `help wanted` - Extra attention is needed
- `good first issue` - Good for newcomers

## Development Tips

### Debugging

- Use logging extensively with appropriate levels
- Test with both Claude API and Ollama models
- Test on different operating systems when possible
- Use the built-in activity monitor for performance insights

### AI Model Integration

- Always provide fallback options
- Handle API rate limits and errors gracefully
- Test with different model configurations
- Consider token limits and response times

### UI Development

- Test with different screen resolutions and DPI settings
- Ensure accessibility features work properly
- Follow platform-specific UI guidelines
- Test with different themes and color schemes

## Release Process

Releases are automated through the "Enhance Yourself" mode integration:

1. **Development** happens on feature branches
2. **Pull requests** are reviewed and merged to main
3. **Automated testing** ensures code quality
4. **Semantic versioning** determines version numbers
5. **Release automation** creates GitHub releases
6. **Distribution** packages are built automatically

## Questions and Support

- **GitHub Discussions**: For general questions and community discussion
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check the wiki and docs/ directory
- **Code Review**: Request reviews on pull requests

## Recognition

Contributors will be recognized in:

- **README.md** acknowledgments section
- **CHANGELOG.md** for specific contributions
- **GitHub contributors** page
- **Release notes** for significant contributions

Thank you for contributing to SuperMini! Your efforts help make AI more accessible and useful for everyone.