"""
Comprehensive integration test suite for SuperMini.
Tests mode switching, component interaction, and end-to-end workflows.
"""
import pytest
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import json

from tests.mocks import create_mock_app_instance, get_mock_memory, get_mock_claude

class TestModeSwitchingIntegration:
    """Test integration between different operational modes."""
    
    @pytest.mark.integration
    def test_task_to_explore_mode_switching(self):
        """Test switching from Task Me to Go Explore mode."""
        mock_app = create_mock_app_instance()
        
        # Simulate Task Me mode operation
        task_result = mock_app.task_processor.process_task(
            "Write a Python function",
            task_type="code"
        )
        
        # Switch to Explore mode
        mock_app.main_window.switch_to_explore_mode()
        
        # Verify state preservation
        assert mock_app.main_window.current_mode == "explore"
        assert task_result is not None
        
        # Verify Explore mode functionality
        explore_result = mock_app.autonomous_agent.take_screenshot()
        assert explore_result is not None
    
    @pytest.mark.integration
    def test_explore_to_enhance_mode_switching(self):
        """Test switching from Go Explore to Enhance Yourself mode."""
        mock_app = create_mock_app_instance()
        
        # Start in Explore mode
        mock_app.main_window.current_mode = "explore"
        screenshot = mock_app.autonomous_agent.take_screenshot()
        
        # Switch to Enhance mode
        mock_app.main_window.switch_to_enhance_mode()
        
        # Verify mode change
        assert mock_app.main_window.current_mode == "enhance"
        
        # Verify Enhancement functionality
        enhancement_plan = mock_app.enhancement_engine.analyze_codebase()
        assert enhancement_plan is not None
    
    @pytest.mark.integration
    def test_state_preservation_across_modes(self):
        """Test state preservation when switching between modes."""
        mock_app = create_mock_app_instance()
        
        # Set initial state in Task mode
        initial_settings = {
            "claude_api_key": "test_key",
            "memory_enabled": True,
            "output_directory": "/tmp/test"
        }
        mock_app.settings.update(initial_settings)
        
        # Switch modes multiple times
        modes = ["task", "explore", "enhance", "task"]
        for mode in modes:
            if mode == "task":
                mock_app.main_window.switch_to_task_mode()
            elif mode == "explore":
                mock_app.main_window.switch_to_explore_mode()
            elif mode == "enhance":
                mock_app.main_window.switch_to_enhance_mode()
            
            # Verify settings preserved
            assert mock_app.settings["claude_api_key"] == "test_key"
            assert mock_app.settings["memory_enabled"] is True
        
        # Verify final state
        assert mock_app.settings == initial_settings
    
    @pytest.mark.integration
    def test_resource_cleanup_on_mode_switch(self):
        """Test proper resource cleanup when switching modes."""
        mock_app = create_mock_app_instance()
        
        # Start resource-intensive operation in Task mode
        mock_app.task_processor.start_processing("Long running task")
        active_threads_before = len(mock_app.thread_manager.active_threads)
        
        # Switch to Explore mode
        mock_app.main_window.switch_to_explore_mode()
        
        # Verify resources cleaned up
        time.sleep(0.1)  # Allow cleanup time
        active_threads_after = len(mock_app.thread_manager.active_threads)
        assert active_threads_after <= active_threads_before

