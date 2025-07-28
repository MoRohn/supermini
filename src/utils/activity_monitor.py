#!/usr/bin/env python3
"""
Enhanced Activity Monitoring and Logging System
Provides real-time transparency for autonomous operations
"""

import sys
import os
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
from collections import defaultdict, deque

try:
    from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
    from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class ActivityLevel(Enum):
    """Activity logging levels"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ActivityType(Enum):
    """Types of activities to monitor"""
    TASK_START = "task_start"
    TASK_END = "task_end"
    AUTONOMOUS_ACTION = "autonomous_action"
    SAFETY_CHECK = "safety_check"
    AI_QUERY = "ai_query"
    AI_RESPONSE = "ai_response"
    FILE_OPERATION = "file_operation"
    SCREENSHOT = "screenshot"
    USER_INTERACTION = "user_interaction"
    SYSTEM_EVENT = "system_event"
    ERROR_EVENT = "error_event"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class ActivityEvent:
    """Data class for activity events"""
    timestamp: float
    event_id: str
    activity_type: ActivityType
    level: ActivityLevel
    title: str
    description: str
    details: Dict[str, Any]
    duration: Optional[float] = None
    parent_task_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ActivityLogger:
    """Enhanced logging system for activity monitoring"""
    
    def __init__(self, log_dir: Path, max_events: int = 10000):
        self.log_dir = log_dir
        self.max_events = max_events
        self.events = deque(maxlen=max_events)
        self.event_listeners = []
        self.session_id = f"session_{int(time.time())}"
        self.lock = threading.RLock()
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
        self.active_tasks = {}
        
        # Event counters
        self.event_counters = defaultdict(int)
        
        # Setup enhanced logging (after initializing counters)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup enhanced file and memory logging"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Activity log file
        activity_log_file = self.log_dir / f"activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create custom formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for activity logs
        self.file_handler = logging.FileHandler(activity_log_file)
        self.file_handler.setFormatter(formatter)
        self.file_handler.setLevel(logging.DEBUG)
        
        # Create activity logger
        self.logger = logging.getLogger('SuperMini.Activity')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)
        
        self.log_activity(
            ActivityType.SYSTEM_EVENT,
            ActivityLevel.INFO,
            "Activity Monitor Started",
            "Enhanced activity monitoring system initialized",
            {"session_id": self.session_id, "log_file": str(activity_log_file)}
        )
    
    def log_activity(self, 
                    activity_type: ActivityType, 
                    level: ActivityLevel,
                    title: str, 
                    description: str, 
                    details: Dict[str, Any] = None,
                    duration: Optional[float] = None,
                    parent_task_id: Optional[str] = None) -> str:
        """Log an activity event"""
        
        with self.lock:
            event_id = f"evt_{int(time.time() * 1000000)}"
            timestamp = time.time()
            
            event = ActivityEvent(
                timestamp=timestamp,
                event_id=event_id,
                activity_type=activity_type,
                level=level,
                title=title,
                description=description,
                details=details or {},
                duration=duration,
                parent_task_id=parent_task_id,
                session_id=self.session_id
            )
            
            # Add to memory store
            self.events.append(event)
            
            # Update counters
            self.event_counters[activity_type] += 1
            self.event_counters[level] += 1
            
            # Log to file
            log_message = f"{activity_type.value} | {title} | {description}"
            if details:
                log_message += f" | Details: {json.dumps(details, default=str)}"
            
            if level == ActivityLevel.CRITICAL:
                self.logger.critical(log_message)
            elif level == ActivityLevel.ERROR:
                self.logger.error(log_message)
            elif level == ActivityLevel.WARNING:
                self.logger.warning(log_message)
            elif level == ActivityLevel.INFO:
                self.logger.info(log_message)
            elif level == ActivityLevel.DEBUG:
                self.logger.debug(log_message)
            else:  # TRACE
                self.logger.debug(f"TRACE: {log_message}")
            
            # Notify listeners
            self.notify_listeners(event)
            
            return event_id
    
    def add_listener(self, callback: Callable[[ActivityEvent], None]):
        """Add an event listener"""
        self.event_listeners.append(callback)
    
    def notify_listeners(self, event: ActivityEvent):
        """Notify all listeners of new event"""
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error notifying listener: {e}")
    
    def start_task(self, task_id: str, task_type: str, description: str, details: Dict[str, Any] = None) -> str:
        """Start tracking a task"""
        with self.lock:
            self.active_tasks[task_id] = {
                "start_time": time.time(),
                "task_type": task_type,
                "description": description,
                "details": details or {}
            }
        
        return self.log_activity(
            ActivityType.TASK_START,
            ActivityLevel.INFO,
            f"Task Started: {task_type}",
            description,
            {"task_id": task_id, **(details or {})},
            parent_task_id=task_id
        )
    
    def end_task(self, task_id: str, success: bool = True, result_details: Dict[str, Any] = None) -> str:
        """End tracking a task with detailed completion summary"""
        with self.lock:
            if task_id in self.active_tasks:
                task_info = self.active_tasks[task_id]
                duration = time.time() - task_info["start_time"]
                del self.active_tasks[task_id]
                
                # Record performance metric
                self.performance_metrics[task_info["task_type"]].append(duration)
                
                level = ActivityLevel.INFO if success else ActivityLevel.ERROR
                title = f"Task {'Completed' if success else 'Failed'}: {task_info['task_type']}"
                
                # Create detailed completion summary
                completion_summary = self._generate_task_completion_summary(
                    task_info, result_details, duration, success
                )
                
                details = {
                    "task_id": task_id,
                    "success": success,
                    "duration": duration,
                    "completion_summary": completion_summary,
                    **(result_details or {})
                }
                
                return self.log_activity(
                    ActivityType.TASK_END,
                    level,
                    title,
                    completion_summary,  # Use detailed summary as description
                    details,
                    duration=duration,
                    parent_task_id=task_id
                )
    
    def _generate_task_completion_summary(self, task_info: Dict[str, Any], 
                                        result_details: Dict[str, Any], 
                                        duration: float, success: bool) -> str:
        """Generate a detailed completion summary for tasks"""
        summary_parts = []
        
        # Basic task info
        task_type = task_info.get("task_type", "unknown")
        description = task_info.get("description", "")[:100]
        if len(task_info.get("description", "")) > 100:
            description += "..."
        
        summary_parts.append(f"Task: {description}")
        summary_parts.append(f"Type: {task_type}")
        summary_parts.append(f"Duration: {duration:.2f}s")
        summary_parts.append(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if result_details:
            # Add specific result metrics
            if "generated_files_count" in result_details:
                count = result_details["generated_files_count"]
                summary_parts.append(f"Files Generated: {count}")
                
                # Show generated file names if available
                if "files_generated" in result_details and result_details["files_generated"]:
                    files = result_details["files_generated"]
                    if len(files) <= 3:
                        file_list = ", ".join([Path(f).name for f in files])
                        summary_parts.append(f"Files: [{file_list}]")
                    else:
                        recent_files = ", ".join([Path(f).name for f in files[-2:]])
                        summary_parts.append(f"Recent Files: [{recent_files}] (+{len(files)-2} more)")
            
            if "steps_completed" in result_details:
                steps = result_details["steps_completed"]
                summary_parts.append(f"Steps Completed: {steps}")
            
            if "continue_count" in result_details and result_details["continue_count"] > 0:
                continues = result_details["continue_count"]
                summary_parts.append(f"Auto-Continues: {continues}")
            
            if "autonomous_mode" in result_details:
                if result_details["autonomous_mode"]:
                    summary_parts.append("🤖 Autonomous Mode")
            
            if "score" in result_details and result_details["score"]:
                score = result_details["score"]
                summary_parts.append(f"Quality Score: {score:.2f}")
            
            # Add performance rating based on duration and success
            if success:
                if duration < 10:
                    summary_parts.append("⚡ Fast Completion")
                elif duration > 60:
                    summary_parts.append("🐌 Long Duration")
            
            if "error" in result_details:
                error = str(result_details["error"])[:50]
                if len(str(result_details["error"])) > 50:
                    error += "..."
                summary_parts.append(f"Error: {error}")
        
        return " | ".join(summary_parts)
    
    def log_autonomous_action(self, action: str, step: int, task_id: str, 
                            result: str = None, safety_check: Dict[str, Any] = None):
        """Log autonomous action with detailed context"""
        details = {
            "action": action,
            "step": step,
            "task_id": task_id,
            "timestamp": time.time()
        }
        
        if result:
            details["result"] = result
        if safety_check:
            details["safety_check"] = safety_check
        
        self.log_activity(
            ActivityType.AUTONOMOUS_ACTION,
            ActivityLevel.INFO,
            f"Autonomous Action Step {step}",
            f"Executed: {action}",
            details,
            parent_task_id=task_id
        )
    
    def log_ai_interaction(self, query: str, response: str, model: str, 
                          duration: float, task_id: str = None):
        """Log AI query and response"""
        # Log query
        self.log_activity(
            ActivityType.AI_QUERY,
            ActivityLevel.DEBUG,
            f"AI Query to {model}",
            query[:200] + "..." if len(query) > 200 else query,
            {
                "model": model,
                "query_length": len(query),
                "task_id": task_id
            },
            parent_task_id=task_id
        )
        
        # Log response
        self.log_activity(
            ActivityType.AI_RESPONSE,
            ActivityLevel.DEBUG,
            f"AI Response from {model}",
            response[:200] + "..." if len(response) > 200 else response,
            {
                "model": model,
                "response_length": len(response),
                "duration": duration,
                "task_id": task_id
            },
            duration=duration,
            parent_task_id=task_id
        )
    
    def log_safety_check(self, action: str, is_safe: bool, reason: str, task_id: str = None):
        """Log safety validation"""
        level = ActivityLevel.INFO if is_safe else ActivityLevel.WARNING
        
        self.log_activity(
            ActivityType.SAFETY_CHECK,
            level,
            f"Safety Check: {'PASSED' if is_safe else 'FAILED'}",
            f"Action: {action} | Reason: {reason}",
            {
                "action": action,
                "is_safe": is_safe,
                "reason": reason,
                "task_id": task_id
            },
            parent_task_id=task_id
        )
    
    def log_file_operation(self, operation: str, file_path: str, success: bool, details: Dict[str, Any] = None):
        """Log file operations"""
        level = ActivityLevel.INFO if success else ActivityLevel.ERROR
        
        self.log_activity(
            ActivityType.FILE_OPERATION,
            level,
            f"File {operation}: {'Success' if success else 'Failed'}",
            file_path,
            {
                "operation": operation,
                "file_path": file_path,
                "success": success,
                **(details or {})
            }
        )
    
    def log_screenshot(self, screenshot_path: str, purpose: str, task_id: str = None):
        """Log screenshot capture"""
        self.log_activity(
            ActivityType.SCREENSHOT,
            ActivityLevel.DEBUG,
            "Screenshot Captured",
            f"Purpose: {purpose}",
            {
                "screenshot_path": screenshot_path,
                "purpose": purpose,
                "task_id": task_id
            },
            parent_task_id=task_id
        )
    
    def get_recent_events(self, count: int = 100, 
                         activity_type: ActivityType = None,
                         level: ActivityLevel = None,
                         since: datetime = None) -> List[ActivityEvent]:
        """Get recent events with filtering"""
        with self.lock:
            events = list(self.events)
            
            # Apply filters
            if activity_type:
                events = [e for e in events if e.activity_type == activity_type]
            
            if level:
                events = [e for e in events if e.level == level]
            
            if since:
                since_timestamp = since.timestamp()
                events = [e for e in events if e.timestamp >= since_timestamp]
            
            # Sort by timestamp (most recent first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return events[:count]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get enhanced performance statistics and analysis"""
        with self.lock:
            stats = {}
            
            # Task performance metrics
            for task_type, durations in self.performance_metrics.items():
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    stats[task_type] = {
                        "count": len(durations),
                        "avg_duration": avg_duration,
                        "min_duration": min(durations),
                        "max_duration": max(durations),
                        "total_duration": sum(durations),
                        "performance_grade": self._calculate_performance_grade(avg_duration),
                        "success_rate": self._calculate_success_rate(task_type)
                    }
            
            # Activity analysis
            recent_events = list(self.events)[-100:] if len(self.events) > 100 else list(self.events)
            
            # Calculate task completion trends
            task_completions = [e for e in recent_events if e.activity_type == ActivityType.TASK_END]
            if task_completions:
                successful_tasks = [e for e in task_completions if e.details.get("success", False)]
                stats["recent_success_rate"] = len(successful_tasks) / len(task_completions) * 100
                
                # Average file generation
                files_generated = [e.details.get("generated_files_count", 0) for e in task_completions]
                stats["avg_files_per_task"] = sum(files_generated) / len(files_generated) if files_generated else 0
                
                # Auto-continue usage
                auto_continues = [e.details.get("continue_count", 0) for e in task_completions]
                stats["avg_auto_continues"] = sum(auto_continues) / len(auto_continues) if auto_continues else 0
            
            # Add event counters
            stats["event_counts"] = dict(self.event_counters)
            stats["active_tasks"] = len(self.active_tasks)
            stats["total_events"] = len(self.events)
            
            # System health indicators
            error_events = [e for e in recent_events if e.level in [ActivityLevel.ERROR, ActivityLevel.CRITICAL]]
            stats["recent_error_rate"] = len(error_events) / len(recent_events) * 100 if recent_events else 0
            
            # Activity frequency (events per minute over last hour)
            now = time.time()
            hour_ago = now - 3600
            recent_hour_events = [e for e in recent_events if e.timestamp >= hour_ago]
            stats["events_per_minute"] = len(recent_hour_events) / 60 if recent_hour_events else 0
            
            return stats
    
    def _calculate_performance_grade(self, avg_duration: float) -> str:
        """Calculate performance grade based on average task duration"""
        if avg_duration < 5:
            return "A+ (Excellent)"
        elif avg_duration < 15:
            return "A (Very Good)"
        elif avg_duration < 30:
            return "B (Good)"
        elif avg_duration < 60:
            return "C (Fair)"
        else:
            return "D (Slow)"
    
    def _calculate_success_rate(self, task_type: str) -> float:
        """Calculate success rate for a specific task type"""
        task_events = [e for e in self.events if 
                      e.activity_type == ActivityType.TASK_END and 
                      e.details.get("task_type") == task_type]
        
        if not task_events:
            return 0.0
        
        successful = [e for e in task_events if e.details.get("success", False)]
        return len(successful) / len(task_events) * 100
    
    def export_activity_log(self, output_path: Path, 
                           since: datetime = None, 
                           format: str = "json") -> bool:
        """Export activity log to file"""
        try:
            events = self.get_recent_events(count=len(self.events), since=since)
            
            if format.lower() == "json":
                data = {
                    "export_timestamp": time.time(),
                    "session_id": self.session_id,
                    "event_count": len(events),
                    "events": [asdict(event) for event in events]
                }
                
                with open(output_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif format.lower() == "csv":
                import csv
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow([
                        "Timestamp", "Event ID", "Activity Type", "Level",
                        "Title", "Description", "Duration", "Task ID"
                    ])
                    
                    # Events
                    for event in events:
                        writer.writerow([
                            datetime.fromtimestamp(event.timestamp).isoformat(),
                            event.event_id,
                            event.activity_type.value,
                            event.level.value,
                            event.title,
                            event.description,
                            event.duration or "",
                            event.parent_task_id or ""
                        ])
            
            self.log_activity(
                ActivityType.FILE_OPERATION,
                ActivityLevel.INFO,
                "Activity Log Exported",
                f"Exported {len(events)} events to {output_path}",
                {"output_path": str(output_path), "format": format, "event_count": len(events)}
            )
            
            return True
            
        except Exception as e:
            self.log_activity(
                ActivityType.ERROR_EVENT,
                ActivityLevel.ERROR,
                "Export Failed",
                f"Failed to export activity log: {e}",
                {"error": str(e), "output_path": str(output_path)}
            )
            return False

if PYQT_AVAILABLE:
    class ActivityMonitorWidget(QObject):
        """Real-time activity monitor widget for GUI"""
        
        activity_updated = pyqtSignal(ActivityEvent)
        
        def __init__(self, activity_logger: ActivityLogger):
            super().__init__()
            self.activity_logger = activity_logger
            self.activity_logger.add_listener(self.on_activity_event)
            
            # Setup refresh timer
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self.refresh_display)
            self.refresh_timer.start(1000)  # Refresh every second
        
        def on_activity_event(self, event: ActivityEvent):
            """Handle new activity event"""
            self.activity_updated.emit(event)
        
        def refresh_display(self):
            """Refresh the display periodically"""
            pass  # Can be overridden by subclasses
        
        def create_activity_view(self) -> QVBoxLayout:
            """Create the activity monitoring view"""
            layout = QVBoxLayout()
            
            # Controls
            controls_layout = QHBoxLayout()
            
            # Level filter
            self.level_filter = QComboBox()
            self.level_filter.addItems(["All Levels"] + [level.value for level in ActivityLevel])
            controls_layout.addWidget(QLabel("Level:"))
            controls_layout.addWidget(self.level_filter)
            
            # Type filter
            self.type_filter = QComboBox()
            self.type_filter.addItems(["All Types"] + [t.value for t in ActivityType])
            controls_layout.addWidget(QLabel("Type:"))
            controls_layout.addWidget(self.type_filter)
            
            # Search
            self.search_box = QLineEdit()
            self.search_box.setPlaceholderText("Search events...")
            controls_layout.addWidget(QLabel("Search:"))
            controls_layout.addWidget(self.search_box)
            
            # Clear button
            clear_btn = QPushButton("Clear")
            clear_btn.clicked.connect(self.clear_display)
            controls_layout.addWidget(clear_btn)
            
            layout.addLayout(controls_layout)
            
            # Activity display
            self.activity_display = QTextEdit()
            self.activity_display.setReadOnly(True)
            self.activity_display.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 10px;
                }
            """)
            layout.addWidget(self.activity_display)
            
            # Connect filters
            self.level_filter.currentTextChanged.connect(self.update_display)
            self.type_filter.currentTextChanged.connect(self.update_display)
            self.search_box.textChanged.connect(self.update_display)
            
            # Connect activity updates
            self.activity_updated.connect(self.append_activity)
            
            return layout
        
        def append_activity(self, event: ActivityEvent):
            """Append new activity to display"""
            # Format timestamp
            timestamp = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S.%f")[:-3]
            
            # Color coding
            color = {
                ActivityLevel.CRITICAL: "#ff4444",
                ActivityLevel.ERROR: "#ff6666",
                ActivityLevel.WARNING: "#ffaa44",
                ActivityLevel.INFO: "#44ff44",
                ActivityLevel.DEBUG: "#4444ff",
                ActivityLevel.TRACE: "#888888"
            }.get(event.level, "#ffffff")
            
            # Format message
            message = f'<span style="color: {color};">[{timestamp}] {event.level.value:8s} | {event.activity_type.value:20s} | {event.title}</span>'
            
            if event.description:
                message += f'<br><span style="color: #cccccc; margin-left: 20px;">└─ {event.description}</span>'
            
            # Add to display
            self.activity_display.append(message)
            
            # Auto-scroll to bottom
            scrollbar = self.activity_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        
        def update_display(self):
            """Update display with current filters"""
            # Get filtered events
            level_filter = self.level_filter.currentText()
            type_filter = self.type_filter.currentText()
            search_text = self.search_box.text().lower()
            
            # Apply filters
            level = None if level_filter == "All Levels" else ActivityLevel(level_filter)
            activity_type = None if type_filter == "All Types" else ActivityType(type_filter)
            
            events = self.activity_logger.get_recent_events(
                count=1000,
                level=level,
                activity_type=activity_type
            )
            
            # Apply search filter
            if search_text:
                events = [e for e in events if 
                         search_text in e.title.lower() or 
                         search_text in e.description.lower()]
            
            # Clear and repopulate
            self.activity_display.clear()
            
            # Reverse to show oldest first
            for event in reversed(events):
                self.append_activity(event)
        
        def clear_display(self):
            """Clear the activity display"""
            self.activity_display.clear()

# Global activity logger instance
_activity_logger = None

def get_activity_logger(log_dir: Path = None) -> ActivityLogger:
    """Get or create the global activity logger"""
    global _activity_logger
    
    if _activity_logger is None:
        if log_dir is None:
            log_dir = Path.home() / "SuperMini_Output" / "logs"
        _activity_logger = ActivityLogger(log_dir)
    
    return _activity_logger

def log_activity(activity_type: ActivityType, level: ActivityLevel, 
                title: str, description: str, details: Dict[str, Any] = None,
                duration: Optional[float] = None, parent_task_id: Optional[str] = None) -> str:
    """Convenience function for logging activities"""
    logger = get_activity_logger()
    return logger.log_activity(activity_type, level, title, description, details, duration, parent_task_id)