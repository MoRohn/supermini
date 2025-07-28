"""
Advanced Safety Framework for Recursive Autonomous AI Operations
Provides multi-level safety controls, resource monitoring, and risk assessment
"""

import time
import logging
import psutil
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib
import os
import signal

class RiskLevel(Enum):
    """Risk assessment levels for operations"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class SafetyViolation(Enum):
    """Types of safety violations"""
    RESOURCE_LIMIT = "resource_limit"
    RECURSION_DEPTH = "recursion_depth"
    EXECUTION_TIME = "execution_time"
    UNSAFE_OPERATION = "unsafe_operation"
    SYSTEM_RISK = "system_risk"
    USER_INTERVENTION = "user_intervention"

@dataclass
class SafetyLimits:
    """Configuration for safety limits"""
    max_recursion_depth: int = 5
    max_execution_time: float = 3600  # 1 hour
    max_memory_usage_mb: float = 2048  # 2GB
    max_cpu_usage_percent: float = 80.0
    max_file_size_mb: float = 100
    max_files_generated: int = 50
    max_subtasks: int = 100
    allowed_file_extensions: List[str] = None
    forbidden_operations: List[str] = None
    
    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = [
                "py", "js", "ts", "java", "cpp", "c", "cs", "rb", "go", "rs", "php", 
                "html", "css", "json", "xml", "yml", "yaml", "md", "txt", "sh", "sql"
            ]
        if self.forbidden_operations is None:
            self.forbidden_operations = [
                "rm -rf", "sudo", "chmod 777", "format", "delete system32",
                "dd if=", "mkfs", "fdisk", "passwd", "shutdown", "reboot",
                "iptables", "firewall", "network", "sudo su", "su -"
            ]

@dataclass
class SafetyEvent:
    """Records safety-related events"""
    timestamp: float
    event_type: SafetyViolation
    severity: RiskLevel
    description: str
    context: Dict[str, Any]
    action_taken: str
    plan_id: Optional[str] = None
    subtask_id: Optional[str] = None

class ResourceMonitor:
    """Monitors system resources and detects dangerous conditions"""
    
    def __init__(self, limits: SafetyLimits):
        self.limits = limits
        self.monitoring = False
        self.monitor_thread = None
        self.resource_history = []
        self.alert_callbacks = []
        
    def start_monitoring(self):
        """Start resource monitoring in background thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Resource monitoring started")
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        logging.info("Resource monitoring stopped")
        
    def add_alert_callback(self, callback: Callable[[SafetyEvent], None]):
        """Add callback for resource alerts"""
        self.alert_callbacks.append(callback)
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Check memory usage
                memory_usage = psutil.virtual_memory().percent
                memory_mb = psutil.virtual_memory().used / (1024 * 1024)
                
                # Check CPU usage
                cpu_usage = psutil.cpu_percent(interval=1)
                
                # Record current state
                current_stats = {
                    "timestamp": time.time(),
                    "memory_percent": memory_usage,
                    "memory_mb": memory_mb,
                    "cpu_percent": cpu_usage
                }
                self.resource_history.append(current_stats)
                
                # Keep only last 100 readings
                if len(self.resource_history) > 100:
                    self.resource_history.pop(0)
                
                # Check for violations
                violations = self._check_resource_violations(current_stats)
                for violation in violations:
                    self._trigger_alert(violation)
                    
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logging.error(f"Resource monitoring error: {e}")
                time.sleep(10)
                
    def _check_resource_violations(self, stats: Dict[str, Any]) -> List[SafetyEvent]:
        """Check current stats for violations"""
        violations = []
        
        # Memory violations
        if stats["memory_mb"] > self.limits.max_memory_usage_mb:
            violations.append(SafetyEvent(
                timestamp=stats["timestamp"],
                event_type=SafetyViolation.RESOURCE_LIMIT,
                severity=RiskLevel.HIGH,
                description=f"Memory usage ({stats['memory_mb']:.1f}MB) exceeds limit ({self.limits.max_memory_usage_mb}MB)",
                context=stats,
                action_taken="monitoring"
            ))
            
        # CPU violations
        if stats["cpu_percent"] > self.limits.max_cpu_usage_percent:
            violations.append(SafetyEvent(
                timestamp=stats["timestamp"],
                event_type=SafetyViolation.RESOURCE_LIMIT,
                severity=RiskLevel.MEDIUM,
                description=f"CPU usage ({stats['cpu_percent']:.1f}%) exceeds limit ({self.limits.max_cpu_usage_percent}%)",
                context=stats,
                action_taken="monitoring"
            ))
            
        return violations
        
    def _trigger_alert(self, event: SafetyEvent):
        """Trigger alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                logging.error(f"Alert callback failed: {e}")
                
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get current resource usage summary"""
        if not self.resource_history:
            return {"status": "no_data"}
            
        latest = self.resource_history[-1]
        avg_memory = sum(r["memory_mb"] for r in self.resource_history[-10:]) / min(10, len(self.resource_history))
        avg_cpu = sum(r["cpu_percent"] for r in self.resource_history[-10:]) / min(10, len(self.resource_history))
        
        return {
            "current_memory_mb": latest["memory_mb"],
            "current_cpu_percent": latest["cpu_percent"],
            "avg_memory_mb": avg_memory,
            "avg_cpu_percent": avg_cpu,
            "memory_limit_mb": self.limits.max_memory_usage_mb,
            "cpu_limit_percent": self.limits.max_cpu_usage_percent,
            "within_limits": (latest["memory_mb"] < self.limits.max_memory_usage_mb and 
                            latest["cpu_percent"] < self.limits.max_cpu_usage_percent)
        }

