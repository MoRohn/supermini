#!/usr/bin/env python3
"""Test the GUI exploration mode with automated button clicking"""

import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from supermini import SuperMiniMainWindow

def test_explore_mode():
    app = QApplication(sys.argv)
    window = SuperMiniMainWindow()
    window.show()
    
    def run_test():
        try:
            print("=== Testing Go Explore Mode ===")
            
            # Switch to explore tab
            print("1. Switching to Go Explore tab...")
            window.mode_tabs.setCurrentIndex(1)  # Index 1 is Go Explore
            QTest.qWait(500)
            
            # Check if buttons exist
            if hasattr(window, 'start_explore_btn'):
                print("2. Found start_explore_btn")
                
                # Set interval to 0 for immediate testing
                if hasattr(window, 'explore_interval_spinbox'):
                    print("3. Setting interval to 1 minute...")
                    window.explore_interval_spinbox.setValue(1)
                else:
                    print("3. Warning: explore_interval_spinbox not found")
                
                # Click start exploration
                print("4. Clicking Start Exploration...")
                QTest.mouseClick(window.start_explore_btn, Qt.MouseButton.LeftButton)
                
                # Wait a moment
                QTest.qWait(2000)
                
                # Check status
                if hasattr(window, 'exploration_status'):
                    status = window.exploration_status.text()
                    print(f"5. Exploration status: {status}")
                
                # Check if exploration thread started
                if hasattr(window, 'explore_thread') and window.explore_thread:
                    print("6. Exploration thread is running!")
                    
                    # Wait for some results
                    print("7. Waiting for results...")
                    QTest.qWait(5000)
                    
                    # Stop exploration
                    if hasattr(window, 'stop_explore_btn') and window.stop_explore_btn.isEnabled():
                        print("8. Clicking Stop Exploration...")
                        QTest.mouseClick(window.stop_explore_btn, Qt.MouseButton.LeftButton)
                else:
                    print("6. ERROR: Exploration thread did not start!")
                    
            else:
                print("ERROR: start_explore_btn not found!")
                
            # Check for any error messages
            if hasattr(window, 'results_text'):
                results = window.results_text.toPlainText()
                if "Error" in results:
                    print(f"\nERROR FOUND IN RESULTS:\n{results}")
                    
        except Exception as e:
            print(f"\nEXCEPTION OCCURRED: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Exit after test
            QTimer.singleShot(1000, app.quit)
    
    # Run test after window is shown
    QTimer.singleShot(1000, run_test)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_explore_mode()