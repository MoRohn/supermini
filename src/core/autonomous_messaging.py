"""
Autonomous Transparent Messaging Framework
==========================================

This module provides autonomous message formatting using Ollama models to create
clean, standardized, bulleted outlines with headers for all user-facing messages.

Key Features:
- Real-time message enhancement using local AI models
- Standardized output formats with professional headers
- Intelligent message type detection and routing
- Caching system for performance optimization
- Graceful fallback when formatting fails

Author: SuperMini AI Framework
Created: 2025-07-27
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import hashlib
import re

try:
    import aiohttp
    ASYNC_HTTP_AVAILABLE = True
except ImportError:
    ASYNC_HTTP_AVAILABLE = False


class MessageType(Enum):
    """Enumeration of message types for specialized formatting"""
    TASK_RESULT = "task_result"
    PROGRESS_UPDATE = "progress_update"
    ERROR_MESSAGE = "error_message"
    FILE_SUMMARY = "file_summary"
    SYSTEM_STATUS = "system_status"
    ENHANCEMENT_RESULT = "enhancement_result"
    AUTONOMOUS_ACTION = "autonomous_action"


class MessagePriority(Enum):
    """Message processing priority levels"""
    CRITICAL = "critical"  # Immediate processing required
    HIGH = "high"         # Process within 1 second
    NORMAL = "normal"     # Process within 3 seconds
    LOW = "low"          # Process when resources available


@dataclass
class FormattedMessage:
    """
    Data structure for autonomously formatted messages
    
    This class represents the result of AI-enhanced message formatting,
    providing structured, user-friendly content with standardized formatting.
    """
    header: str                    # Clean, professional header with emoji
    bullet_points: List[str]      # Structured bullet point list
    summary: str                  # Concise one-line summary
    action_items: List[str]       # Next steps or recommendations
    technical_details: str        # Detailed technical information
    message_type: MessageType     # Type classification for routing
    priority: MessagePriority     # Processing priority level
    timestamp: datetime           # Creation timestamp
    html_content: str            # Pre-formatted HTML for GUI display
    processing_time: float       # Time taken to format message
    cache_key: str              # Unique key for caching
    model_used: str             # AI model used for formatting
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['message_type'] = self.message_type.value
        result['priority'] = self.priority.value
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormattedMessage':
        """Create instance from dictionary"""
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = MessagePriority(data['priority'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class MessageCache:
    """
    High-performance caching system for formatted messages
    
    Provides intelligent caching with LRU eviction and content-based keys
    to optimize repeated message formatting operations.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[FormattedMessage, float]] = {}
        self.access_times: Dict[str, float] = {}
        
    def _generate_cache_key(self, content: str, message_type: MessageType) -> str:
        """Generate unique cache key based on content and type"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{message_type.value}:{content_hash[:16]}"
    
    def get(self, content: str, message_type: MessageType) -> Optional[FormattedMessage]:
        """Retrieve cached formatted message if available and valid"""
        cache_key = self._generate_cache_key(content, message_type)
        
        if cache_key in self.cache:
            message, timestamp = self.cache[cache_key]
            
            # Check if cache entry is still valid
            if time.time() - timestamp < self.ttl_seconds:
                self.access_times[cache_key] = time.time()
                return message
            else:
                # Remove expired entry
                del self.cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]
        
        return None
    
    def put(self, content: str, message_type: MessageType, formatted_message: FormattedMessage):
        """Store formatted message in cache"""
        cache_key = self._generate_cache_key(content, message_type)
        
        # Evict oldest entries if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        formatted_message.cache_key = cache_key
        self.cache[cache_key] = (formatted_message, time.time())
        self.access_times[cache_key] = time.time()
    
    def _evict_lru(self):
        """Evict least recently used cache entries"""
        if not self.access_times:
            return
            
        # Find and remove 10% of oldest entries
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        evict_count = max(1, len(sorted_keys) // 10)
        
        for cache_key, _ in sorted_keys[:evict_count]:
            if cache_key in self.cache:
                del self.cache[cache_key]
            if cache_key in self.access_times:
                del self.access_times[cache_key]
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        self.access_times.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'hit_rate': getattr(self, '_hit_rate', 0.0)
        }


class MessageFormatter:
    """
    Autonomous message formatting using Ollama models
    
    This class provides intelligent message enhancement by using local AI models
    to transform raw technical output into clean, standardized, user-friendly formats.
    """
    
    def __init__(self, ollama_manager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize MessageFormatter with Ollama integration
        
        Args:
            ollama_manager: OllamaManager instance for AI model access
            config: Optional configuration dictionary
        """
        self.ollama = ollama_manager
        self.config = config or {}
        self.cache = MessageCache(
            max_size=self.config.get('cache_size', 1000),
            ttl_seconds=self.config.get('cache_ttl', 3600)
        )
        
        # Performance tracking
        self.stats = {
            'messages_formatted': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_processing_time': 0.0,
            'total_processing_time': 0.0,
            'errors': 0
        }
        
        # Initialize specialized prompts
        self.formatting_prompts = self._initialize_prompts()
        
        # Fallback formatting templates
        self.fallback_templates = self._initialize_fallback_templates()
        
        logging.info("MessageFormatter initialized with autonomous formatting capabilities")
    
    def _initialize_prompts(self) -> Dict[MessageType, str]:
        """Initialize specialized formatting prompts for different message types"""
        return {
            MessageType.TASK_RESULT: """
Transform this AI task result into a clean, professional summary with structured formatting.

Requirements:
- Create a clear header with appropriate emoji and status
- List 3-5 key accomplishments as bullet points
- Include performance metrics if available
- Keep technical details minimal and user-friendly
- Use consistent formatting with headers and sections
- Be concise but informative

Raw Content: {content}
Task Type: {task_type}
Execution Time: {execution_time}
Files Generated: {file_count}

Format as:
Header: [Status with emoji]
Summary: [One-line summary]
Bullet Points: [Key accomplishments]
Performance: [Metrics if available]

Return only the formatted content, no explanations.
""",
            
            MessageType.PROGRESS_UPDATE: """
Create a clean progress update with structured formatting.

Requirements:
- Clear progress indicator with percentage or status
- Current step and next action
- Time estimates if available
- Encouraging and professional tone
- Use bullet points for multiple items

Raw Content: {content}
Progress Percentage: {progress}
Current Step: {current_step}

Format as structured progress update with clear headers and bullet points.
Return only the formatted content.
""",
            
            MessageType.ERROR_MESSAGE: """
Transform this error into a user-friendly message with clear action steps.

Requirements:
- Clear problem statement with appropriate emoji
- List of specific issues found
- Recommended actions as bullet points
- Hide technical jargon, focus on solutions
- Encouraging tone suggesting next steps

Raw Error: {content}
Error Type: {error_type}
Context: {context}

Format as:
Header: [Problem description with emoji]
Issues: [Key problems as bullets]
Solutions: [Action steps as bullets]

Return only the formatted content, be helpful and solution-focused.
""",
            
            MessageType.FILE_SUMMARY: """
Create a professional file summary with clear organization.

Requirements:
- List files with descriptions and sizes
- Group by file type if multiple types
- Include creation time and purpose
- Use emojis for file types
- Keep descriptions concise but informative

Raw Content: {content}
File Count: {file_count}
Total Size: {total_size}

Format as organized file listing with headers and bullet points.
Return only the formatted content.
""",
            
            MessageType.SYSTEM_STATUS: """
Format system status information clearly and professionally.

Requirements:
- Clear status indicators with emojis
- Key metrics as bullet points
- Resource usage information
- Any alerts or recommendations
- Use color-coding concepts (green/yellow/red)

Raw Content: {content}
System Load: {system_load}
Memory Usage: {memory_usage}

Format as status dashboard with clear headers and indicators.
Return only the formatted content.
""",
            
            MessageType.ENHANCEMENT_RESULT: """
Present enhancement results with impact focus.

Requirements:
- Clear summary of improvements made
- Impact metrics and benefits
- List of changes as bullet points
- Performance improvements highlighted
- Professional and accomplishment-focused tone

Raw Content: {content}
Enhancement Type: {enhancement_type}
Impact Score: {impact_score}

Format as improvement summary with clear headers and benefits.
Return only the formatted content.
""",
            
            MessageType.AUTONOMOUS_ACTION: """
Present autonomous actions clearly with transparency.

Requirements:
- Clear description of action taken
- Reasoning behind the action
- Results and outcomes
- Next steps if applicable
- Transparent but reassuring tone

Raw Content: {content}
Action Type: {action_type}
Confidence: {confidence}

Format as autonomous action report with clear transparency.
Return only the formatted content.
"""
        }
    
    def _initialize_fallback_templates(self) -> Dict[MessageType, str]:
        """Initialize fallback templates when AI formatting fails"""
        return {
            MessageType.TASK_RESULT: """
✅ Task Completed
═══════════════════════════════════════

📋 Result Summary
• Task executed successfully
• Processing completed

📊 Details
{content}
""",
            
            MessageType.ERROR_MESSAGE: """
❌ Error Occurred
═══════════════════════════════════════

🔍 Issue Details
• An error was encountered during execution

🛠️ Error Information
{content}
""",
            
            MessageType.PROGRESS_UPDATE: """
⚡ Progress Update
═══════════════════════════════════════

📈 Current Status
• Task in progress
• Processing continues

📋 Details
{content}
""",
        }
    
    async def format_message(self, 
                           content: str, 
                           message_type: MessageType,
                           context: Optional[Dict[str, Any]] = None,
                           priority: MessagePriority = MessagePriority.NORMAL) -> FormattedMessage:
        """
        Autonomously format a message using AI enhancement
        
        Args:
            content: Raw message content to format
            message_type: Type of message for specialized formatting
            context: Additional context information
            priority: Processing priority level
            
        Returns:
            FormattedMessage: AI-enhanced formatted message
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cached_message = self.cache.get(content, message_type)
            if cached_message:
                self.stats['cache_hits'] += 1
                return cached_message
            
            self.stats['cache_misses'] += 1
            
            # Prepare formatting context
            format_context = context or {}
            format_context.update({
                'content': content,
                'message_type': message_type.value,
                'timestamp': datetime.now().isoformat()
            })
            
            # Get appropriate prompt template
            prompt_template = self.formatting_prompts.get(message_type)
            if not prompt_template:
                return self._create_fallback_message(content, message_type, start_time)
            
            # Format prompt with context
            try:
                formatted_prompt = prompt_template.format(**format_context)
            except KeyError as e:
                logging.warning(f"Missing context key for formatting: {e}")
                formatted_prompt = prompt_template.replace('{content}', content)
            
            # Query Ollama for AI enhancement
            model_used = "qwen2.5-coder:7b"  # Primary model for technical content
            enhanced_content = self.ollama.query(formatted_prompt)
            
            if not enhanced_content:
                # Try fallback model
                model_used = "llama3.2:3b"
                enhanced_content = self.ollama.query(formatted_prompt)
            
            if not enhanced_content:
                return self._create_fallback_message(content, message_type, start_time)
            
            # Parse and structure the enhanced content
            formatted_message = self._parse_enhanced_content(
                enhanced_content, 
                content, 
                message_type, 
                priority,
                model_used,
                start_time
            )
            
            # Cache the result
            self.cache.put(content, message_type, formatted_message)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            return formatted_message
            
        except Exception as e:
            logging.error(f"Message formatting failed: {e}")
            self.stats['errors'] += 1
            return self._create_fallback_message(content, message_type, start_time)
    
    def _parse_enhanced_content(self, 
                              enhanced_content: str,
                              original_content: str,
                              message_type: MessageType,
                              priority: MessagePriority,
                              model_used: str,
                              start_time: float) -> FormattedMessage:
        """Parse AI-enhanced content into structured FormattedMessage"""
        
        # Extract structured components using regex patterns
        header_match = re.search(r'Header:\s*(.+?)(?:\n|$)', enhanced_content, re.IGNORECASE)
        summary_match = re.search(r'Summary:\s*(.+?)(?:\n|$)', enhanced_content, re.IGNORECASE)
        
        # Extract bullet points
        bullet_points = []
        bullet_pattern = r'[•·▪▫‣⁃]\s*(.+?)(?:\n|$)'
        for match in re.finditer(bullet_pattern, enhanced_content):
            bullet_points.append(match.group(1).strip())
        
        # If structured parsing fails, use intelligent content splitting
        if not header_match and not bullet_points:
            lines = enhanced_content.strip().split('\n')
            header = lines[0] if lines else "📋 Information"
            bullet_points = [line.strip() for line in lines[1:] if line.strip()]
        else:
            header = header_match.group(1) if header_match else "📋 Information"
        
        summary = summary_match.group(1) if summary_match else bullet_points[0] if bullet_points else "Information processed"
        
        # Extract action items (lines starting with action words)
        action_items = []
        action_pattern = r'(?:Next|Action|Recommend|Try|Consider|Check):\s*(.+?)(?:\n|$)'
        for match in re.finditer(action_pattern, enhanced_content, re.IGNORECASE):
            action_items.append(match.group(1).strip())
        
        # Generate HTML content
        html_content = self._generate_html_content(header, bullet_points, summary, action_items, original_content)
        
        return FormattedMessage(
            header=header,
            bullet_points=bullet_points,
            summary=summary,
            action_items=action_items,
            technical_details=original_content,
            message_type=message_type,
            priority=priority,
            timestamp=datetime.now(),
            html_content=html_content,
            processing_time=time.time() - start_time,
            cache_key="",  # Will be set by cache
            model_used=model_used
        )
    
    def _generate_html_content(self, 
                             header: str,
                             bullet_points: List[str],
                             summary: str,
                             action_items: List[str],
                             technical_details: str) -> str:
        """Generate HTML content for GUI display"""
        
        html_parts = [
            f'<div style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif; line-height: 1.6;">',
            f'<div style="background: linear-gradient(135deg, #4CAF50 0%, #059669 100%); color: white; padding: 16px; border-radius: 8px; margin-bottom: 16px;">',
            f'<h2 style="margin: 0; font-size: 18px; font-weight: 600;">{header}</h2>',
            f'<p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;">{summary}</p>',
            f'</div>'
        ]
        
        if bullet_points:
            html_parts.extend([
                f'<div style="background-color: #f8f9fa; padding: 16px; border-radius: 6px; border-left: 4px solid #4CAF50; margin-bottom: 16px;">',
                f'<h3 style="color: #059669; margin-top: 0; margin-bottom: 12px; font-size: 16px;">📋 Key Points</h3>',
                f'<ul style="margin: 0; padding-left: 20px;">'
            ])
            
            for point in bullet_points:
                html_parts.append(f'<li style="margin: 6px 0; color: #2d3748;">{point}</li>')
            
            html_parts.extend(['</ul>', '</div>'])
        
        if action_items:
            html_parts.extend([
                f'<div style="background-color: #fff3cd; padding: 16px; border-radius: 6px; border-left: 4px solid #ffc107; margin-bottom: 16px;">',
                f'<h3 style="color: #856404; margin-top: 0; margin-bottom: 12px; font-size: 16px;">⚡ Next Steps</h3>',
                f'<ul style="margin: 0; padding-left: 20px;">'
            ])
            
            for item in action_items:
                html_parts.append(f'<li style="margin: 6px 0; color: #856404;">{item}</li>')
            
            html_parts.extend(['</ul>', '</div>'])
        
        # Collapsible technical details
        if technical_details and len(technical_details) > 100:
            html_parts.extend([
                f'<details style="background-color: #f1f3f4; padding: 12px; border-radius: 6px; margin-top: 16px;">',
                f'<summary style="cursor: pointer; font-weight: 600; color: #5f6368;">🔧 Technical Details</summary>',
                f'<pre style="background-color: #ffffff; padding: 12px; border-radius: 4px; margin-top: 8px; overflow-x: auto; font-size: 12px; border: 1px solid #dadce0;">{technical_details}</pre>',
                f'</details>'
            ])
        
        html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _create_fallback_message(self, 
                               content: str,
                               message_type: MessageType,
                               start_time: float) -> FormattedMessage:
        """Create fallback message when AI formatting fails"""
        
        template = self.fallback_templates.get(message_type, self.fallback_templates[MessageType.TASK_RESULT])
        
        # Simple content parsing for fallback
        lines = content.strip().split('\n')
        header = "📋 Information"
        bullet_points = [line.strip() for line in lines if line.strip()]
        summary = lines[0] if lines else "Information processed"
        
        html_content = template.format(content=content)
        
        return FormattedMessage(
            header=header,
            bullet_points=bullet_points,
            summary=summary,
            action_items=[],
            technical_details=content,
            message_type=message_type,
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            html_content=html_content,
            processing_time=time.time() - start_time,
            cache_key="",
            model_used="fallback"
        )
    
    def _update_stats(self, processing_time: float):
        """Update performance statistics"""
        self.stats['messages_formatted'] += 1
        self.stats['total_processing_time'] += processing_time
        self.stats['avg_processing_time'] = (
            self.stats['total_processing_time'] / self.stats['messages_formatted']
        )
    
    async def format_task_result(self, task_result) -> FormattedMessage:
        """Format a TaskResult object with specialized handling"""
        context = {
            'task_type': getattr(task_result, 'task_type', 'unknown'),
            'execution_time': getattr(task_result, 'execution_time', 0.0),
            'file_count': len(getattr(task_result, 'generated_files', []))
        }
        
        content = getattr(task_result, 'result', str(task_result))
        
        return await self.format_message(
            content=content,
            message_type=MessageType.TASK_RESULT,
            context=context,
            priority=MessagePriority.HIGH
        )
    
    async def format_progress_update(self, progress_info: Dict[str, Any]) -> FormattedMessage:
        """Format progress update with real-time enhancement"""
        context = {
            'progress': progress_info.get('percentage', 0),
            'current_step': progress_info.get('current_step', 'Processing'),
            'eta': progress_info.get('eta', 'Unknown')
        }
        
        content = progress_info.get('message', 'Task in progress')
        
        return await self.format_message(
            content=content,
            message_type=MessageType.PROGRESS_UPDATE,
            context=context,
            priority=MessagePriority.HIGH
        )
    
    async def format_error_message(self, error_info: Dict[str, Any]) -> FormattedMessage:
        """Format error messages with helpful guidance"""
        context = {
            'error_type': error_info.get('type', 'unknown'),
            'context': error_info.get('context', 'general')
        }
        
        content = error_info.get('message', str(error_info))
        
        return await self.format_message(
            content=content,
            message_type=MessageType.ERROR_MESSAGE,
            context=context,
            priority=MessagePriority.CRITICAL
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive formatting statistics"""
        cache_stats = self.cache.stats()
        hit_rate = 0.0
        if self.stats['cache_hits'] + self.stats['cache_misses'] > 0:
            hit_rate = self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses'])
        
        return {
            **self.stats,
            'cache_hit_rate': hit_rate,
            'cache_stats': cache_stats
        }
    
    def clear_cache(self):
        """Clear message formatting cache"""
        self.cache.clear()
        logging.info("Message formatting cache cleared")
    
    def is_available(self) -> bool:
        """Check if message formatting is available"""
        return self.ollama is not None


