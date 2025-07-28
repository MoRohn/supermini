#!/usr/bin/env python3
"""Quick test of all three modes"""

import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from supermini import SuperMiniMainWindow

def test_all_modes():
    app = QApplication(sys.argv)
    window = SuperMiniMainWindow()
    window.show()
    
    test_results = []
    
    def test_explore_mode():
        print("\n=== Testing Go Explore Mode ===")
        try:
            # Switch to explore tab
            window.mode_tabs.setCurrentIndex(1)
            QTest.qWait(500)
            
            # Set interval to minimum (5 seconds)
            if hasattr(window, 'explore_interval_spinbox'):
                window.explore_interval_spinbox.setValue(5)
                print("✓ Set interval to 5 seconds")
            
            # Click start
            if hasattr(window, 'start_explore_btn'):
                QTest.mouseClick(window.start_explore_btn, Qt.MouseButton.LeftButton)
                print("✓ Started exploration")
                
                # Wait a bit
                QTest.qWait(2000)
                
                # Check if thread started
                if hasattr(window, 'explore_thread') and window.explore_thread and window.explore_thread.isRunning():
                    print("✓ Exploration thread is running!")
                    test_results.append(("Go Explore", "PASS"))
                    
                    # Stop it
                    if hasattr(window, 'stop_explore_btn'):
                        QTest.mouseClick(window.stop_explore_btn, Qt.MouseButton.LeftButton)
                        print("✓ Stopped exploration")
                else:
                    print("✗ Exploration thread did not start")
                    test_results.append(("Go Explore", "FAIL - Thread not running"))
            else:
                print("✗ start_explore_btn not found")
                test_results.append(("Go Explore", "FAIL - Button not found"))
                
        except Exception as e:
            print(f"✗ Exception: {e}")
            test_results.append(("Go Explore", f"FAIL - {e}"))
    
    def test_task_mode():
        print("\n=== Testing Task Me Mode ===")
        try:
            # Switch to task tab
            window.mode_tabs.setCurrentIndex(0)
            QTest.qWait(500)
            
            # Enter a simple prompt
            if hasattr(window, 'task_input'):
                window.task_input.setPlainText("Write a hello world Python script")
                print("✓ Entered test prompt")
                
                # Click process
                if hasattr(window, 'process_btn'):
                    QTest.mouseClick(window.process_btn, Qt.MouseButton.LeftButton)
                    print("✓ Started task processing")
                    
                    # Wait a bit
                    QTest.qWait(3000)
                    
                    # Check results
                    if hasattr(window, 'results_text'):
                        results = window.results_text.toPlainText()
                        if results and len(results) > 10:
                            print("✓ Got results")
                            test_results.append(("Task Me", "PASS"))
                        else:
                            print("✗ No results")
                            test_results.append(("Task Me", "FAIL - No results"))
                else:
                    print("✗ process_btn not found")
                    test_results.append(("Task Me", "FAIL - Button not found"))
            else:
                print("✗ prompt_text not found")
                test_results.append(("Task Me", "FAIL - Prompt field not found"))
                
        except Exception as e:
            print(f"✗ Exception: {e}")
            test_results.append(("Task Me", f"FAIL - {e}"))
    
    def test_enhance_mode():
        print("\n=== Testing Enhance Yourself Mode ===")
        try:
            # Switch to enhance tab
            window.mode_tabs.setCurrentIndex(2)
            QTest.qWait(500)
            
            # Set interval to minimum (30 seconds)
            if hasattr(window, 'enhance_interval_spinbox'):
                window.enhance_interval_spinbox.setValue(30)
                print("✓ Set interval to 30 seconds")
            
            # Click start
            if hasattr(window, 'start_enhance_btn'):
                QTest.mouseClick(window.start_enhance_btn, Qt.MouseButton.LeftButton)
                print("✓ Started enhancement")
                
                # Wait a bit
                QTest.qWait(2000)
                
                # Check if thread started
                if hasattr(window, 'enhance_thread') and window.enhance_thread and window.enhance_thread.isRunning():
                    print("✓ Enhancement thread is running!")
                    test_results.append(("Enhance Yourself", "PASS"))
                    
                    # Stop it
                    if hasattr(window, 'stop_enhance_btn'):
                        QTest.mouseClick(window.stop_enhance_btn, Qt.MouseButton.LeftButton)
                        print("✓ Stopped enhancement")
                else:
                    print("✗ Enhancement thread did not start")
                    test_results.append(("Enhance Yourself", "FAIL - Thread not running"))
            else:
                print("✗ start_enhance_btn not found")
                test_results.append(("Enhance Yourself", "FAIL - Button not found"))
                
        except Exception as e:
            print(f"✗ Exception: {e}")
            test_results.append(("Enhance Yourself", f"FAIL - {e}"))
    
    def run_all_tests():
        test_explore_mode()
        QTest.qWait(1000)
        
        test_task_mode()
        QTest.qWait(1000)
        
        test_enhance_mode()
        QTest.qWait(1000)
        
        # Print summary
        print("\n=== TEST SUMMARY ===")
        for mode, result in test_results:
            print(f"{mode}: {result}")
        
        # Exit
        app.quit()
    
    # Run tests after window is shown
    QTimer.singleShot(2000, run_all_tests)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_all_modes()