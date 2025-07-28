#!/usr/bin/env python3
"""
Autonomous Agent Integration using Simular AI Agent-S Framework
Enhances SuperMini with autonomous computer interaction capabilities
"""

import sys
import os
import json
import logging
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import base64

# Enhanced activity monitoring (delayed import to prevent hanging)
ACTIVITY_MONITORING_AVAILABLE = False

# Define fallback classes first
class ActivityType:
    USER_INTERACTION = "user_interaction"
    SYSTEM_EVENT = "system_event"
    AUTONOMOUS_ACTION = "autonomous_action"
    SAFETY_CHECK = "safety_check"
    AI_QUERY = "ai_query"
    AI_RESPONSE = "ai_response"
    FILE_OPERATION = "file_operation"
    SCREENSHOT = "screenshot"
    ERROR_EVENT = "error_event"
    PERFORMANCE_METRIC = "performance_metric"
    TASK_START = "task_start"
    TASK_END = "task_end"

class ActivityLevel:
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Fallback functions
def get_activity_logger(*args, **kwargs):
    return None
def log_activity_event(*args, **kwargs):
        pass

# Note: Real activity monitoring import is disabled to prevent hanging
# Activity monitoring will be available through the main application

try:
    from gui_agents.s2.agents.agent_s import AgentS2
    from gui_agents.s2.agents.grounding import OSWorldACI
    GUI_AGENTS_AVAILABLE = True
except (ImportError, ValueError) as e:
    if "OPENAI_API_KEY" in str(e):
        logging.warning("OpenAI API key required for autonomous features. Set OPENAI_API_KEY environment variable.")
    else:
        logging.warning("gui-agents not available. Install with 'pip install gui-agents'")
    GUI_AGENTS_AVAILABLE = False

@dataclass
class AutonomousTask:
    """Data class for autonomous task configuration"""
    task_id: str
    instruction: str
    task_type: str
    context: Dict[str, Any]
    max_steps: int = 10
    timeout: int = 300  # 5 minutes
    requires_confirmation: bool = True
    safety_checks: List[str] = None

@dataclass
class AutonomousResult:
    """Data class for autonomous task results"""
    task_id: str
    success: bool
    steps_taken: List[Dict[str, Any]]
    final_state: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None
    screenshots: List[str] = None