class MessagePipeline:
    """
    Real-time message processing and enhancement pipeline
    
    Provides high-performance, asynchronous message processing with intelligent
    queuing, priority handling, and batch optimization capabilities.
    """
    
    def __init__(self, formatter: MessageFormatter, max_queue_size: int = 100):
        """
        Initialize message processing pipeline
        
        Args:
            formatter: MessageFormatter instance for AI enhancement
            max_queue_size: Maximum number of queued messages
        """
        self.formatter = formatter
        self.max_queue_size = max_queue_size
        self.processing_queue = asyncio.Queue(maxsize=max_queue_size)
        self.priority_queue = asyncio.PriorityQueue()
        self.is_running = False
        self.worker_tasks = []
        
        # Performance tracking
        self.pipeline_stats = {
            'messages_processed': 0,
            'queue_overflows': 0,
            'avg_queue_time': 0.0,
            'total_queue_time': 0.0
        }
        
        logging.info("MessagePipeline initialized for real-time processing")
    
    async def start(self, num_workers: int = 3):
        """Start the message processing pipeline"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start worker tasks for parallel processing
        for i in range(num_workers):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.worker_tasks.append(task)
        
        logging.info(f"MessagePipeline started with {num_workers} workers")
    
    async def stop(self):
        """Stop the message processing pipeline"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        logging.info("MessagePipeline stopped")
    
    async def _worker_loop(self, worker_id: str):
        """Main worker loop for processing messages"""
        logging.info(f"Message worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get next message from priority queue with timeout
                try:
                    priority_item = await asyncio.wait_for(
                        self.priority_queue.get(), 
                        timeout=1.0
                    )
                    priority, queue_time, message_data = priority_item
                    
                except asyncio.TimeoutError:
                    continue
                
                # Process the message
                await self._process_message_item(message_data, queue_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker {worker_id} error: {e}")
        
        logging.info(f"Message worker {worker_id} stopped")
    
    async def _process_message_item(self, message_data: Dict[str, Any], queue_time: float):
        """Process individual message item"""
        try:
            content = message_data['content']
            message_type = message_data['message_type']
            context = message_data.get('context', {})
            callback = message_data.get('callback')
            
            # Format the message
            formatted_message = await self.formatter.format_message(
                content=content,
                message_type=message_type,
                context=context
            )
            
            # Update pipeline statistics
            queue_wait_time = time.time() - queue_time
            self._update_pipeline_stats(queue_wait_time)
            
            # Execute callback if provided
            if callback:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(formatted_message)
                    else:
                        callback(formatted_message)
                except Exception as e:
                    logging.error(f"Message callback failed: {e}")
            
        except Exception as e:
            logging.error(f"Message processing failed: {e}")
    
    async def submit_message(self, 
                           content: str,
                           message_type: MessageType,
                           context: Optional[Dict[str, Any]] = None,
                           priority: MessagePriority = MessagePriority.NORMAL,
                           callback: Optional[callable] = None) -> bool:
        """
        Submit message for asynchronous processing
        
        Args:
            content: Raw message content
            message_type: Type of message for specialized formatting
            context: Additional context information
            priority: Processing priority level
            callback: Optional callback function for result
            
        Returns:
            bool: True if message was queued, False if queue is full
        """
        if not self.is_running:
            await self.start()
        
        # Check queue capacity
        if self.priority_queue.qsize() >= self.max_queue_size:
            self.pipeline_stats['queue_overflows'] += 1
            logging.warning("Message queue overflow, dropping message")
            return False
        
        # Create message data
        message_data = {
            'content': content,
            'message_type': message_type,
            'context': context,
            'callback': callback
        }
        
        # Convert priority to numeric value for queue ordering
        priority_value = {
            MessagePriority.CRITICAL: 0,
            MessagePriority.HIGH: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.LOW: 3
        }.get(priority, 2)
        
        # Add to priority queue
        await self.priority_queue.put((priority_value, time.time(), message_data))
        return True
    
    async def process_message_stream(self, message_stream, callback: callable):
        """Process stream of messages with real-time formatting"""
        async for message in message_stream:
            await self.submit_message(
                content=message.get('content', ''),
                message_type=MessageType(message.get('type', 'task_result')),
                context=message.get('context'),
                priority=MessagePriority(message.get('priority', 'normal')),
                callback=callback
            )
    
    async def batch_enhance_messages(self, messages: List[Dict[str, Any]]) -> List[FormattedMessage]:
        """Process multiple messages in batch with optimization"""
        results = []
        
        # Group messages by type for batch optimization
        type_groups = {}
        for msg in messages:
            msg_type = msg.get('message_type', MessageType.TASK_RESULT)
            if msg_type not in type_groups:
                type_groups[msg_type] = []
            type_groups[msg_type].append(msg)
        
        # Process each group
        for message_type, group_messages in type_groups.items():
            for msg_data in group_messages:
                formatted_message = await self.formatter.format_message(
                    content=msg_data['content'],
                    message_type=message_type,
                    context=msg_data.get('context', {}),
                    priority=MessagePriority.LOW  # Batch processing is low priority
                )
                results.append(formatted_message)
        
        return results
    
    def _update_pipeline_stats(self, queue_wait_time: float):
        """Update pipeline performance statistics"""
        self.pipeline_stats['messages_processed'] += 1
        self.pipeline_stats['total_queue_time'] += queue_wait_time
        self.pipeline_stats['avg_queue_time'] = (
            self.pipeline_stats['total_queue_time'] / 
            self.pipeline_stats['messages_processed']
        )
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        return {
            **self.pipeline_stats,
            'queue_size': self.priority_queue.qsize(),
            'max_queue_size': self.max_queue_size,
            'is_running': self.is_running,
            'active_workers': len(self.worker_tasks)
        }


class AutonomousMessagingManager:
    """
    High-level manager for autonomous transparent messaging
    
    Provides a unified interface for autonomous message formatting with
    intelligent fallback, performance optimization, and seamless integration.
    """
    
    def __init__(self, ollama_manager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize autonomous messaging manager
        
        Args:
            ollama_manager: OllamaManager instance for AI integration
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.formatter = MessageFormatter(ollama_manager, config)
        self.pipeline = MessagePipeline(self.formatter, 
                                      max_queue_size=config.get('queue_size', 100))
        
        # Settings
        self.autonomous_enabled = config.get('autonomous_enabled', True)
        self.fallback_on_error = config.get('fallback_on_error', True)
        self.real_time_processing = config.get('real_time_processing', True)
        
        logging.info("AutonomousMessagingManager initialized")
    
    async def enhance_message(self, 
                            content: str,
                            message_type: str = "task_result",
                            context: Optional[Dict[str, Any]] = None,
                            priority: str = "normal",
                            use_cache: bool = True) -> FormattedMessage:
        """
        Enhance message with autonomous formatting
        
        Args:
            content: Raw message content
            message_type: Type of message ("task_result", "error_message", etc.)
            context: Additional context information
            priority: Processing priority ("critical", "high", "normal", "low")
            use_cache: Whether to use cached results
            
        Returns:
            FormattedMessage: Autonomously enhanced message
        """
        if not self.autonomous_enabled:
            return self._create_simple_message(content, message_type)
        
        try:
            # Convert string enums to proper types
            msg_type = MessageType(message_type)
            msg_priority = MessagePriority(priority)
            
            # Format message using AI enhancement
            formatted_message = await self.formatter.format_message(
                content=content,
                message_type=msg_type,
                context=context,
                priority=msg_priority
            )
            
            return formatted_message
            
        except Exception as e:
            logging.error(f"Autonomous message enhancement failed: {e}")
            
            if self.fallback_on_error:
                return self._create_simple_message(content, message_type)
            else:
                raise
    
    async def enhance_task_result(self, task_result) -> FormattedMessage:
        """Enhance TaskResult with specialized formatting"""
        return await self.formatter.format_task_result(task_result)
    
    async def enhance_progress_update(self, progress_info: Dict[str, Any]) -> FormattedMessage:
        """Enhance progress update with real-time formatting"""
        return await self.formatter.format_progress_update(progress_info)
    
    async def enhance_error_message(self, error_info: Dict[str, Any]) -> FormattedMessage:
        """Enhance error message with helpful guidance"""
        return await self.formatter.format_error_message(error_info)
    
    def _create_simple_message(self, content: str, message_type: str) -> FormattedMessage:
        """Create simple fallback message without AI enhancement"""
        return FormattedMessage(
            header=f"📋 {message_type.replace('_', ' ').title()}",
            bullet_points=[content],
            summary=content[:100] + "..." if len(content) > 100 else content,
            action_items=[],
            technical_details=content,
            message_type=MessageType(message_type),
            priority=MessagePriority.NORMAL,
            timestamp=datetime.now(),
            html_content=f"<div>{content}</div>",
            processing_time=0.0,
            cache_key="",
            model_used="fallback"
        )
    
    async def start_real_time_processing(self):
        """Start real-time message processing pipeline"""
        if self.real_time_processing:
            await self.pipeline.start()
    
    async def stop_real_time_processing(self):
        """Stop real-time message processing pipeline"""
        await self.pipeline.stop()
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics for the messaging system"""
        return {
            'formatter_stats': self.formatter.get_stats(),
            'pipeline_stats': self.pipeline.get_pipeline_stats(),
            'settings': {
                'autonomous_enabled': self.autonomous_enabled,
                'fallback_on_error': self.fallback_on_error,
                'real_time_processing': self.real_time_processing
            }
        }
    
    def configure(self, **settings):
        """Update messaging system configuration"""
        for key, value in settings.items():
            if key in ['autonomous_enabled', 'fallback_on_error', 'real_time_processing']:
                setattr(self, key, value)
                logging.info(f"Messaging setting updated: {key}={value}")