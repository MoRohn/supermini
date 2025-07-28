#!/usr/bin/env python3
"""
Test script for autonomous capabilities integration
Tests the basic functionality without requiring GUI interaction
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_autonomous_imports():
    """Test that autonomous modules can be imported"""
    print("Testing autonomous imports...")
    
    try:
        from src.autonomous.autonomous_agent import (
            AutonomousAgent, 
            AutonomousWorkflowManager, 
            AutonomousTask,
            SafetyManager
        )
        print("✅ Autonomous agent imports successful")
        return True
    except ImportError as e:
        print(f"❌ Autonomous agent import failed: {e}")
        return False

def test_safety_manager():
    """Test safety manager functionality"""
    print("\nTesting safety manager...")
    
    try:
        from src.autonomous.autonomous_agent import SafetyManager
        
        safety = SafetyManager()
        
        # Test safe action
        is_safe, msg = safety.validate_action("ls -la", {})
        assert is_safe, f"Safe action should be allowed: {msg}"
        print("✅ Safe action validation passed")
        
        # Test restricted action
        is_safe, msg = safety.validate_action("rm -rf /", {})
        assert not is_safe, "Restricted action should be blocked"
        print("✅ Restricted action validation passed")
        
        # Test confirmation requirement
        requires_conf = safety.requires_confirmation("sudo install package")
        assert requires_conf, "High-risk action should require confirmation"
        print("✅ Confirmation requirement test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Safety manager test failed: {e}")
        return False

def test_autonomous_task_creation():
    """Test autonomous task creation"""
    print("\nTesting autonomous task creation...")
    
    try:
        from src.autonomous.autonomous_agent import AutonomousTask
        
        task = AutonomousTask(
            task_id="test_001",
            instruction="Take a screenshot of the desktop",
            task_type="automation",
            context={"test": True}
        )
        
        assert task.task_id == "test_001"
        assert task.instruction == "Take a screenshot of the desktop"
        assert task.task_type == "automation"
        assert task.context == {"test": True}
        
        print("✅ Autonomous task creation passed")
        return True
        
    except Exception as e:
        print(f"❌ Autonomous task creation failed: {e}")
        return False

def test_autonomous_agent_init():
    """Test autonomous agent initialization"""
    print("\nTesting autonomous agent initialization...")
    
    try:
        from src.autonomous.autonomous_agent import AutonomousAgent
        
        config = {
            "model": "gpt-4-vision-preview",
            "api_key": "test-key",
            "max_tokens": 4096,
            "temperature": 0.1
        }
        
        agent = AutonomousAgent(config)
        
        # Check basic properties
        assert agent.config == config
        assert agent.safety_manager is not None
        assert hasattr(agent, 'active_tasks')
        assert hasattr(agent, 'task_history')
        
        print("✅ Autonomous agent initialization passed")
        
        # Test capabilities reporting
        capabilities = agent.get_autonomous_capabilities()
        assert "supported_platforms" in capabilities
        assert "safety_features" in capabilities
        print("✅ Capabilities reporting passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Autonomous agent initialization failed: {e}")
        return False

def test_aimm_integration():
    """Test integration with main SuperMini application"""
    print("\nTesting SuperMini integration...")
    
    try:
        # Test import without running the full application
        print("   Testing autonomous integration in main module...")
        
        # Test that our autonomous classes are available
        from src.autonomous.autonomous_agent import AutonomousAgent
        print("   ✅ AutonomousAgent can be imported by main module")
        
        # Test configuration compatibility
        config = {
            "model": "gpt-4-vision-preview",
            "api_key": "test-key",
            "max_tokens": 4096,
            "temperature": 0.1
        }
        
        agent = AutonomousAgent(config)
        print("   ✅ AutonomousAgent compatible with SuperMini config format")
        
        print("✅ SuperMini integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ SuperMini integration test failed: {e}")
        return False

def test_workflow_manager():
    """Test workflow manager functionality"""
    print("\nTesting workflow manager...")
    
    try:
        from src.autonomous.autonomous_agent import AutonomousAgent, AutonomousWorkflowManager, AutonomousTask
        
        config = {"model": "test", "api_key": "test"}
        agent = AutonomousAgent(config)
        workflow_manager = AutonomousWorkflowManager(agent)
        
        # Create test tasks
        task1 = AutonomousTask("task1", "First task", "test", {})
        task2 = AutonomousTask("task2", "Second task", "test", {})
        
        # Create workflow
        workflow_id = workflow_manager.create_workflow("Test Workflow", [task1, task2])
        assert workflow_id in workflow_manager.workflows
        
        workflow = workflow_manager.workflows[workflow_id]
        assert workflow["name"] == "Test Workflow"
        assert len(workflow["tasks"]) == 2
        
        print("✅ Workflow manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Workflow manager test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🤖 Starting Autonomous Capabilities Test Suite")
    print("=" * 50)
    
    tests = [
        test_autonomous_imports,
        test_safety_manager,
        test_autonomous_task_creation,
        test_autonomous_agent_init,
        test_workflow_manager,
        test_aimm_integration
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Autonomous integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)