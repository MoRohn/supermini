#!/usr/bin/env python3
"""
Test script for button adaptiveness and scaling validation.
This script tests the enhanced responsive button system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen
import logging

# Import our enhanced theme
try:
    from supermini import ModernTheme
    print("✅ Successfully imported ModernTheme")
except ImportError as e:
    print(f"❌ Failed to import ModernTheme: {e}")
    sys.exit(1)

class ButtonTestWindow(QMainWindow):
    """Test window for validating button responsiveness"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧪 Button Responsiveness Test")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup test UI with various button configurations"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Test different button types
        self.create_button_test_section(main_layout, "Compact Buttons", "compact")
        self.create_button_test_section(main_layout, "Default Buttons", "default")
        self.create_button_test_section(main_layout, "Large Buttons", "large")
        self.create_button_test_section(main_layout, "Primary Buttons", "primary")
        self.create_button_test_section(main_layout, "Hero Buttons", "hero")
        
        # Test different contexts
        self.create_context_test_section(main_layout)
        
        # Test different variants
        self.create_variant_test_section(main_layout)
        
        central_widget.setLayout(main_layout)
    
    def create_button_test_section(self, parent_layout, title: str, button_type: str):
        """Create a test section for a specific button type"""
        # Section label
        label = QLabel(f"📊 {title}")
        label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00ff88;")
        parent_layout.addWidget(label)
        
        # Button container
        button_layout = QHBoxLayout()
        
        # Create test buttons
        btn1 = QPushButton("Test Button 1")
        btn2 = QPushButton("Test Button 2")
        btn3 = QPushButton("Disabled Button")
        btn3.setEnabled(False)
        
        # Apply responsive properties
        for btn in [btn1, btn2, btn3]:
            ModernTheme.apply_responsive_button_properties(btn, button_type, "main", "default")
        
        # Setup container
        buttons_list = [btn1, btn2, btn3]
        ModernTheme.setup_responsive_button_container(button_layout, buttons_list, 600)
        
        button_layout.addWidget(btn1)
        button_layout.addWidget(btn2)
        button_layout.addWidget(btn3)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
    
    def create_context_test_section(self, parent_layout):
        """Test different button contexts"""
        label = QLabel("🎯 Context Testing")
        label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00ff88;")
        parent_layout.addWidget(label)
        
        contexts = ["sidebar", "dialog", "main", "fullscreen"]
        for context in contexts:
            context_layout = QHBoxLayout()
            context_label = QLabel(f"{context.title()}:")
            context_label.setMinimumWidth(100)
            
            btn = QPushButton(f"{context.title()} Button")
            ModernTheme.apply_responsive_button_properties(btn, "default", context, "default")
            
            context_layout.addWidget(context_label)
            context_layout.addWidget(btn)
            context_layout.addStretch()
            
            parent_layout.addLayout(context_layout)
    
    def create_variant_test_section(self, parent_layout):
        """Test different button variants"""
        label = QLabel("🎨 Variant Testing")
        label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00ff88;")
        parent_layout.addWidget(label)
        
        variant_layout = QHBoxLayout()
        
        variants = [
            ("default", "Default"),
            ("primary", "Primary"),
            ("danger", "Danger"),
            ("success", "Success")
        ]
        
        for variant_key, variant_name in variants:
            btn = QPushButton(variant_name)
            ModernTheme.apply_responsive_button_properties(btn, "default", "main", variant_key)
            variant_layout.addWidget(btn)
        
        variant_layout.addStretch()
        parent_layout.addLayout(variant_layout)

def test_scaling_functionality():
    """Test core scaling functionality"""
    print("🔍 Testing scaling functionality...")
    
    # Test basic scaling
    base_value = 44
    scaled = ModernTheme.scale_value(base_value)
    print(f"   Base value: {base_value}px → Scaled: {scaled}px")
    
    # Test button size calculation
    size_config = ModernTheme.get_responsive_button_size("default", "main")
    print(f"   Default button size: {size_config}")
    
    # Test adaptive spacing
    spacing_config = ModernTheme.get_adaptive_button_spacing(600, 3)
    print(f"   Adaptive spacing (600px, 3 buttons): {spacing_config}")
    
    print("✅ Scaling functionality tests passed")

def test_button_responsiveness():
    """Test button responsiveness across different scenarios"""
    print("🔍 Testing button responsiveness...")
    
    # Test different container widths
    widths = [300, 500, 800, 1200]
    for width in widths:
        spacing = ModernTheme.get_adaptive_button_spacing(width, 2)
        print(f"   Width {width}px: gap={spacing['gap']}px, layout={spacing['layout_direction']}")
    
    # Test accessibility mode impact
    print("   Testing accessibility adjustments...")
    normal_size = ModernTheme.get_responsive_button_size("default", "main")
    
    # Simulate accessibility mode
    ModernTheme._accessibility_mode = True
    accessible_size = ModernTheme.get_responsive_button_size("default", "main")
    ModernTheme._accessibility_mode = False  # Reset
    
    print(f"   Normal: {normal_size['min_height']}px → Accessible: {accessible_size['min_height']}px")
    
    print("✅ Button responsiveness tests passed")

def run_visual_test():
    """Run visual test with GUI"""
    print("🎨 Running visual test...")
    
    app = QApplication(sys.argv)
    
    # Initialize theme with current app
    ModernTheme.initialize_scaling(app)
    
    # Create and show test window
    window = ButtonTestWindow()
    
    # Apply the full theme style
    style = f"""
    {ModernTheme.get_main_window_style()}
    {ModernTheme.get_button_style()}
    {ModernTheme.get_accessibility_style()}
    """
    window.setStyleSheet(style)
    
    window.show()
    
    print("✅ Visual test window displayed")
    print("   Please verify:")
    print("   - Buttons scale appropriately for your screen")
    print("   - Different button types have proper sizing")
    print("   - Hover and focus states work correctly")
    print("   - Spacing is consistent and readable")
    
    # Don't exec() - just show and return for testing
    app.processEvents()
    return app, window

def main():
    """Main test function"""
    print("🚀 Starting Button Responsiveness Tests")
    print("=" * 50)
    
    try:
        # Test 1: Core functionality
        test_scaling_functionality()
        print()
        
        # Test 2: Responsiveness
        test_button_responsiveness()
        print()
        
        # Test 3: Visual validation
        app, window = run_visual_test()
        print()
        
        print("✅ All button responsiveness tests completed successfully!")
        print("   The visual test window is now displayed for manual verification.")
        
        # Keep window open for manual testing
        input("Press Enter to close the test window...")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)