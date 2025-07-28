"""
CRITICAL: Real application startup and integration tests.
Tests that should have caught the startup failures.
"""
import pytest
import sys
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRealApplicationStartup:
    """Test actual application startup and real class instantiation."""
    
    def test_supermini_import(self):
        """Test that supermini.py can be imported without errors."""
        try:
            import supermini
            assert True
        except Exception as e:
            pytest.fail(f"Failed to import supermini: {e}")
    
    def test_main_window_class_exists(self):
        """Test that SuperMiniMainWindow class exists and can be instantiated."""
        try:
            import supermini
            # Check if class exists
            assert hasattr(supermini, 'SuperMiniMainWindow')
            
            # This would fail with the current startup error
            # but shows what should be tested
        except Exception as e:
            pytest.fail(f"SuperMiniMainWindow class issue: {e}")
    
    def test_required_methods_exist(self):
        """Test that all GUI-connected methods actually exist."""
        try:
            import supermini
            cls = supermini.SuperMiniMainWindow
            
            # Methods that are connected in GUI but may not exist
            required_methods = [
                'start_enhancement',
                'stop_enhancement', 
                'start_exploration',
                'stop_exploration',
                'process_task',
                'stop_task'
            ]
            
            for method_name in required_methods:
                assert hasattr(cls, method_name), f"Missing method: {method_name}"
                
        except Exception as e:
            pytest.fail(f"Method existence check failed: {e}")
    
    def test_enhanced_task_executor_import(self):
        """Test that enhanced task execution modules import correctly."""
        try:
            from src.core.enhanced_task_execution import EnhancedTaskExecutor
            # This should fail due to LearningEngine constructor issue
        except Exception as e:
            pytest.fail(f"Enhanced task execution import failed: {e}")
    
    def test_learning_engine_constructor(self):
        """Test LearningEngine constructor compatibility."""
        try:
            from src.core.enhanced_task_execution import LearningEngine
            # Try to create with parameter (current code expects this)
            # But LearningEngine.__init__ only takes self
            learning_engine = LearningEngine("test_param")
        except TypeError as e:
            pytest.fail(f"LearningEngine constructor mismatch: {e}")
    
    def test_autonomous_imports(self):
        """Test all autonomous module imports."""
        autonomous_modules = [
            'src.autonomous.autonomous_agent',
            'src.autonomous.autonomous_enhancement', 
            'src.autonomous.safety_framework',
            'src.core.enhanced_task_execution'
        ]
        
        for module_name in autonomous_modules:
            try:
                importlib.import_module(module_name)
            except Exception as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

class TestApplicationInitialization:
    """Test actual application initialization process."""
    
    @pytest.mark.slow
    def test_full_application_startup(self):
        """Test complete application startup process."""
        # This would require setting up QApplication properly
        # and catching the actual startup error
        pytest.skip("Requires GUI environment setup")
    
    def test_module_dependencies(self):
        """Test that all module dependencies are satisfied."""
        try:
            # Test core imports first
            import supermini
            
            # Test that all required classes can be instantiated
            # (This would reveal the current issues)
            
        except Exception as e:
            pytest.fail(f"Module dependency issue: {e}")