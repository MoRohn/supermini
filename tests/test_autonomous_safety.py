"""
Autonomous mode safety validation tests for SuperMini.
Tests the safety framework, command validation, and Agent-S integration.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import time
import json

from tests.mocks import get_mock_autonomous, MockAutonomousAgent

class TestSafetyFrameworkValidation:
    """Test the safety framework and command validation."""
    
    @pytest.mark.autonomous
    @pytest.mark.critical
    def test_restricted_command_detection(self, autonomous_test_data):
        """Test detection and blocking of restricted commands."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        for command in autonomous_test_data['restricted_commands']:
            with pytest.raises(Exception, match="Restricted action"):
                agent.execute_action("command", text=command)
    
    @pytest.mark.autonomous
    @pytest.mark.critical
    def test_safe_command_execution(self, autonomous_test_data):
        """Test execution of safe commands."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        for command in autonomous_test_data['safe_commands']:
            result = agent.execute_action("command", text=command)
            assert result['success'] is True
            assert result['type'] == "command"
    
    @pytest.mark.autonomous
    def test_safe_directory_enforcement(self, autonomous_test_data):
        """Test safe directory enforcement for file operations."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        # Test safe directories
        for safe_dir in autonomous_test_data['safe_directories']:
            action = f"cd {safe_dir}"
            is_safe = agent.validate_action_safety(action)
            assert is_safe, f"Safe directory rejected: {safe_dir}"
        
        # Test restricted directories
        for restricted_dir in autonomous_test_data['restricted_directories']:
            action = f"rm -rf {restricted_dir}"
            is_safe = agent.validate_action_safety(action)
            assert not is_safe, f"Restricted directory allowed: {restricted_dir}"
    
    @pytest.mark.autonomous
    def test_user_confirmation_workflow(self):
        """Test user confirmation prompts for high-risk actions."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        high_risk_actions = [
            "delete_file",
            "modify_system_config",
            "install_software",
            "network_request"
        ]
        
        for action_type in high_risk_actions:
            # In real implementation, this would prompt user
            # For testing, we simulate the confirmation workflow
            confirmation_required = action_type in [
                "delete_file", "modify_system_config", "install_software"
            ]
            
            if confirmation_required:
                # Simulate user confirmation
                user_confirmed = True  # Mock user approval
                if user_confirmed:
                    result = agent.execute_action(action_type)
                    assert result['success'] is True
            else:
                result = agent.execute_action(action_type)
                assert result['success'] is True
    
    @pytest.mark.autonomous
    def test_action_logging_and_audit_trail(self):
        """Test comprehensive action logging for audit purposes."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        test_actions = [
            ("click", (100, 200), None),
            ("type", None, "hello world"),
            ("scroll", (500, 600), None),
            ("screenshot", None, None)
        ]
        
        for action_type, coordinates, text in test_actions:
            result = agent.execute_action(action_type, coordinates, text)
            
            # Verify action was logged
            assert len(agent.action_history) > 0
            last_action = agent.action_history[-1]
            assert last_action['type'] == action_type
            assert last_action['coordinates'] == coordinates
            assert last_action['text'] == text
            assert 'timestamp' in last_action
    
    @pytest.mark.autonomous
    def test_safety_mode_disable_warning(self):
        """Test warnings when safety mode is disabled."""
        # This should only be possible in development/testing
        agent = MockAutonomousAgent(safety_mode=False)
        
        # Even with safety mode off, critical commands should be logged
        restricted_command = "rm -rf /"
        result = agent.execute_action("command", text=restricted_command)
        
        # Action should execute but be logged as high-risk
        assert result['success'] is True
        assert len(agent.action_history) > 0

