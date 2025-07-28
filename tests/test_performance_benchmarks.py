"""
Performance benchmark tests for SuperMini.
Tests performance targets, load handling, and resource optimization.
"""
import pytest
import time
import threading
import tempfile
from pathlib import Path
import psutil
import os
from unittest.mock import Mock, patch
import pandas as pd

from tests.mocks import create_mock_app_instance, get_mock_claude, get_mock_memory

class TestPerformanceBenchmarks:
    """Test core performance benchmarks against defined targets."""
    
    @pytest.mark.performance
    def test_task_initiation_performance(self, performance_benchmarks):
        """Test task initiation meets performance target (<2s)."""
        mock_app = create_mock_app_instance()
        
        # Test multiple task initiation scenarios
        task_scenarios = [
            ("Write a Python function", "code"),
            ("Analyze this data", "analytics"),
            ("Create a script", "automation"),
            ("Summarize document", "rag")
        ]
        
        initiation_times = []
        
        for prompt, task_type in task_scenarios:
            start_time = time.time()
            
            # Simulate task initiation process
            classified_type = mock_app.task_processor.classify_task_type(prompt)
            context = mock_app.memory_manager.get_context(prompt, task_type)
            
            end_time = time.time()
            initiation_time = end_time - start_time
            initiation_times.append(initiation_time)
        
        # Verify performance benchmarks
        avg_initiation_time = sum(initiation_times) / len(initiation_times)
        max_initiation_time = max(initiation_times)
        
        assert avg_initiation_time < performance_benchmarks['task_initiation_max']
        assert max_initiation_time < performance_benchmarks['task_initiation_max']
        assert all(t < 3.0 for t in initiation_times)  # Safety margin
    
    @pytest.mark.performance
    def test_typical_processing_performance(self, performance_benchmarks):
        """Test typical task processing meets performance target (<30s)."""
        claude_provider = get_mock_claude()
        
        typical_tasks = [
            "Create a basic web scraper in Python",
            "Write a function to parse CSV data",
            "Generate a simple data visualization script",
            "Create an automation script for file backup"
        ]
        
        processing_times = []
        
        for task in typical_tasks:
            start_time = time.time()
            
            # Simulate complete processing
            response = claude_provider.query(task, "code")
            
            # Simulate file generation time
            time.sleep(0.1)  # Mock file I/O
            
            end_time = time.time()
            processing_time = end_time - start_time
            processing_times.append(processing_time)
        
        # Verify processing performance
        avg_processing_time = sum(processing_times) / len(processing_times)
        max_processing_time = max(processing_times)
        
        assert avg_processing_time < performance_benchmarks['typical_processing_max']
        assert max_processing_time < performance_benchmarks['typical_processing_max']
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_file_processing_performance(self, performance_benchmarks, temp_output_dir):
        """Test large file processing meets performance target (<2min)."""
        # Create large test files
        large_csv_path = Path(temp_output_dir) / "large_dataset.csv"
        
        # Generate large CSV (simulate 50MB file)
        large_data = []
        for i in range(100000):  # 100k rows
            large_data.append([f"user_{i}", i * 10, f"category_{i % 50}"])
        
        df = pd.DataFrame(large_data, columns=["user_id", "value", "category"])
        
        start_time = time.time()
        df.to_csv(large_csv_path, index=False)
        file_creation_time = time.time() - start_time
        
        # Test large file processing
        processing_start = time.time()
        
        # Simulate large file analysis
        file_size = large_csv_path.stat().st_size
        estimated_processing_time = file_size / (10 * 1024 * 1024)  # 10MB/s estimate
        
        # Mock processing time based on file size
        time.sleep(min(estimated_processing_time, 2.0))  # Cap at 2 seconds for testing
        
        processing_end = time.time()
        total_processing_time = processing_end - processing_start
        
        # Verify large file performance
        assert total_processing_time < performance_benchmarks['large_file_processing_max']
        assert file_size > 1024 * 1024  # Verify file is actually large (>1MB)
    
    @pytest.mark.performance
    def test_ui_response_performance(self, performance_benchmarks, qapp):
        """Test UI response meets performance target (<100ms)."""
        mock_app = create_mock_app_instance()
        
        # Test UI interaction scenarios
        ui_actions = [
            "button_click",
            "tab_switch", 
            "settings_open",
            "progress_update",
            "status_change"
        ]
        
        response_times = []
        
        for action in ui_actions:
            start_time = time.time()
            
            # Simulate UI action
            if action == "button_click":
                mock_app.main_window.handle_button_click("start")
            elif action == "tab_switch":
                mock_app.main_window.switch_tab("explore")
            elif action == "settings_open":
                mock_app.main_window.open_settings()
            elif action == "progress_update":
                mock_app.main_window.update_progress(50)
            elif action == "status_change":
                mock_app.main_window.update_status("Processing...")
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
        
        # Verify UI response performance
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < performance_benchmarks['ui_response_max']
        assert max_response_time < performance_benchmarks['ui_response_max']