class OperationValidator:
    """Validates operations for safety before execution"""
    
    def __init__(self, limits: SafetyLimits):
        self.limits = limits
        self.operation_patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, Any]:
        """Compile dangerous operation patterns"""
        import re
        
        patterns = {
            "file_operations": [
                re.compile(r'\brm\s+-r[f]?\s+/', re.IGNORECASE),
                re.compile(r'\bformat\s+[a-z]:', re.IGNORECASE),
                re.compile(r'\bdel\s+/[sq]\s+', re.IGNORECASE),
            ],
            "system_commands": [
                re.compile(r'\bsudo\s+', re.IGNORECASE),
                re.compile(r'\bsu\s+-', re.IGNORECASE),
                re.compile(r'\bchmod\s+777', re.IGNORECASE),
                re.compile(r'\bshutdown', re.IGNORECASE),
                re.compile(r'\breboot', re.IGNORECASE),
            ],
            "network_operations": [
                re.compile(r'\biptables\s+', re.IGNORECASE),
                re.compile(r'\bfirewall\s+', re.IGNORECASE),
                re.compile(r'\bnetstat\s+', re.IGNORECASE),
            ]
        }
        
        return patterns
        
    def validate_operation(self, operation: str, context: Dict[str, Any] = None) -> Tuple[bool, RiskLevel, str]:
        """Validate if operation is safe to execute"""
        if context is None:
            context = {}
            
        # Check against forbidden operations
        for forbidden in self.limits.forbidden_operations:
            if forbidden.lower() in operation.lower():
                return False, RiskLevel.CRITICAL, f"Contains forbidden operation: {forbidden}"
        
        # Check against compiled patterns
        risk_level = RiskLevel.LOW
        warnings = []
        
        for category, patterns in self.operation_patterns.items():
            for pattern in patterns:
                if pattern.search(operation):
                    if category == "file_operations":
                        risk_level = max(risk_level, RiskLevel.HIGH)
                        warnings.append(f"Dangerous file operation detected")
                    elif category == "system_commands":
                        risk_level = max(risk_level, RiskLevel.CRITICAL)
                        warnings.append(f"System-level command detected")
                    elif category == "network_operations":
                        risk_level = max(risk_level, RiskLevel.MEDIUM)
                        warnings.append(f"Network operation detected")
        
        # Additional validation based on context
        if context.get("recursion_depth", 0) > 3 and risk_level >= RiskLevel.MEDIUM:
            risk_level = RiskLevel.CRITICAL
            warnings.append("High-risk operation at deep recursion level")
            
        # File extension validation
        if "file_path" in context:
            file_path = Path(context["file_path"])
            if file_path.suffix.lstrip('.') not in self.limits.allowed_file_extensions:
                return False, RiskLevel.HIGH, f"File extension '{file_path.suffix}' not allowed"
        
        if risk_level >= RiskLevel.CRITICAL:
            return False, risk_level, "; ".join(warnings)
        elif warnings:
            return True, risk_level, "; ".join(warnings)
        else:
            return True, RiskLevel.LOW, "Operation appears safe"

