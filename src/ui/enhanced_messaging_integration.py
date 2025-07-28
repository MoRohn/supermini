"""
Enhanced Messaging Integration for SuperMini GUI
=================================================

This module provides seamless integration of the autonomous messaging framework
with the SuperMini PyQt6 GUI, enabling real-time message enhancement and
standardized user communication.

Key Features:
- Real-time message processing for GUI updates
- Asynchronous message enhancement without blocking UI
- Intelligent message type detection and routing
- Performance monitoring and adaptive processing
- Graceful fallback when AI enhancement is unavailable

Author: SuperMini AI Framework
Created: 2025-07-27
"""

import asyncio
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import QLabel, QProgressBar, QTextEdit

from ..core.autonomous_messaging import (
    AutonomousMessagingManager, 
    FormattedMessage, 
    MessageType,
    MessagePriority
)


class MessageEnhancementThread(QThread):
    """
    Qt thread for asynchronous message enhancement
    
    Handles autonomous message formatting in a separate thread to prevent
    GUI blocking while maintaining responsive user interface.
    """
    
    # Signals for communication with main GUI thread
    message_enhanced = pyqtSignal(object)  # FormattedMessage
    enhancement_failed = pyqtSignal(str)   # Error message
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal()
    
    def __init__(self, messaging_manager: AutonomousMessagingManager):
        super().__init__()
        self.messaging_manager = messaging_manager
        self.processing_queue = []
        self.is_processing = False
        self.stop_requested = False
        
    def enhance_message(self, content: str, message_type: str, context: Optional[Dict[str, Any]] = None):
        """Queue message for enhancement processing"""
        self.processing_queue.append({
            'content': content,
            'message_type': message_type,
            'context': context or {},
            'timestamp': time.time()
        })
        
        if not self.is_processing and not self.isRunning():
            self.start()
    
    def run(self):
        """Main thread execution loop"""
        self.is_processing = True
        self.processing_started.emit()
        
        # Set up event loop for async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            while self.processing_queue and not self.stop_requested:
                message_data = self.processing_queue.pop(0)
                
                try:
                    # Process message using async messaging manager
                    formatted_message = loop.run_until_complete(
                        self.messaging_manager.enhance_message(
                            content=message_data['content'],
                            message_type=message_data['message_type'],
                            context=message_data['context'],
                            priority="high"
                        )
                    )
                    
                    # Emit result to main GUI thread
                    self.message_enhanced.emit(formatted_message)
                    
                except Exception as e:
                    logging.error(f"Message enhancement failed: {e}")
                    self.enhancement_failed.emit(str(e))
                
                # Small delay to prevent overwhelming the system
                if not self.stop_requested:
                    self.msleep(100)  # 100ms delay
                    
        finally:
            loop.close()
            self.is_processing = False
            self.processing_finished.emit()
    
    def request_stop(self):
        """Request thread to stop processing"""
        self.stop_requested = True


