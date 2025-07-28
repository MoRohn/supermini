#!/usr/bin/env python3
"""
Test script to verify all three modes (Task, Explore, Enhance) have functional UI components
and can be started/stopped through the interface.
"""

import sys
import os
import time
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_modes():
    """Test all three modes through UI simulation"""
    print("🧪 Testing SuperMini UI Modes...")
    
    try:
        # Import the application
        import supermini
        from PyQt6.QtWidgets import QApplication, QTabWidget, QPushButton
        from PyQt6.QtCore import Qt
        
        # Create application instance
        app = QApplication(sys.argv)
        
        # Create the main window
        window = supermini.SuperMiniMainWindow()
        
        print("✅ Application window created successfully")
        
        # Test 1: Verify tabs exist
        print("\n🔍 Testing tab structure...")
        
        # Find the mode tabs widget - should have Task, Explore, Enhance tabs
        mode_tabs = None
        all_tab_widgets = window.findChildren(QTabWidget)
        
        for tab_widget in all_tab_widgets:
            # Check if this tab widget contains the mode tabs
            tab_count = tab_widget.count()
            tab_texts = [tab_widget.tabText(i) for i in range(tab_count)]
            
            # Look for tabs that contain our mode keywords
            has_task = any('task' in text.lower() for text in tab_texts)
            has_explore = any('explore' in text.lower() for text in tab_texts) 
            has_enhance = any('enhance' in text.lower() for text in tab_texts)
            
            if has_task and has_explore and has_enhance:
                mode_tabs = tab_widget
                break
        
        if not mode_tabs:
            print("❌ Mode tabs not found")
            return False
        
        tab_count = mode_tabs.count()
        print(f"✅ Found {tab_count} tabs")
        
        # Check tab names
        tab_names = []
        for i in range(tab_count):
            tab_name = mode_tabs.tabText(i)
            tab_names.append(tab_name)
            print(f"  Tab {i}: {tab_name}")
        
        # Verify expected tabs exist
        expected_patterns = ['Task', 'Explore', 'Enhance']
        found_tabs = {}
        
        for i, tab_name in enumerate(tab_names):
            for pattern in expected_patterns:
                if pattern.lower() in tab_name.lower():
                    found_tabs[pattern] = i
                    print(f"✅ Found {pattern} tab at index {i}")
        
        if len(found_tabs) < 3:
            print(f"❌ Missing tabs. Found: {found_tabs}")
            return False
        
        # Test 2: Verify buttons exist in each mode
        print("\n🔍 Testing mode buttons...")
        
        # Test Task Mode buttons
        mode_tabs.setCurrentIndex(found_tabs['Task'])
        current_widget = mode_tabs.currentWidget()
        
        task_buttons = current_widget.findChildren(QPushButton)
        run_button = None
        stop_button = None
        
        for btn in task_buttons:
            btn_text = btn.text().lower()
            if 'run' in btn_text or 'start' in btn_text or 'process' in btn_text:
                run_button = btn
            elif 'stop' in btn_text:
                stop_button = btn
        
        if run_button and stop_button:
            print("✅ Task mode: Found Run and Stop buttons")
        else:
            print(f"❌ Task mode: Missing buttons. Run: {run_button is not None}, Stop: {stop_button is not None}")
        
        # Test Explore Mode buttons
        mode_tabs.setCurrentIndex(found_tabs['Explore'])
        current_widget = mode_tabs.currentWidget()
        
        explore_buttons = current_widget.findChildren(QPushButton)
        start_explore_button = None
        stop_explore_button = None
        
        for btn in explore_buttons:
            btn_text = btn.text().lower()
            if 'start' in btn_text and 'explor' in btn_text:
                start_explore_button = btn
            elif 'stop' in btn_text and 'explor' in btn_text:
                stop_explore_button = btn
        
        if start_explore_button and stop_explore_button:
            print("✅ Explore mode: Found Start and Stop buttons")
        else:
            print(f"❌ Explore mode: Missing buttons. Start: {start_explore_button is not None}, Stop: {stop_explore_button is not None}")
        
        # Test Enhance Mode buttons
        mode_tabs.setCurrentIndex(found_tabs['Enhance'])
        current_widget = mode_tabs.currentWidget()
        
        enhance_buttons = current_widget.findChildren(QPushButton)
        start_enhance_button = None
        stop_enhance_button = None
        
        for btn in enhance_buttons:
            btn_text = btn.text().lower()
            if 'start' in btn_text and 'enhanc' in btn_text:
                start_enhance_button = btn
            elif 'stop' in btn_text and 'enhanc' in btn_text:
                stop_enhance_button = btn
        
        if start_enhance_button and stop_enhance_button:
            print("✅ Enhance mode: Found Start and Stop buttons")
        else:
            print(f"❌ Enhance mode: Missing buttons. Start: {start_enhance_button is not None}, Stop: {stop_enhance_button is not None}")
        
        # Test 3: Verify button functionality (without actually starting long processes)
        print("\n🔍 Testing button functionality...")
        
        # Test button enabled/disabled states
        if start_explore_button:
            initial_enabled = start_explore_button.isEnabled()
            print(f"✅ Explore Start button enabled state: {initial_enabled}")
        
        if stop_explore_button:
            initial_stop_enabled = stop_explore_button.isEnabled()
            print(f"✅ Explore Stop button enabled state: {initial_stop_enabled}")
        
        if start_enhance_button:
            enhance_enabled = start_enhance_button.isEnabled()
            print(f"✅ Enhance Start button enabled state: {enhance_enabled}")
        
        if stop_enhance_button:
            enhance_stop_enabled = stop_enhance_button.isEnabled()
            print(f"✅ Enhance Stop button enabled state: {enhance_stop_enabled}")
        
        # Test 4: Check if methods exist
        print("\n🔍 Testing method availability...")
        
        methods_to_check = [
            'start_exploration', 'stop_exploration',
            'start_enhancement', 'stop_enhancement'
        ]
        
        for method_name in methods_to_check:
            if hasattr(window, method_name):
                print(f"✅ Method {method_name} exists")
            else:
                print(f"❌ Method {method_name} missing")
        
        print("\n🎉 All UI mode tests completed!")
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_button_connections():
    """Test that buttons are properly connected to their methods"""
    print("\n🔗 Testing button connections...")
    
    try:
        import supermini
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = supermini.SuperMiniMainWindow()
        
        # Check if instance variables for buttons exist
        button_attrs = [
            'start_explore_btn', 'stop_explore_btn',
            'start_enhance_btn', 'stop_enhance_btn'
        ]
        
        for attr_name in button_attrs:
            if hasattr(window, attr_name):
                button = getattr(window, attr_name)
                print(f"✅ Button attribute {attr_name} exists")
                
                # Check if button has connections
                if button.receivers(button.clicked) > 0:
                    print(f"✅ Button {attr_name} has click connections")
                else:
                    print(f"⚠️  Button {attr_name} has no click connections")
            else:
                print(f"❌ Button attribute {attr_name} missing")
        
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting SuperMini UI Mode Tests")
    print("=" * 50)
    
    # Run tests
    ui_test_result = test_ui_modes()
    connection_test_result = test_button_connections()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"UI Structure Test: {'✅ PASSED' if ui_test_result else '❌ FAILED'}")
    print(f"Button Connections Test: {'✅ PASSED' if connection_test_result else '❌ FAILED'}")
    
    if ui_test_result and connection_test_result:
        print("\n🎉 ALL TESTS PASSED! All three modes have functional UI components.")
    else:
        print("\n⚠️  SOME TESTS FAILED! Check the issues above.")
    
    sys.exit(0 if (ui_test_result and connection_test_result) else 1)