#!/usr/bin/env python3
"""
SuperMini Autonomous Integration
Integrates all enhanced autonomous capabilities into the existing SuperMini application
Provides backwards compatibility while adding cutting-edge autonomous features
"""

import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import enhanced components
try:
    from autonomous_orchestrator import AutonomousOrchestrator, AutonomousMode, AutonomousContext
    from enhanced_task_execution import EnhancedTaskExecutor, ExecutionMode, TaskExecutionConfig
    from enhanced_safety_framework import SafetyMonitor, UserControlInterface
    from recursive_engine import SmartTaskDecomposer
    from dynamic_planning_components import PlanPerformanceMonitor, ContextTracker
    ENHANCED_AUTONOMOUS_AVAILABLE = True
    logging.info("Enhanced autonomous components loaded successfully")
except ImportError as e:
    logging.warning(f"Enhanced autonomous components not available: {e}")
    ENHANCED_AUTONOMOUS_AVAILABLE = False

class EnhancedTaskProcessor:
    """Enhanced wrapper for the original TaskProcessor with autonomous capabilities"""
    
    def __init__(self, original_processor, memory_manager, output_dir: Path):
        self.original_processor = original_processor
        self.memory = memory_manager
        self.output_dir = output_dir
        
        # Initialize enhanced components if available
        if ENHANCED_AUTONOMOUS_AVAILABLE:
            self.enhanced_executor = EnhancedTaskExecutor(original_processor, memory_manager, output_dir)
            self.safety_monitor = SafetyMonitor(output_dir)
            self.user_control = UserControlInterface(self.safety_monitor)
            self.orchestrator = AutonomousOrchestrator(original_processor, memory_manager, output_dir)
            
            # Enhanced capabilities enabled
            self.autonomous_capabilities = True
            logging.info("Enhanced autonomous task processor initialized")
        else:
            # Fallback to original functionality
            self.enhanced_executor = None
            self.safety_monitor = None
            self.user_control = None
            self.orchestrator = None
            self.autonomous_capabilities = False
            logging.info("Task processor initialized with original functionality only")
    
    def process_task(self, prompt: str, files: List[str] = None, task_type: str = None,
                    use_memory: bool = True, auto_continue: bool = False, 
                    max_continues: int = 10, autonomous_mode: bool = False,
                    execution_mode: str = "regular", **kwargs) -> Any:
        """Enhanced process_task with autonomous capabilities"""
        
        # If enhanced capabilities are not available, fall back to original
        if not self.autonomous_capabilities:
            return self.original_processor.process_task(
                prompt, files, task_type, use_memory, auto_continue, max_continues, autonomous_mode
            )
        
        # Safety evaluation for autonomous operations
        if autonomous_mode or execution_mode != "regular":
            safety_result = self._evaluate_operation_safety(prompt, files, task_type, execution_mode)
            
            if not safety_result["safe"]:
                return self._handle_safety_violation(safety_result, prompt, files, task_type)
        
        # Determine execution approach
        if autonomous_mode or execution_mode in ["autonomous", "exploration", "enhancement", "hybrid"]:
            return self._execute_enhanced_mode(prompt, files, task_type, execution_mode, kwargs)
        else:
            return self._execute_regular_enhanced(prompt, files, task_type, use_memory, 
                                                auto_continue, max_continues)
    
    def _execute_enhanced_mode(self, prompt: str, files: List[str], task_type: str, 
                             execution_mode: str, kwargs: Dict[str, Any]) -> Any:
        """Execute using enhanced autonomous capabilities"""
        try:
            # Create execution configuration
            config = TaskExecutionConfig(
                mode=ExecutionMode(execution_mode),
                autonomous_enabled=True,
                recursive_expansion=kwargs.get("recursive_expansion", True),
                adaptive_planning=kwargs.get("adaptive_planning", True),
                auto_continue=kwargs.get("auto_continue", True),
                max_recursion_depth=kwargs.get("max_recursion_depth", 5),
                max_continues=kwargs.get("max_continues", 10),
                safety_checks=kwargs.get("safety_checks", True),
                user_oversight=kwargs.get("user_oversight", True)
            )
            
            # Execute with enhanced capabilities
            enhanced_result = self.enhanced_executor.execute_task_enhanced(
                prompt, files, task_type, config
            )
            
            # Convert enhanced result back to original format for compatibility
            return self._convert_enhanced_result_to_original(enhanced_result)
            
        except Exception as e:
            logging.error(f"Enhanced execution failed, falling back to original: {e}")
            return self._execute_regular_enhanced(prompt, files, task_type, True, True, 10)
    
    def _execute_regular_enhanced(self, prompt: str, files: List[str], task_type: str,
                                use_memory: bool, auto_continue: bool, max_continues: int) -> Any:
        """Execute regular mode with enhancements"""
        try:
            # Use enhanced executor in regular mode if available
            if self.enhanced_executor:
                config = TaskExecutionConfig(
                    mode=ExecutionMode.REGULAR,
                    autonomous_enabled=False,
                    auto_continue=auto_continue,
                    max_continues=max_continues
                )
                
                enhanced_result = self.enhanced_executor.execute_task_enhanced(
                    prompt, files, task_type, config
                )
                
                return self._convert_enhanced_result_to_original(enhanced_result)
            else:
                # Pure fallback to original
                return self.original_processor.process_task(
                    prompt, files, task_type, use_memory, auto_continue, max_continues, False
                )
                
        except Exception as e:
            logging.error(f"Enhanced regular execution failed: {e}")
            # Ultimate fallback
            return self.original_processor.process_task(
                prompt, files, task_type, use_memory, auto_continue, max_continues, False
            )
    
    def _evaluate_operation_safety(self, prompt: str, files: List[str], 
                                 task_type: str, execution_mode: str) -> Dict[str, Any]:
        """Evaluate safety of the operation"""
        if not self.safety_monitor:
            return {"safe": True}  # No safety monitoring available
        
        operation = {
            "prompt": prompt,
            "files": files or [],
            "task_type": task_type,
            "execution_mode": execution_mode,
            "timestamp": time.time()
        }
        
        context = {
            "autonomous_mode": execution_mode != "regular",
            "file_count": len(files) if files else 0,
            "prompt_length": len(prompt)
        }
        
        return self.safety_monitor.evaluate_safety(operation, context)
    
    def _handle_safety_violation(self, safety_result: Dict[str, Any], 
                                prompt: str, files: List[str], task_type: str) -> Any:
        """Handle safety violations"""
        # Create a mock TaskResult for safety violations
        class SafetyViolationResult:
            def __init__(self, safety_result):
                self.success = False
                self.result = f"Operation blocked due to safety violations: {safety_result.get('risk_level', 'unknown')} risk"
                self.generated_files = []
                self.task_steps = ["Safety evaluation", "Operation blocked"]
                self.score = 0.0
                self.execution_time = 0.0
                self.safety_violations = safety_result.get("violations", [])
                self.required_actions = safety_result.get("required_actions", [])
        
        return SafetyViolationResult(safety_result)
    
    def _convert_enhanced_result_to_original(self, enhanced_result) -> Any:
        """Convert enhanced execution result to original TaskResult format"""
        # Create a TaskResult-like object for compatibility
        class CompatibilityTaskResult:
            def __init__(self, enhanced_result):
                self.success = enhanced_result.success
                self.result = enhanced_result.result
                self.generated_files = enhanced_result.generated_files
                self.execution_time = enhanced_result.execution_time
                self.score = enhanced_result.performance_metrics.get("score", 0.5)
                
                # Enhanced fields (available but not used by original code)
                self.mode_used = enhanced_result.mode_used.value
                self.autonomous_actions = enhanced_result.autonomous_actions
                self.adaptations_made = enhanced_result.adaptations_made
                self.learning_outcomes = enhanced_result.learning_outcomes
                self.recursion_depth = enhanced_result.recursion_depth
                self.subtasks_completed = enhanced_result.subtasks_completed
                
                # Create task_steps for compatibility
                self.task_steps = ["Task execution started"]
                if enhanced_result.autonomous_actions:
                    self.task_steps.extend([f"Autonomous action: {action.get('type', 'unknown')}" 
                                          for action in enhanced_result.autonomous_actions[:3]])
                if enhanced_result.adaptations_made:
                    self.task_steps.extend([f"Adaptation: {adaptation.get('type', 'unknown')}" 
                                          for adaptation in enhanced_result.adaptations_made[:2]])
                self.task_steps.append(f"Task {'completed' if self.success else 'failed'}")
        
        return CompatibilityTaskResult(enhanced_result)
    
    # Expose enhanced capabilities through new methods
    def execute_autonomous_exploration(self, prompt: str, files: List[str] = None) -> Any:
        """Execute autonomous exploration mode"""
        if not self.autonomous_capabilities:
            return self.process_task(prompt, files, auto_continue=True, max_continues=15)
        
        return self.process_task(prompt, files, execution_mode="exploration", autonomous_mode=True)
    
    def execute_autonomous_enhancement(self, prompt: str, files: List[str] = None) -> Any:
        """Execute autonomous enhancement mode"""
        if not self.autonomous_capabilities:
            return self.process_task(prompt, files, auto_continue=True, max_continues=12)
        
        return self.process_task(prompt, files, execution_mode="enhancement", autonomous_mode=True)
    
    def execute_hybrid_mode(self, prompt: str, files: List[str] = None) -> Any:
        """Execute hybrid adaptive mode"""
        if not self.autonomous_capabilities:
            return self.process_task(prompt, files, auto_continue=True, max_continues=10)
        
        return self.process_task(prompt, files, execution_mode="hybrid", autonomous_mode=True)
    
    def get_autonomous_suggestions(self, prompt: str, task_type: str = None) -> List[Dict[str, Any]]:
        """Get autonomous suggestions for a task"""
        if not self.autonomous_capabilities:
            return [{"suggestion": "Enhanced autonomous capabilities not available", "confidence": 0.0}]
        
        try:
            # Use enhanced mode manager to get recommendations
            from enhanced_task_execution import EnhancedModeManager
            mode_manager = EnhancedModeManager(self.enhanced_executor)
            recommendations = mode_manager.get_mode_recommendations(prompt, task_type)
            
            return [{
                "suggestion": f"Use {rec['mode'].value} mode: {rec['rationale']}",
                "confidence": rec['confidence'],
                "mode": rec['mode'].value
            } for rec in recommendations]
            
        except Exception as e:
            logging.error(f"Failed to get autonomous suggestions: {e}")
            return [{"suggestion": "Unable to generate suggestions", "confidence": 0.0}]
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        if not self.safety_monitor:
            return {"status": "Safety monitoring not available"}
        
        return self.safety_monitor.get_safety_status()
    
    def get_pending_confirmations(self) -> List[Dict[str, Any]]:
        """Get pending safety confirmations"""
        if not self.user_control:
            return []
        
        return self.user_control.get_pending_confirmations()
    
    def provide_safety_confirmation(self, violation_id: str, approved: bool, explanation: str = "") -> Dict[str, Any]:
        """Provide safety confirmation"""
        if not self.user_control:
            return {"success": False, "error": "User control not available"}
        
        return self.user_control.provide_confirmation(violation_id, approved, explanation)
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop all autonomous operations"""
        results = {"safety_stop": {"success": False}, "executor_stop": {"success": False}}
        
        if self.safety_monitor:
            results["safety_stop"] = self.safety_monitor.emergency_stop()
        
        if self.enhanced_executor:
            self.enhanced_executor.stop_execution()
            results["executor_stop"] = {"success": True, "message": "Enhanced executor stopped"}
        
        # Also stop original processor
        if hasattr(self.original_processor, 'request_stop'):
            self.original_processor.request_stop()
        
        return results
    
    def resume_operations(self) -> Dict[str, Any]:
        """Resume operations after emergency stop"""
        results = {"safety_resume": {"success": False}, "executor_resume": {"success": False}}
        
        if self.safety_monitor:
            results["safety_resume"] = self.safety_monitor.resume_monitoring()
        
        if self.enhanced_executor:
            self.enhanced_executor.resume_execution()
            results["executor_resume"] = {"success": True, "message": "Enhanced executor resumed"}
        
        # Also reset original processor
        if hasattr(self.original_processor, 'reset_stop_flag'):
            self.original_processor.reset_stop_flag()
        
        return results
    
    # Forward all other methods to original processor for compatibility
    def __getattr__(self, name):
        """Forward unknown attributes to original processor"""
        return getattr(self.original_processor, name)

def integrate_autonomous_capabilities(original_supermini_app):
    """Integrate autonomous capabilities into existing SuperMini application"""
    if not hasattr(original_supermini_app, 'processor'):
        logging.error("Original SuperMini app does not have processor attribute")
        return original_supermini_app
    
    try:
        # Replace the processor with enhanced version
        original_processor = original_supermini_app.processor
        memory_manager = original_supermini_app.memory
        output_dir = original_supermini_app.data_dir
        
        # Create enhanced processor
        enhanced_processor = EnhancedTaskProcessor(original_processor, memory_manager, output_dir)
        
        # Replace processor in the app
        original_supermini_app.processor = enhanced_processor
        
        # Add new methods to the app
        original_supermini_app.execute_autonomous_exploration = enhanced_processor.execute_autonomous_exploration
        original_supermini_app.execute_autonomous_enhancement = enhanced_processor.execute_autonomous_enhancement
        original_supermini_app.execute_hybrid_mode = enhanced_processor.execute_hybrid_mode
        original_supermini_app.get_autonomous_suggestions = enhanced_processor.get_autonomous_suggestions
        original_supermini_app.get_safety_status = enhanced_processor.get_safety_status
        original_supermini_app.get_pending_confirmations = enhanced_processor.get_pending_confirmations
        original_supermini_app.provide_safety_confirmation = enhanced_processor.provide_safety_confirmation
        original_supermini_app.emergency_stop_autonomous = enhanced_processor.emergency_stop
        original_supermini_app.resume_autonomous_operations = enhanced_processor.resume_operations
        
        logging.info("Successfully integrated autonomous capabilities into SuperMini")
        return original_supermini_app
        
    except Exception as e:
        logging.error(f"Failed to integrate autonomous capabilities: {e}")
        return original_supermini_app

# Add enhanced UI components
def add_enhanced_ui_components(main_window):
    """Add enhanced UI components for autonomous capabilities"""
    if not ENHANCED_AUTONOMOUS_AVAILABLE:
        logging.warning("Enhanced autonomous components not available for UI integration")
        return
    
    try:
        # This would add new UI elements for autonomous control
        # For now, we'll log that the capability is available
        logging.info("Enhanced UI components available for integration")
        
        # Add enhanced mode selection
        if hasattr(main_window, 'add_autonomous_controls'):
            main_window.add_autonomous_controls()
        
    except Exception as e:
        logging.error(f"Failed to add enhanced UI components: {e}")

# Enhanced thread classes for autonomous operations
class EnhancedExploreThread:
    """Enhanced exploration thread with autonomous capabilities"""
    
    def __init__(self, processor, files, iteration_delay_hours=0, iteration_delay_minutes=30):
        self.processor = processor
        self.files = files
        self.iteration_delay = (iteration_delay_hours * 3600) + (iteration_delay_minutes * 60)
        self.running = True
        self.iteration = 0
    
    def run(self):
        """Run enhanced exploration with autonomous capabilities"""
        if hasattr(self.processor, 'execute_autonomous_exploration'):
            # Use enhanced autonomous exploration
            result = self.processor.execute_autonomous_exploration(
                "Autonomous exploration and experimentation mode activated",
                self.files
            )
            return result
        else:
            # Fallback to original exploration logic
            logging.warning("Enhanced exploration not available, using original logic")
            return None

class EnhancedEnhanceThread:
    """Enhanced enhancement thread with recursive self-improvement"""
    
    def __init__(self, processor, app_path, files, iteration_delay_hours=0, iteration_delay_minutes=60):
        self.processor = processor
        self.app_path = app_path
        self.files = files
        self.iteration_delay = (iteration_delay_hours * 3600) + (iteration_delay_minutes * 60)
        self.running = True
        self.iteration = 0
    
    def run(self):
        """Run enhanced self-improvement with recursive capabilities"""
        if hasattr(self.processor, 'execute_autonomous_enhancement'):
            # Use enhanced autonomous enhancement
            enhancement_prompt = f"""
Autonomous self-enhancement mode for SuperMini application.
Target application: {self.app_path}
Available files: {self.files}

Analyze, improve, and enhance the application autonomously.
Focus on meaningful improvements while maintaining safety and stability.
"""
            result = self.processor.execute_autonomous_enhancement(
                enhancement_prompt,
                self.files
            )
            return result
        else:
            # Fallback to original enhancement logic
            logging.warning("Enhanced self-improvement not available, using original logic")
            return None