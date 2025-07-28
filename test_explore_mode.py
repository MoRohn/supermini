#!/usr/bin/env python3
"""Test script to directly test the exploration mode functionality"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from supermini import TaskProcessor, ExploreThread
    from PyQt6.QtCore import QCoreApplication, QThread
    from PyQt6.QtWidgets import QApplication
    import signal
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    
    # Create processor
    processor = TaskProcessor()
    
    # Create explore thread
    explore_thread = ExploreThread(
        processor=processor,
        files=[],
        iteration_delay_hours=0,
        iteration_delay_minutes=1  # 1 minute for testing
    )
    
    # Connect signals
    def on_result(result, files, iteration):
        print(f"\n=== EXPLORATION RESULT (Iteration {iteration}) ===")
        print(f"Result: {result}")
        print(f"Files: {files}")
        print("=" * 50)
    
    def on_error(error):
        print(f"\n!!! EXPLORATION ERROR !!!")
        print(f"Error: {error}")
        print("!" * 50)
        app.quit()
    
    def on_progress(progress):
        print(f"Progress: {progress}%")
    
    explore_thread.result_signal.connect(on_result)
    explore_thread.error_signal.connect(on_error)
    explore_thread.progress_signal.connect(on_progress)
    
    # Start exploration
    print("Starting exploration thread...")
    explore_thread.start()
    
    # Run for a short time then exit
    import threading
    def stop_after_delay():
        import time
        time.sleep(30)  # Run for 30 seconds
        print("\nStopping exploration...")
        explore_thread.stop()
        app.quit()
    
    timer_thread = threading.Thread(target=stop_after_delay)
    timer_thread.daemon = True
    timer_thread.start()
    
    sys.exit(app.exec())
    
except Exception as e:
    logging.error(f"Test failed with error: {e}", exc_info=True)
    sys.exit(1)