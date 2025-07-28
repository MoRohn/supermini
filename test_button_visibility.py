#!/usr/bin/env python3
"""
Test script to specifically check button visibility and layout in the Explore and Enhance tabs
"""

import sys
import os
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_button_visibility():
    """Test button visibility and layout positioning"""
    print("🔍 Testing Button Visibility and Layout...")
    
    try:
        # Import the application
        import supermini
        from PyQt6.QtWidgets import QApplication, QTabWidget, QPushButton
        from PyQt6.QtCore import Qt
        
        # Create application instance
        app = QApplication(sys.argv)
        
        # Create the main window
        window = supermini.SuperMiniMainWindow()
        window.show()  # Actually show the window for proper visibility testing
        
        print("✅ Application window created successfully")
        
        # Find the mode tabs widget
        mode_tabs = None
        all_tab_widgets = window.findChildren(QTabWidget)
        
        for tab_widget in all_tab_widgets:
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
        
        # Test Explore Tab
        print("\n🧭 Testing EXPLORE Tab Layout:")
        explore_tab_index = None
        for i in range(mode_tabs.count()):
            if 'explore' in mode_tabs.tabText(i).lower():
                explore_tab_index = i
                break
        
        if explore_tab_index is not None:
            mode_tabs.setCurrentIndex(explore_tab_index)
            explore_widget = mode_tabs.currentWidget()
            
            # Check widget hierarchy
            print(f"   Explore tab widget type: {type(explore_widget).__name__}")
            print(f"   Explore tab visible: {explore_widget.isVisible()}")
            print(f"   Explore tab enabled: {explore_widget.isEnabled()}")
            
            # Find all buttons in explore tab
            explore_buttons = explore_widget.findChildren(QPushButton)
            print(f"   Total buttons found: {len(explore_buttons)}")
            
            for i, btn in enumerate(explore_buttons):
                btn_text = btn.text()
                btn_visible = btn.isVisible()
                btn_enabled = btn.isEnabled()
                btn_geometry = btn.geometry()
                print(f"   Button {i+1}: '{btn_text}' | Visible: {btn_visible} | Enabled: {btn_enabled} | Geo: {btn_geometry.width()}x{btn_geometry.height()}")
        
        # Test Enhance Tab
        print("\n⚡ Testing ENHANCE Tab Layout:")
        enhance_tab_index = None
        for i in range(mode_tabs.count()):
            if 'enhance' in mode_tabs.tabText(i).lower():
                enhance_tab_index = i
                break
        
        if enhance_tab_index is not None:
            mode_tabs.setCurrentIndex(enhance_tab_index)
            enhance_widget = mode_tabs.currentWidget()
            
            # Check widget hierarchy
            print(f"   Enhance tab widget type: {type(enhance_widget).__name__}")
            print(f"   Enhance tab visible: {enhance_widget.isVisible()}")
            print(f"   Enhance tab enabled: {enhance_widget.isEnabled()}")
            
            # Find all buttons in enhance tab
            enhance_buttons = enhance_widget.findChildren(QPushButton)
            print(f"   Total buttons found: {len(enhance_buttons)}")
            
            for i, btn in enumerate(enhance_buttons):
                btn_text = btn.text()
                btn_visible = btn.isVisible()
                btn_enabled = btn.isEnabled()
                btn_geometry = btn.geometry()
                print(f"   Button {i+1}: '{btn_text}' | Visible: {btn_visible} | Enabled: {btn_enabled} | Geo: {btn_geometry.width()}x{btn_geometry.height()}")
        
        # Test access to specific button attributes
        print("\n🔗 Testing Direct Button Access:")
        
        button_attrs = [
            'start_explore_btn', 'stop_explore_btn',
            'start_enhance_btn', 'stop_enhance_btn'
        ]
        
        for attr_name in button_attrs:
            if hasattr(window, attr_name):
                button = getattr(window, attr_name)
                if button:
                    print(f"   ✅ {attr_name}: Text='{button.text()}' | Visible={button.isVisible()} | Enabled={button.isEnabled()}")
                    print(f"      Parent: {type(button.parent()).__name__} | Geometry: {button.geometry().width()}x{button.geometry().height()}")
                else:
                    print(f"   ❌ {attr_name}: Button is None")
            else:
                print(f"   ❌ {attr_name}: Attribute missing")
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Button Visibility Test")
    print("=" * 50)
    
    result = test_button_visibility()
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 Button visibility test completed!")
    else:
        print("⚠️ Button visibility test failed!")
    
    sys.exit(0 if result else 1)