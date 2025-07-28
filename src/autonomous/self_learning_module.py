"""
Self-Learning Adaptation Module (SLAM) for SuperMini
Provides performance analysis, algorithm optimization, and adaptive learning
"""

import time
import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque, defaultdict
import statistics
import pickle
import hashlib
from threading import Lock
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    timestamp: float
    task_type: str
    execution_time: float
    success: bool
    quality_score: float
    resource_usage: Dict[str, float]
    context: Dict[str, Any]
    algorithm_config: Dict[str, Any]
    
@dataclass
class OptimizationSuggestion:
    """Algorithm optimization suggestion"""
    parameter: str
    current_value: Any
    suggested_value: Any
    confidence: float
    reasoning: str
    expected_improvement: float

@dataclass
class LearningPattern:
    """Discovered learning pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    conditions: Dict[str, Any]
    optimization: Dict[str, Any]
    success_rate: float
    sample_size: int
    confidence: float

class PerformanceAnalyzer:
    """Analyzes task execution performance and identifies improvement opportunities"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.performance_history = deque(maxlen=max_history)
        self.pattern_cache = {}
        self.analysis_lock = Lock()
        
    def record_performance(self, metric: PerformanceMetric):
        """Record a performance measurement"""
        with self.analysis_lock:
            self.performance_history.append(metric)
            
        logging.debug(f"Recorded performance: {metric.task_type} - {metric.execution_time:.2f}s - Success: {metric.success}")
        
    def analyze_performance_trends(self, task_type: Optional[str] = None, 
                                 time_window: float = 3600) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        with self.analysis_lock:
            current_time = time.time()
            
            # Filter relevant metrics
            relevant_metrics = [
                m for m in self.performance_history 
                if (task_type is None or m.task_type == task_type) and 
                   (current_time - m.timestamp) <= time_window
            ]
            
        if not relevant_metrics:
            return {"status": "no_data", "task_type": task_type}
            
        # Calculate basic statistics
        execution_times = [m.execution_time for m in relevant_metrics]
        quality_scores = [m.quality_score for m in relevant_metrics if m.success]
        success_rate = sum(1 for m in relevant_metrics if m.success) / len(relevant_metrics)
        
        trends = {
            "task_type": task_type,
            "sample_size": len(relevant_metrics),
            "time_window_hours": time_window / 3600,
            "success_rate": success_rate,
            "avg_execution_time": statistics.mean(execution_times),
            "median_execution_time": statistics.median(execution_times),
            "execution_time_std": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
            "avg_quality_score": statistics.mean(quality_scores) if quality_scores else 0,
            "performance_trend": self._calculate_trend(relevant_metrics),
            "bottlenecks": self._identify_bottlenecks(relevant_metrics),
            "optimization_opportunities": self._find_optimization_opportunities(relevant_metrics)
        }
        
        return trends
        
    def _calculate_trend(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate performance trend direction"""
        if len(metrics) < 5:
            return {"direction": "insufficient_data"}
            
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Split into early and late halves
        mid_point = len(sorted_metrics) // 2
        early_metrics = sorted_metrics[:mid_point]
        late_metrics = sorted_metrics[mid_point:]
        
        early_avg_time = statistics.mean(m.execution_time for m in early_metrics)
        late_avg_time = statistics.mean(m.execution_time for m in late_metrics)
        
        early_success_rate = sum(1 for m in early_metrics if m.success) / len(early_metrics)
        late_success_rate = sum(1 for m in late_metrics if m.success) / len(late_metrics)
        
        time_improvement = (early_avg_time - late_avg_time) / early_avg_time
        success_improvement = late_success_rate - early_success_rate
        
        if time_improvement > 0.1 and success_improvement >= 0:
            direction = "improving"
        elif time_improvement < -0.1 or success_improvement < -0.1:
            direction = "degrading"
        else:
            direction = "stable"
            
        return {
            "direction": direction,
            "time_improvement": time_improvement,
            "success_improvement": success_improvement,
            "early_avg_time": early_avg_time,
            "late_avg_time": late_avg_time,
            "early_success_rate": early_success_rate,
            "late_success_rate": late_success_rate
        }
        
    def _identify_bottlenecks(self, metrics: List[PerformanceMetric]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Resource usage bottlenecks
        resource_usage = defaultdict(list)
        for metric in metrics:
            for resource, usage in metric.resource_usage.items():
                resource_usage[resource].append(usage)
                
        for resource, usages in resource_usage.items():
            avg_usage = statistics.mean(usages)
            max_usage = max(usages)
            
            if avg_usage > 80 or max_usage > 95:  # High resource usage
                bottlenecks.append({
                    "type": "resource",
                    "resource": resource,
                    "avg_usage": avg_usage,
                    "max_usage": max_usage,
                    "severity": "high" if max_usage > 95 else "medium"
                })
        
        # Execution time bottlenecks
        execution_times = [m.execution_time for m in metrics]
        if execution_times:
            avg_time = statistics.mean(execution_times)
            p95_time = np.percentile(execution_times, 95)
            
            if p95_time > avg_time * 3:  # Long tail of slow executions
                bottlenecks.append({
                    "type": "execution_time",
                    "avg_time": avg_time,
                    "p95_time": p95_time,
                    "slowdown_factor": p95_time / avg_time,
                    "severity": "high" if p95_time > avg_time * 5 else "medium"
                })
                
        return bottlenecks
        
    def _find_optimization_opportunities(self, metrics: List[PerformanceMetric]) -> List[OptimizationSuggestion]:
        """Find specific optimization opportunities"""
        opportunities = []
        
        # Analyze algorithm configurations that perform well
        config_performance = defaultdict(list)
        
        for metric in metrics:
            if metric.success:
                config_key = json.dumps(metric.algorithm_config, sort_keys=True)
                config_performance[config_key].append(metric)
                
        # Find best performing configurations
        best_configs = []
        for config_str, config_metrics in config_performance.items():
            if len(config_metrics) >= 3:  # Sufficient sample size
                avg_time = statistics.mean(m.execution_time for m in config_metrics)
                avg_quality = statistics.mean(m.quality_score for m in config_metrics)
                success_rate = sum(1 for m in config_metrics if m.success) / len(config_metrics)
                
                score = (avg_quality * success_rate) / (avg_time + 1)  # Higher is better
                best_configs.append((score, json.loads(config_str), config_metrics))
                
        if best_configs:
            # Sort by performance score
            best_configs.sort(reverse=True, key=lambda x: x[0])
            best_config = best_configs[0][1]
            
            # Compare with average configuration
            current_config = self._get_average_config(metrics)
            
            for param, best_value in best_config.items():
                if param in current_config:
                    current_value = current_config[param]
                    if best_value != current_value:
                        opportunities.append(OptimizationSuggestion(
                            parameter=param,
                            current_value=current_value,
                            suggested_value=best_value,
                            confidence=0.8,
                            reasoning=f"Top performing configuration uses {best_value} vs current {current_value}",
                            expected_improvement=0.15
                        ))
                        
        return opportunities
        
    def _get_average_config(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate average algorithm configuration"""
        config_values = defaultdict(list)
        
        for metric in metrics:
            for param, value in metric.algorithm_config.items():
                if isinstance(value, (int, float)):
                    config_values[param].append(value)
                    
        return {param: statistics.mean(values) for param, values in config_values.items()}

class AlgorithmOptimizer:
    """Optimizes algorithm parameters based on performance analysis"""
    
    def __init__(self, performance_analyzer: PerformanceAnalyzer):
        self.analyzer = performance_analyzer
        self.optimization_history = []
        self.parameter_ranges = {}
        self.learning_rate = 0.1
        
    def register_parameter(self, name: str, value_range: Tuple[Any, Any], param_type: type = float):
        """Register a parameter for optimization"""
        self.parameter_ranges[name] = {
            "range": value_range,
            "type": param_type,
            "current_value": value_range[0],
            "best_value": value_range[0],
            "best_performance": 0.0
        }
        
    def optimize_parameters(self, task_type: str) -> Dict[str, Any]:
        """Optimize algorithm parameters for a specific task type"""
        trends = self.analyzer.analyze_performance_trends(task_type)
        
        if trends.get("status") == "no_data":
            return {"status": "insufficient_data"}
            
        opportunities = trends.get("optimization_opportunities", [])
        optimizations = {}
        
        for opportunity in opportunities:
            param_name = opportunity.parameter
            
            if param_name in self.parameter_ranges:
                param_info = self.parameter_ranges[param_name]
                
                # Apply learning rate to suggested change
                current_val = param_info["current_value"]
                suggested_val = opportunity.suggested_value
                
                if param_info["type"] == float:
                    new_val = current_val + self.learning_rate * (suggested_val - current_val)
                    # Clamp to valid range
                    min_val, max_val = param_info["range"]
                    new_val = max(min_val, min(max_val, new_val))
                else:
                    new_val = suggested_val
                    
                param_info["current_value"] = new_val
                optimizations[param_name] = new_val
                
                logging.info(f"Optimized parameter {param_name}: {current_val} -> {new_val}")
                
        # Record optimization attempt
        self.optimization_history.append({
            "timestamp": time.time(),
            "task_type": task_type,
            "optimizations": optimizations,
            "performance_before": trends
        })
        
        return {
            "status": "optimized",
            "optimizations": optimizations,
            "reasoning": [op.reasoning for op in opportunities]
        }
        
    def apply_bayesian_optimization(self, task_type: str, n_iterations: int = 10) -> Dict[str, Any]:
        """Apply Bayesian optimization for parameter tuning"""
        try:
            from skopt import gp_minimize
            from skopt.space import Real, Integer
        except ImportError:
            logging.warning("scikit-optimize not available, falling back to simple optimization")
            return self.optimize_parameters(task_type)
            
        # Define search space
        space = []
        param_names = []
        
        for name, info in self.parameter_ranges.items():
            if info["type"] == float:
                min_val, max_val = info["range"]
                space.append(Real(min_val, max_val, name=name))
                param_names.append(name)
            elif info["type"] == int:
                min_val, max_val = info["range"]
                space.append(Integer(min_val, max_val, name=name))
                param_names.append(name)
                
        if not space:
            return {"status": "no_parameters_to_optimize"}
            
        # Objective function
        def objective(params):
            # This would need to be implemented to actually test parameter combinations
            # For now, return a mock score based on historical data
            return np.random.random()  # Placeholder
            
        # Run optimization
        result = gp_minimize(objective, space, n_calls=n_iterations, random_state=42)
        
        # Apply best parameters
        optimizations = {}
        for i, param_name in enumerate(param_names):
            self.parameter_ranges[param_name]["current_value"] = result.x[i]
            optimizations[param_name] = result.x[i]
            
        return {
            "status": "bayesian_optimized",
            "optimizations": optimizations,
            "best_score": -result.fun,
            "n_iterations": n_iterations
        }

class PatternRecognizer:
    """Recognizes patterns in task execution and learns from them"""
    
    def __init__(self, min_pattern_support: int = 5):
        self.min_pattern_support = min_pattern_support
        self.discovered_patterns = {}
        self.pattern_applications = defaultdict(int)
        
    def discover_patterns(self, metrics: List[PerformanceMetric]) -> List[LearningPattern]:
        """Discover patterns in execution data"""
        patterns = []
        
        # Group metrics by context features
        context_groups = defaultdict(list)
        
        for metric in metrics:
            # Create context signature
            context_features = {
                "task_type": metric.task_type,
                "complexity": self._estimate_complexity(metric.context),
                "resource_profile": self._classify_resource_usage(metric.resource_usage)
            }
            
            context_key = json.dumps(context_features, sort_keys=True)
            context_groups[context_key].append(metric)
            
        # Analyze each group for patterns
        for context_str, group_metrics in context_groups.items():
            if len(group_metrics) >= self.min_pattern_support:
                pattern = self._analyze_group_pattern(context_str, group_metrics)
                if pattern:
                    patterns.append(pattern)
                    
        return patterns
        
    def _estimate_complexity(self, context: Dict[str, Any]) -> str:
        """Estimate task complexity from context"""
        complexity_indicators = [
            len(str(context.get("prompt", ""))),
            len(context.get("files", [])),
            context.get("recursion_depth", 0),
            len(context.get("subtasks", []))
        ]
        
        total_complexity = sum(complexity_indicators)
        
        if total_complexity < 50:
            return "low"
        elif total_complexity < 200:
            return "medium"
        else:
            return "high"
            
    def _classify_resource_usage(self, resource_usage: Dict[str, float]) -> str:
        """Classify resource usage pattern"""
        cpu_usage = resource_usage.get("cpu", 0)
        memory_usage = resource_usage.get("memory", 0)
        
        if cpu_usage > 70 and memory_usage > 70:
            return "intensive"
        elif cpu_usage > 50 or memory_usage > 50:
            return "moderate"
        else:
            return "light"
            
    def _analyze_group_pattern(self, context_str: str, metrics: List[PerformanceMetric]) -> Optional[LearningPattern]:
        """Analyze a group of metrics for optimization patterns"""
        if not metrics:
            return None
            
        context = json.loads(context_str)
        
        # Find successful metrics
        successful_metrics = [m for m in metrics if m.success]
        success_rate = len(successful_metrics) / len(metrics)
        
        if success_rate < 0.5:  # Not a successful pattern
            return None
            
        # Analyze algorithm configurations of successful runs
        config_analysis = defaultdict(list)
        
        for metric in successful_metrics:
            for param, value in metric.algorithm_config.items():
                config_analysis[param].append(value)
                
        # Find optimal parameter ranges
        optimization = {}
        for param, values in config_analysis.items():
            if len(values) >= 3:
                if all(isinstance(v, (int, float)) for v in values):
                    optimization[param] = {
                        "mean": statistics.mean(values),
                        "median": statistics.median(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0,
                        "range": (min(values), max(values))
                    }
                    
        pattern_id = hashlib.md5((context_str + str(optimization)).encode()).hexdigest()[:8]
        
        return LearningPattern(
            pattern_id=pattern_id,
            pattern_type="optimization",
            description=f"Optimal configuration for {context['task_type']} tasks with {context['complexity']} complexity",
            conditions=context,
            optimization=optimization,
            success_rate=success_rate,
            sample_size=len(metrics),
            confidence=min(0.95, success_rate * (len(metrics) / 10))
        )
        
    def apply_pattern(self, pattern: LearningPattern, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a learned pattern to current configuration"""
        optimized_config = current_config.copy()
        
        for param, optimization in pattern.optimization.items():
            if param in optimized_config:
                if "mean" in optimization:
                    # Use the mean value from successful runs
                    optimized_config[param] = optimization["mean"]
                    
        self.pattern_applications[pattern.pattern_id] += 1
        
        return optimized_config

class AdaptiveLearningSystem:
    """Main adaptive learning system that coordinates all components"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.learning_data_dir = output_dir / "data" / "learning"
        self.learning_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.performance_analyzer = PerformanceAnalyzer()
        self.algorithm_optimizer = AlgorithmOptimizer(self.performance_analyzer)
        self.pattern_recognizer = PatternRecognizer()
        
        # Learning state
        self.learning_enabled = True
        self.adaptation_history = []
        self.current_adaptations = {}
        
        # Load existing learning data
        self._load_learning_data()
        
    def record_task_performance(self, task_result: Dict[str, Any], algorithm_config: Dict[str, Any]):
        """Record task performance for learning"""
        if not self.learning_enabled:
            return
            
        # Extract performance metrics
        metric = PerformanceMetric(
            timestamp=time.time(),
            task_type=task_result.get("task_type", "unknown"),
            execution_time=task_result.get("execution_time", 0.0),
            success=task_result.get("success", False),
            quality_score=task_result.get("quality_score", 0.5),
            resource_usage=task_result.get("resource_usage", {}),
            context=task_result.get("context", {}),
            algorithm_config=algorithm_config
        )
        
        self.performance_analyzer.record_performance(metric)
        
        # Trigger learning if we have enough data
        if len(self.performance_analyzer.performance_history) % 50 == 0:
            self._trigger_learning_cycle()
            
    def adapt_for_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt algorithm configuration for a specific task"""
        # Apply current adaptations
        base_config = self.current_adaptations.get(task_type, {})
        
        # Apply relevant patterns
        patterns = self._find_applicable_patterns(task_type, context)
        adapted_config = base_config.copy()
        
        for pattern in patterns:
            adapted_config = self.pattern_recognizer.apply_pattern(pattern, adapted_config)
            
        return adapted_config
        
    def _trigger_learning_cycle(self):
        """Trigger a complete learning cycle"""
        logging.info("Starting adaptive learning cycle")
        
        # Analyze recent performance
        recent_metrics = list(self.performance_analyzer.performance_history)[-200:]  # Last 200 tasks
        
        # Discover new patterns
        new_patterns = self.pattern_recognizer.discover_patterns(recent_metrics)
        
        for pattern in new_patterns:
            self.pattern_recognizer.discovered_patterns[pattern.pattern_id] = pattern
            logging.info(f"Discovered new pattern: {pattern.description}")
            
        # Optimize parameters for each task type
        task_types = set(m.task_type for m in recent_metrics)
        
        for task_type in task_types:
            optimization_result = self.algorithm_optimizer.optimize_parameters(task_type)
            
            if optimization_result.get("status") == "optimized":
                self.current_adaptations[task_type] = optimization_result["optimizations"]
                
                adaptation_record = {
                    "timestamp": time.time(),
                    "task_type": task_type,
                    "adaptations": optimization_result["optimizations"],
                    "reasoning": optimization_result.get("reasoning", [])
                }
                self.adaptation_history.append(adaptation_record)
                
                logging.info(f"Adapted parameters for {task_type}: {optimization_result['optimizations']}")
                
        # Save learning data
        self._save_learning_data()
        
    def _find_applicable_patterns(self, task_type: str, context: Dict[str, Any]) -> List[LearningPattern]:
        """Find patterns applicable to current task"""
        applicable_patterns = []
        
        complexity = self.pattern_recognizer._estimate_complexity(context)
        
        for pattern in self.pattern_recognizer.discovered_patterns.values():
            if (pattern.conditions.get("task_type") == task_type and
                pattern.conditions.get("complexity") == complexity and
                pattern.confidence > 0.7):
                applicable_patterns.append(pattern)
                
        # Sort by confidence
        applicable_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return applicable_patterns[:3]  # Top 3 patterns
        
    def _save_learning_data(self):
        """Save learning data to disk"""
        try:
            # Save performance history
            performance_file = self.learning_data_dir / "performance_history.pkl"
            with open(performance_file, 'wb') as f:
                pickle.dump(list(self.performance_analyzer.performance_history), f)
                
            # Save discovered patterns
            patterns_file = self.learning_data_dir / "patterns.json"
            patterns_data = {
                pattern_id: asdict(pattern) 
                for pattern_id, pattern in self.pattern_recognizer.discovered_patterns.items()
            }
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
                
            # Save current adaptations
            adaptations_file = self.learning_data_dir / "adaptations.json"
            with open(adaptations_file, 'w') as f:
                json.dump(self.current_adaptations, f, indent=2)
                
            logging.debug("Learning data saved successfully")
            
        except Exception as e:
            logging.error(f"Failed to save learning data: {e}")
            
    def _load_learning_data(self):
        """Load existing learning data from disk"""
        try:
            # Load performance history
            performance_file = self.learning_data_dir / "performance_history.pkl"
            if performance_file.exists():
                with open(performance_file, 'rb') as f:
                    history = pickle.load(f)
                    for metric in history:
                        self.performance_analyzer.performance_history.append(metric)
                        
            # Load patterns
            patterns_file = self.learning_data_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                    for pattern_id, pattern_dict in patterns_data.items():
                        pattern = LearningPattern(**pattern_dict)
                        self.pattern_recognizer.discovered_patterns[pattern_id] = pattern
                        
            # Load adaptations
            adaptations_file = self.learning_data_dir / "adaptations.json"
            if adaptations_file.exists():
                with open(adaptations_file, 'r') as f:
                    self.current_adaptations = json.load(f)
                    
            logging.info(f"Loaded {len(self.performance_analyzer.performance_history)} performance records")
            logging.info(f"Loaded {len(self.pattern_recognizer.discovered_patterns)} patterns")
            logging.info(f"Loaded adaptations for {len(self.current_adaptations)} task types")
            
        except Exception as e:
            logging.error(f"Failed to load learning data: {e}")
            
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning system state"""
        return {
            "learning_enabled": self.learning_enabled,
            "performance_records": len(self.performance_analyzer.performance_history),
            "discovered_patterns": len(self.pattern_recognizer.discovered_patterns),
            "active_adaptations": len(self.current_adaptations),
            "adaptation_history": len(self.adaptation_history),
            "last_learning_cycle": max([a["timestamp"] for a in self.adaptation_history]) if self.adaptation_history else None
        }
        
    def enable_learning(self):
        """Enable adaptive learning"""
        self.learning_enabled = True
        logging.info("Adaptive learning enabled")
        
    def disable_learning(self):
        """Disable adaptive learning"""
        self.learning_enabled = False
        logging.info("Adaptive learning disabled")