class HierarchicalStopController:
    """Manages hierarchical stop propagation across recursion levels"""
    
    def __init__(self):
        self.stop_flags = {}  # plan_id -> stop_flag
        self.stop_callbacks = {}  # plan_id -> list of callbacks
        self.hierarchy = {}  # child_plan_id -> parent_plan_id
        self.lock = threading.Lock()
        
    def register_plan(self, plan_id: str, parent_plan_id: Optional[str] = None):
        """Register a new plan in the hierarchy"""
        with self.lock:
            self.stop_flags[plan_id] = False
            self.stop_callbacks[plan_id] = []
            if parent_plan_id:
                self.hierarchy[plan_id] = parent_plan_id
                
    def add_stop_callback(self, plan_id: str, callback: Callable[[], None]):
        """Add callback to be called when plan is stopped"""
        with self.lock:
            if plan_id in self.stop_callbacks:
                self.stop_callbacks[plan_id].append(callback)
                
    def request_stop(self, plan_id: str, propagate_down: bool = True, propagate_up: bool = False):
        """Request stop for a plan and optionally propagate"""
        with self.lock:
            if plan_id not in self.stop_flags:
                return
                
            self.stop_flags[plan_id] = True
            
            # Call stop callbacks
            for callback in self.stop_callbacks[plan_id]:
                try:
                    callback()
                except Exception as e:
                    logging.error(f"Stop callback failed for {plan_id}: {e}")
            
            # Propagate down to children
            if propagate_down:
                children = [child for child, parent in self.hierarchy.items() if parent == plan_id]
                for child_id in children:
                    self.request_stop(child_id, propagate_down=True, propagate_up=False)
                    
            # Propagate up to parent
            if propagate_up and plan_id in self.hierarchy:
                parent_id = self.hierarchy[plan_id]
                self.request_stop(parent_id, propagate_down=False, propagate_up=True)
                
        logging.info(f"Stop requested for plan {plan_id}")
        
    def is_stop_requested(self, plan_id: str) -> bool:
        """Check if stop is requested for a plan"""
        with self.lock:
            return self.stop_flags.get(plan_id, False)
            
    def reset_stop_flag(self, plan_id: str):
        """Reset stop flag for a plan"""
        with self.lock:
            if plan_id in self.stop_flags:
                self.stop_flags[plan_id] = False
                
    def cleanup_plan(self, plan_id: str):
        """Clean up plan from hierarchy"""
        with self.lock:
            self.stop_flags.pop(plan_id, None)
            self.stop_callbacks.pop(plan_id, None)
            # Remove from hierarchy
            self.hierarchy.pop(plan_id, None)
            # Remove as parent
            to_remove = [child for child, parent in self.hierarchy.items() if parent == plan_id]
            for child in to_remove:
                self.hierarchy.pop(child, None)