class SafetyManager:
    """Manages safety checks and restrictions for autonomous operations"""
    
    def __init__(self):
        self.restricted_commands = [
            'rm -rf /',
            'sudo rm',
            'format',
            'del /s',
            'shutdown',
            'reboot'
        ]
        self.safe_directories = [
            str(Path.home() / "SuperMini_Output"),
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            "/tmp"
        ]
    
    def validate_action(self, action: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate if an action is safe to execute"""
        action_lower = action.lower()
        
        # Check for restricted commands
        for restricted in self.restricted_commands:
            if restricted in action_lower:
                return False, f"Restricted command detected: {restricted}"
        
        # Check for file operations outside safe directories
        if any(cmd in action_lower for cmd in ['rm', 'del', 'mv', 'cp']):
            # Extract path from action (simplified)
            if not any(safe_dir in action for safe_dir in self.safe_directories):
                return False, "File operation outside safe directories"
        
        return True, "Action validated"
    
    def requires_confirmation(self, action: str) -> bool:
        """Check if action requires user confirmation"""
        high_risk_actions = [
            'install', 'uninstall', 'delete', 'remove',
            'format', 'chmod', 'chown', 'sudo'
        ]
        return any(risk in action.lower() for risk in high_risk_actions)

class AutonomousAgent:
    """Main autonomous agent class integrating Simular AI capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.safety_manager = SafetyManager()
        self.agent = None
        self.grounding_agent = None
        self.active_tasks = {}
        self.task_history = []
        
        # Initialize activity logger
        self.activity_logger = get_activity_logger()
        
        # Log agent initialization
        log_activity_event(
            ActivityType.SYSTEM_EVENT,
            ActivityLevel.INFO,
            "Autonomous Agent Initializing",
            "Starting autonomous agent with Simular AI integration",
            {"config_keys": list(config.keys()), "gui_agents_available": GUI_AGENTS_AVAILABLE}
        )
        
        # Initialize Agent-S if available
        if GUI_AGENTS_AVAILABLE:
            self.setup_agent_s()
        else:
            logging.warning("Agent-S not available - autonomous features limited")
            log_activity_event(
                ActivityType.SYSTEM_EVENT,
                ActivityLevel.WARNING,
                "Agent-S Unavailable",
                "GUI agents not available - autonomous features will be limited",
                {"install_command": "pip install gui-agents>=0.1.2"}
            )
    
    def setup_agent_s(self):
        """Initialize the Agent-S framework"""
        try:
            # Configure engine parameters
            engine_params = {
                "model": self.config.get("model", "gpt-4-vision-preview"),
                "api_key": self.config.get("api_key", ""),
                "max_tokens": self.config.get("max_tokens", 4096),
                "temperature": self.config.get("temperature", 0.1)
            }
            
            # Initialize grounding agent for macOS
            self.grounding_agent = OSWorldACI(
                platform="darwin",  # macOS
                action_space="pyautogui"
            )
            
            # Initialize Agent-S
            self.agent = AgentS2(
                engine_params=engine_params,
                grounding_agent=self.grounding_agent,
                platform="darwin",
                action_space="pyautogui",
                observation_type="screenshot"
            )
            
            logging.info("Agent-S initialized successfully")
            log_activity_event(
                ActivityType.SYSTEM_EVENT,
                ActivityLevel.INFO,
                "Agent-S Initialized",
                "Successfully initialized Agent-S framework for autonomous operations",
                {
                    "model": self.config.get("model", "unknown"),
                    "platform": "darwin",
                    "action_space": "pyautogui"
                }
            )
            
        except Exception as e:
            logging.error(f"Failed to initialize Agent-S: {e}")
            log_activity_event(
                ActivityType.ERROR_EVENT,
                ActivityLevel.ERROR,
                "Agent-S Initialization Failed",
                f"Failed to initialize Agent-S framework: {str(e)}",
                {"error": str(e), "config": self.config}
            )
            self.agent = None
    
    def execute_autonomous_task(self, task: AutonomousTask) -> AutonomousResult:
        """Execute an autonomous task using Agent-S"""
        start_time = time.time()
        steps_taken = []
        screenshots = []
        
        # Start task tracking
        if self.activity_logger:
            self.activity_logger.start_task(
                task.task_id,
                task.task_type,
                task.instruction,
                {
                    "max_steps": task.max_steps,
                    "timeout": task.timeout,
                    "requires_confirmation": task.requires_confirmation,
                    "context": task.context
                }
            )
        
        try:
            if not self.agent:
                error_msg = "Agent-S not available"
                log_activity_event(
                    ActivityType.ERROR_EVENT,
                    ActivityLevel.ERROR,
                    "Autonomous Task Failed",
                    error_msg,
                    {"task_id": task.task_id, "reason": "agent_not_available"},
                    parent_task_id=task.task_id
                )
                
                # End task tracking
                if self.activity_logger:
                    self.activity_logger.end_task(task.task_id, False, {"error": error_msg})
                
                return AutonomousResult(
                    task_id=task.task_id,
                    success=False,
                    steps_taken=steps_taken,
                    final_state={},
                    execution_time=time.time() - start_time,
                    error_message=error_msg
                )
            
            # Store active task
            self.active_tasks[task.task_id] = task
            
            log_activity_event(
                ActivityType.AUTONOMOUS_ACTION,
                ActivityLevel.INFO,
                "Autonomous Task Started",
                f"Beginning autonomous execution: {task.instruction}",
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "max_steps": task.max_steps
                },
                parent_task_id=task.task_id
            )
            
            # Take initial screenshot for context
            screenshot_path = self.take_screenshot(f"initial_{task.task_id}")
            if screenshot_path:
                screenshots.append(screenshot_path)
                if self.activity_logger:
                    self.activity_logger.log_screenshot(
                        screenshot_path, 
                        "Initial state capture", 
                        task.task_id
                    )
            
            # Execute task steps
            for step in range(task.max_steps):
                step_start_time = time.time()
                
                log_activity_event(
                    ActivityType.AUTONOMOUS_ACTION,
                    ActivityLevel.DEBUG,
                    f"Autonomous Step {step + 1}",
                    f"Starting step {step + 1} of {task.max_steps}",
                    {"step": step + 1, "task_id": task.task_id},
                    parent_task_id=task.task_id
                )
                
                try:
                    # Get current observation (screenshot)
                    observation = self.get_observation()
                    
                    log_activity_event(
                        ActivityType.SCREENSHOT,
                        ActivityLevel.TRACE,
                        "Screen Observation Captured",
                        "Captured current screen state for AI analysis",
                        {"step": step + 1, "task_id": task.task_id},
                        parent_task_id=task.task_id
                    )
                    
                    # Query the agent for next action
                    ai_query_start = time.time()
                    info, action = self.agent.predict(
                        instruction=task.instruction,
                        observation=observation
                    )
                    ai_query_duration = time.time() - ai_query_start
                    
                    # Log AI interaction
                    if self.activity_logger:
                        self.activity_logger.log_ai_interaction(
                            f"Step {step + 1}: {task.instruction}",
                            str(action),
                            self.config.get("model", "Agent-S"),
                            ai_query_duration,
                            task.task_id
                        )
                    
                    # Safety validation
                    if action:
                        action_str = str(action[0]) if isinstance(action, list) else str(action)
                        is_safe, safety_msg = self.safety_manager.validate_action(
                            action_str, task.context
                        )
                        
                        # Log safety check
                        if self.activity_logger:
                            self.activity_logger.log_safety_check(
                                action_str, is_safe, safety_msg, task.task_id
                            )
                        
                        if not is_safe:
                            steps_taken.append({
                                "step": step,
                                "action": "blocked",
                                "reason": safety_msg,
                                "timestamp": time.time()
                            })
                            
                            log_activity_event(
                                ActivityType.SAFETY_CHECK,
                                ActivityLevel.WARNING,
                                "Action Blocked",
                                f"Step {step + 1} action blocked by safety check: {safety_msg}",
                                {
                                    "step": step + 1,
                                    "action": action_str,
                                    "reason": safety_msg,
                                    "task_id": task.task_id
                                },
                                parent_task_id=task.task_id
                            )
                            continue
                        
                        # Check if confirmation required
                        if (task.requires_confirmation and 
                            self.safety_manager.requires_confirmation(action_str)):
                            # In a real implementation, this would show a dialog
                            logging.info(f"Action requires confirmation: {action_str}")
                            
                            log_activity_event(
                                ActivityType.USER_INTERACTION,
                                ActivityLevel.INFO,
                                "Confirmation Required",
                                f"Step {step + 1} requires user confirmation: {action_str}",
                                {
                                    "step": step + 1,
                                    "action": action_str,
                                    "task_id": task.task_id,
                                    "confirmation_reason": "high_risk_action"
                                },
                                parent_task_id=task.task_id
                            )
                            
                            steps_taken.append({
                                "step": step,
                                "action": "confirmation_required",
                                "details": action_str,
                                "timestamp": time.time()
                            })
                            continue
                    
                    # Execute the action
                    if action:
                        action_execution_start = time.time()
                        action_str = str(action[0]) if isinstance(action, list) else str(action)
                        
                        log_activity_event(
                            ActivityType.AUTONOMOUS_ACTION,
                            ActivityLevel.INFO,
                            f"Executing Step {step + 1}",
                            f"Executing autonomous action: {action_str}",
                            {
                                "step": step + 1,
                                "action": action_str,
                                "task_id": task.task_id,
                                "ai_info": str(info) if info else None
                            },
                            parent_task_id=task.task_id
                        )
                        
                        try:
                            if isinstance(action, list) and action:
                                exec(action[0])
                            else:
                                exec(str(action))
                            
                            action_execution_time = time.time() - action_execution_start
                            
                            # Log autonomous action with detailed tracking
                            if self.activity_logger:
                                self.activity_logger.log_autonomous_action(
                                    action_str, step + 1, task.task_id, 
                                    "success", {"execution_time": action_execution_time}
                                )
                            
                            steps_taken.append({
                                "step": step,
                                "action": "executed",
                                "details": str(action),
                                "info": info,
                                "timestamp": time.time(),
                                "execution_time": action_execution_time
                            })
                            
                            log_activity_event(
                                ActivityType.AUTONOMOUS_ACTION,
                                ActivityLevel.INFO,
                                f"Step {step + 1} Completed",
                                f"Successfully executed: {action_str}",
                                {
                                    "step": step + 1,
                                    "action": action_str,
                                    "execution_time": action_execution_time,
                                    "task_id": task.task_id
                                },
                                duration=action_execution_time,
                                parent_task_id=task.task_id
                            )
                            
                        except Exception as action_error:
                            log_activity_event(
                                ActivityType.ERROR_EVENT,
                                ActivityLevel.ERROR,
                                f"Step {step + 1} Failed",
                                f"Action execution failed: {str(action_error)}",
                                {
                                    "step": step + 1,
                                    "action": action_str,
                                    "error": str(action_error),
                                    "task_id": task.task_id
                                },
                                parent_task_id=task.task_id
                            )
                            raise action_error
                        
                        # Take screenshot after action
                        screenshot_path = self.take_screenshot(f"step_{step}_{task.task_id}")
                        if screenshot_path:
                            screenshots.append(screenshot_path)
                            if self.activity_logger:
                                self.activity_logger.log_screenshot(
                                    screenshot_path, 
                                    f"Post-action state (Step {step + 1})", 
                                    task.task_id
                                )
                        
                        # Brief pause between actions
                        time.sleep(1)
                    
                    # Check if task is complete
                    if self.is_task_complete(task, info):
                        log_activity_event(
                            ActivityType.AUTONOMOUS_ACTION,
                            ActivityLevel.INFO,
                            "Task Completion Detected",
                            f"Task {task.task_id} appears to be complete after step {step + 1}",
                            {
                                "step": step + 1,
                                "task_id": task.task_id,
                                "completion_info": str(info) if info else None
                            },
                            parent_task_id=task.task_id
                        )
                        break
                        
                except Exception as step_error:
                    step_duration = time.time() - step_start_time
                    logging.error(f"Error in step {step}: {step_error}")
                    
                    log_activity_event(
                        ActivityType.ERROR_EVENT,
                        ActivityLevel.ERROR,
                        f"Step {step + 1} Error",
                        f"Error during autonomous step execution: {str(step_error)}",
                        {
                            "step": step + 1,
                            "error": str(step_error),
                            "step_duration": step_duration,
                            "task_id": task.task_id
                        },
                        duration=step_duration,
                        parent_task_id=task.task_id
                    )
                    
                    steps_taken.append({
                        "step": step,
                        "action": "error",
                        "error": str(step_error),
                        "timestamp": time.time(),
                        "duration": step_duration
                    })
            
            # Clean up
            del self.active_tasks[task.task_id]
            
            total_execution_time = time.time() - start_time
            
            # End task tracking successfully
            if self.activity_logger:
                self.activity_logger.end_task(
                    task.task_id, 
                    True, 
                    {
                        "steps_completed": len(steps_taken),
                        "screenshots_taken": len(screenshots),
                        "total_execution_time": total_execution_time
                    }
                )
            
            log_activity_event(
                ActivityType.TASK_END,
                ActivityLevel.INFO,
                "Autonomous Task Completed",
                f"Successfully completed autonomous task: {task.instruction}",
                {
                    "task_id": task.task_id,
                    "steps_completed": len(steps_taken),
                    "screenshots_taken": len(screenshots),
                    "execution_time": total_execution_time,
                    "success": True
                },
                duration=total_execution_time,
                parent_task_id=task.task_id
            )
            
            return AutonomousResult(
                task_id=task.task_id,
                success=True,
                steps_taken=steps_taken,
                final_state={"completed": True},
                execution_time=total_execution_time,
                screenshots=screenshots
            )
            
        except Exception as e:
            total_execution_time = time.time() - start_time
            logging.error(f"Autonomous task execution failed: {e}")
            
            # End task tracking with failure
            if self.activity_logger:
                self.activity_logger.end_task(
                    task.task_id, 
                    False, 
                    {
                        "error": str(e),
                        "steps_attempted": len(steps_taken),
                        "execution_time": total_execution_time
                    }
                )
            
            log_activity_event(
                ActivityType.TASK_END,
                ActivityLevel.ERROR,
                "Autonomous Task Failed",
                f"Autonomous task failed with error: {str(e)}",
                {
                    "task_id": task.task_id,
                    "error": str(e),
                    "steps_attempted": len(steps_taken),
                    "execution_time": total_execution_time,
                    "success": False
                },
                duration=total_execution_time,
                parent_task_id=task.task_id
            )
            
            return AutonomousResult(
                task_id=task.task_id,
                success=False,
                steps_taken=steps_taken,
                final_state={},
                execution_time=total_execution_time,
                error_message=str(e),
                screenshots=screenshots
            )
    
    def get_observation(self) -> Any:
        """Get current screen observation for the agent"""
        try:
            # Take screenshot using system command
            screenshot_path = Path.home() / "SuperMini_Output" / "temp" / "current_screen.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            # macOS screenshot command
            subprocess.run([
                "screencapture", "-x", str(screenshot_path)
            ], check=True)
            
            # Read and encode image
            with open(screenshot_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            return {
                "type": "screenshot",
                "data": image_data,
                "path": str(screenshot_path)
            }
            
        except Exception as e:
            logging.error(f"Failed to get observation: {e}")
            return None
    
    def take_screenshot(self, filename: str) -> Optional[str]:
        """Take and save a screenshot"""
        try:
            output_dir = Path.home() / "SuperMini_Output" / "autonomous" / "screenshots"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = output_dir / f"{filename}_{int(time.time())}.png"
            
            subprocess.run([
                "screencapture", "-x", str(screenshot_path)
            ], check=True)
            
            return str(screenshot_path)
            
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")
            return None
    
    def is_task_complete(self, task: AutonomousTask, info: Any) -> bool:
        """Check if the autonomous task is complete"""
        # Simple completion detection - could be enhanced
        if info and isinstance(info, dict):
            return info.get("task_complete", False)
        
        # Check for common completion indicators
        completion_indicators = [
            "completed", "finished", "done", "success"
        ]
        
        if isinstance(info, str):
            return any(indicator in info.lower() for indicator in completion_indicators)
        
        return False
    
    def create_workflow_task(self, description: str, task_type: str, 
                           context: Dict[str, Any] = None) -> AutonomousTask:
        """Create an autonomous task from a workflow description"""
        task_id = f"auto_{int(time.time() * 1000)}"
        
        return AutonomousTask(
            task_id=task_id,
            instruction=description,
            task_type=task_type,
            context=context or {},
            max_steps=15,
            timeout=600,  # 10 minutes
            requires_confirmation=True
        )
    
    def suggest_autonomous_actions(self, current_context: Dict[str, Any]) -> List[str]:
        """Suggest autonomous actions based on current context"""
        suggestions = []
        
        # Analyze current context and suggest improvements
        if "files" in current_context:
            files = current_context["files"]
            if any(f.endswith('.py') for f in files):
                suggestions.append("Run Python linting and formatting")
                suggestions.append("Execute automated tests")
            
            if any(f.endswith('.csv') for f in files):
                suggestions.append("Generate data analysis report")
                suggestions.append("Create visualizations")
        
        if "task_type" in current_context:
            task_type = current_context["task_type"]
            
            if task_type == "code":
                suggestions.extend([
                    "Set up development environment",
                    "Install missing dependencies",
                    "Create project documentation"
                ])
            
            elif task_type == "automation":
                suggestions.extend([
                    "Test automation scripts",
                    "Schedule recurring tasks",
                    "Create backup procedures"
                ])
        
        return suggestions
    
    def get_autonomous_capabilities(self) -> Dict[str, Any]:
        """Return current autonomous capabilities"""
        return {
            "agent_s_available": GUI_AGENTS_AVAILABLE,
            "supported_platforms": ["darwin"],  # macOS
            "supported_actions": [
                "screenshot_analysis",
                "ui_interaction",
                "file_operations",
                "application_control",
                "system_automation"
            ],
            "safety_features": [
                "command_validation",
                "restricted_operations",
                "confirmation_prompts",
                "safe_directory_limits"
            ]
        }

class AutonomousWorkflowManager:
    """Manages autonomous workflows and task orchestration"""
    
    def __init__(self, agent: AutonomousAgent):
        self.agent = agent
        self.workflows = {}
        self.active_workflows = {}
    
    def create_workflow(self, name: str, tasks: List[AutonomousTask]) -> str:
        """Create a new autonomous workflow"""
        workflow_id = f"workflow_{int(time.time() * 1000)}"
        self.workflows[workflow_id] = {
            "name": name,
            "tasks": tasks,
            "created": time.time(),
            "status": "created"
        }
        return workflow_id
    
    def execute_workflow(self, workflow_id: str) -> List[AutonomousResult]:
        """Execute an autonomous workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow["status"] = "running"
        self.active_workflows[workflow_id] = workflow
        
        results = []
        
        try:
            for task in workflow["tasks"]:
                result = self.agent.execute_autonomous_task(task)
                results.append(result)
                
                # Stop workflow if a critical task fails
                if not result.success and task.task_type == "critical":
                    break
            
            workflow["status"] = "completed"
            
        except Exception as e:
            logging.error(f"Workflow execution failed: {e}")
            workflow["status"] = "failed"
        
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
        
        return results
    
    def suggest_workflow_optimizations(self, workflow_id: str) -> List[str]:
        """Suggest optimizations for a workflow"""
        if workflow_id not in self.workflows:
            return []
        
        suggestions = [
            "Add error handling between tasks",
            "Implement parallel task execution where possible",
            "Add checkpoint saves for long workflows",
            "Include progress monitoring and reporting"
        ]
        
        return suggestions