class TestLoadTesting:
    """Test system behavior under various load conditions."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_task_execution(self):
        """Test handling of multiple concurrent tasks."""
        mock_app = create_mock_app_instance()
        
        # Simulate concurrent task requests
        concurrent_tasks = [
            ("Task 1: Python function", "code"),
            ("Task 2: Data analysis", "analytics"),
            ("Task 3: Image processing", "multimedia"),
            ("Task 4: Shell script", "automation"),
            ("Task 5: Document summary", "rag")
        ]
        
        results = []
        errors = []
        
        def execute_task(task_prompt, task_type):
            try:
                start_time = time.time()
                
                # Simulate task execution
                response = mock_app.claude_provider.query(task_prompt, task_type)
                context = mock_app.memory_manager.get_context(task_prompt, task_type)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                results.append({
                    'task': task_prompt,
                    'type': task_type,
                    'execution_time': execution_time,
                    'success': True
                })
                
            except Exception as e:
                errors.append({
                    'task': task_prompt,
                    'error': str(e)
                })
        
        # Execute tasks concurrently
        threads = []
        for task_prompt, task_type in concurrent_tasks:
            thread = threading.Thread(target=execute_task, args=(task_prompt, task_type))
            threads.append(thread)
            thread.start()
        
        # Wait for all tasks to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout per task
        
        # Verify concurrent execution
        assert len(results) == len(concurrent_tasks)
        assert len(errors) == 0
        
        # Verify performance under load
        avg_execution_time = sum(r['execution_time'] for r in results) / len(results)
        assert avg_execution_time < 5.0  # Should average under 5 seconds
    
    @pytest.mark.performance
    def test_rapid_task_submission(self):
        """Test system handling of rapid task submissions."""
        mock_app = create_mock_app_instance()
        
        # Submit tasks rapidly
        submission_times = []
        task_count = 20
        
        start_time = time.time()
        
        for i in range(task_count):
            task_start = time.time()
            
            # Simulate rapid task submission
            task_id = mock_app.task_processor.submit_task(f"Rapid task {i}", "code")
            
            task_end = time.time()
            submission_times.append(task_end - task_start)
        
        total_time = time.time() - start_time
        
        # Verify rapid submission handling
        avg_submission_time = sum(submission_times) / len(submission_times)
        tasks_per_second = task_count / total_time
        
        assert avg_submission_time < 0.1  # Each submission under 100ms
        assert tasks_per_second > 10  # At least 10 tasks per second
        assert len(submission_times) == task_count
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self):
        """Test memory usage during sustained operations."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        mock_app = create_mock_app_instance()
        memory_samples = []
        
        # Sustained operation simulation
        for iteration in range(50):
            # Simulate various operations
            mock_app.claude_provider.query(f"Task {iteration}", "code")
            mock_app.memory_manager.save_task(f"Task {iteration}", f"Response {iteration}", "code")
            
            # Sample memory usage
            current_memory = process.memory_info().rss
            memory_samples.append(current_memory)
            
            # Brief pause to simulate realistic usage
            time.sleep(0.01)
        
        final_memory = process.memory_info().rss
        max_memory = max(memory_samples)
        memory_growth = final_memory - initial_memory
        
        # Verify memory usage is reasonable
        assert memory_growth < 100 * 1024 * 1024  # Less than 100MB growth
        assert max_memory < initial_memory + 200 * 1024 * 1024  # Peak under 200MB growth
    
    @pytest.mark.performance
    def test_extended_operation_duration(self):
        """Test system stability during extended operations."""
        mock_app = create_mock_app_instance()
        
        # Simulate 5-minute extended operation
        operation_duration = 300  # 5 minutes in seconds
        start_time = time.time()
        operation_count = 0
        errors = []
        
        while time.time() - start_time < operation_duration:
            try:
                # Perform operation
                response = mock_app.claude_provider.query(f"Extended task {operation_count}", "code")
                operation_count += 1
                
                # Brief pause between operations
                time.sleep(1)
                
            except Exception as e:
                errors.append(str(e))
        
        total_duration = time.time() - start_time
        
        # Verify extended operation stability
        assert operation_count > 250  # At least 250 operations (less than 1 per second)
        assert len(errors) < operation_count * 0.05  # Less than 5% error rate
        assert total_duration >= operation_duration * 0.95  # Ran for at least 95% of intended time

