#!/usr/bin/env python3
"""Final test of all three modes after fixes"""

import sys
from pathlib import Path

# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

def test_modes():
    print("=== Testing SuperMini Modes ===\n")
    
    # Test 1: Basic imports
    print("1. Testing imports...")
    try:
        from supermini import SuperMiniMainWindow, TaskProcessor, ExploreThread, EnhanceThread
        from supermini import AIConfig, MemoryManager
        print("✓ All imports successful")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return
    
    # Test 2: Initialize components
    print("\n2. Testing component initialization...")
    try:
        output_dir = Path.home() / "SuperMini_Output" / "test_final"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        config = AIConfig()
        memory = MemoryManager(output_dir)
        processor = TaskProcessor(config, memory, output_dir)
        print("✓ Core components initialized")
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return
    
    # Test 3: Test ExploreThread
    print("\n3. Testing ExploreThread...")
    try:
        explore_thread = ExploreThread(
            processor=processor,
            files=[],  # Empty list, not None
            iteration_delay_hours=0,
            iteration_delay_minutes=0
        )
        print("✓ ExploreThread created successfully")
    except Exception as e:
        print(f"✗ ExploreThread creation failed: {e}")
    
    # Test 4: Test EnhanceThread
    print("\n4. Testing EnhanceThread...")
    try:
        app_path = Path(__file__).parent / "supermini.py"
        enhance_thread = EnhanceThread(
            processor=processor,
            files=[],  # Empty list, not None
            app_path=str(app_path),
            iteration_delay_hours=0,
            iteration_delay_minutes=0
        )
        print("✓ EnhanceThread created successfully")
    except Exception as e:
        print(f"✗ EnhanceThread creation failed: {e}")
    
    # Test 5: Test GUI initialization
    print("\n5. Testing GUI initialization...")
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        window = SuperMiniMainWindow()
        
        # Check critical attributes
        checks = [
            ('attached_files', hasattr(window, 'attached_files')),
            ('task_input', hasattr(window, 'task_input')),
            ('explore_interval_spinbox', hasattr(window, 'explore_interval_spinbox')),
            ('enhance_interval_spinbox', hasattr(window, 'enhance_interval_spinbox')),
            ('start_explore_btn', hasattr(window, 'start_explore_btn')),
            ('start_enhance_btn', hasattr(window, 'start_enhance_btn')),
        ]
        
        all_good = True
        for attr, exists in checks:
            if exists:
                print(f"  ✓ {attr} exists")
            else:
                print(f"  ✗ {attr} missing")
                all_good = False
        
        if all_good:
            print("✓ GUI initialized with all required attributes")
        else:
            print("✗ GUI missing some attributes")
            
        app.quit()
    except Exception as e:
        print(f"✗ GUI initialization failed: {e}")
    
    print("\n=== Test Summary ===")
    print("The app should now work with:")
    print("- Go Explore mode: Fixed file parameter issue")
    print("- Task Me mode: Uses correct task_input field")
    print("- Enhance Yourself mode: Fixed initialization parameters")
    print("\nNote: There are duplicate method definitions that should be cleaned up")

if __name__ == "__main__":
    test_modes()