class EnhancedMessageDisplay(QObject):
    """
    Enhanced message display component with autonomous formatting
    
    Provides intelligent message enhancement and display capabilities
    for SuperMini GUI components with real-time processing.
    """
    
    def __init__(self, messaging_manager: AutonomousMessagingManager, parent=None):
        super().__init__(parent)
        self.messaging_manager = messaging_manager
        self.enhancement_thread = MessageEnhancementThread(messaging_manager)
        
        # Connect enhancement thread signals
        self.enhancement_thread.message_enhanced.connect(self._handle_enhanced_message)
        self.enhancement_thread.enhancement_failed.connect(self._handle_enhancement_failure)
        
        # Display components cache
        self.display_components = {}
        
        # Performance tracking
        self.display_stats = {
            'messages_displayed': 0,
            'enhancements_success': 0,
            'enhancements_failed': 0,
            'avg_enhancement_time': 0.0
        }
        
        logging.info("EnhancedMessageDisplay initialized")
    
    def register_display_component(self, component_id: str, component):
        """Register GUI component for enhanced message display"""
        self.display_components[component_id] = component
        logging.info(f"Display component registered: {component_id}")
    
    def display_enhanced_message(self, 
                                content: str,
                                message_type: str = "task_result",
                                component_id: str = "default",
                                context: Optional[Dict[str, Any]] = None,
                                immediate: bool = False):
        """
        Display message with autonomous enhancement
        
        Args:
            content: Raw message content to enhance and display
            message_type: Type of message for specialized formatting
            component_id: ID of registered display component
            context: Additional context for enhancement
            immediate: If True, enhance synchronously (blocking)
        """
        if immediate:
            # Synchronous enhancement (may block UI briefly)
            self._display_message_sync(content, message_type, component_id, context)
        else:
            # Asynchronous enhancement (non-blocking)
            self._display_message_async(content, message_type, component_id, context)
    
    def _display_message_sync(self, content: str, message_type: str, component_id: str, context: Dict[str, Any]):
        """Display message with synchronous enhancement"""
        try:
            # Create event loop for sync operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            formatted_message = loop.run_until_complete(
                self.messaging_manager.enhance_message(
                    content=content,
                    message_type=message_type,
                    context=context,
                    priority="high"
                )
            )
            
            loop.close()
            
            # Display formatted message
            self._render_formatted_message(formatted_message, component_id)
            self.display_stats['enhancements_success'] += 1
            
        except Exception as e:
            logging.error(f"Synchronous message enhancement failed: {e}")
            self._display_fallback_message(content, component_id)
            self.display_stats['enhancements_failed'] += 1
    
    def _display_message_async(self, content: str, message_type: str, component_id: str, context: Dict[str, Any]):
        """Display message with asynchronous enhancement"""
        # Store component ID for later use
        context = context or {}
        context['component_id'] = component_id
        
        # Queue message for background enhancement
        self.enhancement_thread.enhance_message(content, message_type, context)
    
    def _handle_enhanced_message(self, formatted_message: FormattedMessage):
        """Handle enhanced message result from background thread"""
        try:
            # Extract component ID from context
            component_id = "default"
            if hasattr(formatted_message, 'technical_details'):
                # Try to extract component_id from context if stored in technical_details
                pass
            
            # Render the enhanced message
            self._render_formatted_message(formatted_message, component_id)
            self.display_stats['enhancements_success'] += 1
            
        except Exception as e:
            logging.error(f"Failed to display enhanced message: {e}")
            self.display_stats['enhancements_failed'] += 1
    
    def _handle_enhancement_failure(self, error_message: str):
        """Handle enhancement failure from background thread"""
        logging.warning(f"Message enhancement failed: {error_message}")
        self.display_stats['enhancements_failed'] += 1
        
        # Could display a fallback message or notification here
    
    def _render_formatted_message(self, formatted_message: FormattedMessage, component_id: str):
        """Render formatted message to specified GUI component"""
        component = self.display_components.get(component_id)
        if not component:
            logging.warning(f"Display component not found: {component_id}")
            return
        
        try:
            # Handle different component types
            if isinstance(component, QTextEdit):
                component.setHtml(formatted_message.html_content)
            elif isinstance(component, QLabel):
                component.setText(formatted_message.header)
            elif hasattr(component, 'setHtml'):
                component.setHtml(formatted_message.html_content)
            elif hasattr(component, 'setText'):
                component.setText(formatted_message.summary)
            else:
                logging.warning(f"Unsupported component type for {component_id}")
            
            self.display_stats['messages_displayed'] += 1
            
        except Exception as e:
            logging.error(f"Failed to render message to component {component_id}: {e}")
    
    def _display_fallback_message(self, content: str, component_id: str):
        """Display fallback message when enhancement fails"""
        component = self.display_components.get(component_id)
        if not component:
            return
        
        try:
            # Simple fallback display
            if isinstance(component, QTextEdit):
                component.setPlainText(content)
            elif isinstance(component, QLabel):
                component.setText(content[:100] + "..." if len(content) > 100 else content)
            elif hasattr(component, 'setText'):
                component.setText(content)
                
        except Exception as e:
            logging.error(f"Failed to display fallback message: {e}")
    
    def get_display_stats(self) -> Dict[str, Any]:
        """Get display performance statistics"""
        return self.display_stats.copy()
    
    def clear_stats(self):
        """Clear display statistics"""
        self.display_stats = {
            'messages_displayed': 0,
            'enhancements_success': 0,
            'enhancements_failed': 0,
            'avg_enhancement_time': 0.0
        }


