"""
Recursive Task Expansion Engine (RTEE) for SuperMini
Provides autonomous task decomposition, planning, and recursive execution
Enhanced with dynamic adaptation and intelligent planning capabilities for 2025 autonomous AI patterns.
"""

import time
import logging
import json
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict, field
from pathlib import Path
from threading import Lock
import hashlib
import uuid
from enum import Enum
from collections import deque

class TaskStatus(Enum):
    """Enhanced task status enumeration"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ADAPTING = "adapting"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class AdaptationType(Enum):
    """Types of task adaptation"""
    REQUIREMENT_CHANGE = "requirement_change"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_CORRECTION = "error_correction"
    CONTEXT_UPDATE = "context_update"
    RESOURCE_REALLOCATION = "resource_reallocation"

@dataclass
class AdaptationRecord:
    """Records task adaptations for learning"""
    adaptation_id: str
    timestamp: float
    adaptation_type: AdaptationType
    original_description: str
    adapted_description: str
    trigger_reason: str
    success_improvement: float = 0.0
    performance_impact: Dict[str, float] = field(default_factory=dict)

@dataclass
class SubTask:
    """Enhanced subtask with adaptive capabilities"""
    id: str
    name: str
    description: str
    task_type: str
    dependencies: List[str]
    priority: int
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    generated_files: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    retry_count: int = 0
    max_retries: int = 3
    adaptation_history: List[AdaptationRecord] = field(default_factory=list)
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    learning_feedback: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    
    def adapt_description(self, new_description: str, adaptation_type: AdaptationType, 
                         trigger_reason: str) -> AdaptationRecord:
        """Adapt the task description and record the change"""
        adaptation = AdaptationRecord(
            adaptation_id=str(uuid.uuid4()),
            timestamp=time.time(),
            adaptation_type=adaptation_type,
            original_description=self.description,
            adapted_description=new_description,
            trigger_reason=trigger_reason
        )
        
        self.adaptation_history.append(adaptation)
        self.description = new_description
        self.last_modified = time.time()
        
        return adaptation
    
    def update_performance_metrics(self, metrics: Dict[str, float]):
        """Update performance metrics for the task"""
        self.performance_metrics.update(metrics)
        self.last_modified = time.time()
    
    def add_learning_feedback(self, feedback: str):
        """Add learning feedback to improve future similar tasks"""
        self.learning_feedback.append(feedback)
        self.last_modified = time.time()

@dataclass 
class ExecutionPlan:
    """Dynamic execution plan that can expand during runtime"""
    id: str
    original_prompt: str
    task_type: str
    subtasks: List[SubTask]
    execution_order: List[str]
    status: str = "planning"  # planning, executing, completed, failed
    recursion_depth: int = 0
    max_recursion_depth: int = 5
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

# Import enhanced components
try:
    from dynamic_planning_components import (
        PlanPerformanceMonitor, ContextTracker, AdaptationEngine,
        PlanPerformanceMetrics
    )
    ENHANCED_PLANNING_AVAILABLE = True
except ImportError:
    logging.warning("Enhanced planning components not available")
    ENHANCED_PLANNING_AVAILABLE = False
    # Fallback classes
    class PlanPerformanceMonitor:
        def __init__(self): pass
        def record_performance(self, *args, **kwargs): pass
    class ContextTracker:
        def __init__(self): pass
        def analyze_planning_context(self, prompt, task_type, context=None):
            return context or {}
    class AdaptationEngine:
        def __init__(self): pass
        def recommend_adaptation(self, context, issues):
            return {"strategy": None, "confidence": 0.0}

class SmartTaskDecomposer:
    """Enhanced AI-powered task decomposer with learning and adaptation"""
    
    def __init__(self, claude_manager, ollama_manager):
        self.claude = claude_manager
        self.ollama = ollama_manager
        self.decomposition_cache = {}
        self.decomposition_history = deque(maxlen=100)
        self.successful_patterns = {}
        self.learning_database = {}
        
    def analyze_task_complexity(self, prompt: str, task_type: str) -> Dict[str, float]:
        """Analyze task complexity to inform decomposition strategy"""
        complexity_analysis = {
            "length_complexity": min(1.0, len(prompt.split()) / 100),
            "structural_complexity": self._analyze_structural_complexity(prompt),
            "domain_complexity": self._analyze_domain_complexity(prompt, task_type),
            "dependency_complexity": self._analyze_dependency_indicators(prompt),
            "ambiguity_score": self._analyze_ambiguity(prompt)
        }
        
        overall_complexity = sum(complexity_analysis.values()) / len(complexity_analysis)
        complexity_analysis["overall_complexity"] = overall_complexity
        
        return complexity_analysis
    
    def _analyze_structural_complexity(self, prompt: str) -> float:
        """Analyze structural complexity of the prompt"""
        complexity_indicators = [
            len([word for word in prompt.split() if word.lower() in ["and", "then", "also", "additionally"]]) / len(prompt.split()),
            len([char for char in prompt if char in "()[]{})"]) / len(prompt),
            prompt.count(":") / len(prompt.split()),
            len([word for word in prompt.split() if word.lower() in ["if", "when", "unless", "provided"]]) / len(prompt.split())
        ]
        return min(1.0, sum(complexity_indicators))
    
    def _analyze_domain_complexity(self, prompt: str, task_type: str) -> float:
        """Analyze domain-specific complexity"""
        domain_keywords = {
            "code": ["algorithm", "function", "class", "api", "database", "framework"],
            "multimedia": ["image", "video", "audio", "processing", "editing", "conversion"],
            "rag": ["document", "analysis", "summarize", "extract", "knowledge"],
            "automation": ["script", "workflow", "schedule", "trigger", "pipeline"],
            "analytics": ["data", "visualization", "statistics", "analysis", "charts"]
        }
        
        keywords = domain_keywords.get(task_type, [])
        matches = sum(1 for keyword in keywords if keyword.lower() in prompt.lower())
        return min(1.0, matches / max(1, len(keywords)))
    
    def _analyze_dependency_indicators(self, prompt: str) -> float:
        """Analyze indicators of task dependencies"""
        dependency_words = ["after", "before", "depends", "requires", "following", "previous", "subsequent"]
        matches = sum(1 for word in dependency_words if word.lower() in prompt.lower())
        return min(1.0, matches / len(prompt.split()) * 10)  # Scale up for visibility
    
    def _analyze_ambiguity(self, prompt: str) -> float:
        """Analyze ambiguity in the prompt"""
        ambiguous_words = ["maybe", "possibly", "might", "could", "perhaps", "something", "somehow"]
        vague_words = ["good", "nice", "better", "optimize", "improve", "enhance"]
        
        ambiguous_count = sum(1 for word in ambiguous_words if word.lower() in prompt.lower())
        vague_count = sum(1 for word in vague_words if word.lower() in prompt.lower())
        
        return min(1.0, (ambiguous_count + vague_count) / len(prompt.split()) * 5)
        
    def decompose_task(self, prompt: str, task_type: str, context: Dict[str, Any] = None) -> List[SubTask]:
        """Decompose a complex task into subtasks"""
        cache_key = hashlib.md5(f"{prompt}_{task_type}".encode()).hexdigest()
        
        if cache_key in self.decomposition_cache:
            logging.info("Using cached task decomposition")
            return self._create_subtasks_from_cache(self.decomposition_cache[cache_key])
        
        decomposition_prompt = self._build_decomposition_prompt(prompt, task_type, context)
        
        # Try Claude first, fallback to Ollama
        response = self.claude.query(decomposition_prompt)
        if not response:
            response = self.ollama.query(decomposition_prompt)
            
        if not response:
            # Fallback to basic decomposition
            return self._create_basic_subtasks(prompt, task_type)
            
        subtasks = self._parse_decomposition_response(response, task_type)
        
        # Cache the decomposition
        self.decomposition_cache[cache_key] = [asdict(task) for task in subtasks]
        
        return subtasks
    
    def _build_decomposition_prompt(self, prompt: str, task_type: str, context: Dict[str, Any] = None) -> str:
        """Build the AI prompt for task decomposition"""
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
        return f"""
