"""
Mock AI providers for testing SuperMini without external dependencies.
"""
import time
import random
from unittest.mock import Mock, MagicMock
from pathlib import Path
import json

class MockClaudeProvider:
    """Mock Claude API provider for testing."""
    
    def __init__(self, simulate_errors=False, response_delay=0.1):
        self.simulate_errors = simulate_errors
        self.response_delay = response_delay
        self.call_count = 0
        self.responses_dir = Path(__file__).parent.parent / "data" / "responses"
        
    def query(self, prompt, task_type="general", temperature=0.7, max_tokens=4000):
        """Mock Claude query with realistic responses."""
        self.call_count += 1
        
        # Simulate API delay
        time.sleep(self.response_delay)
        
        # Simulate intermittent errors
        if self.simulate_errors and random.random() < 0.1:
            raise Exception("Mock Claude API error")
        
        # Return task-specific responses
        response_file_map = {
            "code": "code_response.txt",
            "multimedia": "multimedia_response.txt", 
            "rag": "rag_response.txt",
            "automation": "automation_response.txt",
            "analytics": "analytics_response.txt"
        }
        
        response_file = response_file_map.get(task_type, "code_response.txt")
        response_path = self.responses_dir / response_file
        
        if response_path.exists():
            with open(response_path, 'r') as f:
                return f.read()
        else:
            return f"Mock Claude response for {task_type} task. Prompt: {prompt[:100]}..."
    
    def is_available(self):
        """Check if Claude API is available."""
        if self.simulate_errors and random.random() < 0.05:
            return False
        return True
    
    def get_usage_stats(self):
        """Return mock usage statistics."""
        return {
            "total_calls": self.call_count,
            "total_tokens": self.call_count * 150,
            "cost_estimate": self.call_count * 0.01
        }

class MockOllamaProvider:
    """Mock Ollama provider for testing."""
    
    def __init__(self, simulate_errors=False, response_delay=0.2):
        self.simulate_errors = simulate_errors
        self.response_delay = response_delay
        self.call_count = 0
        self.available_models = ["qwen2.5-coder:7b", "llama3.2:3b"]
        self.responses_dir = Path(__file__).parent.parent / "data" / "responses"
        
    def query(self, prompt, model="qwen2.5-coder:7b", temperature=0.7):
        """Mock Ollama query."""
        self.call_count += 1
        
        # Simulate processing delay
        time.sleep(self.response_delay)
        
        # Simulate errors
        if self.simulate_errors and random.random() < 0.15:
            raise Exception("Mock Ollama connection error")
        
        if model not in self.available_models:
            raise Exception(f"Model {model} not available")
        
        # Return mock response
        ollama_response_file = self.responses_dir / "ollama_general.txt"
        if ollama_response_file.exists():
            with open(ollama_response_file, 'r') as f:
                return f.read()
        else:
            return f"Mock Ollama response using {model}. Input: {prompt[:50]}..."
    
    def is_available(self):
        """Check if Ollama service is available."""
        if self.simulate_errors and random.random() < 0.1:
            return False
        return True
    
    def list_models(self):
        """List available models."""
        return self.available_models
    
    def health_check(self):
        """Perform health check."""
        return {
            "status": "healthy" if self.is_available() else "unhealthy",
            "models_available": len(self.available_models),
            "total_calls": self.call_count
        }