class ProgressMessageEnhancer(QObject):
    """
    Specialized component for enhancing progress messages
    
    Provides real-time progress message enhancement with minimal latency
    and optimized performance for frequent updates.
    """
    
    # Signals for progress updates
    progress_enhanced = pyqtSignal(str, str)  # header, message
    
    def __init__(self, messaging_manager: AutonomousMessagingManager):
        super().__init__()
        self.messaging_manager = messaging_manager
        
        # Cache for recent progress messages
        self.progress_cache = {}
        self.cache_ttl = 10.0  # 10 seconds TTL for progress messages
        
    def enhance_progress_message(self, 
                                progress_info: Dict[str, Any],
                                use_cache: bool = True) -> None:
        """
        Enhance progress message with intelligent caching
        
        Args:
            progress_info: Progress information dictionary
            use_cache: Whether to use cached results for similar progress
        """
        message = progress_info.get('message', 'Processing...')
        percentage = progress_info.get('percentage', 0)
        
        # Create cache key based on message pattern and percentage range
        cache_key = f"{self._get_message_pattern(message)}:{percentage//10}"
        
        if use_cache and cache_key in self.progress_cache:
            cached_data, timestamp = self.progress_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                # Use cached enhanced message
                self.progress_enhanced.emit(cached_data['header'], cached_data['message'])
                return
        
        # Enhance message asynchronously
        threading.Thread(
            target=self._enhance_progress_async,
            args=(progress_info, cache_key),
            daemon=True
        ).start()
    
    def _enhance_progress_async(self, progress_info: Dict[str, Any], cache_key: str):
        """Enhance progress message in background thread"""
        try:
            # Set up async context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Enhance the message
            formatted_message = loop.run_until_complete(
                self.messaging_manager.enhance_progress_update(progress_info)
            )
            
            loop.close()
            
            # Cache the result
            self.progress_cache[cache_key] = (
                {
                    'header': formatted_message.header,
                    'message': formatted_message.summary
                },
                time.time()
            )
            
            # Emit the enhanced message
            self.progress_enhanced.emit(formatted_message.header, formatted_message.summary)
            
        except Exception as e:
            logging.error(f"Progress message enhancement failed: {e}")
            # Emit fallback message
            fallback_header = f"⚡ Progress: {progress_info.get('percentage', 0)}%"
            fallback_message = progress_info.get('message', 'Processing...')
            self.progress_enhanced.emit(fallback_header, fallback_message)
    
    def _get_message_pattern(self, message: str) -> str:
        """Extract pattern from message for intelligent caching"""
        # Remove numbers and specific details to create a pattern
        import re
        pattern = re.sub(r'\d+', 'N', message)
        pattern = re.sub(r'\b\w+\.(py|js|html|css|txt)\b', 'FILE', pattern)
        return pattern[:50]  # Limit pattern length


class TaskResultEnhancer(QObject):
    """
    Specialized component for enhancing task result messages
    
    Provides comprehensive task result enhancement with intelligent
    categorization and context-aware formatting.
    """
    
    # Signals for task result updates
    result_enhanced = pyqtSignal(object)  # FormattedMessage
    
    def __init__(self, messaging_manager: AutonomousMessagingManager):
        super().__init__()
        self.messaging_manager = messaging_manager
    
    def enhance_task_result(self, task_result, callback: Optional[Callable] = None):
        """
        Enhance task result with comprehensive formatting
        
        Args:
            task_result: TaskResult object to enhance
            callback: Optional callback for result handling
        """
        # Extract relevant information from task result
        context = {
            'task_type': getattr(task_result, 'task_type', 'unknown'),
            'execution_time': getattr(task_result, 'execution_time', 0.0),
            'success': getattr(task_result, 'success', True),
            'file_count': len(getattr(task_result, 'generated_files', [])),
            'total_size': self._calculate_total_size(getattr(task_result, 'generated_files', []))
        }
        
        # Enhance asynchronously
        threading.Thread(
            target=self._enhance_result_async,
            args=(task_result, context, callback),
            daemon=True
        ).start()
    
    def _enhance_result_async(self, task_result, context: Dict[str, Any], callback: Optional[Callable]):
        """Enhance task result in background thread"""
        try:
            # Set up async context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Enhance the task result
            formatted_message = loop.run_until_complete(
                self.messaging_manager.enhance_task_result(task_result)
            )
            
            loop.close()
            
            # Emit or callback with result
            if callback:
                callback(formatted_message)
            else:
                self.result_enhanced.emit(formatted_message)
                
        except Exception as e:
            logging.error(f"Task result enhancement failed: {e}")
            # Create fallback formatted message
            fallback_message = self._create_fallback_result(task_result, context)
            
            if callback:
                callback(fallback_message)
            else:
                self.result_enhanced.emit(fallback_message)
    
    def _calculate_total_size(self, file_paths: List[str]) -> str:
        """Calculate total size of generated files"""
        total_bytes = 0
        for file_path in file_paths:
            try:
                path_obj = Path(file_path)
                if path_obj.exists():
                    total_bytes += path_obj.stat().st_size
            except Exception:
                continue
        
        # Format size
        if total_bytes < 1024:
            return f"{total_bytes} B"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.1f} KB"
        else:
            return f"{total_bytes / (1024 * 1024):.1f} MB"
    
    def _create_fallback_result(self, task_result, context: Dict[str, Any]):
        """Create fallback formatted message for task result"""
        from ..core.autonomous_messaging import FormattedMessage, MessageType, MessagePriority
        from datetime import datetime
        
        success = context.get('success', True)
        header = "✅ Task Completed Successfully" if success else "❌ Task Failed"
        summary = f"Task executed in {context.get('execution_time', 0):.1f} seconds"
        
        bullet_points = [
            f"Task type: {context.get('task_type', 'unknown')}",
            f"Files generated: {context.get('file_count', 0)}",
            f"Total size: {context.get('total_size', '0 B')}"
        ]
        
        return FormattedMessage(
            header=header,
            bullet_points=bullet_points,
            summary=summary,
            action_items=[],
            technical_details=str(task_result),
            message_type=MessageType.TASK_RESULT,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            html_content=f"<div><h3>{header}</h3><p>{summary}</p></div>",
            processing_time=0.0,
            cache_key="",
            model_used="fallback"
        )


