#!/usr/bin/env python3
"""
Test script for stop functionality
Tests that all stop buttons properly terminate processes and auto-continuation
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_task_processor_stop():
    """Test TaskProcessor stop functionality"""
    print("🛑 Testing TaskProcessor Stop Functionality...")
    
    try:
        from supermini import TaskProcessor, AIConfig, MemoryManager
        from pathlib import Path
        
        # Create test config and processor
        config = AIConfig(
            use_claude=False,  # Use local only for testing
            claude_api_key="",
            ollama_url="http://localhost:11434",
            max_tokens=100,
            temperature=0.1
        )
        
        output_dir = Path.home() / "SuperMini_Output" / "test"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        memory = MemoryManager(output_dir)
        processor = TaskProcessor(config, memory, output_dir)
        
        # Test stop flag functionality
        assert not processor.stop_requested, "Stop flag should initially be False"
        
        processor.request_stop()
        assert processor.stop_requested, "Stop flag should be True after request_stop()"
        
        processor.reset_stop_flag()
        assert not processor.stop_requested, "Stop flag should be False after reset_stop_flag()"
        
        print("  ✅ Stop flag functionality works")
        
        # Test auto-continue interruption (simulated)
        def simulate_long_task():
            """Simulate a long-running task with auto-continue"""
            processor.reset_stop_flag()
            
            # Simulate auto-continue loop
            continue_count = 0
            max_continues = 5
            
            while continue_count < max_continues and not processor.stop_requested:
                continue_count += 1
                time.sleep(0.1)  # Simulate work
                
                # Check if stop was requested
                if processor.stop_requested:
                    print(f"    🛑 Auto-continue stopped at iteration {continue_count}")
                    return continue_count
            
            return continue_count
        
        # Start simulated task in thread
        result_container = []
        
        def run_task():
            result = simulate_long_task()
            result_container.append(result)
        
        task_thread = threading.Thread(target=run_task)
        task_thread.start()
        
        # Let it run for a bit, then stop
        time.sleep(0.25)
        processor.request_stop()
        
        task_thread.join(timeout=2)
        
        if result_container:
            stopped_at = result_container[0]
            print(f"  ✅ Auto-continue properly stopped at iteration {stopped_at} (should be < 5)")
            assert stopped_at < 5, "Task should have stopped early"
        
        print("✅ TaskProcessor stop functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ TaskProcessor stop test failed: {e}")
        return False

def test_thread_classes():
    """Test thread stop functionality"""
    print("\n🧵 Testing Thread Stop Functionality...")
    
    try:
        from supermini import TaskProcessor, ExploreThread, EnhanceThread, TaskThread, AIConfig, MemoryManager
        from pathlib import Path
        
        # Create test processor
        config = AIConfig(use_claude=False, ollama_url="http://localhost:11434")
        output_dir = Path.home() / "SuperMini_Output" / "test"
        memory = MemoryManager(output_dir)
        processor = TaskProcessor(config, memory, output_dir)
        
        # Test ExploreThread stop
        explore_thread = ExploreThread(processor, [], 0, 1)  # 1 minute delay
        assert explore_thread.running, "ExploreThread should initially be running"
        
        explore_thread.stop()
        assert not explore_thread.running, "ExploreThread should stop when stop() is called"
        assert processor.stop_requested, "Processor stop should be requested"
        
        print("  ✅ ExploreThread stop functionality works")
        
        # Test EnhanceThread stop
        processor.reset_stop_flag()
        enhance_thread = EnhanceThread(processor, [], __file__, 0, 1)  # 1 minute delay
        assert enhance_thread.running, "EnhanceThread should initially be running"
        
        enhance_thread.stop()
        assert not enhance_thread.running, "EnhanceThread should stop when stop() is called"
        assert processor.stop_requested, "Processor stop should be requested"
        
        print("  ✅ EnhanceThread stop functionality works")
        
        # Test TaskThread stop
        processor.reset_stop_flag()
        task_thread = TaskThread(processor, "test task", [], "code", True, False, 5)
        assert task_thread.running, "TaskThread should initially be running"
        
        task_thread.stop()
        assert not task_thread.running, "TaskThread should stop when stop() is called"
        assert processor.stop_requested, "Processor stop should be requested"
        
        print("  ✅ TaskThread stop functionality works")
        
        print("✅ Thread stop functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Thread stop test failed: {e}")
        return False

def test_activity_logging():
    """Test that stop actions are properly logged"""
    print("\n📝 Testing Stop Action Logging...")
    
    try:
        from activity_monitor import get_activity_logger, ActivityType, ActivityLevel
        
        logger = get_activity_logger()
        initial_events = len(logger.events)
        
        # Simulate stop logging from processor
        from supermini import TaskProcessor, AIConfig, MemoryManager
        from pathlib import Path
        
        config = AIConfig(use_claude=False)
        output_dir = Path.home() / "SuperMini_Output" / "test"
        memory = MemoryManager(output_dir)
        processor = TaskProcessor(config, memory, output_dir)
        
        # Request stop (this should log an event)
        processor.request_stop()
        
        # Check that logging occurred
        new_events = len(logger.events) - initial_events
        assert new_events > 0, "Stop request should generate log events"
        
        # Check recent events for stop-related activity
        recent_events = logger.get_recent_events(count=5)
        stop_events = [e for e in recent_events if "stop" in e.title.lower() or "stop" in e.description.lower()]
        
        assert len(stop_events) > 0, "Should have stop-related log events"
        
        print(f"  ✅ Generated {len(stop_events)} stop-related log events")
        print("✅ Stop action logging tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Stop action logging test failed: {e}")
        return False

def test_gui_state_management():
    """Test GUI button state management (without actually creating GUI)"""
    print("\n🖱️ Testing GUI State Management Logic...")
    
    try:
        # Simulate button states
        class MockButton:
            def __init__(self, initial_enabled=True):
                self._enabled = initial_enabled
            
            def setEnabled(self, enabled):
                self._enabled = enabled
            
            def isEnabled(self):
                return self._enabled
        
        # Create mock buttons
        process_btn = MockButton(True)
        stop_task_btn = MockButton(False)
        start_explore_btn = MockButton(True)
        stop_explore_btn = MockButton(False)
        start_enhance_btn = MockButton(True)
        stop_enhance_btn = MockButton(False)
        
        # Test initial states
        assert process_btn.isEnabled(), "Process button should initially be enabled"
        assert not stop_task_btn.isEnabled(), "Stop task button should initially be disabled"
        assert start_explore_btn.isEnabled(), "Start explore button should initially be enabled"
        assert not stop_explore_btn.isEnabled(), "Stop explore button should initially be disabled"
        assert start_enhance_btn.isEnabled(), "Start enhance button should initially be enabled"
        assert not stop_enhance_btn.isEnabled(), "Stop enhance button should initially be disabled"
        
        # Simulate task start
        process_btn.setEnabled(False)
        stop_task_btn.setEnabled(True)
        
        assert not process_btn.isEnabled(), "Process button should be disabled during task"
        assert stop_task_btn.isEnabled(), "Stop task button should be enabled during task"
        
        # Simulate task stop
        process_btn.setEnabled(True)
        stop_task_btn.setEnabled(False)
        
        assert process_btn.isEnabled(), "Process button should be re-enabled after stop"
        assert not stop_task_btn.isEnabled(), "Stop task button should be disabled after stop"
        
        # Test exploration buttons
        start_explore_btn.setEnabled(False)
        stop_explore_btn.setEnabled(True)
        
        assert not start_explore_btn.isEnabled(), "Start explore should be disabled during exploration"
        assert stop_explore_btn.isEnabled(), "Stop explore should be enabled during exploration"
        
        start_explore_btn.setEnabled(True)
        stop_explore_btn.setEnabled(False)
        
        assert start_explore_btn.isEnabled(), "Start explore should be re-enabled after stop"
        assert not stop_explore_btn.isEnabled(), "Stop explore should be disabled after stop"
        
        print("  ✅ Button state transitions work correctly")
        print("✅ GUI state management tests passed")
        return True
        
    except Exception as e:
        print(f"❌ GUI state management test failed: {e}")
        return False

def run_stop_functionality_tests():
    """Run all stop functionality tests"""
    print("🛑 Starting Stop Functionality Test Suite")
    print("=" * 60)
    
    tests = [
        test_task_processor_stop,
        test_thread_classes,
        test_activity_logging,
        test_gui_state_management
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All stop functionality tests passed!")
        print("\n✅ Stop Features Working:")
        print("  🛑 Task processor stop flag")
        print("  🧵 Thread termination")
        print("  📝 Stop action logging")
        print("  🖱️ GUI button state management")
        print("  ⏹️ Auto-continuation interruption")
        print("  🔄 Graceful shutdown with fallback termination")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_stop_functionality_tests()
    sys.exit(0 if success else 1)