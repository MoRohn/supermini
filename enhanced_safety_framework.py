#!/usr/bin/env python3
"""
Enhanced Safety Framework
Comprehensive safety monitoring and control system for autonomous AI operations.
Provides multi-layered safety validation, user control interfaces, and emergency stop capabilities.
"""

import logging
import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import re
import queue
from datetime import datetime, timedelta

class SafetyLevel(Enum):
    """Safety threat levels"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"
    BLOCKED = "blocked"

class SafetyViolationType(Enum):
    """Types of safety violations"""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DANGEROUS_OPERATION = "dangerous_operation"
    RESOURCE_ABUSE = "resource_abuse"
    DATA_EXPOSURE = "data_exposure"
    SYSTEM_MODIFICATION = "system_modification"
    ESCALATION_ATTEMPT = "escalation_attempt"
    UNSAFE_PATTERN = "unsafe_pattern"

class UserControlAction(Enum):
    """User control actions"""
    APPROVE = "approve"
    DENY = "deny"
    MODIFY = "modify"
    PAUSE = "pause"
    TERMINATE = "terminate"
    ESCALATE = "escalate"

@dataclass
class SafetyViolation:
    """Represents a safety violation"""
    violation_id: str
    violation_type: SafetyViolationType
    risk_level: SafetyLevel
    description: str
    context: Dict[str, Any]
    detected_at: float = field(default_factory=time.time)
    resolved: bool = False
    resolution: Optional[str] = None
    user_action: Optional[UserControlAction] = None
    auto_resolved: bool = False

@dataclass
class SafetyPolicy:
    """Safety policy definition"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    severity: SafetyLevel = SafetyLevel.MEDIUM_RISK
    auto_block: bool = False
    require_confirmation: bool = True

@dataclass
class UserConfirmation:
    """User confirmation request"""
    confirmation_id: str
    violation_id: str
    prompt: str
    options: List[str]
    timeout_seconds: int = 300
    created_at: float = field(default_factory=time.time)
    response: Optional[str] = None
    responded_at: Optional[float] = None