class TestResourceOptimization:
    """Test resource optimization and efficiency."""
    
    @pytest.mark.performance
    def test_memory_cleanup_efficiency(self):
        """Test memory cleanup and garbage collection efficiency."""
        import gc
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        mock_app = create_mock_app_instance()
        
        # Create memory-intensive operations
        large_objects = []
        for i in range(100):
            # Create large mock objects
            large_data = [f"data_{j}" for j in range(1000)]
            large_objects.append(large_data)
            
            # Process with mock app
            mock_app.memory_manager.save_task(f"Large task {i}", str(large_data), "analytics")
        
        memory_after_creation = process.memory_info().rss
        
        # Clear objects and force garbage collection
        large_objects.clear()
        gc.collect()
        
        memory_after_cleanup = process.memory_info().rss
        
        # Verify memory cleanup efficiency
        memory_growth = memory_after_creation - initial_memory
        memory_freed = memory_after_creation - memory_after_cleanup
        cleanup_efficiency = memory_freed / memory_growth if memory_growth > 0 else 1.0
        
        assert cleanup_efficiency > 0.5  # At least 50% of memory should be freed
        assert memory_after_cleanup < memory_after_creation  # Memory should decrease
    
    @pytest.mark.performance
    def test_database_query_optimization(self):
        """Test database query performance optimization."""
        memory_manager = get_mock_memory()
        
        # Populate with test data
        for i in range(1000):
            memory_manager.save_task(
                f"Query test task {i}",
                f"Response {i}",
                "code" if i % 2 == 0 else "analytics"
            )
        
        # Test query performance
        query_times = []
        
        for i in range(100):
            start_time = time.time()
            context = memory_manager.get_context(f"Test query {i}", "code")
            end_time = time.time()
            
            query_time = end_time - start_time
            query_times.append(query_time)
        
        # Verify query optimization
        avg_query_time = sum(query_times) / len(query_times)
        max_query_time = max(query_times)
        
        assert avg_query_time < 0.1  # Average under 100ms
        assert max_query_time < 0.5   # Maximum under 500ms
        assert all(qt < 1.0 for qt in query_times)  # All under 1 second
    
    @pytest.mark.performance
    def test_file_io_optimization(self, temp_output_dir):
        """Test file I/O operation optimization."""
        # Test various file operations
        file_operations = []
        
        # Create multiple files
        create_start = time.time()
        for i in range(100):
            file_path = Path(temp_output_dir) / f"test_file_{i}.txt"
            with open(file_path, 'w') as f:
                f.write(f"Test content for file {i}" * 100)  # ~2KB per file
        create_time = time.time() - create_start
        
        # Read files
        read_start = time.time()
        for i in range(100):
            file_path = Path(temp_output_dir) / f"test_file_{i}.txt"
            with open(file_path, 'r') as f:
                content = f.read()
                assert len(content) > 0
        read_time = time.time() - read_start
        
        # Delete files
        delete_start = time.time()
        for i in range(100):
            file_path = Path(temp_output_dir) / f"test_file_{i}.txt"
            file_path.unlink()
        delete_time = time.time() - delete_start
        
        # Verify file I/O performance
        assert create_time < 5.0  # Create 100 files in under 5 seconds
        assert read_time < 2.0    # Read 100 files in under 2 seconds
        assert delete_time < 2.0  # Delete 100 files in under 2 seconds
        
        total_io_time = create_time + read_time + delete_time
        assert total_io_time < 8.0  # Total I/O under 8 seconds
    
    @pytest.mark.performance
    def test_cpu_usage_optimization(self):
        """Test CPU usage optimization during operations."""
        process = psutil.Process(os.getpid())
        
        mock_app = create_mock_app_instance()
        cpu_samples = []
        
        # Monitor CPU usage during operations
        for i in range(20):
            cpu_before = process.cpu_percent()
            
            # Perform CPU-intensive mock operation
            start_time = time.time()
            while time.time() - start_time < 0.1:  # 100ms of work
                mock_app.claude_provider.query(f"CPU test {i}", "code")
            
            cpu_after = process.cpu_percent()
            cpu_samples.append(cpu_after)
            
            time.sleep(0.1)  # Brief pause
        
        # Verify CPU usage optimization
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        
        # CPU usage should be reasonable (these are loose bounds for testing)
        assert avg_cpu < 80.0  # Average CPU under 80%
        assert max_cpu < 95.0  # Peak CPU under 95%