class MessagingIntegrationManager:
    """
    High-level manager for messaging integration with SuperMini GUI
    
    Provides unified interface for all autonomous messaging capabilities
    with seamless integration into existing GUI components.
    """
    
    def __init__(self, ollama_manager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize messaging integration manager
        
        Args:
            ollama_manager: OllamaManager instance for AI integration
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize core messaging components
        self.messaging_manager = AutonomousMessagingManager(ollama_manager, config)
        self.message_display = EnhancedMessageDisplay(self.messaging_manager)
        self.progress_enhancer = ProgressMessageEnhancer(self.messaging_manager)
        self.result_enhancer = TaskResultEnhancer(self.messaging_manager)
        
        # Integration settings
        self.auto_start_pipeline = config.get('auto_start_pipeline', True)
        self.enable_real_time = config.get('enable_real_time', True)
        
        # Performance monitoring
        self.integration_stats = {
            'total_messages': 0,
            'enhanced_messages': 0,
            'fallback_messages': 0,
            'avg_response_time': 0.0
        }
        
        logging.info("MessagingIntegrationManager initialized")
    
    async def initialize(self):
        """Initialize asynchronous components"""
        if self.auto_start_pipeline:
            await self.messaging_manager.start_real_time_processing()
        
        logging.info("Messaging integration fully initialized")
    
    def register_gui_component(self, component_id: str, component):
        """Register GUI component for enhanced messaging"""
        self.message_display.register_display_component(component_id, component)
    
    def enhance_task_result_display(self, task_result, component_id: str = "results"):
        """Enhance and display task result"""
        def display_callback(formatted_message):
            self.message_display._render_formatted_message(formatted_message, component_id)
        
        self.result_enhancer.enhance_task_result(task_result, display_callback)
        self.integration_stats['total_messages'] += 1
    
    def enhance_progress_display(self, progress_info: Dict[str, Any], progress_label: QLabel, status_label: QLabel):
        """Enhance and display progress information"""
        def progress_callback(header: str, message: str):
            progress_label.setText(header)
            status_label.setText(message)
        
        self.progress_enhancer.progress_enhanced.connect(progress_callback)
        self.progress_enhancer.enhance_progress_message(progress_info)
        self.integration_stats['total_messages'] += 1
    
    def enhance_error_display(self, error_info: Dict[str, Any], component_id: str = "results"):
        """Enhance and display error message"""
        self.message_display.display_enhanced_message(
            content=error_info.get('message', 'An error occurred'),
            message_type="error_message",
            component_id=component_id,
            context=error_info
        )
        self.integration_stats['total_messages'] += 1
    
    def enhance_status_display(self, status_info: Dict[str, Any], component_id: str = "status"):
        """Enhance and display system status"""
        self.message_display.display_enhanced_message(
            content=status_info.get('message', 'System status update'),
            message_type="system_status",
            component_id=component_id,
            context=status_info
        )
        self.integration_stats['total_messages'] += 1
    
    async def enhance_message(self, 
                            content: str,
                            message_type: str = "task_result",
                            context: Optional[Dict[str, Any]] = None,
                            priority: str = "normal",
                            use_cache: bool = True):
        """
        Enhance message with autonomous formatting (direct interface)
        
        Args:
            content: Raw message content
            message_type: Type of message ("task_result", "error_message", etc.)
            context: Additional context information
            priority: Processing priority ("critical", "high", "normal", "low")
            use_cache: Whether to use cached results
            
        Returns:
            FormattedMessage: Autonomously enhanced message
        """
        return await self.messaging_manager.enhance_message(
            content=content,
            message_type=message_type,
            context=context,
            priority=priority,
            use_cache=use_cache
        )
    
    async def enhance_error_message(self, error_info: Dict[str, Any]):
        """Enhance error message with helpful guidance (direct interface)"""
        return await self.messaging_manager.enhance_error_message(error_info)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all messaging components"""
        return {
            'integration_stats': self.integration_stats,
            'messaging_manager_stats': self.messaging_manager.get_comprehensive_stats(),
            'display_stats': self.message_display.get_display_stats(),
            'settings': {
                'auto_start_pipeline': self.auto_start_pipeline,
                'enable_real_time': self.enable_real_time
            }
        }
    
    async def shutdown(self):
        """Shutdown messaging integration gracefully"""
        await self.messaging_manager.stop_real_time_processing()
        
        # Stop enhancement threads
        if hasattr(self.message_display.enhancement_thread, 'request_stop'):
            self.message_display.enhancement_thread.request_stop()
        
        logging.info("Messaging integration shutdown complete")
    
    def configure_messaging(self, **settings):
        """Configure messaging system settings"""
        self.messaging_manager.configure(**settings)
        
        # Update local settings
        for key, value in settings.items():
            if key in ['auto_start_pipeline', 'enable_real_time']:
                setattr(self, key, value)
        
        logging.info(f"Messaging integration configured with: {settings}")


# Convenience functions for easy integration

def create_messaging_integration(ollama_manager, config: Optional[Dict[str, Any]] = None) -> MessagingIntegrationManager:
    """
    Create and initialize messaging integration manager
    
    Args:
        ollama_manager: OllamaManager instance
        config: Optional configuration dictionary
        
    Returns:
        MessagingIntegrationManager: Fully configured messaging integration
    """
    return MessagingIntegrationManager(ollama_manager, config)


def enhance_gui_component_messaging(gui_component, messaging_integration: MessagingIntegrationManager, component_id: str):
    """
    Enhance a GUI component with autonomous messaging capabilities
    
    Args:
        gui_component: PyQt6 widget to enhance
        messaging_integration: MessagingIntegrationManager instance
        component_id: Unique identifier for the component
    """
    messaging_integration.register_gui_component(component_id, gui_component)
    
    # Add enhancement method to component
    def display_enhanced_message(content: str, message_type: str = "task_result", context: Optional[Dict[str, Any]] = None):
        messaging_integration.message_display.display_enhanced_message(
            content=content,
            message_type=message_type,
            component_id=component_id,
            context=context
        )
    
    gui_component.display_enhanced_message = display_enhanced_message
    
    logging.info(f"GUI component enhanced with autonomous messaging: {component_id}")


# Example usage patterns for different message types

EXAMPLE_USAGE = """
# Initialize messaging integration
messaging = create_messaging_integration(ollama_manager)
await messaging.initialize()

# Register GUI components
messaging.register_gui_component("results", results_text_widget)
messaging.register_gui_component("progress", progress_label)
messaging.register_gui_component("status", status_bar)

# Enhance task result display
messaging.enhance_task_result_display(task_result, "results")

# Enhance progress updates
progress_info = {"percentage": 75, "message": "Processing files...", "eta": "30 seconds"}
messaging.enhance_progress_display(progress_info, progress_label, status_label)

# Enhance error messages
error_info = {"message": "Connection failed", "type": "network", "context": "api_call"}
messaging.enhance_error_display(error_info, "results")

# Get comprehensive statistics
stats = messaging.get_comprehensive_stats()
print(f"Messages enhanced: {stats['integration_stats']['enhanced_messages']}")
"""