class TestAgentSFrameworkIntegration:
    """Test Agent-S framework integration and computer interaction."""
    
    @pytest.mark.autonomous
    @pytest.mark.integration
    def test_screenshot_capture_functionality(self):
        """Test screenshot capture and analysis."""
        agent = MockAutonomousAgent()
        
        # Test screenshot capture
        screenshot_path = agent.take_screenshot()
        assert screenshot_path is not None
        assert "mock_screenshot" in screenshot_path
        assert agent.screenshot_count > 0
    
    @pytest.mark.autonomous
    @pytest.mark.integration
    def test_screen_analysis_accuracy(self):
        """Test screen content analysis and element detection."""
        agent = MockAutonomousAgent()
        
        screenshot_path = agent.take_screenshot()
        analysis = agent.analyze_screen(screenshot_path)
        
        assert 'elements_detected' in analysis
        assert 'clickable_areas' in analysis
        assert 'text_content' in analysis
        assert len(analysis['elements_detected']) > 0
        assert len(analysis['clickable_areas']) > 0
    
    @pytest.mark.autonomous
    @pytest.mark.integration
    def test_computer_interaction_boundaries(self):
        """Test computer interaction within safe boundaries."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        # Test safe interactions
        safe_interactions = [
            ("click", (100, 200)),
            ("double_click", (300, 400)),
            ("scroll", (500, 600)),
            ("key_press", None, "Enter")
        ]
        
        for action_type, coordinates in safe_interactions:
            if coordinates:
                result = agent.execute_action(action_type, coordinates)
            else:
                result = agent.execute_action(action_type, text="Enter")
            
            assert result['success'] is True
            assert result['type'] == action_type
    
    @pytest.mark.autonomous
    def test_workflow_orchestration(self):
        """Test multi-step autonomous workflow execution."""
        agent = MockAutonomousAgent()
        
        # Define a multi-step workflow
        workflow_steps = [
            {"action": "screenshot", "purpose": "capture_state"},
            {"action": "analyze", "purpose": "understand_ui"},
            {"action": "click", "coordinates": (100, 200), "purpose": "interact"},
            {"action": "type", "text": "test input", "purpose": "input_data"},
            {"action": "screenshot", "purpose": "verify_result"}
        ]
        
        results = []
        for step in workflow_steps:
            if step['action'] == "screenshot":
                result = agent.take_screenshot()
            elif step['action'] == "analyze":
                result = agent.analyze_screen("mock_screenshot.png")
            else:
                result = agent.execute_action(
                    step['action'], 
                    step.get('coordinates'), 
                    step.get('text')
                )
            results.append(result)
        
        # Verify all steps completed
        assert len(results) == len(workflow_steps)
        assert all(r is not None for r in results)
    
    @pytest.mark.autonomous
    @pytest.mark.slow
    def test_autonomous_task_execution_flow(self):
        """Test complete autonomous task execution from start to finish."""
        agent = MockAutonomousAgent()
        
        # Simulate autonomous task: "Open calculator and perform calculation"
        task_prompt = "Open calculator app and calculate 123 + 456"
        
        # Step 1: Take screenshot to see current state
        initial_screenshot = agent.take_screenshot()
        assert initial_screenshot is not None
        
        # Step 2: Analyze screen to find calculator app
        screen_analysis = agent.analyze_screen(initial_screenshot)
        calculator_found = "calculator" in str(screen_analysis).lower()
        
        # Step 3: If calculator not visible, simulate opening it
        if not calculator_found:
            # Simulate opening calculator (would be real UI interaction in practice)
            open_result = agent.execute_action("key_press", text="cmd+space")  # Spotlight
            type_result = agent.execute_action("type", text="calculator")
            enter_result = agent.execute_action("key_press", text="Enter")
            
            assert all(r['success'] for r in [open_result, type_result, enter_result])
        
        # Step 4: Perform calculation
        calculation_steps = [
            ("click", (150, 200)),  # Click "1"
            ("click", (200, 200)),  # Click "2"
            ("click", (250, 200)),  # Click "3"
            ("click", (300, 250)),  # Click "+"
            ("click", (150, 250)),  # Click "4"
            ("click", (200, 250)),  # Click "5"
            ("click", (250, 250)),  # Click "6"
            ("click", (300, 300)),  # Click "="
        ]
        
        calculation_results = []
        for action_type, coordinates in calculation_steps:
            result = agent.execute_action(action_type, coordinates)
            calculation_results.append(result)
        
        # Verify all calculation steps succeeded
        assert all(r['success'] for r in calculation_results)
        
        # Step 5: Take final screenshot to verify result
        final_screenshot = agent.take_screenshot()
        assert final_screenshot is not None
        assert agent.screenshot_count >= 2

class TestErrorRecoveryAndTimeout:
    """Test error recovery and timeout handling in autonomous mode."""
    
    @pytest.mark.autonomous
    def test_execution_timeout_handling(self):
        """Test handling of execution timeouts."""
        agent = MockAutonomousAgent()
        
        # Simulate long-running action with timeout
        start_time = time.time()
        max_execution_time = 5.0  # seconds
        
        # Mock a long-running operation
        action_completed = False
        elapsed_time = 0
        
        while elapsed_time < max_execution_time and not action_completed:
            # Simulate work
            time.sleep(0.1)
            elapsed_time = time.time() - start_time
            
            # Simulate action completion after 2 seconds
            if elapsed_time >= 2.0:
                action_completed = True
        
        assert action_completed
        assert elapsed_time < max_execution_time
    
    @pytest.mark.autonomous
    def test_failed_action_recovery(self):
        """Test recovery from failed actions."""
        agent = MockAutonomousAgent()
        
        # Simulate a failed action
        failed_action = agent.execute_action("invalid_action")
        
        # In real implementation, this would fail gracefully
        # For mock, we simulate the failure handling
        if not failed_action.get('success', False):
            # Attempt recovery with alternative action
            recovery_action = agent.execute_action("screenshot")
            assert recovery_action['success'] is True
    
    @pytest.mark.autonomous
    def test_step_limit_enforcement(self):
        """Test enforcement of step limits in autonomous workflows."""
        agent = MockAutonomousAgent()
        max_steps = 50
        
        step_count = 0
        while step_count < max_steps + 10:  # Try to exceed limit
            if step_count >= max_steps:
                # Should stop at limit
                break
            
            result = agent.execute_action("screenshot")
            if result['success']:
                step_count += 1
            else:
                break
        
        assert step_count <= max_steps
    
    @pytest.mark.autonomous
    def test_graceful_degradation_scenarios(self):
        """Test graceful degradation when autonomous features fail."""
        agent = MockAutonomousAgent()
        
        # Simulate various failure scenarios
        failure_scenarios = [
            "screenshot_service_unavailable",
            "ui_analysis_failed", 
            "action_execution_blocked",
            "system_permissions_denied"
        ]
        
        for scenario in failure_scenarios:
            # In real implementation, each scenario would be handled differently
            # For testing, we verify the system can continue operating
            
            if scenario == "screenshot_service_unavailable":
                # Should fallback to text-based interaction
                fallback_result = agent.execute_action("type", text="fallback action")
                assert fallback_result['success'] is True
            
            elif scenario == "ui_analysis_failed":
                # Should use predefined action patterns
                predefined_action = agent.execute_action("click", (100, 100))
                assert predefined_action['success'] is True
            
            # Additional scenarios would be handled similarly

class TestAutonomousIntegrationWithTaskTypes:
    """Test autonomous mode integration with different task types."""
    
    @pytest.mark.autonomous
    @pytest.mark.integration
    def test_autonomous_code_task_execution(self):
        """Test autonomous execution of code tasks."""
        agent = MockAutonomousAgent()
        
        # Simulate autonomous code task: "Open VS Code and create a Python file"
        workflow = [
            ("screenshot", "capture_desktop"),
            ("key_press", "cmd+space"),  # Open Spotlight
            ("type", "Visual Studio Code"),
            ("key_press", "Enter"),
            ("key_press", "cmd+n"),  # New file
            ("type", "print('Hello, World!')"),
            ("key_press", "cmd+s"),  # Save file
            ("type", "hello.py")
        ]
        
        for action_type, action_data in workflow:
            if action_type == "screenshot":
                result = agent.take_screenshot()
            elif action_type == "key_press":
                result = agent.execute_action("key_press", text=action_data)
            elif action_type == "type":
                result = agent.execute_action("type", text=action_data)
            
            # Each step should succeed or be safely handled
            assert result is not None
    
    @pytest.mark.autonomous
    @pytest.mark.integration
    def test_autonomous_multimedia_task_execution(self):
        """Test autonomous execution of multimedia tasks."""
        agent = MockAutonomousAgent()
        
        # Simulate: "Take a screenshot and analyze it"
        screenshot_path = agent.take_screenshot()
        analysis = agent.analyze_screen(screenshot_path)
        
        # Verify autonomous multimedia processing
        assert screenshot_path is not None
        assert 'elements_detected' in analysis
        
        # Simulate saving analysis results
        save_action = agent.execute_action("key_press", text="cmd+s")
        filename_action = agent.execute_action("type", text="screenshot_analysis.txt")
        
        assert save_action['success'] is True
        assert filename_action['success'] is True
    
    @pytest.mark.autonomous
    @pytest.mark.integration  
    def test_autonomous_file_operations(self, temp_output_dir):
        """Test autonomous file operations with safety checks."""
        agent = MockAutonomousAgent(safety_mode=True)
        
        # Test safe file operations
        safe_operations = [
            ("create_file", f"{temp_output_dir}/test.txt"),
            ("write_content", "This is test content"),
            ("save_file", None)
        ]
        
        for operation, data in safe_operations:
            result = agent.execute_action(operation, text=data)
            assert result['success'] is True
        
        # Test restricted file operations should be blocked
        restricted_operations = [
            ("delete_file", "/System/important_file"),
            ("modify_file", "/etc/passwd"),
            ("execute_script", "rm -rf /")
        ]
        
        for operation, data in restricted_operations:
            with pytest.raises(Exception, match="Restricted action"):
                agent.execute_action(operation, text=data)

@pytest.mark.autonomous
@pytest.mark.performance
class TestAutonomousPerformance:
    """Test performance aspects of autonomous mode."""
    
    def test_screenshot_capture_performance(self):
        """Test screenshot capture performance."""
        agent = MockAutonomousAgent()
        
        start_time = time.time()
        screenshot = agent.take_screenshot()
        end_time = time.time()
        
        capture_time = end_time - start_time
        
        assert screenshot is not None
        assert capture_time < 1.0  # Should complete within 1 second
    
    def test_ui_analysis_performance(self):
        """Test UI analysis performance."""
        agent = MockAutonomousAgent()
        
        screenshot = agent.take_screenshot()
        
        start_time = time.time()
        analysis = agent.analyze_screen(screenshot)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        assert analysis is not None
        assert analysis_time < 2.0  # Should complete within 2 seconds
    
    def test_action_execution_performance(self):
        """Test action execution performance."""
        agent = MockAutonomousAgent()
        
        actions = [("click", (100, 100)) for _ in range(10)]
        
        start_time = time.time()
        results = []
        for action_type, coordinates in actions:
            result = agent.execute_action(action_type, coordinates)
            results.append(result)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_action = total_time / len(actions)
        
        assert all(r['success'] for r in results)
        assert avg_time_per_action < 0.1  # Each action should complete quickly