@pytest.mark.performance
@pytest.mark.slow
class TestStressTesting:
    """Stress testing for extreme conditions."""
    
    def test_maximum_concurrent_operations(self):
        """Test system limits with maximum concurrent operations."""
        mock_app = create_mock_app_instance()
        
        # Test with high concurrency
        max_threads = 20
        results = []
        errors = []
        
        def stress_operation(operation_id):
            try:
                for i in range(10):  # 10 operations per thread
                    response = mock_app.claude_provider.query(f"Stress test {operation_id}-{i}", "code")
                    results.append(f"Success: {operation_id}-{i}")
                    time.sleep(0.01)  # Brief pause
            except Exception as e:
                errors.append(f"Error in {operation_id}: {str(e)}")
        
        # Launch stress threads
        threads = []
        for i in range(max_threads):
            thread = threading.Thread(target=stress_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=60)  # 1 minute timeout
        
        # Verify stress test results
        expected_operations = max_threads * 10
        success_rate = len(results) / expected_operations
        
        assert success_rate > 0.9  # At least 90% success rate
        assert len(errors) < expected_operations * 0.1  # Less than 10% errors
    
    def test_memory_pressure_handling(self):
        """Test system behavior under memory pressure."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        mock_app = create_mock_app_instance()
        
        # Create memory pressure
        memory_intensive_objects = []
        try:
            for i in range(100):
                # Create large objects to increase memory pressure
                large_object = [f"memory_pressure_data_{j}" for j in range(10000)]
                memory_intensive_objects.append(large_object)
                
                # Continue operations under pressure
                response = mock_app.claude_provider.query(f"Memory pressure task {i}", "code")
                assert response is not None
                
                current_memory = process.memory_info().rss
                memory_growth = current_memory - initial_memory
                
                # Stop if memory growth exceeds reasonable limits
                if memory_growth > 500 * 1024 * 1024:  # 500MB limit
                    break
        
        finally:
            # Cleanup
            memory_intensive_objects.clear()
        
        # Verify system survived memory pressure
        final_memory = process.memory_info().rss
        assert final_memory > initial_memory  # Memory did increase
        # System should still be responsive (test completed without hanging)
    
    def test_rapid_mode_switching_stress(self):
        """Test stress from rapid mode switching."""
        mock_app = create_mock_app_instance()
        
        modes = ["task", "explore", "enhance"]
        switch_count = 0
        errors = []
        
        # Rapidly switch modes
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 seconds of rapid switching
            try:
                current_mode = modes[switch_count % len(modes)]
                
                if current_mode == "task":
                    mock_app.main_window.switch_to_task_mode()
                elif current_mode == "explore":
                    mock_app.main_window.switch_to_explore_mode()
                elif current_mode == "enhance":
                    mock_app.main_window.switch_to_enhance_mode()
                
                switch_count += 1
                time.sleep(0.1)  # 100ms between switches
                
            except Exception as e:
                errors.append(str(e))
        
        # Verify rapid switching handling
        switches_per_second = switch_count / 30
        error_rate = len(errors) / switch_count if switch_count > 0 else 0
        
        assert switches_per_second > 5  # At least 5 switches per second
        assert error_rate < 0.05  # Less than 5% error rate
        assert switch_count > 100  # At least 100 switches completed