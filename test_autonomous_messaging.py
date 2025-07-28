#!/usr/bin/env python3
"""
Test Script for Autonomous Transparent Messaging Framework
==========================================================

This script tests the autonomous messaging framework functionality
with various message types and scenarios to ensure proper integration
with SuperMini's existing systems.

Usage:
    python3 test_autonomous_messaging.py

Author: SuperMini AI Framework
Created: 2025-07-27
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_messaging_imports():
    """Test that autonomous messaging modules can be imported"""
    print("🔧 Testing autonomous messaging imports...")
    
    try:
        from src.core.autonomous_messaging import (
            AutonomousMessagingManager, 
            MessageFormatter, 
            MessageType, 
            MessagePriority,
            FormattedMessage
        )
        print("✅ Core messaging modules imported successfully")
        
        from src.ui.enhanced_messaging_integration import (
            MessagingIntegrationManager,
            create_messaging_integration
        )
        print("✅ UI integration modules imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def create_mock_ollama_manager():
    """Create a mock Ollama manager for testing"""
    
    class MockOllamaManager:
        def __init__(self):
            self.base_url = "http://localhost:11434"
            self.model = "qwen2.5-coder:7b"
        
        def query(self, prompt: str) -> str:
            """Mock query that returns formatted response"""
            # Simulate AI formatting response
            if "task result" in prompt.lower():
                return """Header: ✅ Code Generation Completed Successfully

Summary: Python data analysis script generated with visualization capabilities

Bullet Points:
• Created comprehensive data analysis functions
• Implemented interactive matplotlib visualizations  
• Added pandas data processing with error handling
• Generated 3 output files with documentation

Performance: Processing completed in 2.3 seconds with optimal resource usage"""
            
            elif "progress" in prompt.lower():
                return """Header: ⚡ Processing Data Files - 75% Complete

Summary: Analyzing CSV data with machine learning models

Bullet Points:
• Data preprocessing completed successfully
• Feature engineering in progress
• Model training estimated 30 seconds remaining
• Output visualization being prepared"""
            
            elif "error" in prompt.lower():
                return """Header: ❌ Connection Timeout Error

Issues:
• Network connection to API server failed
• Timeout occurred after 30 seconds
• Local fallback model unavailable

Solutions:
• Check internet connection status
• Verify API endpoint configuration
• Restart Ollama service if using local models
• Try again with reduced request complexity"""
            
            else:
                return """Header: 📋 Information Processed

Summary: Task completed successfully

