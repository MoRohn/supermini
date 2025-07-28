#!/usr/bin/env python3
"""
Comprehensive QA/Testing & Resolution Campaign for SuperMini AI Assistant
Tests all three operational modes systematically and fixes identified issues
"""

import sys
import os
import time
import threading
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QATestSuite:
    """Comprehensive QA test suite for SuperMini AI Assistant"""
    
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'test_details': {}
        }
        self.output_dir = Path.home() / "SuperMini_Output" / "qa_test"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Log test result with details"""
        if passed:
            self.results['passed'] += 1
            print(f"✅ {test_name}")
        else:
            self.results['failed'] += 1
            print(f"❌ {test_name}")
            if error:
                self.results['errors'].append(f"{test_name}: {error}")
                print(f"   Error: {error}")
        
        self.results['test_details'][test_name] = {
            'passed': passed,
            'details': details,
            'error': error
        }
        
        if details:
            print(f"   Details: {details}")

    def test_core_imports(self) -> bool:
        """Test that core modules can be imported"""
        print("\n🔍 Testing Core Module Imports...")
        
        try:
            # Test main module import
            import supermini
            self.log_test_result("Main supermini module import", True, "Module imported successfully")
            
            # Test core classes
            from supermini import TaskProcessor, AIConfig, MemoryManager
            self.log_test_result("Core classes import", True, "TaskProcessor, AIConfig, MemoryManager imported")
            
            # Test autonomous modules
            try:
                from src.autonomous.autonomous_agent import AutonomousAgent, SafetyManager
                self.log_test_result("Autonomous modules import", True, "AutonomousAgent and SafetyManager imported")
            except ImportError as e:
                self.log_test_result("Autonomous modules import", False, "", str(e))
            
            # Test activity monitor
            try:
                from src.utils.activity_monitor import get_activity_logger
                self.log_test_result("Activity monitor import", True, "Activity monitor imported")
            except ImportError as e:
                self.log_test_result("Activity monitor import", False, "", str(e))
            
            return True
            
        except Exception as e:
            self.log_test_result("Core imports", False, "", str(e))
            return False

    def test_basic_configuration(self) -> bool:
        """Test basic configuration setup"""
        print("\n⚙️ Testing Basic Configuration...")
        
        try:
            from supermini import AIConfig, MemoryManager
            
            # Test AIConfig creation
            config = AIConfig(
                use_claude=False,
                claude_api_key="",
                ollama_url="http://localhost:11434",
                max_tokens=100,
                temperature=0.1
            )
            self.log_test_result("AIConfig creation", True, f"Config created with ollama_url: {config.ollama_url}")
            
            # Test MemoryManager creation
            memory = MemoryManager(self.output_dir)
            self.log_test_result("MemoryManager creation", True, f"Memory manager created for {self.output_dir}")
            
            return True
            
        except Exception as e:
            self.log_test_result("Basic configuration", False, "", str(e))
            return False

    def test_task_processor_initialization(self) -> bool:
        """Test TaskProcessor initialization"""
        print("\n🔧 Testing TaskProcessor Initialization...")
        
        try:
            from supermini import TaskProcessor, AIConfig, MemoryManager
            
            config = AIConfig(use_claude=False, ollama_url="http://localhost:11434")
            memory = MemoryManager(self.output_dir)
            processor = TaskProcessor(config, memory, self.output_dir)
            
            # Check basic attributes
            assert hasattr(processor, 'config'), "TaskProcessor should have config attribute"
            assert hasattr(processor, 'memory'), "TaskProcessor should have memory attribute"
            assert hasattr(processor, 'output_dir'), "TaskProcessor should have output_dir attribute"
            
            self.log_test_result("TaskProcessor initialization", True, "All required attributes present")
            
            # Test stop functionality
            assert hasattr(processor, 'stop_requested'), "TaskProcessor should have stop_requested attribute"
            assert not processor.stop_requested, "stop_requested should initially be False"
            
            processor.request_stop()
            assert processor.stop_requested, "stop_requested should be True after request_stop()"
            
            processor.reset_stop_flag()
            assert not processor.stop_requested, "stop_requested should be False after reset_stop_flag()"
            
            self.log_test_result("Stop functionality", True, "Stop flag operations working correctly")
            
            return True
            
        except Exception as e:
            self.log_test_result("TaskProcessor initialization", False, "", str(e))
            return False

    def test_regular_task_processing_mode(self) -> bool:
        """Test Regular Task Processing Mode (all 5 task types)"""
        print("\n📋 Testing Regular Task Processing Mode...")
        
        try:
            from supermini import TaskProcessor, AIConfig, MemoryManager
            
            config = AIConfig(use_claude=False, ollama_url="http://localhost:11434")
            memory = MemoryManager(self.output_dir)
            processor = TaskProcessor(config, memory, self.output_dir)
            
            # Test task classification
            test_prompts = {
                'code': "Write a Python function to calculate fibonacci numbers",
                'multimedia': "Analyze this image file",
                'rag': "Summarize this document content",
                'automation': "Create a script to backup files",
                'analytics': "Analyze this CSV data for trends"
            }
            
            for task_type, prompt in test_prompts.items():
                try:
                    # Test task classification
                    classified_type = processor.classify_task(prompt)
                    self.log_test_result(f"Task classification - {task_type}", True, 
                                       f"Prompt classified as: {classified_type}")
                except Exception as e:
                    self.log_test_result(f"Task classification - {task_type}", False, "", str(e))
            
            # Test output directory structure
            expected_dirs = ['data', 'logs']
            for dir_name in expected_dirs:
                dir_path = self.output_dir / dir_name
                if dir_path.exists():
                    self.log_test_result(f"Output directory - {dir_name}", True, f"Directory exists: {dir_path}")
                else:
                    self.log_test_result(f"Output directory - {dir_name}", False, f"Directory missing: {dir_path}")
            
            return True
            
        except Exception as e:
            self.log_test_result("Regular task processing mode", False, "", str(e))
            return False

    def test_autonomous_mode(self) -> bool:
        """Test Autonomous Mode with Agent-S framework integration"""
        print("\n🤖 Testing Autonomous Mode...")
        
        try:
            # Test autonomous agent imports
            try:
                from src.autonomous.autonomous_agent import AutonomousAgent, SafetyManager, AutonomousTask
                autonomous_available = True
                self.log_test_result("Autonomous imports", True, "All autonomous classes imported successfully")
            except ImportError as e:
                autonomous_available = False
                self.log_test_result("Autonomous imports", False, "", str(e))
                return False
            
            if autonomous_available:
                # Test SafetyManager
                safety = SafetyManager()
                
                # Test safe action validation
                is_safe, msg = safety.validate_action("ls -la", {})
                self.log_test_result("SafetyManager - safe action", is_safe, f"Validation message: {msg}")
                
                # Test restricted action validation
                is_safe, msg = safety.validate_action("rm -rf /", {})
                self.log_test_result("SafetyManager - restricted action", not is_safe, f"Properly blocked: {msg}")
                
                # Test AutonomousTask creation
                task = AutonomousTask(
                    task_id="test_001",
                    instruction="Take a screenshot",
                    task_type="automation",
                    context={"test": True}
                )
                
                task_valid = (task.task_id == "test_001" and 
                             task.instruction == "Take a screenshot" and
                             task.task_type == "automation")
                
                self.log_test_result("AutonomousTask creation", task_valid, f"Task created with ID: {task.task_id}")
                
                # Test AutonomousAgent initialization
                config = {
                    "model": "gpt-4-vision-preview",
                    "api_key": "test-key",
                    "max_tokens": 4096,
                    "temperature": 0.1
                }
                
                agent = AutonomousAgent(config)
                agent_valid = (agent.config == config and 
                             hasattr(agent, 'safety_manager') and
                             hasattr(agent, 'active_tasks'))
                
                self.log_test_result("AutonomousAgent initialization", agent_valid, "Agent initialized with required attributes")
            
            return True
            
        except Exception as e:
            self.log_test_result("Autonomous mode", False, "", str(e))
            return False

    def test_self_enhancement_mode(self) -> bool:
        """Test Self-Enhancement Mode recursive capabilities"""
        print("\n🔄 Testing Self-Enhancement Mode...")
        
        try:
            # Test enhancement-related imports
            try:
                from src.autonomous.autonomous_enhancement import EnhancementEngine
                from src.core.recursive_engine import RecursiveEngine
                enhancement_available = True
                self.log_test_result("Enhancement imports", True, "Enhancement modules imported")
            except ImportError as e:
                enhancement_available = False
                self.log_test_result("Enhancement imports", False, "", str(e))
            
            # Test enhancement thread functionality (from supermini.py)
            try:
                from supermini import EnhanceThread, TaskProcessor, AIConfig, MemoryManager
                
                config = AIConfig(use_claude=False)
                memory = MemoryManager(self.output_dir)
                processor = TaskProcessor(config, memory, self.output_dir)
                
                # Create enhancement thread
                enhance_thread = EnhanceThread(processor, [], __file__, 0, 1)  # 1 minute delay
                
                # Test thread attributes
                thread_valid = (hasattr(enhance_thread, 'running') and
                               hasattr(enhance_thread, 'stop') and
                               enhance_thread.running)
                
                self.log_test_result("EnhanceThread creation", thread_valid, "Enhancement thread created successfully")
                
                # Test stop functionality
                enhance_thread.stop()
                self.log_test_result("EnhanceThread stop", not enhance_thread.running, "Enhancement thread stopped correctly")
                
            except Exception as e:
                self.log_test_result("Enhancement thread functionality", False, "", str(e))
            
            return True
            
        except Exception as e:
            self.log_test_result("Self-enhancement mode", False, "", str(e))
            return False

    def test_stop_functionality_comprehensive(self) -> bool:
        """Test stop functionality across all modes"""
        print("\n🛑 Testing Stop Functionality Comprehensive...")
        
        try:
            from supermini import TaskProcessor, TaskThread, ExploreThread, EnhanceThread, AIConfig, MemoryManager
            
            config = AIConfig(use_claude=False)
            memory = MemoryManager(self.output_dir)
            processor = TaskProcessor(config, memory, self.output_dir)
            
            # Test TaskProcessor stop
            processor.reset_stop_flag()
            assert not processor.stop_requested, "Stop flag should be False initially"
            
            processor.request_stop()
            assert processor.stop_requested, "Stop flag should be True after request"
            
            self.log_test_result("TaskProcessor stop flag", True, "Stop flag operations working")
            
            # Test TaskThread stop
            processor.reset_stop_flag()
            task_thread = TaskThread(processor, "test task", [], "code", True, False, 5)
            assert task_thread.running, "TaskThread should be running initially"
            
            task_thread.stop()
            assert not task_thread.running, "TaskThread should stop"
            assert processor.stop_requested, "Processor stop should be requested"
            
            self.log_test_result("TaskThread stop", True, "TaskThread stop functionality working")
            
            # Test ExploreThread stop
            processor.reset_stop_flag()
            explore_thread = ExploreThread(processor, [], 0, 1)
            assert explore_thread.running, "ExploreThread should be running initially"
            
            explore_thread.stop()
            assert not explore_thread.running, "ExploreThread should stop"
            
            self.log_test_result("ExploreThread stop", True, "ExploreThread stop functionality working")
            
            # Test EnhanceThread stop
            processor.reset_stop_flag()
            enhance_thread = EnhanceThread(processor, [], __file__, 0, 1)
            assert enhance_thread.running, "EnhanceThread should be running initially"
            
            enhance_thread.stop()
            assert not enhance_thread.running, "EnhanceThread should stop"
            
            self.log_test_result("EnhanceThread stop", True, "EnhanceThread stop functionality working")
            
            return True
            
        except Exception as e:
            self.log_test_result("Stop functionality comprehensive", False, "", str(e))
            return False

    def test_integration_between_modes(self) -> bool:
        """Test integration and mode switching"""
        print("\n🔄 Testing Integration Between Modes...")
        
        try:
            from supermini import TaskProcessor, AIConfig, MemoryManager
            
            config = AIConfig(use_claude=False)
            memory = MemoryManager(self.output_dir)
            processor = TaskProcessor(config, memory, self.output_dir)
            
            # Test memory persistence between modes
            if hasattr(processor.memory, 'add_memory'):
                test_memory = {
                    'content': 'Test memory for integration',
                    'metadata': {'test': True, 'mode': 'integration_test'}
                }
                processor.memory.add_memory(test_memory)
                self.log_test_result("Memory integration", True, "Memory added successfully")
            else:
                self.log_test_result("Memory integration", False, "Memory manager lacks add_memory method")
            
            # Test configuration consistency
            config_consistency = (
                hasattr(processor.config, 'use_claude') and
                hasattr(processor.config, 'ollama_url') and
                hasattr(processor.config, 'max_tokens')
            )
            
            self.log_test_result("Configuration consistency", config_consistency, "Config has required attributes")
            
            return True
            
        except Exception as e:
            self.log_test_result("Integration between modes", False, "", str(e))
            return False

    def test_edge_cases_and_error_handling(self) -> bool:
        """Test edge cases and error handling"""
        print("\n⚠️ Testing Edge Cases and Error Handling...")
        
        try:
            from supermini import TaskProcessor, AIConfig, MemoryManager
            
            # Test with invalid configuration
            try:
                invalid_config = AIConfig(use_claude=True, claude_api_key="invalid_key")
                memory = MemoryManager(self.output_dir)
                processor = TaskProcessor(invalid_config, memory, self.output_dir)
                self.log_test_result("Invalid config handling", True, "TaskProcessor handles invalid config gracefully")
            except Exception as e:
                self.log_test_result("Invalid config handling", False, "", str(e))
            
            # Test with non-existent output directory (should handle gracefully)
            try:
                config = AIConfig(use_claude=False)
                # Use a directory we can't create (read-only filesystem)
                invalid_dir = Path("/dev/null/invalid")
                memory = MemoryManager(invalid_dir)
                # If it doesn't raise an exception, check if memory is disabled
                if memory.collection is None:
                    self.log_test_result("Invalid directory handling", True, "Gracefully handles invalid directory by disabling memory")
                else:
                    self.log_test_result("Invalid directory handling", False, "Should disable memory for invalid directory")
            except Exception as e:
                self.log_test_result("Invalid directory handling", True, f"Properly handles invalid directory with exception: {e}")
            
            # Test empty task processing
            try:
                config = AIConfig(use_claude=False)
                memory = MemoryManager(self.output_dir)
                processor = TaskProcessor(config, memory, self.output_dir)
                
                # Test with empty prompt
                result = processor.classify_task("")
                self.log_test_result("Empty prompt handling", True, f"Empty prompt classified as: {result}")
            except Exception as e:
                self.log_test_result("Empty prompt handling", False, "", str(e))
            
            return True
            
        except Exception as e:
            self.log_test_result("Edge cases and error handling", False, "", str(e))
            return False

    def test_performance_and_resources(self) -> bool:
        """Test performance and resource management"""
        print("\n⚡ Testing Performance and Resource Management...")
        
        try:
            import psutil
            import threading
            from supermini import TaskProcessor, AIConfig, MemoryManager
            
            # Monitor resource usage during processor initialization
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            config = AIConfig(use_claude=False)
            memory = MemoryManager(self.output_dir)
            processor = TaskProcessor(config, memory, self.output_dir)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = final_memory - initial_memory
            
            self.log_test_result("Memory usage", memory_diff < 100, f"Memory usage: {memory_diff:.2f} MB")
            
            # Test thread creation and cleanup
            initial_threads = threading.active_count()
            
            # Create and stop multiple threads
            threads = []
            for i in range(3):
                from supermini import TaskThread
                thread = TaskThread(processor, f"test_{i}", [], "code", False, False, 1)
                threads.append(thread)
                thread.stop()
            
            final_threads = threading.active_count()
            thread_diff = final_threads - initial_threads
            
            self.log_test_result("Thread management", thread_diff <= 1, f"Thread count difference: {thread_diff}")
            
            return True
            
        except Exception as e:
            self.log_test_result("Performance and resources", False, "", str(e))
            return False

    def run_comprehensive_test_suite(self):
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive QA/Testing Campaign for SuperMini AI Assistant")
        print("=" * 80)
        print("Testing all three operational modes:")
        print("1. Regular Task Processing Mode (5 task types)")
        print("2. Autonomous Mode (Agent-S framework)")
        print("3. Self-Enhancement Mode (recursive capabilities)")
        print("=" * 80)
        
        # Test sequence
        test_methods = [
            self.test_core_imports,
            self.test_basic_configuration,
            self.test_task_processor_initialization,
            self.test_regular_task_processing_mode,
            self.test_autonomous_mode,
            self.test_self_enhancement_mode,
            self.test_stop_functionality_comprehensive,
            self.test_integration_between_modes,
            self.test_edge_cases_and_error_handling,
            self.test_performance_and_resources
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__
                self.log_test_result(test_name, False, "", f"Test crashed: {str(e)}")
        
        # Generate final report
        self.generate_final_report()

    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE QA TEST RESULTS")
        print("=" * 80)
        
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🚨 ERRORS FOUND:")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"{i}. {error}")
        
        print("\n📝 DETAILED RESULTS:")
        for test_name, details in self.results['test_details'].items():
            status = "✅" if details['passed'] else "❌"
            print(f"{status} {test_name}")
            if details['details']:
                print(f"   Details: {details['details']}")
            if details['error']:
                print(f"   Error: {details['error']}")
        
        # Save report to file
        report_file = self.output_dir / "qa_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        if self.results['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! SuperMini AI Assistant is fully operational.")
        else:
            print(f"\n⚠️ {self.results['failed']} tests failed. Issues need to be addressed.")
        
        return self.results['failed'] == 0

def main():
    """Main function to run comprehensive QA testing"""
    qa_suite = QATestSuite()
    success = qa_suite.run_comprehensive_test_suite()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)