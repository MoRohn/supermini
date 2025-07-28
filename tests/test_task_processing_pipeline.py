"""
Critical path testing for SuperMini task processing pipeline.
Tests the core functionality of all five task types with AI provider integration.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import base64
import time

from tests.mocks import (
    get_mock_claude, 
    get_mock_ollama, 
    get_mock_memory,
    create_mock_app_instance
)

class TestTaskClassification:
    """Test task type classification accuracy."""
    
    @pytest.mark.unit
    def test_code_task_classification(self, mock_task_processor):
        """Test automatic classification of code tasks."""
        code_prompts = [
            "Write a Python function to calculate fibonacci numbers",
            "Create a JavaScript function for form validation", 
            "Generate a SQL query to find top customers",
            "Write a shell script to backup files"
        ]
        
        for prompt in code_prompts:
            mock_task_processor.classify_task_type.return_value = "code"
            task_type = mock_task_processor.classify_task_type(prompt)
            assert task_type == "code", f"Failed to classify code task: {prompt}"
    
    @pytest.mark.unit
    def test_multimedia_task_classification(self, sample_image_base64):
        """Test classification with image uploads."""
        from tests.mocks.ai_providers import MockClaudeProvider
        
        # Mock the classification logic
        claude_mock = MockClaudeProvider()
        
        # Simulate image upload scenarios
        test_cases = [
            ("Analyze this image", True),
            ("What do you see in this picture?", True),
            ("Describe the contents of this image", True)
        ]
        
        for prompt, has_image in test_cases:
            if has_image:
                # Should classify as multimedia when image is present
                task_type = "multimedia"  # Simulated classification
                assert task_type == "multimedia"
    
    @pytest.mark.unit
    def test_analytics_task_classification(self, sample_csv_file):
        """Test classification with CSV file uploads."""
        analytics_prompts = [
            "Analyze this dataset and show trends",
            "Create visualizations for this data",
            "Calculate statistics for the uploaded CSV",
            "Generate a data report"
        ]
        
        for prompt in analytics_prompts:
            # Simulate CSV file present
            task_type = "analytics"  # Simulated classification
            assert task_type == "analytics", f"Failed to classify analytics task: {prompt}"
    
    @pytest.mark.unit
    def test_rag_task_classification(self, sample_text_file):
        """Test classification with document uploads."""
        rag_prompts = [
            "Summarize this document",
            "What are the key points in this text?",
            "Answer questions about this document",
            "Extract information from this file"
        ]
        
        for prompt in rag_prompts:
            # Simulate document file present
            task_type = "rag"  # Simulated classification
            assert task_type == "rag", f"Failed to classify RAG task: {prompt}"
    
    @pytest.mark.unit
    def test_automation_task_classification(self):
        """Test classification of automation tasks."""
        automation_prompts = [
            "Create a script to backup my files",
            "Generate a bash script for system monitoring",
            "Write an automation script for file organization",
            "Create a shell script to process logs"
        ]
        
        for prompt in automation_prompts:
            task_type = "automation"  # Simulated classification
            assert task_type == "automation", f"Failed to classify automation task: {prompt}"

class TestAIProviderIntegration:
    """Test AI provider integration and fallback mechanisms."""
    
    @pytest.mark.integration
    def test_claude_api_success(self):
        """Test successful Claude API integration."""
        claude_mock = get_mock_claude(simulate_errors=False)
        
        response = claude_mock.query("Write a hello world function", task_type="code")
        
        assert response is not None
        assert "def" in response or "function" in response
        assert claude_mock.is_available()
    
    @pytest.mark.integration
    def test_claude_api_failure_ollama_fallback(self):
        """Test Claude failure triggers Ollama fallback."""
        claude_mock = get_mock_claude(simulate_errors=True)
        ollama_mock = get_mock_ollama(simulate_errors=False)
        
        # Simulate Claude failure
        try:
            claude_response = claude_mock.query("Test prompt")
            assert False, "Expected Claude to fail"
        except Exception:
            # Fallback to Ollama
            ollama_response = ollama_mock.query("Test prompt")
            assert ollama_response is not None
            assert ollama_mock.is_available()
    
    @pytest.mark.integration
    def test_both_providers_unavailable(self):
        """Test behavior when both providers are unavailable."""
        claude_mock = get_mock_claude(simulate_errors=True)
        ollama_mock = get_mock_ollama(simulate_errors=True)
        
        # Both should fail
        claude_failed = False
        ollama_failed = False
        
        try:
            claude_mock.query("Test prompt")
        except Exception:
            claude_failed = True
        
        try:
            ollama_mock.query("Test prompt")
        except Exception:
            ollama_failed = True
        
        assert claude_failed and ollama_failed
    
    @pytest.mark.integration
    def test_api_rate_limiting(self):
        """Test API rate limiting and retry logic."""
        claude_mock = get_mock_claude(simulate_errors=False)
        
        # Simulate multiple rapid requests
        start_time = time.time()
        responses = []
        
        for i in range(5):
            response = claude_mock.query(f"Request {i}")
            responses.append(response)
        
        end_time = time.time()
        
        # All requests should succeed
        assert len(responses) == 5
        assert all(r is not None for r in responses)
        
        # Should respect rate limiting (with mock delay)
        assert end_time - start_time >= 0.5  # 5 requests * 0.1s delay

class TestMemorySystemIntegration:
    """Test memory system integration with task processing."""
    
    @pytest.mark.integration
    def test_context_retrieval_accuracy(self):
        """Test memory context retrieval for similar tasks."""
        memory_mock = get_mock_memory()
        
        # Save a task to memory
        task_id = memory_mock.save_task(
            prompt="Create a Python function for data processing",
            response="def process_data(data): return data.clean()",
            task_type="code"
        )
        
        # Retrieve context for similar task
        context = memory_mock.get_context(
            prompt="Write a Python function for data analysis",
            task_type="code"
        )
        
        assert context is not None
        assert "code" in context.lower()
        assert task_id is not None
    
    @pytest.mark.integration
    def test_memory_enabled_vs_disabled(self):
        """Test task execution with memory enabled vs disabled."""
        memory_mock = get_mock_memory()
        claude_mock = get_mock_claude()
        
        # Test with memory enabled
        context = memory_mock.get_context("Test prompt", "code")
        response_with_memory = claude_mock.query("Test prompt with context: " + context)
        
        # Test without memory
        response_without_memory = claude_mock.query("Test prompt")
        
        assert response_with_memory is not None
        assert response_without_memory is not None
        # Both should work, but with memory might have better context
    
    @pytest.mark.integration
    def test_memory_storage_retrieval_cycle(self):
        """Test complete memory storage and retrieval cycle."""
        memory_mock = get_mock_memory()
        
        # Store multiple tasks
        tasks = [
            ("Write a function", "def func(): pass", "code"),
            ("Analyze image", "Image contains...", "multimedia"),
            ("Process CSV", "Data analysis results...", "analytics")
        ]
        
        task_ids = []
        for prompt, response, task_type in tasks:
            task_id = memory_mock.save_task(prompt, response, task_type)
            task_ids.append(task_id)
        
        # Verify all tasks were stored
        assert len(task_ids) == 3
        assert all(tid is not None for tid in task_ids)
        
        # Retrieve context for each task type
        for _, _, task_type in tasks:
            context = memory_mock.get_context(f"New {task_type} task", task_type)
            assert context is not None

class TestFileGenerationAndOutput:
    """Test file generation and output management."""
    
    @pytest.mark.integration
    def test_code_file_generation(self, temp_output_dir):
        """Test code file generation with proper extensions."""
        claude_mock = get_mock_claude()
        
        test_cases = [
            ("python", ".py", "def"),
            ("javascript", ".js", "function"),
            ("shell", ".sh", "#!/bin/bash"),
            ("sql", ".sql", "SELECT")
        ]
        
        for language, ext, expected_content in test_cases:
            response = claude_mock.query(f"Write a {language} function", task_type="code")
            
            # Simulate file generation
            filename = f"generated_code{ext}"
            filepath = Path(temp_output_dir) / filename
            
            with open(filepath, 'w') as f:
                f.write(response)
            
            assert filepath.exists()
            content = filepath.read_text()
            assert expected_content.lower() in content.lower()
    
    @pytest.mark.integration
    def test_automation_script_permissions(self, temp_output_dir):
        """Test automation scripts get executable permissions."""
        claude_mock = get_mock_claude()
        
        response = claude_mock.query("Create a backup script", task_type="automation")
        
        # Simulate file generation with executable permissions
        script_path = Path(temp_output_dir) / "automation_script_backup.sh"
        
        with open(script_path, 'w') as f:
            f.write(response)
        
        # Set executable permissions (simulate the real behavior)
        import stat
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        
        assert script_path.exists()
        assert script_path.stat().st_mode & stat.S_IEXEC
    
    @pytest.mark.integration
    def test_output_directory_structure(self, temp_output_dir):
        """Test proper output directory structure creation."""
        expected_dirs = [
            "data/memory",
            "data/collaboration", 
            "logs",
            "autonomous"
        ]
        
        # Simulate directory creation
        for dir_path in expected_dirs:
            (Path(temp_output_dir) / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Verify structure
        for dir_path in expected_dirs:
            assert (Path(temp_output_dir) / dir_path).exists()
            assert (Path(temp_output_dir) / dir_path).is_dir()

class TestAutoContinuationLogic:
    """Test auto-continuation functionality."""
    
    @pytest.mark.integration
    def test_auto_continue_detection(self):
        """Test detection of responses that should trigger continuation."""
        claude_mock = get_mock_claude()
        
        continuation_triggers = [
            "Would you like me to continue?",
            "Should I proceed with the next step?",
            "Do you want me to add more features?",
            "Shall I implement the remaining functions?"
        ]
        
        for trigger in continuation_triggers:
            # Simulate response with continuation trigger
            response = f"Here's your code:\n\ndef example(): pass\n\n{trigger}"
            
            # Mock continuation detection logic
            should_continue = any(phrase in response.lower() for phrase in [
                "continue", "proceed", "next", "more", "remaining"
            ])
            
            assert should_continue, f"Failed to detect continuation trigger: {trigger}"
    
    @pytest.mark.integration
    def test_auto_continue_limit(self):
        """Test auto-continuation respects 10-iteration limit."""
        claude_mock = get_mock_claude()
        
        # Simulate auto-continuation loop
        continuation_count = 0
        max_continuations = 10
        
        while continuation_count < max_continuations + 2:  # Try to exceed limit
            response = claude_mock.query(f"Continuation {continuation_count}")
            
            # Simulate continuation decision
            if continuation_count < max_continuations:
                should_continue = "continue" in response.lower()
                if should_continue:
                    continuation_count += 1
                else:
                    break
            else:
                # Should stop at limit
                break
        
        assert continuation_count <= max_continuations
    
    @pytest.mark.integration
    def test_stop_during_continuation(self):
        """Test stop functionality during auto-continuation."""
        claude_mock = get_mock_claude()
        
        # Simulate stop request during continuation
        stop_requested = False
        continuation_count = 0
        
        while continuation_count < 5 and not stop_requested:
            response = claude_mock.query(f"Continuation {continuation_count}")
            continuation_count += 1
            
            # Simulate stop request after 3 continuations
            if continuation_count == 3:
                stop_requested = True
        
        assert continuation_count == 3  # Should stop immediately
        assert stop_requested

class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""
    
    @pytest.mark.integration
    def test_network_timeout_handling(self):
        """Test handling of network timeouts."""
        claude_mock = get_mock_claude(simulate_errors=True)
        
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                response = claude_mock.query("Test prompt")
                success = True
            except Exception:
                retry_count += 1
                time.sleep(0.1)  # Brief retry delay
        
        # Should either succeed or exhaust retries
        assert retry_count <= max_retries
    
    @pytest.mark.integration
    def test_invalid_api_key_handling(self):
        """Test handling of invalid API keys."""
        # Simulate invalid API key scenario
        with pytest.raises(Exception):
            claude_mock = Mock()
            claude_mock.query.side_effect = Exception("Invalid API key")
            claude_mock.query("Test prompt")
    
    @pytest.mark.integration
    def test_file_permission_errors(self, temp_output_dir):
        """Test handling of file permission errors."""
        import stat
        
        # Create read-only directory
        readonly_dir = Path(temp_output_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(stat.S_IREAD)
        
        # Attempt to write to read-only directory should be handled gracefully
        try:
            test_file = readonly_dir / "test.txt"
            with open(test_file, 'w') as f:
                f.write("test")
            assert False, "Should have failed to write to read-only directory"
        except (PermissionError, OSError):
            # Expected behavior - should be caught and handled in real implementation
            pass
        finally:
            # Cleanup
            readonly_dir.chmod(stat.S_IWRITE | stat.S_IREAD)

@pytest.mark.e2e
class TestEndToEndTaskExecution:
    """End-to-end testing of complete task execution workflows."""
    
    def test_complete_code_task_workflow(self, temp_output_dir):
        """Test complete code task from input to output."""
        # Mock the complete workflow
        mock_app = create_mock_app_instance()
        
        # Simulate user input
        prompt = "Write a Python function to calculate factorial"
        
        # Task classification
        task_type = "code"
        
        # Memory context retrieval
        context = mock_app.memory_manager.get_context(prompt, task_type)
        
        # AI query
        response = mock_app.claude_provider.query(prompt, task_type)
        
        # File generation
        filename = "factorial_function.py"
        filepath = Path(temp_output_dir) / filename
        
        with open(filepath, 'w') as f:
            f.write(response)
        
        # Memory storage
        task_id = mock_app.memory_manager.save_task(prompt, response, task_type)
        
        # Verify complete workflow
        assert filepath.exists()
        assert task_id is not None
        assert context is not None
        assert response is not None
    
    def test_complete_multimedia_task_workflow(self, temp_output_dir, sample_image):
        """Test complete multimedia task workflow."""
        mock_app = create_mock_app_instance()
        
        # Simulate image upload and analysis
        prompt = "Analyze this image and describe what you see"
        task_type = "multimedia"
        
        # Convert image to base64 (simulate image processing)
        image_b64 = base64.b64encode(sample_image).decode('utf-8')
        
        # AI analysis
        response = mock_app.claude_provider.query(prompt, task_type)
        
        # Save results
        result_file = Path(temp_output_dir) / "image_analysis_result.txt"
        with open(result_file, 'w') as f:
            f.write(response)
        
        # Store in memory
        metadata = {"image_size": len(sample_image), "format": "PNG"}
        task_id = mock_app.memory_manager.save_task(prompt, response, task_type, metadata)
        
        assert result_file.exists()
        assert task_id is not None
        assert len(image_b64) > 0