You are an expert task decomposition agent. Break down the following {task_type} task into 3-7 manageable subtasks.

Original Task: "{prompt}"
Task Type: {task_type}{context_str}

For each subtask, provide:
1. Name (brief, descriptive)
2. Description (detailed what needs to be done)
3. Task type (code, multimedia, rag, automation, analytics)
4. Dependencies (list of other subtask names this depends on)
5. Priority (1-5, where 1 is highest)

Format your response as JSON:
{{
    "subtasks": [
        {{
            "name": "subtask_name",
            "description": "detailed description",
            "task_type": "code",
            "dependencies": ["other_subtask_name"],
            "priority": 1
        }}
    ],
    "reasoning": "explanation of decomposition strategy"
}}

Guidelines:
- Keep subtasks focused and atomic
- Ensure dependencies are logical and minimal
- Prioritize based on dependency chain and importance
- Each subtask should be completable independently once dependencies are met
- Consider the recursive nature - subtasks may generate their own subtasks
"""

    def _parse_decomposition_response(self, response: str, task_type: str) -> List[SubTask]:
        """Parse AI response into SubTask objects"""
        try:
            data = json.loads(response)
            subtasks = []
            
            for i, subtask_data in enumerate(data.get("subtasks", [])):
                subtask_id = f"subtask_{int(time.time() * 1000000)}_{i}"
                
                subtask = SubTask(
                    id=subtask_id,
                    name=subtask_data.get("name", f"Subtask {i+1}"),
                    description=subtask_data.get("description", ""),
                    task_type=subtask_data.get("task_type", task_type),
                    dependencies=subtask_data.get("dependencies", []),
                    priority=subtask_data.get("priority", 3)
                )
                subtasks.append(subtask)
                
            return subtasks
            
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse decomposition response: {e}")
            return self._create_basic_subtasks("Task decomposition failed", task_type)
    
    def _create_basic_subtasks(self, prompt: str, task_type: str) -> List[SubTask]:
        """Create basic subtasks when AI decomposition fails"""
        base_id = int(time.time() * 1000000)
        
        if task_type == "code":
            return [
                SubTask(f"subtask_{base_id}_1", "Analysis", "Analyze requirements and design approach", "code", [], 1),
                SubTask(f"subtask_{base_id}_2", "Implementation", "Write the main code", "code", ["Analysis"], 2),
                SubTask(f"subtask_{base_id}_3", "Testing", "Test and validate the solution", "code", ["Implementation"], 3)
            ]
        elif task_type == "automation":
            return [
                SubTask(f"subtask_{base_id}_1", "Planning", "Plan automation workflow", "automation", [], 1),
                SubTask(f"subtask_{base_id}_2", "Script Creation", "Create automation script", "automation", ["Planning"], 2)
            ]
        else:
            return [
                SubTask(f"subtask_{base_id}_1", "Main Task", prompt, task_type, [], 1)
            ]
    
    def _create_subtasks_from_cache(self, cached_data: List[Dict]) -> List[SubTask]:
        """Recreate SubTask objects from cached data"""
        subtasks = []
        for data in cached_data:
            subtask = SubTask(**data)
            # Generate new ID to avoid conflicts
            subtask.id = f"subtask_{int(time.time() * 1000000)}_{len(subtasks)}"
            subtasks.append(subtask)
        return subtasks

class DynamicPlanner:
    """Creates and manages expandable execution plans"""
    
    def __init__(self, task_decomposer):
        self.decomposer = task_decomposer
        self.active_plans = {}
        self.plan_lock = Lock()
        
    def create_execution_plan(self, prompt: str, task_type: str, context: Dict[str, Any] = None) -> ExecutionPlan:
        """Create a new dynamic execution plan"""
        plan_id = f"plan_{int(time.time() * 1000000)}"
        
        # Decompose the initial task
        subtasks = self.decomposer.decompose_task(prompt, task_type, context)
        
        # Calculate execution order based on dependencies
        execution_order = self._calculate_execution_order(subtasks)
        
        plan = ExecutionPlan(
            id=plan_id,
            original_prompt=prompt,
            task_type=task_type,
            subtasks=subtasks,
            execution_order=execution_order
        )
        
        with self.plan_lock:
            self.active_plans[plan_id] = plan
            
        logging.info(f"Created execution plan {plan_id} with {len(subtasks)} subtasks")
        return plan
    
    def expand_plan(self, plan: ExecutionPlan, subtask_id: str, new_prompt: str) -> bool:
        """Dynamically expand a plan by decomposing a subtask further"""
        if plan.recursion_depth >= plan.max_recursion_depth:
            logging.warning(f"Max recursion depth reached for plan {plan.id}")
            return False
            
        # Find the subtask to expand
        target_subtask = None
        for subtask in plan.subtasks:
            if subtask.id == subtask_id:
                target_subtask = subtask
                break
                
        if not target_subtask:
            logging.error(f"Subtask {subtask_id} not found in plan {plan.id}")
            return False
            
        # Decompose the subtask
        context = {"parent_task": target_subtask.description, "recursion_depth": plan.recursion_depth + 1}
        new_subtasks = self.decomposer.decompose_task(new_prompt, target_subtask.task_type, context)
        
        # Update subtask IDs to include parent reference
        for i, new_subtask in enumerate(new_subtasks):
            new_subtask.id = f"{subtask_id}_sub_{i}"
            
        # Insert new subtasks after the original subtask
        original_index = plan.subtasks.index(target_subtask)
        plan.subtasks[original_index:original_index+1] = new_subtasks
        
        # Recalculate execution order
        plan.execution_order = self._calculate_execution_order(plan.subtasks)
        plan.recursion_depth += 1
        
        logging.info(f"Expanded plan {plan.id}, added {len(new_subtasks)} new subtasks")
        return True
    
    def _calculate_execution_order(self, subtasks: List[SubTask]) -> List[str]:
        """Calculate optimal execution order based on dependencies and priorities"""
        # Simple topological sort with priority weighting
        order = []
        remaining = {task.id: task for task in subtasks}
        
        while remaining:
            # Find tasks with no unfulfilled dependencies
            ready_tasks = []
            for task_id, task in remaining.items():
                if all(dep_name not in remaining or any(t.name == dep_name for t in subtasks if t.id in order) 
                      for dep_name in task.dependencies):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                # Break circular dependencies by picking highest priority
                ready_tasks = [min(remaining.values(), key=lambda t: t.priority)]
                
            # Sort by priority and add to order
            ready_tasks.sort(key=lambda t: t.priority)
            for task in ready_tasks:
                order.append(task.id)
                del remaining[task.id]
                
        return order

class RecursionLimiter:
    """Prevents infinite recursion and manages resource limits"""
    
    def __init__(self, max_depth: int = 5, max_execution_time: float = 3600, max_subtasks: int = 50):
        self.max_depth = max_depth
        self.max_execution_time = max_execution_time
        self.max_subtasks = max_subtasks
        self.execution_stats = {}
        
    def check_recursion_limits(self, plan: ExecutionPlan) -> Tuple[bool, str]:
        """Check if plan exceeds recursion limits"""
        # Check recursion depth
        if plan.recursion_depth >= self.max_depth:
            return False, f"Maximum recursion depth ({self.max_depth}) exceeded"
            
        # Check number of subtasks
        if len(plan.subtasks) >= self.max_subtasks:
            return False, f"Maximum subtasks ({self.max_subtasks}) exceeded"
            
        # Check execution time
        elapsed_time = time.time() - plan.created_at
        if elapsed_time >= self.max_execution_time:
            return False, f"Maximum execution time ({self.max_execution_time}s) exceeded"
            
        return True, "Within limits"
    
    def should_allow_expansion(self, plan: ExecutionPlan, complexity_score: float = 1.0) -> bool:
        """Determine if plan expansion should be allowed"""
        can_expand, reason = self.check_recursion_limits(plan)
        
        if not can_expand:
            logging.warning(f"Expansion denied for plan {plan.id}: {reason}")
            return False
            
        # Additional heuristics based on complexity
        if complexity_score > 0.8 and plan.recursion_depth >= self.max_depth - 1:
            logging.warning(f"High complexity task denied expansion at depth {plan.recursion_depth}")
            return False
            
        return True
    
    def update_execution_stats(self, plan_id: str, subtask_id: str, execution_time: float, success: bool):
        """Update execution statistics for monitoring"""
        if plan_id not in self.execution_stats:
            self.execution_stats[plan_id] = {
                "total_time": 0.0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "average_time": 0.0
            }
            
        stats = self.execution_stats[plan_id]
        stats["total_time"] += execution_time
        
        if success:
            stats["completed_tasks"] += 1
        else:
            stats["failed_tasks"] += 1
            
        total_tasks = stats["completed_tasks"] + stats["failed_tasks"]
        if total_tasks > 0:
            stats["average_time"] = stats["total_time"] / total_tasks

class RecursiveTaskEngine:
    """Main engine that coordinates recursive task processing"""
    
    def __init__(self, claude_manager, ollama_manager, memory_manager, output_dir: Path):
        self.claude = claude_manager
        self.ollama = ollama_manager
        self.memory = memory_manager
        self.output_dir = output_dir
        
        # Initialize components
        self.decomposer = SmartTaskDecomposer(claude_manager, ollama_manager)
        self.planner = DynamicPlanner(self.decomposer)
        self.limiter = RecursionLimiter()
        
        # Execution state
        self.stop_requested = False
        self.current_plan = None
        
    def request_stop(self):
        """Request stop of recursive execution"""
        self.stop_requested = True
        logging.info("Recursive task engine stop requested")
        
    def reset_stop_flag(self):
        """Reset stop flag for new execution"""
        self.stop_requested = False
        
    def execute_recursive_task(self, prompt: str, task_type: str, files: List[str] = None, 
                             context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a task with recursive expansion capabilities"""
        if files is None:
            files = []
            
        # Create execution plan
        plan = self.planner.create_execution_plan(prompt, task_type, context)
        self.current_plan = plan
        
        try:
            plan.status = "executing"
            results = {
                "plan_id": plan.id,
                "original_prompt": prompt,
                "task_type": task_type,
                "subtask_results": {},
                "generated_files": [],
                "execution_summary": "",
                "success": True,
                "total_execution_time": 0.0
            }
            
            start_time = time.time()
            
            # Execute subtasks in order
            for subtask_id in plan.execution_order:
                if self.stop_requested:
                    logging.info("Recursive execution stopped by user request")
                    break
                    
                subtask = next(t for t in plan.subtasks if t.id == subtask_id)
                
                # Check if dependencies are met
                if not self._dependencies_met(subtask, plan):
                    logging.warning(f"Dependencies not met for subtask {subtask_id}")
                    continue
                    
                # Execute subtask
                subtask_result = self._execute_subtask(subtask, plan, files)
                results["subtask_results"][subtask_id] = subtask_result
                
                # Collect generated files
                if subtask_result.get("generated_files"):
                    results["generated_files"].extend(subtask_result["generated_files"])
                    
                # Check if subtask should be expanded recursively
                if (subtask_result.get("should_expand") and 
                    self.limiter.should_allow_expansion(plan) and
                    not self.stop_requested):
                    
                    expansion_prompt = subtask_result.get("expansion_prompt", subtask.description)
                    self.planner.expand_plan(plan, subtask_id, expansion_prompt)
                    
            results["total_execution_time"] = time.time() - start_time
            plan.status = "completed" if not self.stop_requested else "stopped"
            
            # Generate execution summary
            results["execution_summary"] = self._generate_execution_summary(plan, results)
            
            return results
            
        except Exception as e:
            logging.error(f"Recursive execution failed: {e}")
            plan.status = "failed"
            return {
                "plan_id": plan.id,
                "success": False,
                "error": str(e),
                "execution_summary": f"Execution failed: {e}"
            }
        finally:
            self.current_plan = None
    
    def _dependencies_met(self, subtask: SubTask, plan: ExecutionPlan) -> bool:
        """Check if subtask dependencies are completed"""
        for dep_name in subtask.dependencies:
            dep_task = next((t for t in plan.subtasks if t.name == dep_name), None)
            if not dep_task or dep_task.status != "completed":
                return False
        return True
    
    def _execute_subtask(self, subtask: SubTask, plan: ExecutionPlan, files: List[str]) -> Dict[str, Any]:
        """Execute a single subtask"""
        subtask.status = "in_progress"
        start_time = time.time()
        
        try:
            # Determine if this subtask needs recursive expansion
            should_expand = self._should_expand_subtask(subtask)
            
            # Execute the subtask using appropriate method
            if subtask.task_type == "code":
                result = self._execute_code_subtask(subtask, files)
            elif subtask.task_type == "automation":
                result = self._execute_automation_subtask(subtask, files)
            else:
                result = self._execute_general_subtask(subtask, files)
                
            execution_time = time.time() - start_time
            subtask.execution_time = execution_time
            subtask.status = "completed"
            
            # Update execution stats
            self.limiter.update_execution_stats(plan.id, subtask.id, execution_time, True)
            
            result.update({
                "subtask_id": subtask.id,
                "execution_time": execution_time,
                "should_expand": should_expand,
                "success": True
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            subtask.status = "failed"
            subtask.retry_count += 1
            
            # Update execution stats
            self.limiter.update_execution_stats(plan.id, subtask.id, execution_time, False)
            
            logging.error(f"Subtask {subtask.id} failed: {e}")
            return {
                "subtask_id": subtask.id,
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "should_expand": False
            }
    
    def _should_expand_subtask(self, subtask: SubTask) -> bool:
        """Determine if a subtask should be recursively expanded"""
        # Simple heuristics for expansion
        complexity_keywords = ["complex", "multiple", "various", "comprehensive", "detailed", "advanced"]
        description_lower = subtask.description.lower()
        
        has_complexity = any(keyword in description_lower for keyword in complexity_keywords)
        is_suitable_type = subtask.task_type in ["code", "automation", "analytics"]
        
        return has_complexity and is_suitable_type
    
    def _execute_code_subtask(self, subtask: SubTask, files: List[str]) -> Dict[str, Any]:
        """Execute a code-type subtask"""
        # Use existing code execution logic with enhanced prompting
        enhanced_prompt = f"""
Task: {subtask.description}

Context: This is part of a larger recursive task execution. Focus on this specific subtask.

Previous files available: {files}

Generate clean, working code that fulfills this specific requirement.
"""
        
        response = self.claude.query(enhanced_prompt)
        if not response:
            response = self.ollama.query(enhanced_prompt)
            
        generated_files = []
        if response:
            # Extract and save code blocks
            code_blocks = self._extract_code_blocks(response)
            for i, (language, code) in enumerate(code_blocks):
                if code.strip():
                    extension = self._get_file_extension(language)
                    filename = f"{subtask.name.lower().replace(' ', '_')}_{int(time.time())}_{i}.{extension}"
                    file_path = self.output_dir / filename
                    
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(code)
                        generated_files.append(str(file_path))
                    except Exception as e:
                        logging.error(f"Failed to save code file: {e}")
        
        return {
            "result": response or "Failed to generate code",
            "generated_files": generated_files,
            "expansion_prompt": f"Enhance and optimize: {subtask.description}" if generated_files else None
        }
    
    def _execute_automation_subtask(self, subtask: SubTask, files: List[str]) -> Dict[str, Any]:
        """Execute an automation-type subtask"""
        automation_prompt = f"""
Create an automation solution for: {subtask.description}

Generate a shell script or automation code that accomplishes this task.
Make it robust and include error handling.
"""
        
        response = self.claude.query(automation_prompt)
        if not response:
            response = self.ollama.query(automation_prompt)
            
        generated_files = []
        if response:
            # Save as shell script
            filename = f"automation_{subtask.name.lower().replace(' ', '_')}_{int(time.time())}.sh"
            file_path = self.output_dir / filename
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(response)
                # Make executable
                import stat
                file_path.chmod(file_path.stat().st_mode | stat.S_IEXEC)
                generated_files.append(str(file_path))
            except Exception as e:
                logging.error(f"Failed to save automation script: {e}")
        
        return {
            "result": response or "Failed to generate automation script",
            "generated_files": generated_files,
            "expansion_prompt": f"Add advanced features to: {subtask.description}" if generated_files else None
        }
    
    def _execute_general_subtask(self, subtask: SubTask, files: List[str]) -> Dict[str, Any]:
        """Execute a general subtask"""
        response = self.claude.query(subtask.description)
        if not response:
            response = self.ollama.query(subtask.description)
            
        return {
            "result": response or "Failed to process subtask",
            "generated_files": [],
            "expansion_prompt": None
        }
    
    def _extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from text"""
        import re
        
        # Pattern to match code blocks with language specification
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            language = language or "text"
            code_blocks.append((language, code.strip()))
            
        return code_blocks
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for programming language"""
        extensions = {
            "python": "py", "javascript": "js", "typescript": "ts", "java": "java",
            "cpp": "cpp", "c": "c", "csharp": "cs", "ruby": "rb", "go": "go",
            "rust": "rs", "php": "php", "swift": "swift", "kotlin": "kt",
            "shell": "sh", "bash": "sh", "sql": "sql", "html": "html",
            "css": "css", "json": "json", "xml": "xml", "yaml": "yml"
        }
        return extensions.get(language.lower(), "txt")
    
    def _generate_execution_summary(self, plan: ExecutionPlan, results: Dict[str, Any]) -> str:
        """Generate a summary of the recursive execution"""
        completed_tasks = sum(1 for t in plan.subtasks if t.status == "completed")
        failed_tasks = sum(1 for t in plan.subtasks if t.status == "failed")
        total_files = len(results["generated_files"])
        
        summary = f"""
Recursive Task Execution Summary:
================================
Plan ID: {plan.id}
Original Task: {plan.original_prompt[:100]}...
Task Type: {plan.task_type}

Execution Stats:
- Total Subtasks: {len(plan.subtasks)}
- Completed: {completed_tasks}
- Failed: {failed_tasks}
- Recursion Depth: {plan.recursion_depth}
- Files Generated: {total_files}
- Total Time: {results['total_execution_time']:.2f}s

Status: {plan.status}
"""
        
        if results["generated_files"]:
            summary += f"\nGenerated Files:\n"
            for file_path in results["generated_files"]:
                summary += f"- {Path(file_path).name}\n"
                
        return summary.strip()

# Legacy aliases and compatibility classes for backwards compatibility
TaskDecomposer = SmartTaskDecomposer

class DynamicPlanner:
    """Legacy class for backwards compatibility"""
    def __init__(self, task_decomposer):
        self.decomposer = task_decomposer
        self.active_plans = {}
        self.plan_lock = Lock()
        
    def create_execution_plan(self, prompt: str, task_type: str, context: Dict[str, Any] = None):
        """Legacy method"""
        subtasks = self.decomposer.decompose_task(prompt, task_type, context)
        return ExecutionPlan(
            id=f"plan_{int(time.time() * 1000000)}",
            original_prompt=prompt,
            task_type=task_type,
            subtasks=subtasks,
            execution_order=[task.id for task in subtasks]
        )