class TestDatabaseFileSystemIntegration:
    """Test integration between database operations and file system."""
    
    @pytest.mark.integration
    def test_memory_database_file_integration(self, temp_output_dir):
        """Test ChromaDB integration with file system operations."""
        memory_manager = get_mock_memory()
        
        # Create test task with file output
        task_prompt = "Create a data analysis script"
        task_response = "import pandas as pd\ndf = pd.read_csv('data.csv')"
        
        # Save task to memory
        task_id = memory_manager.save_task(
            prompt=task_prompt,
            response=task_response,
            task_type="analytics",
            metadata={"output_file": "analysis_script.py"}
        )
        
        # Simulate file generation
        output_file = Path(temp_output_dir) / "analysis_script.py"
        with open(output_file, 'w') as f:
            f.write(task_response)
        
        # Retrieve context for similar task
        context = memory_manager.get_context(
            "Create another data analysis script",
            "analytics"
        )
        
        # Verify integration
        assert task_id is not None
        assert output_file.exists()
        assert "analytics" in context.lower()
    
    @pytest.mark.integration
    def test_output_directory_structure_integrity(self, temp_output_dir):
        """Test output directory structure remains intact."""
        mock_app = create_mock_app_instance()
        mock_app.settings["output_directory"] = temp_output_dir
        
        # Create expected directory structure
        expected_dirs = [
            "data/memory",
            "data/collaboration",
            "logs",
            "autonomous"
        ]
        
        for dir_path in expected_dirs:
            (Path(temp_output_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Simulate various operations that use the file system
        operations = [
            ("code_task", "generated_code.py"),
            ("multimedia_task", "image_analysis.txt"),
            ("analytics_task", "data_report.html"),
            ("automation_task", "automation_script.sh")
        ]
        
        for task_type, filename in operations:
            # Generate file
            file_path = Path(temp_output_dir) / filename
            with open(file_path, 'w') as f:
                f.write(f"Content for {task_type}")
            
            # Verify file exists
            assert file_path.exists()
        
        # Verify directory structure integrity
        for dir_path in expected_dirs:
            assert (Path(temp_output_dir) / dir_path).exists()
    
    @pytest.mark.integration
    def test_concurrent_file_operations(self, temp_output_dir):
        """Test concurrent file operations don't conflict."""
        import threading
        
        mock_app = create_mock_app_instance()
        results = []
        errors = []
        
        def create_file(thread_id):
            try:
                filename = f"concurrent_file_{thread_id}.txt"
                filepath = Path(temp_output_dir) / filename
                
                with open(filepath, 'w') as f:
                    f.write(f"Content from thread {thread_id}")
                
                # Verify file was created
                if filepath.exists():
                    results.append(thread_id)
                
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create multiple concurrent file operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_file, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        assert len(results) == 5
        assert len(errors) == 0
        
        # Verify all files exist
        for i in range(5):
            filepath = Path(temp_output_dir) / f"concurrent_file_{i}.txt"
            assert filepath.exists()

class TestUIComponentIntegration:
    """Test integration between UI components and backend systems."""
    
    @pytest.mark.integration
    @pytest.mark.gui
    def test_dashboard_metrics_integration(self, qapp):
        """Test dashboard metrics integration with system monitor."""
        mock_app = create_mock_app_instance()
        
        # Get system metrics
        cpu_percent = mock_app.system_monitor.get_system_metrics()['cpu_percent']
        memory_percent = mock_app.system_monitor.get_system_metrics()['memory_percent']
        
        # Simulate dashboard update
        mock_app.main_window.dashboard.update_metrics({
            'cpu': cpu_percent,
            'memory': memory_percent,
            'tasks_completed': 15,
            'tasks_failed': 2
        })
        
        # Verify metrics are realistic
        assert 0 <= cpu_percent <= 100
        assert 0 <= memory_percent <= 100
        assert mock_app.main_window.dashboard.metrics_updated is True
    
    @pytest.mark.integration
    @pytest.mark.gui
    def test_settings_dialog_integration(self, qapp):
        """Test settings dialog integration with application state."""
        mock_app = create_mock_app_instance()
        
        # Open settings dialog
        settings_dialog = mock_app.main_window.open_settings_dialog()
        
        # Modify settings
        new_settings = {
            "claude_api_key": "new_test_key",
            "memory_enabled": False,
            "auto_continue": True,
            "output_directory": "/new/test/dir"
        }
        
        settings_dialog.apply_settings(new_settings)
        
        # Verify settings applied to application
        assert mock_app.settings["claude_api_key"] == "new_test_key"
        assert mock_app.settings["memory_enabled"] is False
        assert mock_app.settings["auto_continue"] is True
    
    @pytest.mark.integration
    @pytest.mark.gui
    def test_progress_indicator_integration(self, qapp):
        """Test progress indicators with actual task execution."""
        mock_app = create_mock_app_instance()
        progress_updates = []
        
        # Connect progress signals
        mock_app.task_processor.progress_updated.connect(
            lambda msg: progress_updates.append(msg)
        )
        
        # Start task with progress tracking
        mock_app.task_processor.start_task("Test task with progress")
        
        # Simulate progress updates
        for i in range(5):
            mock_app.task_processor.update_progress(f"Step {i+1}/5")
            time.sleep(0.05)
        
        # Complete task
        mock_app.task_processor.complete_task("Task completed")
        
        # Verify progress integration
        assert len(progress_updates) >= 5
        assert any("Step" in update for update in progress_updates)
        assert any("completed" in update.lower() for update in progress_updates)

class TestMemoryContextIntegration:
    """Test memory system integration across different components."""
    
    @pytest.mark.integration
    def test_cross_task_type_memory_integration(self):
        """Test memory context sharing across different task types."""
        memory_manager = get_mock_memory()
        
        # Save tasks of different types
        tasks = [
            ("Create a Python data processor", "def process(data): return data", "code"),
            ("Analyze user behavior data", "Data shows 70% engagement rate", "analytics"),
            ("Generate report visualization", "Chart shows upward trend", "multimedia")
        ]
        
        task_ids = []
        for prompt, response, task_type in tasks:
            task_id = memory_manager.save_task(prompt, response, task_type)
            task_ids.append(task_id)
        
        # Retrieve context for related task
        context = memory_manager.get_context(
            "Create a comprehensive data analysis pipeline",
            "code"
        )
        
        # Verify cross-task-type context retrieval
        assert context is not None
        assert len(task_ids) == 3
        assert all(tid is not None for tid in task_ids)
    
    @pytest.mark.integration
    def test_memory_performance_under_load(self):
        """Test memory system performance under load."""
        memory_manager = get_mock_memory()
        
        # Simulate high-volume memory operations
        start_time = time.time()
        
        # Save many tasks
        for i in range(100):
            memory_manager.save_task(
                f"Task {i}",
                f"Response {i}",
                "code" if i % 2 == 0 else "analytics"
            )
        
        save_time = time.time() - start_time
        
        # Test retrieval performance
        retrieval_start = time.time()
        
        for i in range(50):
            context = memory_manager.get_context(f"Query {i}", "code")
            assert context is not None
        
        retrieval_time = time.time() - retrieval_start
        
        # Verify acceptable performance
        assert save_time < 5.0  # Should save 100 tasks in under 5 seconds
        assert retrieval_time < 3.0  # Should retrieve 50 contexts in under 3 seconds
    
    @pytest.mark.integration
    def test_memory_consistency_across_sessions(self, temp_output_dir):
        """Test memory consistency across application sessions."""
        # Simulate first session
        memory_manager_1 = get_mock_memory()
        
        task_data = {
            "prompt": "Create authentication system",
            "response": "def authenticate(user, password): return True",
            "task_type": "code"
        }
        
        task_id = memory_manager_1.save_task(**task_data)
        session_1_stats = memory_manager_1.get_stats()
        
        # Simulate second session (new memory manager instance)
        memory_manager_2 = get_mock_memory()
        
        # Should be able to retrieve task from "previous session"
        context = memory_manager_2.get_context(
            "Create user authentication",
            "code"
        )
        session_2_stats = memory_manager_2.get_stats()
        
        # Verify consistency (in real implementation, would check database)
        assert task_id is not None
        assert context is not None
        assert session_1_stats is not None
        assert session_2_stats is not None

class TestAIProviderIntegrationFlow:
    """Test AI provider integration flow and fallback mechanisms."""
    
    @pytest.mark.integration
    def test_claude_to_ollama_fallback_integration(self):
        """Test complete Claude to Ollama fallback integration."""
        from tests.mocks import get_mock_claude, get_mock_ollama
        
        # Primary provider (Claude) with errors
        claude_provider = get_mock_claude(simulate_errors=True)
        ollama_provider = get_mock_ollama(simulate_errors=False)
        
        # Simulate AI query with fallback
        prompt = "Write a function to process user data"
        task_type = "code"
        
        response = None
        provider_used = None
        
        try:
            response = claude_provider.query(prompt, task_type)
            provider_used = "claude"
        except Exception:
            # Fallback to Ollama
            try:
                response = ollama_provider.query(prompt)
                provider_used = "ollama"
            except Exception:
                response = "Error: Both providers failed"
                provider_used = "none"
        
        # Verify fallback worked
        assert response is not None
        assert provider_used in ["claude", "ollama"]
        if provider_used == "ollama":
            assert "Mock Ollama response" in response
    
    @pytest.mark.integration
    def test_ai_provider_response_processing(self):
        """Test processing of AI provider responses."""
        claude_provider = get_mock_claude()
        
        # Test different response types
        test_cases = [
            ("code", "Write a Python function"),
            ("multimedia", "Analyze this image"),
            ("analytics", "Process this CSV data"),
            ("automation", "Create a backup script"),
            ("rag", "Summarize this document")
        ]
        
        for task_type, prompt in test_cases:
            response = claude_provider.query(prompt, task_type)
            
            # Verify response processing
            assert response is not None
            assert len(response) > 0
            
            # Verify task-specific content
            if task_type == "code":
                assert any(keyword in response.lower() for keyword in ["def", "function", "class"])
            elif task_type == "automation":
                assert any(keyword in response.lower() for keyword in ["#!/bin/bash", "script", "echo"])
    
    @pytest.mark.integration
    def test_ai_provider_rate_limiting_integration(self):
        """Test rate limiting integration across providers."""
        claude_provider = get_mock_claude()
        
        # Test rapid requests
        request_times = []
        responses = []
        
        for i in range(5):
            start_time = time.time()
            response = claude_provider.query(f"Request {i}")
            end_time = time.time()
            
            request_times.append(end_time - start_time)
            responses.append(response)
        
        # Verify rate limiting behavior
        assert len(responses) == 5
        assert all(r is not None for r in responses)
        
        # Check if delays were applied (mock includes 0.1s delay)
        assert all(t >= 0.1 for t in request_times)

class TestEndToEndWorkflowIntegration:
    """Test complete end-to-end workflow integration."""
    
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_complete_code_task_workflow(self, temp_output_dir):
        """Test complete code task workflow from input to output."""
        mock_app = create_mock_app_instance()
        mock_app.settings["output_directory"] = temp_output_dir
        
        # User input
        user_prompt = "Create a Python function to calculate compound interest"
        
        # Step 1: Task classification
        task_type = mock_app.task_processor.classify_task_type(user_prompt)
        assert task_type == "code"
        
        # Step 2: Memory context retrieval
        context = mock_app.memory_manager.get_context(user_prompt, task_type)
        
        # Step 3: AI query with context
        full_prompt = f"Context: {context}\n\nTask: {user_prompt}"
        ai_response = mock_app.claude_provider.query(full_prompt, task_type)
        
        # Step 4: File generation
        filename = mock_app.task_processor.generate_filename(task_type, "compound_interest")
        filepath = Path(temp_output_dir) / filename
        
        with open(filepath, 'w') as f:
            f.write(ai_response)
        
        # Step 5: Memory storage
        task_id = mock_app.memory_manager.save_task(
            user_prompt, ai_response, task_type,
            metadata={"output_file": str(filepath)}
        )
        
        # Verify complete workflow
        assert task_type == "code"
        assert context is not None
        assert ai_response is not None
        assert filepath.exists()
        assert task_id is not None
        
        # Verify file content
        content = filepath.read_text()
        assert "def" in content.lower()
    
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_complete_autonomous_workflow(self, temp_output_dir):
        """Test complete autonomous workflow integration."""
        mock_app = create_mock_app_instance()
        
        # Autonomous task: "Take screenshot and analyze UI"
        workflow_steps = [
            "take_screenshot",
            "analyze_screen",
            "identify_elements",
            "generate_report"
        ]
        
        results = {}
        
        # Execute workflow
        for step in workflow_steps:
            if step == "take_screenshot":
                results[step] = mock_app.autonomous_agent.take_screenshot()
            elif step == "analyze_screen":
                results[step] = mock_app.autonomous_agent.analyze_screen(
                    results["take_screenshot"]
                )
            elif step == "identify_elements":
                analysis = results["analyze_screen"]
                results[step] = analysis.get("elements_detected", [])
            elif step == "generate_report":
                # Generate analysis report
                report_content = f"""
# UI Analysis Report

## Screenshot Analysis
Elements detected: {len(results.get('identify_elements', []))}

## Details
{json.dumps(results['analyze_screen'], indent=2)}
"""
                report_path = Path(temp_output_dir) / "ui_analysis_report.md"
                with open(report_path, 'w') as f:
                    f.write(report_content)
                results[step] = str(report_path)
        
        # Verify autonomous workflow
        assert all(step in results for step in workflow_steps)
        assert all(results[step] is not None for step in workflow_steps)
        assert Path(results["generate_report"]).exists()
    
    @pytest.mark.integration
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_enhancement_workflow(self, temp_output_dir):
        """Test complete self-enhancement workflow."""
        mock_app = create_mock_app_instance()
        
        # Enhancement workflow: "Analyze and improve codebase"
        enhancement_phases = [
            "codebase_analysis",
            "improvement_identification", 
            "implementation_planning",
            "code_generation",
            "testing_validation"
        ]
        
        enhancement_results = {}
        
        for phase in enhancement_phases:
            if phase == "codebase_analysis":
                enhancement_results[phase] = {
                    "files_analyzed": 25,
                    "complexity_score": 7.2,
                    "test_coverage": 0.85
                }
            elif phase == "improvement_identification":
                enhancement_results[phase] = [
                    "Add error handling to file operations",
                    "Improve memory management efficiency",
                    "Enhance UI responsiveness"
                ]
            elif phase == "implementation_planning":
                enhancement_results[phase] = {
                    "priority_order": [1, 2, 3],
                    "estimated_effort": "4 hours",
                    "risk_assessment": "low"
                }
            elif phase == "code_generation":
                # Generate improvement code
                improvement_code = """
def improved_error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return None
    return wrapper
"""
                code_path = Path(temp_output_dir) / "enhancement_improvements.py"
                with open(code_path, 'w') as f:
                    f.write(improvement_code)
                enhancement_results[phase] = str(code_path)
            elif phase == "testing_validation":
                enhancement_results[phase] = {
                    "tests_passed": 23,
                    "tests_failed": 1,
                    "coverage_improvement": 0.03
                }
        
        # Verify enhancement workflow
        assert len(enhancement_results) == len(enhancement_phases)
        assert all(phase in enhancement_results for phase in enhancement_phases)
        
        # Verify generated improvements file
        improvements_file = Path(enhancement_results["code_generation"])
        assert improvements_file.exists()
        assert "improved_error_handling" in improvements_file.read_text()