class SafetyMonitor:
    """Core safety monitoring system"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Safety state
        self.safety_enabled = True
        self.emergency_stop_active = False
        self.monitoring_active = True
        
        # Violation tracking
        self.violations: Dict[str, SafetyViolation] = {}
        self.violation_history: List[SafetyViolation] = []
        self.safety_policies: Dict[str, SafetyPolicy] = {}
        
        # Pattern tracking
        self.operation_patterns: List[Dict[str, Any]] = []
        self.risk_indicators: Dict[str, float] = {}
        
        # Monitoring lock
        self.monitor_lock = threading.Lock()
        
        # Initialize safety policies
        self._initialize_safety_policies()
        
        # Create safety log directory
        self.safety_log_dir = output_dir / "safety_logs"
        self.safety_log_dir.mkdir(exist_ok=True)
        
        self.logger.info("Safety Monitor initialized")
    
    def evaluate_safety(self, operation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate safety of an operation"""
        if not self.safety_enabled:
            return {"safe": True, "risk_level": SafetyLevel.SAFE.value}
        
        with self.monitor_lock:
            # Record operation for pattern analysis
            self._record_operation(operation, context)
            
            # Evaluate against safety policies
            violations = self._check_safety_policies(operation, context)
            
            # Assess overall risk
            risk_assessment = self._assess_risk_level(violations, operation, context)
            
            # Handle violations
            if violations:
                self._handle_violations(violations, operation, context)
            
            # Update risk indicators
            self._update_risk_indicators(operation, context, violations)
            
            return {
                "safe": risk_assessment["risk_level"] in [SafetyLevel.SAFE, SafetyLevel.LOW_RISK],
                "risk_level": risk_assessment["risk_level"].value,
                "violations": [v.violation_id for v in violations],
                "required_actions": risk_assessment.get("required_actions", []),
                "warnings": risk_assessment.get("warnings", [])
            }
    
    def _initialize_safety_policies(self) -> None:
        """Initialize built-in safety policies"""
        policies = [
            SafetyPolicy(
                policy_id="unauthorized_file_access",
                name="Unauthorized File Access Protection",
                description="Prevent access to sensitive system files and directories",
                rules=[
                    {
                        "type": "file_path_check",
                        "patterns": [
                            r"/etc/.*",
                            r"/root/.*", 
                            r"/var/log/.*",
                            r".*\.ssh.*",
                            r".*\.pem$",
                            r".*\.key$",
                            r".*password.*",
                            r".*secret.*"
                        ],
                        "action": "block"
                    }
                ],
                severity=SafetyLevel.HIGH_RISK,
                auto_block=True
            ),
            
            SafetyPolicy(
                policy_id="dangerous_commands",
                name="Dangerous Command Protection",
                description="Prevent execution of potentially dangerous commands",
                rules=[
                    {
                        "type": "command_check",
                        "patterns": [
                            r"rm\s+-rf\s+/",
                            r"sudo\s+rm",
                            r"chmod\s+777",
                            r"curl.*\|.*sh",
                            r"wget.*\|.*sh",
                            r"dd\s+if=.*of=/dev/",
                            r"mkfs\.",
                            r"fdisk",
                            r"format"
                        ],
                        "action": "require_confirmation"
                    }
                ],
                severity=SafetyLevel.CRITICAL_RISK,
                require_confirmation=True
            ),
            
            SafetyPolicy(
                policy_id="resource_abuse_protection",
                name="Resource Abuse Protection", 
                description="Prevent excessive resource consumption",
                rules=[
                    {
                        "type": "resource_limit_check",
                        "limits": {
                            "max_execution_time": 3600,  # 1 hour
                            "max_file_size": 1073741824,  # 1GB
                            "max_recursion_depth": 10,
                            "max_continues": 20
                        },
                        "action": "warn_and_limit"
                    }
                ],
                severity=SafetyLevel.MEDIUM_RISK
            ),
            
            SafetyPolicy(
                policy_id="data_exposure_protection",
                name="Data Exposure Protection",
                description="Prevent exposure of sensitive data",
                rules=[
                    {
                        "type": "content_scan",
                        "patterns": [
                            r"[A-Za-z0-9+/]{40,}={0,2}",  # Base64 encoded content
                            r"ssh-rsa\s+[A-Za-z0-9+/]+",   # SSH keys
                            r"-----BEGIN.*PRIVATE KEY-----",  # Private keys
                            r"password\s*[:=]\s*['\"][^'\"]+['\"]",  # Passwords
                            r"api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]"  # API keys
                        ],
                        "action": "require_confirmation"
                    }
                ],
                severity=SafetyLevel.HIGH_RISK
            ),
            
            SafetyPolicy(
                policy_id="system_modification_protection",
                name="System Modification Protection",
                description="Control system-level modifications",
                rules=[
                    {
                        "type": "system_action_check",
                        "actions": [
                            "install_package",
                            "modify_system_config",
                            "create_user",
                            "modify_permissions",
                            "network_configuration"
                        ],
                        "action": "require_confirmation"
                    }
                ],
                severity=SafetyLevel.HIGH_RISK
            )
        ]
        
        for policy in policies:
            self.safety_policies[policy.policy_id] = policy
    
    def _record_operation(self, operation: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Record operation for pattern analysis"""
        operation_record = {
            "timestamp": time.time(),
            "operation": operation.copy(),
            "context": context.copy(),
            "operation_hash": self._hash_operation(operation)
        }
        
        self.operation_patterns.append(operation_record)
        
        # Keep only recent operations (last 1000)
        if len(self.operation_patterns) > 1000:
            self.operation_patterns = self.operation_patterns[-1000:]
    
    def _hash_operation(self, operation: Dict[str, Any]) -> str:
        """Create hash of operation for pattern detection"""
        op_str = json.dumps(operation, sort_keys=True)
        return hashlib.sha256(op_str.encode()).hexdigest()[:16]
    
    def _check_safety_policies(self, operation: Dict[str, Any], context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check operation against safety policies"""
        violations = []
        
        for policy_id, policy in self.safety_policies.items():
            if not policy.enabled:
                continue
            
            policy_violations = self._check_policy_rules(policy, operation, context)
            violations.extend(policy_violations)
        
        return violations
    
    def _check_policy_rules(self, policy: SafetyPolicy, operation: Dict[str, Any], 
                           context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check operation against specific policy rules"""
        violations = []
        
        for rule in policy.rules:
            rule_type = rule.get("type")
            
            if rule_type == "file_path_check":
                violations.extend(self._check_file_path_rule(rule, policy, operation, context))
            elif rule_type == "command_check":
                violations.extend(self._check_command_rule(rule, policy, operation, context))
            elif rule_type == "resource_limit_check":
                violations.extend(self._check_resource_limit_rule(rule, policy, operation, context))
            elif rule_type == "content_scan":
                violations.extend(self._check_content_scan_rule(rule, policy, operation, context))
            elif rule_type == "system_action_check":
                violations.extend(self._check_system_action_rule(rule, policy, operation, context))
        
        return violations
    
    def _check_file_path_rule(self, rule: Dict[str, Any], policy: SafetyPolicy,
                             operation: Dict[str, Any], context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check file path access rules"""
        violations = []
        
        # Check files in operation
        files = operation.get("files", [])
        prompt = operation.get("prompt", "")
        
        # Extract file paths from prompt
        file_patterns = [
            r"(/[^\s]+)",  # Unix-style paths
            r"([A-Za-z]:\\[^\s]+)",  # Windows-style paths
        ]
        
        all_paths = files.copy()
        for pattern in file_patterns:
            all_paths.extend(re.findall(pattern, prompt))
        
        # Check each path against rule patterns
        for path in all_paths:
            for danger_pattern in rule.get("patterns", []):
                if re.search(danger_pattern, str(path), re.IGNORECASE):
                    violation = SafetyViolation(
                        violation_id=f"file_access_{int(time.time() * 1000000)}",
                        violation_type=SafetyViolationType.UNAUTHORIZED_ACCESS,
                        risk_level=policy.severity,
                        description=f"Unauthorized file access attempt: {path}",
                        context={
                            "file_path": path,
                            "policy_id": policy.policy_id,
                            "rule_pattern": danger_pattern,
                            "operation": operation
                        }
                    )
                    violations.append(violation)
        
        return violations
    
    def _check_command_rule(self, rule: Dict[str, Any], policy: SafetyPolicy,
                           operation: Dict[str, Any], context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check dangerous command rules"""
        violations = []
        
        prompt = operation.get("prompt", "").lower()
        
        for pattern in rule.get("patterns", []):
            if re.search(pattern, prompt, re.IGNORECASE):
                violation = SafetyViolation(
                    violation_id=f"dangerous_cmd_{int(time.time() * 1000000)}",
                    violation_type=SafetyViolationType.DANGEROUS_OPERATION,
                    risk_level=policy.severity,
                    description=f"Dangerous command detected: {pattern}",
                    context={
                        "command_pattern": pattern,
                        "policy_id": policy.policy_id,
                        "operation": operation
                    }
                )
                violations.append(violation)
        
        return violations
    
    def _check_resource_limit_rule(self, rule: Dict[str, Any], policy: SafetyPolicy,
                                  operation: Dict[str, Any], context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check resource limit rules"""
        violations = []
        
        limits = rule.get("limits", {})
        
        # Check execution time limit
        if "max_execution_time" in limits and context.get("max_execution_time", 0) > limits["max_execution_time"]:
            violation = SafetyViolation(
                violation_id=f"resource_time_{int(time.time() * 1000000)}",
                violation_type=SafetyViolationType.RESOURCE_ABUSE,
                risk_level=policy.severity,
                description=f"Execution time limit exceeded: {context.get('max_execution_time')}s > {limits['max_execution_time']}s",
                context={
                    "limit_type": "execution_time",
                    "requested": context.get("max_execution_time"),
                    "limit": limits["max_execution_time"],
                    "policy_id": policy.policy_id
                }
            )
            violations.append(violation)
        
        # Check recursion depth limit
        if "max_recursion_depth" in limits and context.get("max_recursion_depth", 0) > limits["max_recursion_depth"]:
            violation = SafetyViolation(
                violation_id=f"resource_recursion_{int(time.time() * 1000000)}",
                violation_type=SafetyViolationType.RESOURCE_ABUSE,
                risk_level=policy.severity,
                description=f"Recursion depth limit exceeded: {context.get('max_recursion_depth')} > {limits['max_recursion_depth']}",
                context={
                    "limit_type": "recursion_depth",
                    "requested": context.get("max_recursion_depth"),
                    "limit": limits["max_recursion_depth"],
                    "policy_id": policy.policy_id
                }
            )
            violations.append(violation)
        
        return violations
    
    def _check_content_scan_rule(self, rule: Dict[str, Any], policy: SafetyPolicy,
                                operation: Dict[str, Any], context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check content for sensitive data patterns"""
        violations = []
        
        content = operation.get("prompt", "")
        
        for pattern in rule.get("patterns", []):
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violation = SafetyViolation(
                    violation_id=f"data_exposure_{int(time.time() * 1000000)}",
                    violation_type=SafetyViolationType.DATA_EXPOSURE,
                    risk_level=policy.severity,
                    description=f"Sensitive data pattern detected: {pattern}",
                    context={
                        "pattern": pattern,
                        "matches_count": len(matches),
                        "policy_id": policy.policy_id,
                        "operation": operation
                    }
                )
                violations.append(violation)
        
        return violations
    
    def _check_system_action_rule(self, rule: Dict[str, Any], policy: SafetyPolicy,
                                 operation: Dict[str, Any], context: Dict[str, Any]) -> List[SafetyViolation]:
        """Check system action rules"""
        violations = []
        
        prompt = operation.get("prompt", "").lower()
        
        for action in rule.get("actions", []):
            action_keywords = {
                "install_package": ["install", "pip install", "apt install", "yum install"],
                "modify_system_config": ["etc/", "config", "configuration"],
                "create_user": ["useradd", "adduser", "create user"],
                "modify_permissions": ["chmod", "chown", "permissions"],
                "network_configuration": ["iptables", "firewall", "network"]
            }
            
            keywords = action_keywords.get(action, [])
            for keyword in keywords:
                if keyword in prompt:
                    violation = SafetyViolation(
                        violation_id=f"system_action_{int(time.time() * 1000000)}",
                        violation_type=SafetyViolationType.SYSTEM_MODIFICATION,
                        risk_level=policy.severity,
                        description=f"System modification action detected: {action}",
                        context={
                            "action_type": action,
                            "keyword": keyword,
                            "policy_id": policy.policy_id,
                            "operation": operation
                        }
                    )
                    violations.append(violation)
                    break
        
        return violations
    
    def _assess_risk_level(self, violations: List[SafetyViolation], operation: Dict[str, Any],
                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level of operation"""
        if not violations:
            return {"risk_level": SafetyLevel.SAFE}
        
        # Find highest risk level
        max_risk = SafetyLevel.SAFE
        required_actions = []
        warnings = []
        
        for violation in violations:
            if violation.risk_level.value > max_risk.value:
                max_risk = violation.risk_level
        
        # Determine required actions based on risk level
        if max_risk == SafetyLevel.CRITICAL_RISK:
            required_actions = ["immediate_stop", "user_confirmation"]
        elif max_risk == SafetyLevel.HIGH_RISK:
            required_actions = ["user_confirmation", "detailed_review"]
        elif max_risk == SafetyLevel.MEDIUM_RISK:
            required_actions = ["user_notification"]
            warnings = ["Operation involves moderate risk"]
        elif max_risk == SafetyLevel.LOW_RISK:
            warnings = ["Operation involves minimal risk"]
        
        return {
            "risk_level": max_risk,
            "required_actions": required_actions,
            "warnings": warnings,
            "violation_count": len(violations)
        }
    
    def _handle_violations(self, violations: List[SafetyViolation], operation: Dict[str, Any],
                          context: Dict[str, Any]) -> None:
        """Handle detected safety violations"""
        for violation in violations:
            # Store violation
            self.violations[violation.violation_id] = violation
            self.violation_history.append(violation)
            
            # Log violation
            self._log_safety_violation(violation)
            
            # Check if auto-block is required
            policy = self.safety_policies.get(violation.context.get("policy_id"))
            if policy and policy.auto_block:
                violation.auto_resolved = True
                violation.resolved = True
                violation.resolution = "auto_blocked"
    
    def _update_risk_indicators(self, operation: Dict[str, Any], context: Dict[str, Any],
                               violations: List[SafetyViolation]) -> None:
        """Update risk indicators based on operation"""
        # Track violation frequency
        for violation in violations:
            violation_type = violation.violation_type.value
            if violation_type not in self.risk_indicators:
                self.risk_indicators[violation_type] = 0.0
            
            self.risk_indicators[violation_type] += 0.1
        
        # Decay risk indicators over time
        decay_factor = 0.99
        for indicator in self.risk_indicators:
            self.risk_indicators[indicator] *= decay_factor
    
    def _log_safety_violation(self, violation: SafetyViolation) -> None:
        """Log safety violation to file"""
        log_entry = {
            "timestamp": violation.detected_at,
            "violation_id": violation.violation_id,
            "type": violation.violation_type.value,
            "risk_level": violation.risk_level.value,
            "description": violation.description,
            "context": violation.context
        }
        
        log_file = self.safety_log_dir / f"safety_violations_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to log safety violation: {e}")
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        active_violations = [v for v in self.violations.values() if not v.resolved]
        
        return {
            "safety_enabled": self.safety_enabled,
            "monitoring_active": self.monitoring_active,
            "emergency_stop_active": self.emergency_stop_active,
            "active_violations": len(active_violations),
            "total_violations": len(self.violation_history),
            "risk_indicators": self.risk_indicators.copy(),
            "policies_enabled": sum(1 for p in self.safety_policies.values() if p.enabled),
            "last_check": time.time()
        }
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Activate emergency stop"""
        self.emergency_stop_active = True
        self.monitoring_active = False
        
        # Resolve all active violations
        for violation in self.violations.values():
            if not violation.resolved:
                violation.resolved = True
                violation.resolution = "emergency_stop"
                violation.user_action = UserControlAction.TERMINATE
        
        self.logger.critical("Emergency stop activated - all operations halted")
        
        return {
            "success": True,
            "message": "Emergency stop activated",
            "timestamp": time.time()
        }
    
    def resume_monitoring(self) -> Dict[str, Any]:
        """Resume safety monitoring after emergency stop"""
        self.emergency_stop_active = False
        self.monitoring_active = True
        
        self.logger.info("Safety monitoring resumed")
        
        return {
            "success": True,
            "message": "Safety monitoring resumed",
            "timestamp": time.time()
        }

class UserControlInterface:
    """Interface for user control and confirmation"""
    
    def __init__(self, safety_monitor: SafetyMonitor):
        self.safety_monitor = safety_monitor
        self.logger = logging.getLogger(__name__)
        
        # Confirmation management
        self.pending_confirmations: Dict[str, UserConfirmation] = {}
        self.confirmation_responses: queue.Queue = queue.Queue()
        
        # Control state
        self.user_override_active = False
        self.auto_approve_low_risk = False
        
        self.logger.info("User Control Interface initialized")
    
    def request_user_confirmation(self, violation: SafetyViolation) -> UserConfirmation:
        """Request user confirmation for a safety violation"""
        confirmation_id = f"confirm_{int(time.time() * 1000000)}"
        
        prompt = self._create_confirmation_prompt(violation)
        options = self._get_confirmation_options(violation)
        
        confirmation = UserConfirmation(
            confirmation_id=confirmation_id,
            violation_id=violation.violation_id,
            prompt=prompt,
            options=options
        )
        
        self.pending_confirmations[confirmation_id] = confirmation
        
        self.logger.info(f"User confirmation requested: {confirmation_id}")
        return confirmation
    
    def _create_confirmation_prompt(self, violation: SafetyViolation) -> str:
        """Create user-friendly confirmation prompt"""
        risk_descriptions = {
            SafetyLevel.LOW_RISK: "low risk",
            SafetyLevel.MEDIUM_RISK: "moderate risk",
            SafetyLevel.HIGH_RISK: "high risk",
            SafetyLevel.CRITICAL_RISK: "critical risk"
        }
        
        risk_desc = risk_descriptions.get(violation.risk_level, "unknown risk")
        
        prompt = f"""
Safety Alert - {risk_desc.title()} Operation Detected

Violation: {violation.description}
Risk Level: {violation.risk_level.value}
Type: {violation.violation_type.value}

The AI wants to perform an operation that has been flagged as {risk_desc}.

Would you like to:
"""
        return prompt.strip()
    
    def _get_confirmation_options(self, violation: SafetyViolation) -> List[str]:
        """Get available confirmation options based on violation"""
        base_options = ["Approve", "Deny", "View Details"]
        
        if violation.risk_level in [SafetyLevel.HIGH_RISK, SafetyLevel.CRITICAL_RISK]:
            base_options.extend(["Approve Once", "Block Similar"])
        
        if violation.risk_level == SafetyLevel.CRITICAL_RISK:
            base_options.append("Emergency Stop")
        
        return base_options
    
    def provide_confirmation(self, violation_id: str, approved: bool, explanation: str = "") -> Dict[str, Any]:
        """Provide user confirmation response"""
        if violation_id not in self.safety_monitor.violations:
            return {"success": False, "error": "Violation not found"}
        
        violation = self.safety_monitor.violations[violation_id]
        
        # Find pending confirmation
        confirmation = None
        for conf in self.pending_confirmations.values():
            if conf.violation_id == violation_id:
                confirmation = conf
                break
        
        if not confirmation:
            return {"success": False, "error": "No pending confirmation found"}
        
        # Process response
        confirmation.response = "approved" if approved else "denied"
        confirmation.responded_at = time.time()
        
        # Update violation
        violation.resolved = True
        violation.user_action = UserControlAction.APPROVE if approved else UserControlAction.DENY
        violation.resolution = f"user_{confirmation.response}: {explanation}" if explanation else f"user_{confirmation.response}"
        
        # Remove from pending
        del self.pending_confirmations[confirmation.confirmation_id]
        
        self.logger.info(f"User confirmation provided for {violation_id}: {confirmation.response}")
        
        return {
            "success": True,
            "action": confirmation.response,
            "violation_id": violation_id,
            "timestamp": time.time()
        }
    
    def get_pending_confirmations(self) -> List[Dict[str, Any]]:
        """Get list of pending confirmations"""
        confirmations = []
        
        for conf in self.pending_confirmations.values():
            # Check if expired
            if time.time() - conf.created_at > conf.timeout_seconds:
                self._handle_confirmation_timeout(conf)
                continue
            
            confirmations.append({
                "confirmation_id": conf.confirmation_id,
                "violation_id": conf.violation_id,
                "prompt": conf.prompt,
                "options": conf.options,
                "created_at": conf.created_at,
                "timeout_remaining": max(0, conf.timeout_seconds - (time.time() - conf.created_at))
            })
        
        return confirmations
    
    def _handle_confirmation_timeout(self, confirmation: UserConfirmation) -> None:
        """Handle confirmation timeout"""
        # Default to deny for security
        violation = self.safety_monitor.violations.get(confirmation.violation_id)
        if violation:
            violation.resolved = True
            violation.user_action = UserControlAction.DENY
            violation.resolution = "timeout_denied"
        
        # Remove from pending
        if confirmation.confirmation_id in self.pending_confirmations:
            del self.pending_confirmations[confirmation.confirmation_id]
        
        self.logger.warning(f"Confirmation timeout for {confirmation.violation_id}")
    
    def set_user_override(self, active: bool, duration_minutes: int = 60) -> Dict[str, Any]:
        """Set user override mode"""
        self.user_override_active = active
        
        if active:
            # Schedule override deactivation
            def deactivate_override():
                time.sleep(duration_minutes * 60)
                self.user_override_active = False
                self.logger.info("User override expired and deactivated")
            
            override_thread = threading.Thread(target=deactivate_override, daemon=True)
            override_thread.start()
            
            self.logger.warning(f"User override activated for {duration_minutes} minutes")
        else:
            self.logger.info("User override deactivated")
        
        return {
            "success": True,
            "override_active": self.user_override_active,
            "duration_minutes": duration_minutes if active else 0
        }
    
    def emergency_override(self, justification: str) -> Dict[str, Any]:
        """Emergency override for critical situations"""
        self.user_override_active = True
        
        # Log emergency override
        override_log = {
            "timestamp": time.time(),
            "type": "emergency_override",
            "justification": justification,
            "user": "system_operator"  # Could be enhanced to track actual user
        }
        
        self.logger.critical(f"Emergency override activated: {justification}")
        
        return {
            "success": True,
            "message": "Emergency override activated",
            "expires_in_minutes": 30,  # Emergency override expires quickly
            "justification": justification
        }

# Enhanced Safety Integration Functions

def create_comprehensive_safety_framework(output_dir: Path) -> Tuple[SafetyMonitor, UserControlInterface]:
    """Create complete safety framework"""
    safety_monitor = SafetyMonitor(output_dir)
    user_control = UserControlInterface(safety_monitor)
    
    return safety_monitor, user_control

def validate_autonomous_operation(operation: Dict[str, Any], safety_monitor: SafetyMonitor) -> Dict[str, Any]:
    """Validate autonomous operation for safety"""
    context = {
        "autonomous_mode": True,
        "validation_level": "comprehensive"
    }
    
    return safety_monitor.evaluate_safety(operation, context)

def apply_safety_constraints(config: Dict[str, Any], safety_monitor: SafetyMonitor) -> Dict[str, Any]:
    """Apply safety constraints to configuration"""
    safety_config = config.copy()
    
    # Apply resource limits
    max_safe_execution = 1800  # 30 minutes max
    max_safe_recursion = 5
    max_safe_continues = 15
    
    if safety_config.get("max_execution_time", 0) > max_safe_execution:
        safety_config["max_execution_time"] = max_safe_execution
    
    if safety_config.get("max_recursion_depth", 0) > max_safe_recursion:
        safety_config["max_recursion_depth"] = max_safe_recursion
    
    if safety_config.get("max_continues", 0) > max_safe_continues:
        safety_config["max_continues"] = max_safe_continues
    
    return safety_config

def get_safety_recommendations(operation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get safety recommendations for an operation"""
    recommendations = []
    
    prompt = operation.get("prompt", "").lower()
    
    # Check for high-risk patterns
    if any(word in prompt for word in ["system", "admin", "root", "sudo"]):
        recommendations.append({
            "type": "elevated_privileges",
            "severity": "high",
            "recommendation": "Consider running with reduced privileges or user confirmation",
            "reason": "Operation may require elevated system access"
        })
    
    if any(word in prompt for word in ["delete", "remove", "destroy", "format"]):
        recommendations.append({
            "type": "destructive_operation",
            "severity": "critical",
            "recommendation": "Require explicit user confirmation before proceeding",
            "reason": "Operation appears to be potentially destructive"
        })
    
    if len(prompt) > 2000:
        recommendations.append({
            "type": "complex_operation",
            "severity": "medium",
            "recommendation": "Consider breaking down into smaller, more manageable tasks",
            "reason": "Large prompts may lead to unexpected behavior"
        })
    
    return recommendations