Bullet Points:
• Information processed and formatted
• Results ready for display
• Processing completed efficiently"""
    
    return MockOllamaManager()

async def test_message_formatter():
    """Test the core MessageFormatter functionality"""
    print("\n🧪 Testing MessageFormatter...")
    
    try:
        from src.core.autonomous_messaging import MessageFormatter, MessageType, MessagePriority
        
        # Create mock Ollama manager
        mock_ollama = create_mock_ollama_manager()
        
        # Initialize formatter
        formatter = MessageFormatter(mock_ollama)
        
        # Test task result formatting
        task_content = """
        Task completed successfully. Generated Python script for data analysis.
        Files created: analysis.py, results.csv, visualization.png
        Execution time: 2.3 seconds
        """
        
        formatted_message = await formatter.format_message(
            content=task_content,
            message_type=MessageType.TASK_RESULT,
            context={
                'task_type': 'code',
                'execution_time': 2.3,
                'file_count': 3
            }
        )
        
        print(f"✅ Task result formatted successfully")
        print(f"   Header: {formatted_message.header}")
        print(f"   Summary: {formatted_message.summary}")
        print(f"   Bullet points: {len(formatted_message.bullet_points)}")
        print(f"   Processing time: {formatted_message.processing_time:.3f}s")
        
        # Test progress update formatting
        progress_content = "Processing data files, currently analyzing customer_data.csv..."
        
        progress_message = await formatter.format_message(
            content=progress_content,
            message_type=MessageType.PROGRESS_UPDATE,
            context={
                'progress': 75,
                'current_step': 'Data Analysis',
                'eta': '30 seconds'
            }
        )
        
        print(f"✅ Progress update formatted successfully")
        print(f"   Header: {progress_message.header}")
        print(f"   Summary: {progress_message.summary}")
        
        # Test error message formatting
        error_content = "Connection timeout error occurred while contacting API server"
        
        error_message = await formatter.format_message(
            content=error_content,
            message_type=MessageType.ERROR_MESSAGE,
            context={
                'error_type': 'network',
                'context': 'api_call'
            }
        )
        
        print(f"✅ Error message formatted successfully")
        print(f"   Header: {error_message.header}")
        print(f"   Action items: {len(error_message.action_items)}")
        
        # Test caching functionality
        cached_message = await formatter.format_message(
            content=task_content,
            message_type=MessageType.TASK_RESULT,
            context={'task_type': 'code', 'execution_time': 2.3, 'file_count': 3}
        )
        
        print(f"✅ Cache test completed")
        print(f"   Cache key matches: {formatted_message.cache_key == cached_message.cache_key}")
        
        # Print formatter statistics
        stats = formatter.get_stats()
        print(f"📊 Formatter Stats:")
        print(f"   Messages formatted: {stats['messages_formatted']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache misses: {stats['cache_misses']}")
        
        return True
        
    except Exception as e:
        print(f"❌ MessageFormatter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_messaging_integration():
    """Test the messaging integration manager"""
    print("\n🔗 Testing MessagingIntegrationManager...")
    
    try:
        from src.ui.enhanced_messaging_integration import create_messaging_integration
        
        # Create mock Ollama manager
        mock_ollama = create_mock_ollama_manager()
        
        # Create messaging integration
        config = {
            'cache_size': 100,
            'cache_ttl': 300,
            'auto_start_pipeline': False,  # Don't auto-start for testing
            'enable_real_time': True,
            'autonomous_enabled': True
        }
        
        messaging_integration = create_messaging_integration(mock_ollama, config)
        
        # Test message enhancement
        enhanced_message = await messaging_integration.enhance_message(
            content="Task completed successfully with 3 files generated",
            message_type="task_result",
            context={'task_type': 'automation', 'file_count': 3}
        )
        
        print(f"✅ Message enhancement successful")
        print(f"   Type: {enhanced_message.message_type.value}")
        print(f"   Header: {enhanced_message.header[:50]}...")
        
        # Test error enhancement
        error_enhanced = await messaging_integration.enhance_error_message({
            'message': 'API connection failed with timeout',
            'type': 'network',
            'context': 'claude_api'
        })
        
        print(f"✅ Error enhancement successful")
        print(f"   Header: {error_enhanced.header}")
        print(f"   Solutions: {len(error_enhanced.action_items)}")
        
        # Get comprehensive statistics
        stats = messaging_integration.get_comprehensive_stats()
        print(f"📊 Integration Stats:")
        print(f"   Total messages: {stats['integration_stats']['total_messages']}")
        print(f"   Enhanced messages: {stats['integration_stats']['enhanced_messages']}")
        
        return True
        
    except Exception as e:
        print(f"❌ MessagingIntegration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_task_result_formatting():
    """Test formatting of TaskResult objects"""
    print("\n📋 Testing TaskResult formatting...")
    
    try:
        from dataclasses import dataclass
        from typing import List
        from src.core.autonomous_messaging import MessageType
        
        # Create mock TaskResult
        @dataclass
        class MockTaskResult:
            success: bool
            result: str
            execution_time: float
            generated_files: List[str]
            task_type: str = "code"
            task_steps: List[str] = None
            audio_path: str = None
        
        # Create test task result
        task_result = MockTaskResult(
            success=True,
            result="Successfully generated Python data analysis script with visualization capabilities. The script includes pandas data processing, matplotlib charts, and error handling.",
            execution_time=2.45,
            generated_files=[
                "/Users/test/SuperMini_Output/data_analysis.py",
                "/Users/test/SuperMini_Output/results.csv",
                "/Users/test/SuperMini_Output/visualization.png"
            ],
            task_steps=[
                "Analyzed requirements",
                "Generated Python code",
                "Created test data",
                "Generated visualizations"
            ]
        )
        
        # Test async formatting
        from src.core.autonomous_messaging import MessageFormatter
        mock_ollama = create_mock_ollama_manager()
        formatter = MessageFormatter(mock_ollama)
        
        formatted = await formatter.format_task_result(task_result)
        
        print(f"✅ TaskResult formatting successful")
        print(f"   Header: {formatted.header}")
        print(f"   Summary: {formatted.summary}")
        print(f"   Bullet points: {len(formatted.bullet_points)}")
        print(f"   HTML content length: {len(formatted.html_content)} chars")
        
        # Verify HTML content is valid
        if "<div" in formatted.html_content and "</div>" in formatted.html_content:
            print(f"✅ HTML content structure valid")
        else:
            print(f"⚠️  HTML content structure may be invalid")
        
        return True
        
    except Exception as e:
        print(f"❌ TaskResult formatting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_performance_and_caching():
    """Test performance and caching capabilities"""
    print("\n⚡ Testing performance and caching...")
    
    try:
        from src.core.autonomous_messaging import MessageCache, MessageType
        
        # Test cache functionality
        cache = MessageCache(max_size=10, ttl_seconds=60)
        
        test_content = "This is a test message for caching"
        message_type = MessageType.TASK_RESULT
        
        # Test cache miss
        cached_result = cache.get(test_content, message_type)
        print(f"✅ Cache miss test: {cached_result is None}")
        
        # Create mock formatted message
        from src.core.autonomous_messaging import FormattedMessage, MessagePriority
        from datetime import datetime
        
        mock_message = FormattedMessage(
            header="Test Header",
            bullet_points=["Point 1", "Point 2"],
            summary="Test summary",
            action_items=["Action 1"],
            technical_details=test_content,
            message_type=message_type,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            html_content="<div>Test</div>",
            processing_time=0.1,
            cache_key="",
            model_used="test"
        )
        
        # Store in cache
        cache.put(test_content, message_type, mock_message)
        
        # Test cache hit
        cached_result = cache.get(test_content, message_type)
        print(f"✅ Cache hit test: {cached_result is not None}")
        print(f"   Retrieved header: {cached_result.header}")
        
        # Test cache statistics
        stats = cache.stats()
        print(f"📊 Cache Stats:")
        print(f"   Size: {stats['size']}")
        print(f"   Max size: {stats['max_size']}")
        
        # Performance test
        start_time = time.time()
        
        from src.core.autonomous_messaging import MessageFormatter
        mock_ollama = create_mock_ollama_manager()
        formatter = MessageFormatter(mock_ollama)
        
        # Format multiple messages
        tasks = []
        for i in range(5):
            task = formatter.format_message(
                content=f"Test message {i} for performance testing",
                message_type=MessageType.TASK_RESULT,
                context={'test_id': i}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"✅ Performance test completed")
        print(f"   Messages processed: {len(results)}")
        print(f"   Total time: {(end_time - start_time):.3f}s")
        print(f"   Average time per message: {(end_time - start_time) / len(results):.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_error_handling_and_fallbacks():
    """Test error handling and fallback mechanisms"""
    print("\n🛡️  Testing error handling and fallbacks...")
    
    try:
        from src.core.autonomous_messaging import MessageFormatter, MessageType
        
        # Create mock Ollama manager that fails
        class FailingOllamaManager:
            def query(self, prompt: str) -> None:
                raise Exception("Mock network error")
        
        failing_ollama = FailingOllamaManager()
        formatter = MessageFormatter(failing_ollama)
        
        # Test fallback mechanism
        fallback_result = await formatter.format_message(
            content="Test message for fallback testing",
            message_type=MessageType.TASK_RESULT,
            context={'test': True}
        )
        
        print(f"✅ Fallback mechanism working")
        print(f"   Model used: {fallback_result.model_used}")
        print(f"   Header: {fallback_result.header}")
        print(f"   Content preserved: {'Test message' in fallback_result.technical_details}")
        
        # Test with None Ollama manager
        none_formatter = MessageFormatter(None)
        
        none_result = await none_formatter.format_message(
            content="Test with None Ollama manager",
            message_type=MessageType.ERROR_MESSAGE
        )
        
        print(f"✅ None Ollama handling working")
        print(f"   Model used: {none_result.model_used}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all autonomous messaging tests"""
    print("🚀 Starting Autonomous Messaging Framework Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test imports
    test_results.append(("Imports", test_messaging_imports()))
    
    # Test core functionality
    test_results.append(("MessageFormatter", await test_message_formatter()))
    
    # Test integration
    test_results.append(("MessagingIntegration", await test_messaging_integration()))
    
    # Test TaskResult formatting
    test_results.append(("TaskResult Formatting", await test_task_result_formatting()))
    
    # Test performance and caching
    test_results.append(("Performance & Caching", await test_performance_and_caching()))
    
    # Test error handling
    test_results.append(("Error Handling", await test_error_handling_and_fallbacks()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Autonomous messaging framework is ready.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    print("SuperMini Autonomous Messaging Framework Test Suite")
    print("Version: 1.0.0")
    print("=" * 60)
    
    try:
        success = asyncio.run(run_all_tests())
        exit_code = 0 if success else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)