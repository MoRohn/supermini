"""
Pytest configuration and shared fixtures for SuperMini QA testing.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI testing."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    # Don't quit the app as it might be shared

@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="supermini_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_claude_api():
    """Mock Claude API responses."""
    mock = Mock()
    mock.messages.create.return_value = Mock(
        content=[Mock(text="Mock Claude response for testing")]
    )
    return mock

@pytest.fixture
def mock_ollama_api():
    """Mock Ollama API responses."""
    mock = Mock()
    mock.chat.return_value = {"message": {"content": "Mock Ollama response for testing"}}
    mock.list.return_value = {"models": [{"name": "qwen2.5-coder:7b"}]}
    return mock

@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB client."""
    mock_client = Mock()
    mock_collection = Mock()
    mock_collection.add.return_value = None
    mock_collection.query.return_value = {
        "documents": [["Mock context document"]],
        "metadatas": [[{"task_type": "code", "timestamp": "2025-01-01"}]],
        "distances": [[0.1]]
    }
    mock_client.get_or_create_collection.return_value = mock_collection
    return mock_client

@pytest.fixture
def sample_image():
    """Create a sample test image."""
    # Create a simple RGB image
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer.getvalue()

@pytest.fixture
def sample_image_base64(sample_image):
    """Convert sample image to base64."""
    return base64.b64encode(sample_image).decode('utf-8')

@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    data = {
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]
    }
    df = pd.DataFrame(data)
    return df

@pytest.fixture
def sample_csv_file(temp_output_dir, sample_csv_data):
    """Create a sample CSV file."""
    csv_path = Path(temp_output_dir) / "test_data.csv"
    sample_csv_data.to_csv(csv_path, index=False)
    return str(csv_path)

@pytest.fixture
def sample_text_file(temp_output_dir):
    """Create a sample text file."""
    text_path = Path(temp_output_dir) / "test_document.txt"
    with open(text_path, 'w') as f:
        f.write("This is a sample document for testing RAG functionality.")
    return str(text_path)

@pytest.fixture
def mock_task_processor():
    """Mock TaskProcessor for isolated testing."""
    from unittest.mock import MagicMock
    
    processor = MagicMock()
    processor.stop_requested = False
    processor.auto_continue = False
    processor.memory_enabled = True
    processor.output_directory = "/tmp/test_output"
    
    # Mock methods
    processor.classify_task_type.return_value = "code"
    processor.get_memory_context.return_value = "Mock memory context"
    processor.save_to_memory.return_value = True
    processor.generate_filename.return_value = "test_output.py"
    
    return processor

@pytest.fixture
def mock_system_monitor():
    """Mock SystemMonitor for testing."""
    monitor = Mock()
    monitor.cpu_percent = 25.0
    monitor.memory_percent = 45.0
    monitor.disk_usage = 60.0
    monitor.active_tasks = 1
    monitor.completed_tasks = 5
    monitor.failed_tasks = 0
    return monitor

@pytest.fixture
def mock_ai_providers():
    """Mock both Claude and Ollama providers."""
    return {
        'claude': Mock(
            query=Mock(return_value="Mock Claude response"),
            is_available=Mock(return_value=True)
        ),
        'ollama': Mock(
            query=Mock(return_value="Mock Ollama response"),
            is_available=Mock(return_value=True)
        )
    }

@pytest.fixture
def autonomous_test_data():
    """Test data for autonomous mode testing."""
    return {
        'safe_commands': [
            'ls -la',
            'pwd',
            'echo "hello"',
            'cat /Users/test/safe_file.txt'
        ],
        'restricted_commands': [
            'rm -rf /',
            'sudo rm -rf /System',
            'format C:',
            'del /f /q C:\\*'
        ],
        'safe_directories': [
            '/Users/test/safe_dir',
            '/tmp/test_workspace',
            '~/SuperMini_Output'
        ],
        'restricted_directories': [
            '/System',
            '/usr/bin',
            'C:\\Windows\\System32',
            '/etc'
        ]
    }

@pytest.fixture
def performance_benchmarks():
    """Performance benchmark thresholds."""
    return {
        'task_initiation_max': 2.0,  # seconds
        'typical_processing_max': 30.0,  # seconds
        'large_file_processing_max': 120.0,  # seconds
        'memory_usage_max': 1024 * 1024 * 1024,  # 1GB in bytes
        'ui_response_max': 0.1  # seconds
    }

@pytest.fixture
def test_files_directory():
    """Directory containing test files."""
    test_dir = Path(__file__).parent / "data"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, temp_output_dir):
    """Set up test environment variables."""
    monkeypatch.setenv("SUPERMINI_OUTPUT_DIR", temp_output_dir)
    monkeypatch.setenv("SUPERMINI_TEST_MODE", "true")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key_12345")
    
@pytest.fixture
def mock_screenshot():
    """Mock screenshot data for autonomous testing."""
    # Create a simple test image as screenshot
    img = Image.new('RGB', (1920, 1080), color='blue')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer.getvalue()

# Test markers for organizing test runs
pytestmark = [
    pytest.mark.filterwarnings("ignore:.*deprecated.*:DeprecationWarning"),
    pytest.mark.filterwarnings("ignore:.*PytestCollectionWarning.*")
]