class SafetyManager:
    """Main safety management system"""
    
    def __init__(self, limits: SafetyLimits = None, output_dir: Path = None):
        self.limits = limits or SafetyLimits()
        self.output_dir = output_dir or Path.home() / "SuperMini_Output"
        
        # Initialize components
        self.resource_monitor = ResourceMonitor(self.limits)
        self.operation_validator = OperationValidator(self.limits)
        self.stop_controller = HierarchicalStopController()
        
        # Safety event logging
        self.safety_events = []
        self.safety_log_file = self.output_dir / "logs" / "safety.log"
        self.safety_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # User intervention system
        self.intervention_required = threading.Event()
        self.intervention_response = None
        
        # Setup resource monitoring callbacks
        self.resource_monitor.add_alert_callback(self._handle_resource_alert)
        
    def start_monitoring(self):
        """Start all safety monitoring systems"""
        self.resource_monitor.start_monitoring()
        logging.info("Safety monitoring started")
        
    def stop_monitoring(self):
        """Stop all safety monitoring systems"""
        self.resource_monitor.stop_monitoring()
        logging.info("Safety monitoring stopped")
        
    def validate_plan_execution(self, plan_id: str, plan_data: Dict[str, Any]) -> Tuple[bool, List[SafetyEvent]]:
        """Validate if a plan is safe to execute"""
        events = []
        
        # Check recursion depth
        recursion_depth = plan_data.get("recursion_depth", 0)
        if recursion_depth > self.limits.max_recursion_depth:
            events.append(SafetyEvent(
                timestamp=time.time(),
                event_type=SafetyViolation.RECURSION_DEPTH,
                severity=RiskLevel.HIGH,
                description=f"Recursion depth ({recursion_depth}) exceeds limit ({self.limits.max_recursion_depth})",
                context=plan_data,
                action_taken="plan_rejected",
                plan_id=plan_id
            ))
            
        # Check subtask count
        subtask_count = len(plan_data.get("subtasks", []))
        if subtask_count > self.limits.max_subtasks:
            events.append(SafetyEvent(
                timestamp=time.time(),
                event_type=SafetyViolation.RESOURCE_LIMIT,
                severity=RiskLevel.MEDIUM,
                description=f"Subtask count ({subtask_count}) exceeds limit ({self.limits.max_subtasks})",
                context=plan_data,
                action_taken="plan_rejected",
                plan_id=plan_id
            ))
            
        # Check for high-risk operations in subtasks
        for subtask in plan_data.get("subtasks", []):
            is_safe, risk_level, message = self.operation_validator.validate_operation(
                subtask.get("description", ""), 
                {"recursion_depth": recursion_depth, "plan_id": plan_id}
            )
            
            if not is_safe or risk_level >= RiskLevel.HIGH:
                events.append(SafetyEvent(
                    timestamp=time.time(),
                    event_type=SafetyViolation.UNSAFE_OPERATION,
                    severity=risk_level,
                    description=f"Unsafe operation in subtask: {message}",
                    context={"subtask": subtask, "validation_message": message},
                    action_taken="requires_approval" if risk_level < RiskLevel.CRITICAL else "operation_blocked",
                    plan_id=plan_id,
                    subtask_id=subtask.get("id")
                ))
        
        # Log all events
        for event in events:
            self._log_safety_event(event)
            
        # Determine if execution should proceed
        critical_events = [e for e in events if e.severity == RiskLevel.CRITICAL]
        high_risk_events = [e for e in events if e.severity == RiskLevel.HIGH]
        
        if critical_events:
            return False, events
        elif high_risk_events:
            # Require user approval for high-risk operations
            approved = self._request_user_approval(plan_id, events)
            return approved, events
        else:
            return True, events
            
    def validate_operation(self, operation: str, context: Dict[str, Any] = None) -> Tuple[bool, RiskLevel, str]:
        """Validate a single operation"""
        return self.operation_validator.validate_operation(operation, context)
        
    def request_stop(self, plan_id: str, reason: str = "user_request"):
        """Request stop for a plan"""
        event = SafetyEvent(
            timestamp=time.time(),
            event_type=SafetyViolation.USER_INTERVENTION,
            severity=RiskLevel.MEDIUM,
            description=f"Stop requested: {reason}",
            context={"reason": reason},
            action_taken="stop_propagated",
            plan_id=plan_id
        )
        
        self._log_safety_event(event)
        self.stop_controller.request_stop(plan_id, propagate_down=True)
        
    def is_stop_requested(self, plan_id: str) -> bool:
        """Check if stop is requested"""
        return self.stop_controller.is_stop_requested(plan_id)
        
    def register_plan(self, plan_id: str, parent_plan_id: Optional[str] = None):
        """Register a plan for safety monitoring"""
        self.stop_controller.register_plan(plan_id, parent_plan_id)
        
    def cleanup_plan(self, plan_id: str):
        """Clean up plan from safety monitoring"""
        self.stop_controller.cleanup_plan(plan_id)
        
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get comprehensive safety status summary"""
        resource_summary = self.resource_monitor.get_resource_summary()
        
        recent_events = [e for e in self.safety_events if time.time() - e.timestamp < 3600]  # Last hour
        event_counts = {}
        for event in recent_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
        return {
            "timestamp": time.time(),
            "resource_status": resource_summary,
            "recent_events": len(recent_events),
            "event_breakdown": event_counts,
            "active_plans": len(self.stop_controller.stop_flags),
            "monitoring_active": self.resource_monitor.monitoring,
            "total_safety_events": len(self.safety_events)
        }
        
    def _handle_resource_alert(self, event: SafetyEvent):
        """Handle resource monitoring alerts"""
        self._log_safety_event(event)
        
        # Take action based on severity
        if event.severity >= RiskLevel.HIGH:
            # Emergency stop all operations
            logging.critical(f"Emergency stop triggered: {event.description}")
            for plan_id in list(self.stop_controller.stop_flags.keys()):
                self.request_stop(plan_id, f"Resource emergency: {event.description}")
                
    def _request_user_approval(self, plan_id: str, events: List[SafetyEvent]) -> bool:
        """Request user approval for high-risk operations"""
        # This would integrate with the GUI to show approval dialog
        # For now, default to deny high-risk operations
        logging.warning(f"High-risk operation requires approval for plan {plan_id}")
        
        high_risk_descriptions = [e.description for e in events if e.severity >= RiskLevel.HIGH]
        logging.warning(f"High-risk operations: {'; '.join(high_risk_descriptions)}")
        
        # In a real implementation, this would show a GUI dialog
        # For autonomous operation, default to deny unless explicitly configured
        return False
        
    def _log_safety_event(self, event: SafetyEvent):
        """Log safety event to file and memory"""
        self.safety_events.append(event)
        
        # Keep only last 1000 events in memory
        if len(self.safety_events) > 1000:
            self.safety_events.pop(0)
            
        # Log to file
        try:
            with open(self.safety_log_file, 'a', encoding='utf-8') as f:
                log_entry = {
                    "timestamp": event.timestamp,
                    "event_type": event.event_type.value,
                    "severity": event.severity.name,
                    "description": event.description,
                    "plan_id": event.plan_id,
                    "subtask_id": event.subtask_id,
                    "action_taken": event.action_taken,
                    "context": event.context
                }
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logging.error(f"Failed to write safety log: {e}")

class EmergencyShutdown:
    """Emergency shutdown system for critical safety situations"""
    
    def __init__(self, safety_manager: SafetyManager):
        self.safety_manager = safety_manager
        self.shutdown_triggered = False
        self.shutdown_callbacks = []
        
    def add_shutdown_callback(self, callback: Callable[[], None]):
        """Add callback to execute during emergency shutdown"""
        self.shutdown_callbacks.append(callback)
        
    def trigger_emergency_shutdown(self, reason: str):
        """Trigger emergency shutdown of all operations"""
        if self.shutdown_triggered:
            return
            
        self.shutdown_triggered = True
        logging.critical(f"EMERGENCY SHUTDOWN TRIGGERED: {reason}")
        
        # Stop all plans
        for plan_id in list(self.safety_manager.stop_controller.stop_flags.keys()):
            self.safety_manager.request_stop(plan_id, f"Emergency shutdown: {reason}")
            
        # Execute shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Shutdown callback failed: {e}")
                
        # Log emergency event
        event = SafetyEvent(
            timestamp=time.time(),
            event_type=SafetyViolation.SYSTEM_RISK,
            severity=RiskLevel.CRITICAL,
            description=f"Emergency shutdown: {reason}",
            context={"shutdown_reason": reason},
            action_taken="emergency_shutdown"
        )
        self.safety_manager._log_safety_event(event)
        
        # Stop monitoring
        self.safety_manager.stop_monitoring()
        
    def reset_shutdown(self):
        """Reset shutdown state for new operations"""
        self.shutdown_triggered = False
        logging.info("Emergency shutdown reset")