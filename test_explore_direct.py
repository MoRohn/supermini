#!/usr/bin/env python3
"""Direct test of exploration functionality"""

import logging
import sys
from pathlib import Path
from dataclasses import dataclass
from PyQt6.QtCore import QSettings

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import SuperMini components
sys.path.insert(0, str(Path(__file__).parent))

from supermini import AIConfig, MemoryManager, TaskProcessor, ExploreThread
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

try:
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create output directory
    output_dir = Path.home() / "SuperMini_Output" / "test_explore"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize AI config
    config = AIConfig(
        use_claude=True,
        claude_api_key="",  # Will use from settings if available
        ollama_url="http://localhost:11434",
        ollama_model="qwen2.5-coder:7b",
        max_tokens=4096,
        temperature=0.7
    )
    
    # Try to load Claude API key from settings
    settings = QSettings()
    claude_key = settings.value("claude_api_key", "")
    if claude_key:
        config.claude_api_key = claude_key
    
    # Initialize memory manager
    memory = MemoryManager(output_dir)
    
    # Initialize task processor
    processor = TaskProcessor(config, memory, output_dir)
    
    print("TaskProcessor initialized successfully!")
    
    # Create exploration thread
    explore_thread = ExploreThread(
        processor=processor,
        files=[],
        iteration_delay_hours=0,
        iteration_delay_minutes=0  # No delay for testing
    )
    
    # Connect signals
    def on_result(result, files, iteration):
        print(f"\n{'='*60}")
        print(f"EXPLORATION RESULT - Iteration {iteration}")
        print(f"{'='*60}")
        print(f"Result: {result[:500]}..." if len(result) > 500 else f"Result: {result}")
        print(f"Files generated: {files}")
        print(f"{'='*60}\n")
        
        # Stop after first iteration for testing
        explore_thread.stop()
        app.quit()
    
    def on_error(error):
        print(f"\n{'!'*60}")
        print(f"EXPLORATION ERROR")
        print(f"{'!'*60}")
        print(f"Error: {error}")
        print(f"{'!'*60}\n")
        app.quit()
    
    def on_progress(progress):
        print(f"Progress: {progress}%")
    
    explore_thread.result_signal.connect(on_result)
    explore_thread.error_signal.connect(on_error)
    explore_thread.progress_signal.connect(on_progress)
    
    # Start exploration
    print("\nStarting exploration thread...")
    print("This will run one iteration and then stop.\n")
    explore_thread.start()
    
    # Run the app
    sys.exit(app.exec())
    
except Exception as e:
    logging.error(f"Test failed: {e}", exc_info=True)
    sys.exit(1)