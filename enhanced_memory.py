"""
Enhanced Memory System with Pattern Recognition and Learning
Extends ChromaDB capabilities for advanced AI learning and pattern matching
"""

import time
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import hashlib
from threading import Lock
import pickle

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available")

@dataclass
class TaskMemory:
    """Enhanced task memory structure"""
    task_id: str
    timestamp: float
    prompt: str
    task_type: str
    context: Dict[str, Any]
    result: str
    success: bool
    execution_time: float
    quality_score: float
    algorithm_config: Dict[str, Any]
    generated_files: List[str]
    subtasks: List[str]
    recursion_depth: int
    resource_usage: Dict[str, float]
    user_feedback: Optional[Dict[str, Any]] = None

@dataclass
class PatternMatch:
    """Pattern match result"""
    similarity: float
    task_memory: TaskMemory
    matching_features: List[str]
    confidence: float

@dataclass
class LearningInsight:
    """Discovered learning insight"""
    insight_id: str
    insight_type: str
    description: str
    evidence: List[str]
    confidence: float
    actionable: bool
    recommendation: str

class EnhancedMemoryManager:
    """Enhanced memory manager with advanced pattern recognition"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.memory_dir = data_dir / "memory"
        self.enhanced_memory_dir = data_dir / "enhanced_memory"
        self.enhanced_memory_dir.mkdir(parents=True, exist_ok=True)
        
        # ChromaDB collections
        self.task_collection = None
        self.pattern_collection = None
        self.insight_collection = None
        
        # In-memory caches
        self.task_cache = deque(maxlen=1000)
        self.pattern_cache = {}
        self.insight_cache = {}
        
        # Pattern recognition
        self.feature_extractors = {}
        self.similarity_threshold = 0.7
        self.learning_enabled = True
        
        # Thread safety
        self.memory_lock = Lock()
        
        # Initialize system
        self.setup_enhanced_memory()
        self._register_feature_extractors()
        
    def setup_enhanced_memory(self):
        """Setup enhanced memory system with multiple collections"""
        try:
            if not CHROMADB_AVAILABLE:
                logging.warning("ChromaDB not available - enhanced memory disabled")
                return
                
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(self.memory_dir))
            
            # Create specialized collections
            self.task_collection = client.get_or_create_collection(
                "enhanced_tasks",
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            
            self.pattern_collection = client.get_or_create_collection(
                "task_patterns",
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            
            self.insight_collection = client.get_or_create_collection(
                "learning_insights",
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
            )
            
            logging.info("Enhanced memory system initialized")
            
        except Exception as e:
            logging.error(f"Enhanced memory setup failed: {e}")
            self.task_collection = None
            
    def save_enhanced_task(self, task_memory: TaskMemory) -> bool:
        """Save task with enhanced metadata and features"""
        if not self.task_collection:
            return False
            
        try:
            with self.memory_lock:
                # Extract features for pattern matching
                features = self._extract_task_features(task_memory)
                
                # Create embedding text
                embedding_text = self._create_embedding_text(task_memory, features)
                
                # Prepare metadata
                metadata = asdict(task_memory)
                metadata["features"] = features
                metadata["embedding_text"] = embedding_text
                
                # Save to ChromaDB
                self.task_collection.add(
                    documents=[embedding_text],
                    metadatas=[metadata],
                    ids=[task_memory.task_id]
                )
                
                # Update cache
                self.task_cache.append(task_memory)
                
                # Trigger pattern analysis if enough data
                if len(self.task_cache) % 20 == 0:
                    self._analyze_recent_patterns()
                    
                logging.debug(f"Saved enhanced task: {task_memory.task_id}")
                return True
                
        except Exception as e:
            logging.error(f"Failed to save enhanced task: {e}")
            return False
            
    def retrieve_similar_tasks(self, prompt: str, task_type: str, 
                             context: Dict[str, Any] = None, 
                             n_results: int = 5) -> List[PatternMatch]:
        """Retrieve similar tasks using advanced pattern matching"""
        if not self.task_collection:
            return []
            
        try:
            # Create query from current task
            query_features = self._extract_query_features(prompt, task_type, context or {})
            query_text = self._create_query_text(prompt, task_type, query_features)
            
            # Query ChromaDB
            results = self.task_collection.query(
                query_texts=[query_text],
                n_results=n_results * 2,  # Get more results for filtering
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results["documents"]:
                return []
                
            # Convert to pattern matches with enhanced similarity
            pattern_matches = []
            
            for doc, metadata, distance in zip(results["documents"][0], 
                                             results["metadatas"][0], 
                                             results["distances"][0]):
                
                # Calculate enhanced similarity
                similarity = self._calculate_enhanced_similarity(query_features, metadata.get("features", {}))
                
                if similarity >= self.similarity_threshold:
                    task_memory = TaskMemory(**{k: v for k, v in metadata.items() 
                                              if k not in ["features", "embedding_text"]})
                    
                    matching_features = self._identify_matching_features(query_features, metadata.get("features", {}))
                    confidence = min(similarity, 1.0 - distance)
                    
                    pattern_matches.append(PatternMatch(
                        similarity=similarity,
                        task_memory=task_memory,
                        matching_features=matching_features,
                        confidence=confidence
                    ))
            
            # Sort by confidence and return top results
            pattern_matches.sort(key=lambda x: x.confidence, reverse=True)
            return pattern_matches[:n_results]
            
        except Exception as e:
            logging.error(f"Enhanced task retrieval failed: {e}")
            return []
            
    def discover_learning_insights(self, time_window: float = 86400) -> List[LearningInsight]:
        """Discover actionable learning insights from task history"""
        if not self.task_collection:
            return []
            
        try:
            # Get recent tasks
            current_time = time.time()
            recent_threshold = current_time - time_window
            
            # Query recent tasks
            all_results = self.task_collection.get(
                include=['metadatas']
            )
            
            recent_tasks = [
                TaskMemory(**{k: v for k, v in metadata.items() 
                           if k not in ["features", "embedding_text"]})
                for metadata in all_results["metadatas"]
                if metadata.get("timestamp", 0) >= recent_threshold
            ]
            
            if len(recent_tasks) < 10:
                return []
                
            insights = []
            
            # Analyze performance patterns
            insights.extend(self._analyze_performance_patterns(recent_tasks))
            
            # Analyze failure patterns
            insights.extend(self._analyze_failure_patterns(recent_tasks))
            
            # Analyze resource usage patterns
            insights.extend(self._analyze_resource_patterns(recent_tasks))
            
            # Analyze complexity patterns
            insights.extend(self._analyze_complexity_patterns(recent_tasks))
            
            # Cache insights
            for insight in insights:
                self.insight_cache[insight.insight_id] = insight
                
            return insights
            
        except Exception as e:
            logging.error(f"Learning insight discovery failed: {e}")
            return []
            
    def get_adaptive_context(self, prompt: str, task_type: str, 
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get adaptive context based on learned patterns"""
        similar_tasks = self.retrieve_similar_tasks(prompt, task_type, context, n_results=3)
        
        if not similar_tasks:
            return {"status": "no_similar_tasks"}
            
        # Aggregate insights from similar tasks
        adaptive_context = {
            "similar_task_count": len(similar_tasks),
            "average_confidence": sum(t.confidence for t in similar_tasks) / len(similar_tasks),
            "recommended_config": self._extract_recommended_config(similar_tasks),
            "expected_complexity": self._predict_complexity(similar_tasks),
            "risk_factors": self._identify_risk_factors(similar_tasks),
            "optimization_hints": self._generate_optimization_hints(similar_tasks)
        }
        
        return adaptive_context
        
    def update_task_feedback(self, task_id: str, feedback: Dict[str, Any]) -> bool:
        """Update task with user feedback for learning"""
        try:
            # Update in ChromaDB
            if self.task_collection:
                # Note: ChromaDB doesn't support direct updates, so we'd need to 
                # implement a feedback tracking system separately
                pass
                
            # Update cache
            for task in self.task_cache:
                if task.task_id == task_id:
                    task.user_feedback = feedback
                    break
                    
            logging.info(f"Updated task feedback: {task_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to update task feedback: {e}")
            return False
            
    def _register_feature_extractors(self):
        """Register feature extraction functions"""
        self.feature_extractors = {
            "complexity": self._extract_complexity_features,
            "content": self._extract_content_features,
            "context": self._extract_context_features,
            "performance": self._extract_performance_features,
            "resource": self._extract_resource_features
        }
        
    def _extract_task_features(self, task_memory: TaskMemory) -> Dict[str, Any]:
        """Extract comprehensive features from task memory"""
        features = {}
        
        for feature_type, extractor in self.feature_extractors.items():
            try:
                features[feature_type] = extractor(task_memory)
            except Exception as e:
                logging.error(f"Feature extraction failed for {feature_type}: {e}")
                features[feature_type] = {}
                
        return features
        
    def _extract_complexity_features(self, task_memory: TaskMemory) -> Dict[str, Any]:
        """Extract complexity-related features"""
        return {
            "prompt_length": len(task_memory.prompt),
            "context_size": len(str(task_memory.context)),
            "file_count": len(task_memory.generated_files),
            "recursion_depth": task_memory.recursion_depth,
            "subtask_count": len(task_memory.subtasks),
            "execution_time_category": self._categorize_execution_time(task_memory.execution_time)
        }
        
    def _extract_content_features(self, task_memory: TaskMemory) -> Dict[str, Any]:
        """Extract content-related features"""
        return {
            "task_type": task_memory.task_type,
            "has_files": len(task_memory.generated_files) > 0,
            "has_subtasks": len(task_memory.subtasks) > 0,
            "success": task_memory.success,
            "quality_category": self._categorize_quality(task_memory.quality_score),
            "keywords": self._extract_keywords(task_memory.prompt)
        }
        
    def _extract_context_features(self, task_memory: TaskMemory) -> Dict[str, Any]:
        """Extract context-related features"""
        context = task_memory.context
        return {
            "has_autonomous_mode": context.get("autonomous_mode", False),
            "has_auto_continue": context.get("auto_continue", False),
            "memory_enabled": context.get("use_memory", True),
            "input_file_types": self._extract_file_types(context.get("files", [])),
            "context_complexity": len(str(context))
        }
        
    def _extract_performance_features(self, task_memory: TaskMemory) -> Dict[str, Any]:
        """Extract performance-related features"""
        return {
            "execution_time": task_memory.execution_time,
            "quality_score": task_memory.quality_score,
            "success": task_memory.success,
            "algorithm_config_hash": hashlib.md5(str(sorted(task_memory.algorithm_config.items())).encode()).hexdigest()[:8]
        }
        
    def _extract_resource_features(self, task_memory: TaskMemory) -> Dict[str, Any]:
        """Extract resource usage features"""
        return {
            "cpu_usage": task_memory.resource_usage.get("cpu", 0),
            "memory_usage": task_memory.resource_usage.get("memory", 0),
            "disk_usage": task_memory.resource_usage.get("disk", 0),
            "resource_intensity": self._calculate_resource_intensity(task_memory.resource_usage)
        }
        
    def _extract_query_features(self, prompt: str, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from query for matching"""
        return {
            "complexity": {
                "prompt_length": len(prompt),
                "context_size": len(str(context)),
                "file_count": len(context.get("files", [])),
                "recursion_depth": context.get("recursion_depth", 0)
            },
            "content": {
                "task_type": task_type,
                "has_files": len(context.get("files", [])) > 0,
                "keywords": self._extract_keywords(prompt)
            },
            "context": {
                "has_autonomous_mode": context.get("autonomous_mode", False),
                "has_auto_continue": context.get("auto_continue", False),
                "memory_enabled": context.get("use_memory", True),
                "input_file_types": self._extract_file_types(context.get("files", []))
            }
        }
        
    def _create_embedding_text(self, task_memory: TaskMemory, features: Dict[str, Any]) -> str:
        """Create text for embedding generation"""
        parts = [
            f"Task: {task_memory.prompt}",
            f"Type: {task_memory.task_type}",
            f"Success: {task_memory.success}",
            f"Quality: {task_memory.quality_score:.2f}",
            f"Complexity: {features.get('complexity', {}).get('prompt_length', 0)} chars",
            f"Files: {len(task_memory.generated_files)}",
            f"Time: {task_memory.execution_time:.2f}s"
        ]
        
        return " | ".join(parts)
        
    def _create_query_text(self, prompt: str, task_type: str, features: Dict[str, Any]) -> str:
        """Create query text for similarity search"""
        parts = [
            f"Task: {prompt}",
            f"Type: {task_type}",
            f"Complexity: {features.get('complexity', {}).get('prompt_length', 0)} chars",
            f"Files: {features.get('complexity', {}).get('file_count', 0)}"
        ]
        
        return " | ".join(parts)
        
    def _calculate_enhanced_similarity(self, query_features: Dict[str, Any], 
                                     task_features: Dict[str, Any]) -> float:
        """Calculate enhanced similarity score"""
        if not query_features or not task_features:
            return 0.0
            
        similarity_scores = []
        
        # Content similarity
        content_sim = self._calculate_content_similarity(
            query_features.get("content", {}), 
            task_features.get("content", {})
        )
        similarity_scores.append(content_sim * 0.4)  # 40% weight
        
        # Complexity similarity
        complexity_sim = self._calculate_complexity_similarity(
            query_features.get("complexity", {}), 
            task_features.get("complexity", {})
        )
        similarity_scores.append(complexity_sim * 0.3)  # 30% weight
        
        # Context similarity
        context_sim = self._calculate_context_similarity(
            query_features.get("context", {}), 
            task_features.get("context", {})
        )
        similarity_scores.append(context_sim * 0.3)  # 30% weight
        
        return sum(similarity_scores)
        
    def _calculate_content_similarity(self, query_content: Dict[str, Any], 
                                    task_content: Dict[str, Any]) -> float:
        """Calculate content-based similarity"""
        if query_content.get("task_type") != task_content.get("task_type"):
            return 0.0
            
        # Keyword overlap
        query_keywords = set(query_content.get("keywords", []))
        task_keywords = set(task_content.get("keywords", []))
        
        if query_keywords and task_keywords:
            keyword_overlap = len(query_keywords.intersection(task_keywords)) / len(query_keywords.union(task_keywords))
        else:
            keyword_overlap = 0.0
            
        # File presence similarity
        file_sim = 1.0 if query_content.get("has_files") == task_content.get("has_files") else 0.5
        
        return (keyword_overlap * 0.7) + (file_sim * 0.3)
        
    def _calculate_complexity_similarity(self, query_complexity: Dict[str, Any], 
                                       task_complexity: Dict[str, Any]) -> float:
        """Calculate complexity-based similarity"""
        def normalize_value(value, max_val):
            return min(value / max_val, 1.0) if max_val > 0 else 0.0
            
        # Normalize features
        query_prompt_len = normalize_value(query_complexity.get("prompt_length", 0), 10000)
        task_prompt_len = normalize_value(task_complexity.get("prompt_length", 0), 10000)
        
        query_file_count = normalize_value(query_complexity.get("file_count", 0), 20)
        task_file_count = normalize_value(task_complexity.get("file_count", 0), 20)
        
        # Calculate similarity
        prompt_sim = 1.0 - abs(query_prompt_len - task_prompt_len)
        file_sim = 1.0 - abs(query_file_count - task_file_count)
        
        return (prompt_sim * 0.6) + (file_sim * 0.4)
        
    def _calculate_context_similarity(self, query_context: Dict[str, Any], 
                                    task_context: Dict[str, Any]) -> float:
        """Calculate context-based similarity"""
        similarities = []
        
        # Boolean features
        bool_features = ["has_autonomous_mode", "has_auto_continue", "memory_enabled"]
        for feature in bool_features:
            query_val = query_context.get(feature, False)
            task_val = task_context.get(feature, False)
            similarities.append(1.0 if query_val == task_val else 0.0)
            
        # File type overlap
        query_types = set(query_context.get("input_file_types", []))
        task_types = set(task_context.get("input_file_types", []))
        
        if query_types and task_types:
            type_overlap = len(query_types.intersection(task_types)) / len(query_types.union(task_types))
            similarities.append(type_overlap)
            
        return sum(similarities) / len(similarities) if similarities else 0.0
        
    def _identify_matching_features(self, query_features: Dict[str, Any], 
                                  task_features: Dict[str, Any]) -> List[str]:
        """Identify which features match between query and task"""
        matching = []
        
        # Check task type
        if (query_features.get("content", {}).get("task_type") == 
            task_features.get("content", {}).get("task_type")):
            matching.append("task_type")
            
        # Check complexity similarity
        query_complexity = query_features.get("complexity", {}).get("prompt_length", 0)
        task_complexity = task_features.get("complexity", {}).get("prompt_length", 0)
        
        if abs(query_complexity - task_complexity) / max(query_complexity, task_complexity, 1) < 0.5:
            matching.append("complexity")
            
        # Check context features
        query_context = query_features.get("context", {})
        task_context = task_features.get("context", {})
        
        if query_context.get("has_autonomous_mode") == task_context.get("has_autonomous_mode"):
            matching.append("autonomous_mode")
            
        return matching
        
    def _analyze_recent_patterns(self):
        """Analyze recent tasks for emerging patterns"""
        try:
            recent_tasks = list(self.task_cache)[-50:]  # Last 50 tasks
            
            if len(recent_tasks) < 10:
                return
                
            # Group by task type
            type_groups = defaultdict(list)
            for task in recent_tasks:
                type_groups[task.task_type].append(task)
                
            # Analyze each group
            for task_type, tasks in type_groups.items():
                if len(tasks) >= 5:
                    self._analyze_task_type_pattern(task_type, tasks)
                    
        except Exception as e:
            logging.error(f"Pattern analysis failed: {e}")
            
    def _analyze_task_type_pattern(self, task_type: str, tasks: List[TaskMemory]):
        """Analyze patterns for a specific task type"""
        # Calculate success rate trend
        recent_success_rate = sum(1 for t in tasks[-10:] if t.success) / min(10, len(tasks))
        overall_success_rate = sum(1 for t in tasks if t.success) / len(tasks)
        
        # Calculate performance trend
        recent_avg_time = sum(t.execution_time for t in tasks[-10:]) / min(10, len(tasks))
        overall_avg_time = sum(t.execution_time for t in tasks) / len(tasks)
        
        pattern_id = f"pattern_{task_type}_{int(time.time())}"
        
        # Store pattern insights
        self.pattern_cache[pattern_id] = {
            "task_type": task_type,
            "sample_size": len(tasks),
            "recent_success_rate": recent_success_rate,
            "overall_success_rate": overall_success_rate,
            "recent_avg_time": recent_avg_time,
            "overall_avg_time": overall_avg_time,
            "performance_trend": "improving" if recent_avg_time < overall_avg_time else "stable",
            "quality_trend": "improving" if recent_success_rate > overall_success_rate else "stable"
        }
        
    def _analyze_performance_patterns(self, tasks: List[TaskMemory]) -> List[LearningInsight]:
        """Analyze performance patterns in tasks"""
        insights = []
        
        # Group by task type
        type_groups = defaultdict(list)
        for task in tasks:
            type_groups[task.task_type].append(task)
            
        for task_type, task_list in type_groups.items():
            if len(task_list) < 5:
                continue
                
            # Analyze execution time trends
            times = [t.execution_time for t in task_list]
            avg_time = sum(times) / len(times)
            
            # Find significantly slow tasks
            slow_tasks = [t for t in task_list if t.execution_time > avg_time * 2]
            
            if len(slow_tasks) > len(task_list) * 0.2:  # More than 20% are slow
                insight = LearningInsight(
                    insight_id=f"perf_{task_type}_{int(time.time())}",
                    insight_type="performance",
                    description=f"Performance degradation detected in {task_type} tasks",
                    evidence=[f"{len(slow_tasks)} out of {len(task_list)} tasks are significantly slower"],
                    confidence=0.8,
                    actionable=True,
                    recommendation=f"Consider optimizing {task_type} task processing algorithms"
                )
                insights.append(insight)
                
        return insights
        
    def _analyze_failure_patterns(self, tasks: List[TaskMemory]) -> List[LearningInsight]:
        """Analyze failure patterns in tasks"""
        insights = []
        
        failed_tasks = [t for t in tasks if not t.success]
        
        if len(failed_tasks) > len(tasks) * 0.3:  # More than 30% failures
            # Analyze common failure characteristics
            failure_features = defaultdict(int)
            
            for task in failed_tasks:
                if task.execution_time > 60:  # Long execution time
                    failure_features["long_execution"] += 1
                if len(task.prompt) > 5000:  # Complex prompt
                    failure_features["complex_prompt"] += 1
                if task.recursion_depth > 2:  # Deep recursion
                    failure_features["deep_recursion"] += 1
                    
            # Find most common failure factor
            if failure_features:
                most_common = max(failure_features.items(), key=lambda x: x[1])
                
                insight = LearningInsight(
                    insight_id=f"failure_{int(time.time())}",
                    insight_type="failure_pattern",
                    description=f"High failure rate detected: {len(failed_tasks)}/{len(tasks)} tasks failed",
                    evidence=[f"Most common factor: {most_common[0]} ({most_common[1]} cases)"],
                    confidence=0.7,
                    actionable=True,
                    recommendation=f"Focus on handling {most_common[0]} scenarios better"
                )
                insights.append(insight)
                
        return insights
        
    def _analyze_resource_patterns(self, tasks: List[TaskMemory]) -> List[LearningInsight]:
        """Analyze resource usage patterns"""
        insights = []
        
        # Calculate average resource usage
        cpu_usages = [t.resource_usage.get("cpu", 0) for t in tasks if t.resource_usage]
        memory_usages = [t.resource_usage.get("memory", 0) for t in tasks if t.resource_usage]
        
        if cpu_usages and memory_usages:
            avg_cpu = sum(cpu_usages) / len(cpu_usages)
            avg_memory = sum(memory_usages) / len(memory_usages)
            
            if avg_cpu > 70 or avg_memory > 70:
                insight = LearningInsight(
                    insight_id=f"resource_{int(time.time())}",
                    insight_type="resource_usage",
                    description=f"High resource usage detected",
                    evidence=[f"Average CPU: {avg_cpu:.1f}%, Average Memory: {avg_memory:.1f}%"],
                    confidence=0.9,
                    actionable=True,
                    recommendation="Consider optimizing resource-intensive operations"
                )
                insights.append(insight)
                
        return insights
        
    def _analyze_complexity_patterns(self, tasks: List[TaskMemory]) -> List[LearningInsight]:
        """Analyze task complexity patterns"""
        insights = []
        
        # Analyze relationship between complexity and success
        complex_tasks = [t for t in tasks if len(t.prompt) > 2000 or t.recursion_depth > 1]
        
        if complex_tasks:
            complex_success_rate = sum(1 for t in complex_tasks if t.success) / len(complex_tasks)
            overall_success_rate = sum(1 for t in tasks if t.success) / len(tasks)
            
            if complex_success_rate < overall_success_rate - 0.2:  # 20% lower success
                insight = LearningInsight(
                    insight_id=f"complexity_{int(time.time())}",
                    insight_type="complexity",
                    description="Complex tasks show lower success rate",
                    evidence=[f"Complex task success: {complex_success_rate:.2f} vs overall: {overall_success_rate:.2f}"],
                    confidence=0.8,
                    actionable=True,
                    recommendation="Implement better handling for complex tasks or break them down further"
                )
                insights.append(insight)
                
        return insights
        
    def _extract_recommended_config(self, similar_tasks: List[PatternMatch]) -> Dict[str, Any]:
        """Extract recommended configuration from similar successful tasks"""
        successful_tasks = [match.task_memory for match in similar_tasks 
                          if match.task_memory.success and match.confidence > 0.7]
        
        if not successful_tasks:
            return {}
            
        # Aggregate configurations
        config_values = defaultdict(list)
        
        for task in successful_tasks:
            for param, value in task.algorithm_config.items():
                if isinstance(value, (int, float)):
                    config_values[param].append(value)
                    
        # Calculate recommended values
        recommended = {}
        for param, values in config_values.items():
            if values:
                recommended[param] = sum(values) / len(values)  # Average
                
        return recommended
        
    def _predict_complexity(self, similar_tasks: List[PatternMatch]) -> str:
        """Predict task complexity based on similar tasks"""
        if not similar_tasks:
            return "unknown"
            
        avg_execution_time = sum(match.task_memory.execution_time for match in similar_tasks) / len(similar_tasks)
        avg_file_count = sum(len(match.task_memory.generated_files) for match in similar_tasks) / len(similar_tasks)
        
        if avg_execution_time > 300 or avg_file_count > 10:  # 5 minutes or 10+ files
            return "high"
        elif avg_execution_time > 60 or avg_file_count > 3:  # 1 minute or 3+ files
            return "medium"
        else:
            return "low"
            
    def _identify_risk_factors(self, similar_tasks: List[PatternMatch]) -> List[str]:
        """Identify potential risk factors from similar tasks"""
        risk_factors = []
        
        failure_rate = sum(1 for match in similar_tasks if not match.task_memory.success) / len(similar_tasks)
        
        if failure_rate > 0.3:
            risk_factors.append(f"High failure rate in similar tasks ({failure_rate:.1%})")
            
        avg_time = sum(match.task_memory.execution_time for match in similar_tasks) / len(similar_tasks)
        if avg_time > 300:
            risk_factors.append("Long execution time expected")
            
        deep_recursion_count = sum(1 for match in similar_tasks if match.task_memory.recursion_depth > 2)
        if deep_recursion_count > len(similar_tasks) * 0.5:
            risk_factors.append("Deep recursion likely")
            
        return risk_factors
        
    def _generate_optimization_hints(self, similar_tasks: List[PatternMatch]) -> List[str]:
        """Generate optimization hints from similar tasks"""
        hints = []
        
        successful_tasks = [match for match in similar_tasks if match.task_memory.success]
        
        if successful_tasks:
            # Find common success patterns
            fast_tasks = [match for match in successful_tasks if match.task_memory.execution_time < 30]
            
            if len(fast_tasks) > len(successful_tasks) * 0.5:
                hints.append("Keep task simple for faster execution")
                
            high_quality_tasks = [match for match in successful_tasks if match.task_memory.quality_score > 0.8]
            
            if high_quality_tasks:
                hints.append("Focus on clear, specific prompts for better quality")
                
        return hints
        
    # Utility methods
    def _categorize_execution_time(self, execution_time: float) -> str:
        """Categorize execution time"""
        if execution_time < 10:
            return "fast"
        elif execution_time < 60:
            return "medium"
        elif execution_time < 300:
            return "slow"
        else:
            return "very_slow"
            
    def _categorize_quality(self, quality_score: float) -> str:
        """Categorize quality score"""
        if quality_score >= 0.8:
            return "high"
        elif quality_score >= 0.6:
            return "medium"
        elif quality_score >= 0.4:
            return "low"
        else:
            return "very_low"
            
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return top 10 most frequent
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
        
    def _extract_file_types(self, files: List[str]) -> List[str]:
        """Extract file types from file paths"""
        types = []
        for file_path in files:
            if isinstance(file_path, str):
                ext = Path(file_path).suffix.lower().lstrip('.')
                if ext:
                    types.append(ext)
        return list(set(types))
        
    def _calculate_resource_intensity(self, resource_usage: Dict[str, float]) -> str:
        """Calculate resource intensity category"""
        cpu = resource_usage.get("cpu", 0)
        memory = resource_usage.get("memory", 0)
        
        intensity = (cpu + memory) / 2
        
        if intensity > 80:
            return "very_high"
        elif intensity > 60:
            return "high"
        elif intensity > 40:
            return "medium"
        else:
            return "low"