class MockMemoryManager:
    """Mock memory manager for testing."""
    
    def __init__(self):
        self.memory_store = {}
        self.call_count = 0
        
    def get_context(self, prompt, task_type="general", limit=5):
        """Mock context retrieval."""
        self.call_count += 1
        
        # Return mock context based on task type
        mock_contexts = {
            "code": "Previous code task: Created a Python function for data processing",
            "multimedia": "Previous image analysis: Analyzed product images for e-commerce",
            "rag": "Previous document analysis: Summarized research papers on AI",
            "automation": "Previous automation: Created backup scripts for system maintenance",
            "analytics": "Previous analytics: Analyzed sales data and trends"
        }
        
        return mock_contexts.get(task_type, "No relevant context found")
    
    def save_task(self, prompt, response, task_type, metadata=None):
        """Mock task saving."""
        task_id = f"task_{len(self.memory_store)}"
        self.memory_store[task_id] = {
            "prompt": prompt,
            "response": response,
            "task_type": task_type,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        return task_id
    
    def get_stats(self):
        """Get memory statistics."""
        return {
            "total_tasks": len(self.memory_store),
            "retrieval_calls": self.call_count,
            "storage_size": sum(len(str(task)) for task in self.memory_store.values())
        }

class MockSystemMonitor:
    """Mock system monitor for testing."""
    
    def __init__(self):
        self.metrics_history = []
        
    def get_system_metrics(self):
        """Get mock system metrics."""
        metrics = {
            "cpu_percent": random.uniform(10, 80),
            "memory_percent": random.uniform(30, 70),
            "disk_usage": random.uniform(40, 90),
            "network_io": random.randint(1000, 10000),
            "timestamp": time.time()
        }
        self.metrics_history.append(metrics)
        return metrics
    
    def get_task_metrics(self):
        """Get mock task metrics."""
        return {
            "active_tasks": random.randint(0, 3),
            "completed_tasks": random.randint(50, 200),
            "failed_tasks": random.randint(0, 5),
            "avg_processing_time": random.uniform(5, 45)
        }

class MockAutonomousAgent:
    """Mock autonomous agent for testing."""
    
    def __init__(self, safety_mode=True):
        self.safety_mode = safety_mode
        self.action_history = []
        self.screenshot_count = 0
        
    def take_screenshot(self):
        """Mock screenshot capture."""
        self.screenshot_count += 1
        # Return mock screenshot data
        return f"mock_screenshot_{self.screenshot_count}.png"
    
    def analyze_screen(self, screenshot_path):
        """Mock screen analysis."""
        return {
            "elements_detected": ["button", "text_field", "menu"],
            "clickable_areas": [(100, 200), (300, 400)],
            "text_content": "Mock UI elements detected"
        }
    
    def execute_action(self, action_type, coordinates=None, text=None):
        """Mock action execution."""
        if self.safety_mode and action_type in ["delete", "format", "shutdown"]:
            raise Exception(f"Restricted action: {action_type}")
        
        action = {
            "type": action_type,
            "coordinates": coordinates,
            "text": text,
            "timestamp": time.time(),
            "success": True
        }
        self.action_history.append(action)
        return action
    
    def validate_action_safety(self, action):
        """Mock safety validation."""
        restricted_actions = ["rm -rf", "format", "delete", "sudo"]
        for restricted in restricted_actions:
            if restricted in str(action).lower():
                return False
        return True

def create_mock_app_instance():
    """Create a complete mock SuperMini app instance for testing."""
    mock_app = MagicMock()
    
    # Set up mock components
    mock_app.claude_provider = MockClaudeProvider()
    mock_app.ollama_provider = MockOllamaProvider()
    mock_app.memory_manager = MockMemoryManager()
    mock_app.system_monitor = MockSystemMonitor()
    mock_app.autonomous_agent = MockAutonomousAgent()
    
    # Mock GUI components
    mock_app.main_window = MagicMock()
    mock_app.task_processor = MagicMock()
    mock_app.settings = {
        "claude_api_key": "test_key",
        "output_directory": "/tmp/test_output",
        "memory_enabled": True,
        "auto_continue": False
    }
    
    return mock_app

# Factory functions for easy test setup
def get_mock_claude(simulate_errors=False):
    """Get Claude mock with optional error simulation."""
    return MockClaudeProvider(simulate_errors=simulate_errors)

def get_mock_ollama(simulate_errors=False):
    """Get Ollama mock with optional error simulation."""
    return MockOllamaProvider(simulate_errors=simulate_errors)

def get_mock_memory():
    """Get memory manager mock."""
    return MockMemoryManager()

def get_mock_autonomous(safety_mode=True):
    """Get autonomous agent mock."""
    return MockAutonomousAgent(safety_mode=safety_mode)