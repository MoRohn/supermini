#!/usr/bin/env python3
"""
Test SuperMiniMainWindow initialization steps one by one to identify crash point
"""

import sys
import os
sys.path.insert(0, '/Users/rohnspringfield/supermini')

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

# Import the real SuperMiniMainWindow but override the init
import importlib.util
spec = importlib.util.spec_from_file_location("supermini", "/Users/rohnspringfield/supermini/supermini.py")
supermini_module = importlib.util.module_from_spec(spec)
sys.modules['supermini'] = supermini_module
spec.loader.exec_module(supermini_module)

class SuperMiniStepTest(supermini_module.SuperMiniMainWindow):
    def __init__(self):
        print("DEBUG: Starting step-by-step initialization test")
        
        # Step 1: Basic QMainWindow init
        try:
            print("STEP 1: QMainWindow.__init__")
            QMainWindow.__init__(self)
            print("✅ STEP 1 passed")
        except Exception as e:
            print(f"❌ STEP 1 failed: {e}")
            raise
        
        # Step 2: Basic properties
        try:
            print("STEP 2: Setting basic properties")
            self.setWindowTitle("SuperMini Test")
            self.setGeometry(100, 100, 800, 600)
            print("✅ STEP 2 passed")
        except Exception as e:
            print(f"❌ STEP 2 failed: {e}")
            raise
        
        # Step 3: Thread variables
        try:
            print("STEP 3: Setting up thread variables")
            self.explore_thread = None
            self.enhance_thread = None
            self.task_thread = None
            self.attached_files = []
            print("✅ STEP 3 passed")
        except Exception as e:
            print(f"❌ STEP 3 failed: {e}")
            raise
        
        # Step 4: Directories
        try:
            print("STEP 4: Setting up directories")
            self.setup_directories()
            print("✅ STEP 4 passed")
        except Exception as e:
            print(f"❌ STEP 4 failed: {e}")
            # Don't raise, continue to next step
            print("Continuing to next step...")
        
        # Step 5: Config
        try:
            print("STEP 5: Loading config")
            self.load_config()
            print("✅ STEP 5 passed")
        except Exception as e:
            print(f"❌ STEP 5 failed: {e}")
            print("Continuing to next step...")
        
        # Step 6: Processors (likely problematic)
        try:
            print("STEP 6: Setting up processors")
            self.setup_processors()
            print("✅ STEP 6 passed")
        except Exception as e:
            print(f"❌ STEP 6 failed: {e}")
            print("Skipping remaining steps due to processor failure")
            return
        
        print("All tested steps completed - creating minimal UI instead of full setup")
        
        # Create minimal UI instead of full setup_ui
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        label = QLabel("SuperMini Step Test - Initialization Successful!")
        layout.addWidget(label)
        central_widget.setLayout(layout)

def main():
    try:
        print("Starting SuperMini step-by-step test...")
        app = QApplication(sys.argv)
        print("QApplication created")
        
        print("Creating step test window...")
        window = SuperMiniStepTest()
        print("Step test window created")
        
        print("Showing window...")
        window.show()
        print("Window shown - app should stay open now")
        
        result = app.exec()
        print(f"App finished with result: {result}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()