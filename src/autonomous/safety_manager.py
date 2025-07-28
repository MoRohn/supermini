"""
Safety Manager for SuperMini Autonomous Continuation
Comprehensive safety controls, circuit breakers, and resource monitoring
"""

import time
import logging
import threading
import psutil
import os
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from collections import deque, defaultdict


class SafetyLevel(Enum):
    """Safety alert levels"""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


class ResourceType(Enum):
    """Types of resources to monitor"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    EXECUTION_TIME = "execution_time"
    ITERATION_COUNT = "iteration_count"


@dataclass
class SafetyThreshold:
    """Safety threshold configuration"""
    resource_type: ResourceType
    warning_level: float
    danger_level: float
    critical_level: float
    measurement_window: int  # seconds
    action_on_breach: str   # "warn", "throttle", "stop"


@dataclass
class SafetyValidationResult:
    """Result of safety validation"""
    is_safe: bool
    safety_level: SafetyLevel
    reason: str
    violations: List[str]
    recommendations: List[str]
    resource_status: Dict[str, float]


@dataclass
class CircuitBreakerState:
    """State of a circuit breaker"""
    name: str
    failure_count: int
    last_failure_time: float
    state: str  # "closed", "open", "half_open"
    failure_threshold: int
    recovery_timeout: float
    success_threshold: int
    consecutive_successes: int


class ResourceMonitor:
    """Real-time resource monitoring"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.resource_history = {
            ResourceType.CPU: deque(maxlen=60),      # 1 minute of history
            ResourceType.MEMORY: deque(maxlen=60),
            ResourceType.DISK: deque(maxlen=60)
        }
        self.lock = threading.Lock()
        
    def start_monitoring(self):
        """Start resource monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logging.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect resource metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                # Store in history
                with self.lock:
                    self.resource_history[ResourceType.CPU].append({
                        'timestamp': time.time(),
                        'value': cpu_percent
                    })
                    self.resource_history[ResourceType.MEMORY].append({
                        'timestamp': time.time(),
                        'value': memory_percent
                    })
                    self.resource_history[ResourceType.DISK].append({
                        'timestamp': time.time(),
                        'value': disk_percent
                    })
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logging.error(f"Resource monitoring error: {e}")
                time.sleep(self.monitoring_interval)
    
    def get_current_resources(self) -> Dict[ResourceType, float]:
        """Get current resource utilization"""
        try:
            return {
                ResourceType.CPU: psutil.cpu_percent(interval=0.1),
                ResourceType.MEMORY: psutil.virtual_memory().percent,
                ResourceType.DISK: psutil.disk_usage('/').percent
            }
        except Exception as e:
            logging.error(f"Error getting current resources: {e}")
            return {ResourceType.CPU: 0.0, ResourceType.MEMORY: 0.0, ResourceType.DISK: 0.0}
    
    def get_average_resources(self, window_seconds: int = 30) -> Dict[ResourceType, float]:
        """Get average resource utilization over time window"""
        cutoff_time = time.time() - window_seconds
        averages = {}
        
        with self.lock:
            for resource_type, history in self.resource_history.items():
                recent_values = [
                    entry['value'] for entry in history 
                    if entry['timestamp'] > cutoff_time
                ]
                
                if recent_values:
                    averages[resource_type] = sum(recent_values) / len(recent_values)
                else:
                    averages[resource_type] = 0.0
        
        return averages
    
    def detect_resource_spikes(self, spike_threshold: float = 2.0) -> Dict[ResourceType, bool]:
        """Detect resource usage spikes"""
        spikes = {}
        current = self.get_current_resources()
        averages = self.get_average_resources(60)  # 1 minute average
        
        for resource_type in [ResourceType.CPU, ResourceType.MEMORY, ResourceType.DISK]:
            current_val = current.get(resource_type, 0.0)
            avg_val = averages.get(resource_type, 0.0)
            
            # Detect spike if current usage is significantly higher than average
            if avg_val > 0 and current_val > avg_val * spike_threshold and current_val > 50:
                spikes[resource_type] = True
            else:
                spikes[resource_type] = False
        
        return spikes


class CircuitBreaker:
    """Circuit breaker for failure protection"""
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 success_threshold: int = 3):
        self.name = name
        self.state = CircuitBreakerState(
            name=name,
            failure_count=0,
            last_failure_time=0.0,
            state="closed",  # closed = normal, open = blocking, half_open = testing
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold,
            consecutive_successes=0
        )
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Tuple[bool, Any, str]:
        """Execute function with circuit breaker protection"""
        with self.lock:
            # Check if circuit is open
            if self.state.state == "open":
                # Check if recovery timeout has elapsed
                if time.time() - self.state.last_failure_time > self.state.recovery_timeout:
                    self.state.state = "half_open"
                    self.state.consecutive_successes = 0
                    logging.info(f"Circuit breaker {self.name} moved to half-open state")
                else:
                    return False, None, f"Circuit breaker {self.name} is open"
            
            # Try to execute function
            try:
                result = func(*args, **kwargs)
                
                # Record success
                if self.state.state == "half_open":
                    self.state.consecutive_successes += 1
                    if self.state.consecutive_successes >= self.state.success_threshold:
                        self.state.state = "closed"
                        self.state.failure_count = 0
                        logging.info(f"Circuit breaker {self.name} closed after recovery")
                
                return True, result, "Success"
                
            except Exception as e:
                # Record failure
                self.state.failure_count += 1
                self.state.last_failure_time = time.time()
                self.state.consecutive_successes = 0
                
                if self.state.failure_count >= self.state.failure_threshold:
                    self.state.state = "open"
                    logging.warning(f"Circuit breaker {self.name} opened due to failures")
                
                return False, None, f"Circuit breaker {self.name} caught error: {str(e)}"
    
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        with self.lock:
            return self.state
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        with self.lock:
            self.state.state = "closed"
            self.state.failure_count = 0
            self.state.consecutive_successes = 0
            logging.info(f"Circuit breaker {self.name} manually reset")


class SafetyManager:
    """
    Comprehensive safety management for autonomous continuation
    Monitors resources, enforces limits, and provides emergency controls
    """
    
    def __init__(self):
        # Default safety thresholds
        self.safety_thresholds = {
            ResourceType.CPU: SafetyThreshold(
                resource_type=ResourceType.CPU,
                warning_level=70.0,
                danger_level=85.0,
                critical_level=95.0,
                measurement_window=30,
                action_on_breach="throttle"
            ),
            ResourceType.MEMORY: SafetyThreshold(
                resource_type=ResourceType.MEMORY,
                warning_level=75.0,
                danger_level=90.0,
                critical_level=95.0,
                measurement_window=30,
                action_on_breach="stop"
            ),
            ResourceType.EXECUTION_TIME: SafetyThreshold(
                resource_type=ResourceType.EXECUTION_TIME,
                warning_level=120.0,  # 2 minutes
                danger_level=300.0,   # 5 minutes
                critical_level=600.0, # 10 minutes
                measurement_window=1,
                action_on_breach="stop"
            ),
            ResourceType.ITERATION_COUNT: SafetyThreshold(
                resource_type=ResourceType.ITERATION_COUNT,
                warning_level=8.0,
                danger_level=12.0,
                critical_level=20.0,
                measurement_window=1,
                action_on_breach="stop"
            )
        }
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start_monitoring()
        
        # Circuit breakers
        self.circuit_breakers = {
            'continuation_engine': CircuitBreaker('continuation_engine', failure_threshold=3),
            'quality_assessment': CircuitBreaker('quality_assessment', failure_threshold=2),
            'enhancement_discovery': CircuitBreaker('enhancement_discovery', failure_threshold=2),
            'ai_model_calls': CircuitBreaker('ai_model_calls', failure_threshold=5)
        }
        
        # Safety state tracking
        self.safety_violations = defaultdict(list)
        self.emergency_stop_triggered = False
        self.throttling_active = False
        self.safety_override_active = False
        
        # Pattern detection for anomalies
        self.anomaly_patterns = []
        
        logging.info("SafetyManager initialized with comprehensive monitoring")
    
    def validate_continuation(self, context) -> SafetyValidationResult:
        """
        Main safety validation for continuation requests
        Returns validation result with safety status
        """
        violations = []
        recommendations = []
        safety_level = SafetyLevel.SAFE
        
        try:
            # Check emergency stop
            if self.emergency_stop_triggered:
                return SafetyValidationResult(
                    is_safe=False,
                    safety_level=SafetyLevel.CRITICAL,
                    reason="Emergency stop is active",
                    violations=["Emergency stop triggered"],
                    recommendations=["Reset emergency stop to continue"],
                    resource_status={}
                )
            
            # Check resource utilization
            current_resources = self.resource_monitor.get_current_resources()
            resource_violations = self._check_resource_thresholds(current_resources)
            violations.extend(resource_violations)
            
            # Check execution time
            if hasattr(context, 'execution_time'):
                time_violations = self._check_execution_time(context.execution_time)
                violations.extend(time_violations)
            
            # Check iteration limits
            if hasattr(context, 'iteration_count') and hasattr(context, 'max_iterations'):
                iteration_violations = self._check_iteration_limits(
                    context.iteration_count, context.max_iterations
                )
                violations.extend(iteration_violations)
            
            # Check circuit breaker states
            breaker_violations = self._check_circuit_breakers()
            violations.extend(breaker_violations)
            
            # Check for resource spikes
            spikes = self.resource_monitor.detect_resource_spikes()
            spike_violations = self._check_resource_spikes(spikes)
            violations.extend(spike_violations)
            
            # Determine overall safety level
            if any('critical' in v.lower() for v in violations):
                safety_level = SafetyLevel.CRITICAL
            elif any('danger' in v.lower() for v in violations):
                safety_level = SafetyLevel.DANGER
            elif any('warning' in v.lower() for v in violations):
                safety_level = SafetyLevel.WARNING
            
            # Generate recommendations
            recommendations = self._generate_safety_recommendations(violations, safety_level)
            
            # Determine if safe to continue
            is_safe = safety_level in [SafetyLevel.SAFE, SafetyLevel.WARNING]
            
            # Apply safety actions
            if not is_safe:
                self._apply_safety_actions(safety_level, violations)
            
            return SafetyValidationResult(
                is_safe=is_safe,
                safety_level=safety_level,
                reason=self._generate_safety_reason(safety_level, violations),
                violations=violations,
                recommendations=recommendations,
                resource_status=current_resources
            )
            
        except Exception as e:
            logging.error(f"Safety validation error: {e}")
            return SafetyValidationResult(
                is_safe=False,
                safety_level=SafetyLevel.CRITICAL,
                reason=f"Safety validation failed: {str(e)}",
                violations=[f"Safety system error: {str(e)}"],
                recommendations=["Check safety system integrity"],
                resource_status={}
            )
    
    def _check_resource_thresholds(self, resources: Dict[ResourceType, float]) -> List[str]:
        """Check if resource usage exceeds thresholds"""
        violations = []
        
        for resource_type, current_value in resources.items():
            if resource_type in self.safety_thresholds:
                threshold = self.safety_thresholds[resource_type]
                
                if current_value >= threshold.critical_level:
                    violations.append(f"CRITICAL: {resource_type.value} usage at {current_value:.1f}% "
                                    f"(critical threshold: {threshold.critical_level}%)")
                elif current_value >= threshold.danger_level:
                    violations.append(f"DANGER: {resource_type.value} usage at {current_value:.1f}% "
                                    f"(danger threshold: {threshold.danger_level}%)")
                elif current_value >= threshold.warning_level:
                    violations.append(f"WARNING: {resource_type.value} usage at {current_value:.1f}% "
                                    f"(warning threshold: {threshold.warning_level}%)")
        
        return violations
    
    def _check_execution_time(self, execution_time: float) -> List[str]:
        """Check execution time against thresholds"""
        violations = []
        threshold = self.safety_thresholds[ResourceType.EXECUTION_TIME]
        
        if execution_time >= threshold.critical_level:
            violations.append(f"CRITICAL: Execution time {execution_time:.1f}s exceeds critical limit "
                            f"({threshold.critical_level}s)")
        elif execution_time >= threshold.danger_level:
            violations.append(f"DANGER: Execution time {execution_time:.1f}s exceeds danger limit "
                            f"({threshold.danger_level}s)")
        elif execution_time >= threshold.warning_level:
            violations.append(f"WARNING: Execution time {execution_time:.1f}s exceeds warning limit "
                            f"({threshold.warning_level}s)")
        
        return violations
    
    def _check_iteration_limits(self, current_iteration: int, max_iterations: int) -> List[str]:
        """Check iteration count against limits"""
        violations = []
        threshold = self.safety_thresholds[ResourceType.ITERATION_COUNT]
        
        if current_iteration >= threshold.critical_level:
            violations.append(f"CRITICAL: Iteration count {current_iteration} exceeds critical limit "
                            f"({threshold.critical_level})")
        elif current_iteration >= threshold.danger_level:
            violations.append(f"DANGER: Iteration count {current_iteration} exceeds danger limit "
                            f"({threshold.danger_level})")
        elif current_iteration >= threshold.warning_level:
            violations.append(f"WARNING: Iteration count {current_iteration} exceeds warning limit "
                            f"({threshold.warning_level})")
        
        # Also check against max_iterations
        if current_iteration >= max_iterations * 0.9:
            violations.append(f"WARNING: Approaching maximum iterations "
                            f"({current_iteration}/{max_iterations})")
        
        return violations
    
    def _check_circuit_breakers(self) -> List[str]:
        """Check circuit breaker states"""
        violations = []
        
        for name, breaker in self.circuit_breakers.items():
            state = breaker.get_state()
            if state.state == "open":
                violations.append(f"DANGER: Circuit breaker '{name}' is open "
                                f"(failures: {state.failure_count})")
            elif state.state == "half_open":
                violations.append(f"WARNING: Circuit breaker '{name}' is in recovery mode")
        
        return violations
    
    def _check_resource_spikes(self, spikes: Dict[ResourceType, bool]) -> List[str]:
        """Check for resource usage spikes"""
        violations = []
        
        for resource_type, has_spike in spikes.items():
            if has_spike:
                violations.append(f"WARNING: Detected {resource_type.value} usage spike")
        
        return violations
    
    def _generate_safety_recommendations(self, violations: List[str], 
                                       safety_level: SafetyLevel) -> List[str]:
        """Generate safety recommendations based on violations"""
        recommendations = []
        
        if safety_level == SafetyLevel.CRITICAL:
            recommendations.append("Stop all autonomous operations immediately")
            recommendations.append("Check system resources and restart if necessary")
        
        elif safety_level == SafetyLevel.DANGER:
            recommendations.append("Reduce continuation frequency")
            recommendations.append("Monitor resource usage closely")
            recommendations.append("Consider stopping autonomous operations")
        
        elif safety_level == SafetyLevel.WARNING:
            recommendations.append("Monitor system performance")
            recommendations.append("Consider reducing operation complexity")
        
        # Specific recommendations based on violation types
        if any('memory' in v.lower() for v in violations):
            recommendations.append("Close unused applications to free memory")
        
        if any('cpu' in v.lower() for v in violations):
            recommendations.append("Reduce concurrent operations")
        
        if any('execution time' in v.lower() for v in violations):
            recommendations.append("Reduce maximum iteration limits")
        
        if any('circuit breaker' in v.lower() for v in violations):
            recommendations.append("Wait for circuit breakers to recover")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_safety_reason(self, safety_level: SafetyLevel, violations: List[str]) -> str:
        """Generate safety reason summary"""
        if safety_level == SafetyLevel.SAFE:
            return "All safety checks passed"
        
        violation_count = len(violations)
        primary_violation = violations[0] if violations else "Unknown issue"
        
        if violation_count > 1:
            return f"Multiple safety violations detected: {primary_violation} and {violation_count - 1} others"
        else:
            return primary_violation
    
    def _apply_safety_actions(self, safety_level: SafetyLevel, violations: List[str]):
        """Apply appropriate safety actions based on level"""
        
        if safety_level == SafetyLevel.CRITICAL:
            self.trigger_emergency_stop("Critical safety violations detected")
        
        elif safety_level == SafetyLevel.DANGER:
            # Enable throttling for danger level
            self.throttling_active = True
            logging.warning("Safety throttling activated due to danger level violations")
        
        # Log all violations
        for violation in violations:
            logging.warning(f"Safety violation: {violation}")
            
        # Store violations for analysis
        timestamp = time.time()
        for violation in violations:
            self.safety_violations[safety_level.value].append({
                'timestamp': timestamp,
                'violation': violation
            })
    
    def trigger_emergency_stop(self, reason: str):
        """Trigger emergency stop"""
        self.emergency_stop_triggered = True
        logging.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        
        # Stop resource monitoring
        self.resource_monitor.stop_monitoring()
        
        # Log emergency stop
        self.safety_violations['emergency_stop'].append({
            'timestamp': time.time(),
            'reason': reason
        })
    
    def reset_emergency_stop(self) -> bool:
        """Reset emergency stop if safe to do so"""
        if not self.emergency_stop_triggered:
            return True
        
        # Check if it's safe to reset
        current_resources = self.resource_monitor.get_current_resources()
        resource_violations = self._check_resource_thresholds(current_resources)
        
        if any('critical' in v.lower() for v in resource_violations):
            logging.warning("Cannot reset emergency stop: critical resource violations still present")
            return False
        
        self.emergency_stop_triggered = False
        self.throttling_active = False
        
        # Restart resource monitoring
        self.resource_monitor.start_monitoring()
        
        logging.info("Emergency stop reset successfully")
        return True
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def add_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Add new circuit breaker"""
        breaker = CircuitBreaker(name, **kwargs)
        self.circuit_breakers[name] = breaker
        return breaker
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety status"""
        current_resources = self.resource_monitor.get_current_resources()
        
        # Circuit breaker states
        breaker_states = {}
        for name, breaker in self.circuit_breakers.items():
            state = breaker.get_state()
            breaker_states[name] = {
                'state': state.state,
                'failure_count': state.failure_count,
                'consecutive_successes': state.consecutive_successes
            }
        
        # Recent violations
        recent_violations = {}
        cutoff_time = time.time() - 300  # Last 5 minutes
        
        for level, violations in self.safety_violations.items():
            recent = [v for v in violations if v['timestamp'] > cutoff_time]
            recent_violations[level] = len(recent)
        
        return {
            'emergency_stop_active': self.emergency_stop_triggered,
            'throttling_active': self.throttling_active,
            'safety_override_active': self.safety_override_active,
            'current_resources': {rt.value: val for rt, val in current_resources.items()},
            'circuit_breakers': breaker_states,
            'recent_violations': recent_violations,
            'monitoring_active': self.resource_monitor.is_monitoring,
            'safety_thresholds': {
                rt.value: {
                    'warning': th.warning_level,
                    'danger': th.danger_level,
                    'critical': th.critical_level
                } for rt, th in self.safety_thresholds.items()
            }
        }
    
    def update_safety_threshold(self, resource_type: ResourceType, **kwargs):
        """Update safety threshold for resource type"""
        if resource_type in self.safety_thresholds:
            threshold = self.safety_thresholds[resource_type]
            
            for key, value in kwargs.items():
                if hasattr(threshold, key):
                    setattr(threshold, key, value)
                    logging.info(f"Updated {resource_type.value} threshold {key} to {value}")
    
    def cleanup(self):
        """Cleanup safety manager resources"""
        self.resource_monitor.stop_monitoring()
        logging.info("SafetyManager cleanup completed")