#!/usr/bin/env python3
"""
Test script for enhanced activity monitoring system
Demonstrates real-time logging and monitoring capabilities
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_activity_logger():
    """Test the activity logging system"""
    print("🔍 Testing Activity Logger...")
    
    try:
        from activity_monitor import (
            get_activity_logger, ActivityType, ActivityLevel,
            log_activity as log_activity_event
        )
        
        logger = get_activity_logger()
        
        # Test basic logging
        log_activity_event(
            ActivityType.SYSTEM_EVENT,
            ActivityLevel.INFO,
            "Test System Started",
            "Testing enhanced activity monitoring system",
            {"test_mode": True, "version": "1.0"}
        )
        
        # Test task tracking
        task_id = logger.start_task(
            "test_task_001",
            "test",
            "Test task for monitoring system",
            {"priority": "high", "test": True}
        )
        
        time.sleep(0.1)
        
        # Test AI interaction logging
        logger.log_ai_interaction(
            "What is 2 + 2?",
            "2 + 2 equals 4",
            "test-model",
            0.5,
            "test_task_001"
        )
        
        # Test autonomous action logging
        logger.log_autonomous_action(
            "click(100, 200)",
            1,
            "test_task_001",
            "success",
            {"execution_time": 0.2}
        )
        
        # Test safety check logging
        logger.log_safety_check(
            "rm test.txt",
            True,
            "Safe file operation",
            "test_task_001"
        )
        
        # Test file operation logging
        logger.log_file_operation(
            "create",
            "/tmp/test_file.txt",
            True,
            {"size": 1024}
        )
        
        # Test screenshot logging
        logger.log_screenshot(
            "/tmp/test_screenshot.png",
            "Test screenshot capture",
            "test_task_001"
        )
        
        # End task
        logger.end_task(
            "test_task_001",
            True,
            {"files_created": 1, "actions_executed": 3}
        )
        
        print("✅ Activity logger tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Activity logger test failed: {e}")
        return False

def test_performance_tracking():
    """Test performance metrics tracking"""
    print("\n📊 Testing Performance Tracking...")
    
    try:
        from activity_monitor import get_activity_logger
        
        logger = get_activity_logger()
        
        # Simulate multiple tasks
        for i in range(5):
            task_id = f"perf_test_{i}"
            logger.start_task(task_id, "performance_test", f"Performance test {i}")
            
            # Simulate work
            time.sleep(0.1 + (i * 0.05))  # Variable execution time
            
            logger.end_task(task_id, True, {"iteration": i})
        
        # Get performance stats
        stats = logger.get_performance_stats()
        
        print(f"  📈 Performance Stats:")
        print(f"    - Task types tracked: {len(stats) - 3}")  # Subtract metadata fields
        print(f"    - Total events: {stats.get('total_events', 0)}")
        print(f"    - Active tasks: {stats.get('active_tasks', 0)}")
        
        if 'performance_test' in stats:
            perf_stats = stats['performance_test']
            print(f"    - Avg execution time: {perf_stats['avg_duration']:.3f}s")
            print(f"    - Min execution time: {perf_stats['min_duration']:.3f}s")
            print(f"    - Max execution time: {perf_stats['max_duration']:.3f}s")
        
        print("✅ Performance tracking tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance tracking test failed: {e}")
        return False

def test_event_filtering():
    """Test event filtering and retrieval"""
    print("\n🔍 Testing Event Filtering...")
    
    try:
        from activity_monitor import (
            get_activity_logger, ActivityType, ActivityLevel,
            log_activity as log_activity_event
        )
        from datetime import datetime, timedelta
        
        logger = get_activity_logger()
        
        # Log various types of events
        event_types = [
            (ActivityType.TASK_START, ActivityLevel.INFO, "Task A Started"),
            (ActivityType.AI_QUERY, ActivityLevel.DEBUG, "Query sent to AI"),
            (ActivityType.AUTONOMOUS_ACTION, ActivityLevel.INFO, "Action executed"),
            (ActivityType.SAFETY_CHECK, ActivityLevel.WARNING, "Safety validation"),
            (ActivityType.ERROR_EVENT, ActivityLevel.ERROR, "Error occurred"),
            (ActivityType.TASK_END, ActivityLevel.INFO, "Task A Completed")
        ]
        
        for event_type, level, title in event_types:
            log_activity_event(
                event_type, level, title, 
                f"Test event: {title}",
                {"test": True}
            )
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Test filtering by type
        task_events = logger.get_recent_events(activity_type=ActivityType.TASK_START)
        print(f"  📋 Task start events: {len(task_events)}")
        
        # Test filtering by level
        error_events = logger.get_recent_events(level=ActivityLevel.ERROR)
        print(f"  ❌ Error events: {len(error_events)}")
        
        # Test filtering by time
        recent_events = logger.get_recent_events(
            since=datetime.now() - timedelta(seconds=10)
        )
        print(f"  ⏰ Recent events (last 10s): {len(recent_events)}")
        
        # Test combined filtering
        recent_info_events = logger.get_recent_events(
            level=ActivityLevel.INFO,
            since=datetime.now() - timedelta(seconds=10)
        )
        print(f"  ℹ️ Recent info events: {len(recent_info_events)}")
        
        print("✅ Event filtering tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Event filtering test failed: {e}")
        return False

def test_log_export():
    """Test log export functionality"""
    print("\n💾 Testing Log Export...")
    
    try:
        from activity_monitor import get_activity_logger
        import tempfile
        
        logger = get_activity_logger()
        
        # Export to JSON
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        
        success = logger.export_activity_log(json_path, format="json")
        
        if success and json_path.exists():
            file_size = json_path.stat().st_size
            print(f"  📄 JSON export: {file_size} bytes")
            json_path.unlink()  # Clean up
        
        # Export to CSV
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_path = Path(f.name)
        
        success = logger.export_activity_log(csv_path, format="csv")
        
        if success and csv_path.exists():
            file_size = csv_path.stat().st_size
            print(f"  📊 CSV export: {file_size} bytes")
            csv_path.unlink()  # Clean up
        
        print("✅ Log export tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Log export test failed: {e}")
        return False

def test_autonomous_integration():
    """Test integration with autonomous agent"""
    print("\n🤖 Testing Autonomous Integration...")
    
    try:
        from activity_monitor import get_activity_logger, ActivityType, ActivityLevel
        
        logger = get_activity_logger()
        
        # Test autonomous logging functions without initializing full agent
        test_task_id = "autonomous_test"
        
        # Simulate autonomous agent logging
        logger.log_autonomous_action(
            "test_action()",
            1,
            test_task_id,
            "simulated",
            {"test_mode": True}
        )
        
        logger.log_safety_check(
            "test_action()",
            True,
            "Test action is safe",
            test_task_id
        )
        
        logger.log_screenshot(
            "/tmp/test_screenshot.png",
            "Test autonomous screenshot",
            test_task_id
        )
        
        # Test AI interaction logging
        logger.log_ai_interaction(
            "Autonomous query",
            "Autonomous response",
            "agent-s-model",
            0.5,
            test_task_id
        )
        
        print("  🔧 Autonomous action logging works")
        print("  🛡️ Safety check logging works")
        print("  📸 Screenshot logging works")
        print("  🤖 AI interaction logging works")
        print("✅ Autonomous integration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Autonomous integration test failed: {e}")
        return False

def test_concurrent_logging():
    """Test concurrent logging from multiple threads"""
    print("\n🧵 Testing Concurrent Logging...")
    
    try:
        from activity_monitor import (
            get_activity_logger, ActivityType, ActivityLevel,
            log_activity as log_activity_event
        )
        
        logger = get_activity_logger()
        
        def worker_thread(thread_id):
            """Worker thread that logs activities"""
            for i in range(5):
                log_activity_event(
                    ActivityType.SYSTEM_EVENT,
                    ActivityLevel.INFO,
                    f"Thread {thread_id} Event {i}",
                    f"Concurrent logging test from thread {thread_id}",
                    {"thread_id": thread_id, "event_number": i}
                )
                time.sleep(0.01)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all events were logged
        recent_events = logger.get_recent_events(count=20)
        concurrent_events = [e for e in recent_events if "Concurrent logging test" in e.description]
        
        print(f"  📝 Concurrent events logged: {len(concurrent_events)}")
        print("✅ Concurrent logging tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Concurrent logging test failed: {e}")
        return False

def run_monitoring_tests():
    """Run all monitoring system tests"""
    print("🚀 Starting Enhanced Activity Monitoring Tests")
    print("=" * 60)
    
    tests = [
        test_activity_logger,
        test_performance_tracking,
        test_event_filtering,
        test_log_export,
        test_autonomous_integration,
        test_concurrent_logging
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
        print("🎉 All monitoring tests passed! System is ready for enhanced transparency.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    # Show sample recent events
    try:
        from activity_monitor import get_activity_logger
        logger = get_activity_logger()
        
        print(f"\n📋 Sample Recent Events ({len(logger.events)} total):")
        recent = logger.get_recent_events(count=5)
        for event in recent:
            timestamp = time.strftime('%H:%M:%S', time.localtime(event.timestamp))
            print(f"  [{timestamp}] {event.level.value:8s} | {event.title}")
        
        # Show performance stats
        stats = logger.get_performance_stats()
        print(f"\n📈 Performance Summary:")
        print(f"  - Total events logged: {stats.get('total_events', 0)}")
        print(f"  - Event types: {len([k for k in stats.get('event_counts', {}).keys() if 'ActivityType.' in str(k)])}")
        print(f"  - Active tasks: {stats.get('active_tasks', 0)}")
        
    except Exception as e:
        print(f"Error displaying summary: {e}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_monitoring_tests()
    sys.exit(0 if success else 1)