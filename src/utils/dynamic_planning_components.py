#!/usr/bin/env python3
"""
Dynamic Planning Components for Enhanced Recursive Engine
Supporting classes for intelligent planning and context tracking
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import deque
import json

@dataclass
class PlanPerformanceMetrics:
    """Performance metrics for plan execution"""
    execution_time: float = 0.0
    success_rate: float = 0.0
    resource_efficiency: float = 0.0
    adaptation_frequency: float = 0.0
    learning_rate: float = 0.0
    user_satisfaction: float = 0.0
    
    def update_from_results(self, results: Dict[str, Any]):
        """Update metrics from execution results"""
        if "execution_time" in results:
            self.execution_time = results["execution_time"]
        if "success_rate" in results:
            self.success_rate = results["success_rate"]
        if "resource_efficiency" in results:
            self.resource_efficiency = results["resource_efficiency"]

class PlanPerformanceMonitor:
    """Monitors plan performance and identifies optimization opportunities"""
    
    def __init__(self):
        self.performance_history = deque(maxlen=100)
        self.performance_baselines = {}
        self.improvement_opportunities = []
        
    def record_performance(self, plan_id: str, metrics: PlanPerformanceMetrics):
        """Record performance metrics for a plan"""
        record = {
            "timestamp": time.time(),
            "plan_id": plan_id,
            "metrics": metrics,
            "performance_score": self._calculate_performance_score(metrics)
        }
        
        self.performance_history.append(record)
        self._update_baselines(plan_id, metrics)
        self._identify_improvement_opportunities()
    
    def _calculate_performance_score(self, metrics: PlanPerformanceMetrics) -> float:
        """Calculate overall performance score"""
        weights = {
            "success_rate": 0.4,
            "resource_efficiency": 0.2,
            "execution_time": 0.2,  # Lower is better, so we'll invert
            "adaptation_frequency": 0.1,
            "learning_rate": 0.1
        }
        
        # Normalize execution time (assuming 300s is baseline)
        normalized_exec_time = max(0, 1.0 - (metrics.execution_time / 300.0))
        
        score = (
            metrics.success_rate * weights["success_rate"] +
            metrics.resource_efficiency * weights["resource_efficiency"] +
            normalized_exec_time * weights["execution_time"] +
            metrics.adaptation_frequency * weights["adaptation_frequency"] +
            metrics.learning_rate * weights["learning_rate"]
        )
        
        return min(1.0, max(0.0, score))
    
    def _update_baselines(self, plan_id: str, metrics: PlanPerformanceMetrics):
        """Update performance baselines"""
        if plan_id not in self.performance_baselines:
            self.performance_baselines[plan_id] = {
                "success_rate": metrics.success_rate,
                "resource_efficiency": metrics.resource_efficiency,
                "execution_time": metrics.execution_time,
                "sample_count": 1
            }
        else:
            baseline = self.performance_baselines[plan_id]
            count = baseline["sample_count"]
            
            # Rolling average update
            baseline["success_rate"] = ((baseline["success_rate"] * count) + metrics.success_rate) / (count + 1)
            baseline["resource_efficiency"] = ((baseline["resource_efficiency"] * count) + metrics.resource_efficiency) / (count + 1)
            baseline["execution_time"] = ((baseline["execution_time"] * count) + metrics.execution_time) / (count + 1)
            baseline["sample_count"] = count + 1
    
    def _identify_improvement_opportunities(self):
        """Identify opportunities for improvement"""
        if len(self.performance_history) < 5:
            return
        
        recent_records = list(self.performance_history)[-5:]
        opportunities = []
        
        # Check for declining performance
        scores = [record["performance_score"] for record in recent_records]
        if len(scores) >= 3:
            trend = (scores[-1] + scores[-2]) / 2 - (scores[0] + scores[1]) / 2
            if trend < -0.1:  # Declining trend
                opportunities.append({
                    "type": "performance_decline",
                    "severity": abs(trend),
                    "recommendation": "Consider plan adaptation or strategy change"
                })
        
        # Check for low resource efficiency
        avg_efficiency = sum(record["metrics"].resource_efficiency for record in recent_records) / len(recent_records)
        if avg_efficiency < 0.6:
            opportunities.append({
                "type": "low_resource_efficiency",
                "severity": 1.0 - avg_efficiency,
                "recommendation": "Optimize resource allocation and task scheduling"
            })
        
        # Check for high adaptation frequency (instability)
        avg_adaptation = sum(record["metrics"].adaptation_frequency for record in recent_records) / len(recent_records)
        if avg_adaptation > 0.7:
            opportunities.append({
                "type": "high_adaptation_frequency",
                "severity": avg_adaptation,
                "recommendation": "Improve initial planning to reduce need for adaptations"
            })
        
        self.improvement_opportunities = opportunities

class ContextTracker:
    """Tracks and analyzes context evolution during plan execution"""
    
    def __init__(self):
        self.context_history = deque(maxlen=50)
        self.context_patterns = {}
        self.context_change_triggers = []
        
    def analyze_planning_context(self, prompt: str, task_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze context for planning insights"""
        planning_context = {
            "prompt_complexity": self._analyze_prompt_complexity(prompt),
            "task_type_characteristics": self._get_task_type_characteristics(task_type),
            "historical_patterns": self._find_historical_patterns(prompt, task_type),
            "resource_considerations": self._analyze_resource_needs(prompt, task_type),
            "user_context": context or {}
        }
        
        # Record context for learning
        self._record_context_state(planning_context)
        
        return planning_context
    
    def _analyze_prompt_complexity(self, prompt: str) -> Dict[str, float]:
        """Analyze complexity of the prompt"""
        words = prompt.split()
        sentences = prompt.split('.')
        
        complexity_metrics = {
            "length_complexity": min(1.0, len(words) / 100),
            "sentence_complexity": min(1.0, len(sentences) / 10),
            "keyword_density": self._calculate_keyword_density(prompt),
            "technical_complexity": self._assess_technical_complexity(prompt),
            "ambiguity_level": self._assess_ambiguity_level(prompt)
        }
        
        return complexity_metrics
    
    def _calculate_keyword_density(self, prompt: str) -> float:
        """Calculate density of important keywords"""
        important_keywords = [
            "create", "build", "develop", "implement", "design", "analyze", 
            "optimize", "integrate", "test", "deploy", "automate", "process"
        ]
        
        words = prompt.lower().split()
        keyword_count = sum(1 for word in words if word in important_keywords)
        
        return min(1.0, keyword_count / len(words) * 10)  # Scale up for visibility
    
    def _assess_technical_complexity(self, prompt: str) -> float:
        """Assess technical complexity of the prompt"""
        technical_terms = [
            "algorithm", "database", "api", "framework", "architecture", 
            "protocol", "encryption", "optimization", "integration", "deployment"
        ]
        
        prompt_lower = prompt.lower()
        technical_count = sum(1 for term in technical_terms if term in prompt_lower)
        
        return min(1.0, technical_count / 5)  # Normalize to 0-1
    
    def _assess_ambiguity_level(self, prompt: str) -> float:
        """Assess level of ambiguity in the prompt"""
        ambiguous_words = [
            "maybe", "perhaps", "might", "could", "possibly", "probably",
            "something", "somehow", "somewhere", "good", "better", "nice"
        ]
        
        words = prompt.lower().split()
        ambiguous_count = sum(1 for word in words if word in ambiguous_words)
        
        return min(1.0, ambiguous_count / len(words) * 20)  # Scale up for visibility
    
    def _get_task_type_characteristics(self, task_type: str) -> Dict[str, Any]:
        """Get characteristics specific to the task type"""
        characteristics = {
            "code": {
                "typical_complexity": 0.7,
                "resource_intensity": 0.6,
                "decomposition_benefit": 0.8,
                "common_patterns": ["analyze-design-implement-test", "prototype-refine-optimize"]
            },
            "multimedia": {
                "typical_complexity": 0.5,
                "resource_intensity": 0.8,
                "decomposition_benefit": 0.6,
                "common_patterns": ["input-process-output", "analyze-transform-export"]
            },
            "rag": {
                "typical_complexity": 0.6,
                "resource_intensity": 0.4,
                "decomposition_benefit": 0.7,
                "common_patterns": ["ingest-analyze-extract-summarize", "query-retrieve-synthesize"]
            },
            "automation": {
                "typical_complexity": 0.5,
                "resource_intensity": 0.3,
                "decomposition_benefit": 0.8,
                "common_patterns": ["plan-script-test-deploy", "trigger-process-notify"]
            },
            "analytics": {
                "typical_complexity": 0.7,
                "resource_intensity": 0.5,
                "decomposition_benefit": 0.9,
                "common_patterns": ["collect-clean-analyze-visualize", "explore-model-validate-report"]
            }
        }
        
        return characteristics.get(task_type, {
            "typical_complexity": 0.5,
            "resource_intensity": 0.5,
            "decomposition_benefit": 0.6,
            "common_patterns": ["analyze-implement-validate"]
        })
    
    def _find_historical_patterns(self, prompt: str, task_type: str) -> List[Dict[str, Any]]:
        """Find historical patterns relevant to current context"""
        relevant_patterns = []
        
        # Simple pattern matching based on keywords and task type
        for record in self.context_history:
            if record.get("task_type") == task_type:
                # Calculate similarity based on keyword overlap
                similarity = self._calculate_prompt_similarity(prompt, record.get("prompt", ""))
                
                if similarity > 0.6:  # High similarity threshold
                    relevant_patterns.append({
                        "similarity": similarity,
                        "previous_complexity": record.get("complexity", {}),
                        "success_indicators": record.get("success_indicators", []),
                        "optimization_opportunities": record.get("optimization_opportunities", [])
                    })
        
        return sorted(relevant_patterns, key=lambda x: x["similarity"], reverse=True)[:3]
    
    def _calculate_prompt_similarity(self, prompt1: str, prompt2: str) -> float:
        """Calculate similarity between two prompts"""
        words1 = set(prompt1.lower().split())
        words2 = set(prompt2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _analyze_resource_needs(self, prompt: str, task_type: str) -> Dict[str, float]:
        """Analyze expected resource needs"""
        base_needs = {
            "code": {"cpu": 0.6, "memory": 0.5, "time": 0.7},
            "multimedia": {"cpu": 0.8, "memory": 0.9, "time": 0.6},
            "rag": {"cpu": 0.4, "memory": 0.6, "time": 0.5},
            "automation": {"cpu": 0.3, "memory": 0.3, "time": 0.4},
            "analytics": {"cpu": 0.7, "memory": 0.6, "time": 0.8}
        }
        
        needs = base_needs.get(task_type, {"cpu": 0.5, "memory": 0.5, "time": 0.5})
        
        # Adjust based on prompt complexity
        complexity_factor = len(prompt.split()) / 50  # Normalize around 50 words
        complexity_multiplier = min(1.5, max(0.5, complexity_factor))
        
        adjusted_needs = {
            resource: min(1.0, need * complexity_multiplier)
            for resource, need in needs.items()
        }
        
        return adjusted_needs
    
    def _record_context_state(self, context: Dict[str, Any]):
        """Record current context state for learning"""
        context_record = {
            "timestamp": time.time(),
            "context": context,
            "context_id": f"ctx_{int(time.time() * 1000)}"
        }
        
        self.context_history.append(context_record)
    
    def track_context_evolution(self, plan_id: str, context_changes: List[Dict[str, Any]]):
        """Track how context evolves during plan execution"""
        evolution_record = {
            "timestamp": time.time(),
            "plan_id": plan_id,
            "changes": context_changes,
            "change_frequency": len(context_changes),
            "change_types": [change.get("type", "unknown") for change in context_changes]
        }
        
        self.context_history.append(evolution_record)
        
        # Identify patterns in context changes
        self._analyze_change_patterns(evolution_record)
    
    def _analyze_change_patterns(self, evolution_record: Dict[str, Any]):
        """Analyze patterns in context changes"""
        change_types = evolution_record["change_types"]
        
        # Track frequency of different change types
        for change_type in change_types:
            if change_type not in self.context_patterns:
                self.context_patterns[change_type] = {"count": 0, "plans": set()}
            
            self.context_patterns[change_type]["count"] += 1
            self.context_patterns[change_type]["plans"].add(evolution_record["plan_id"])
        
        # Identify triggers for frequent changes
        if evolution_record["change_frequency"] > 3:  # High change frequency
            self.context_change_triggers.append({
                "timestamp": evolution_record["timestamp"],
                "plan_id": evolution_record["plan_id"],
                "trigger_type": "high_change_frequency",
                "frequency": evolution_record["change_frequency"]
            })
    
    def get_context_insights(self) -> Dict[str, Any]:
        """Get insights about context patterns and trends"""
        if not self.context_history:
            return {"insights": [], "recommendations": []}
        
        insights = []
        recommendations = []
        
        # Analyze change frequency trends
        recent_records = [r for r in self.context_history if "change_frequency" in r][-10:]
        if recent_records:
            avg_change_frequency = sum(r["change_frequency"] for r in recent_records) / len(recent_records)
            
            if avg_change_frequency > 2:
                insights.append(f"High context change frequency detected: {avg_change_frequency:.1f} changes per plan")
                recommendations.append("Consider improving initial planning to reduce need for context changes")
        
        # Analyze most common change types
        if self.context_patterns:
            most_common_change = max(self.context_patterns.items(), key=lambda x: x[1]["count"])
            insights.append(f"Most common context change type: {most_common_change[0]} ({most_common_change[1]['count']} occurrences)")
            
            if most_common_change[1]["count"] > 5:
                recommendations.append(f"Focus on preventing {most_common_change[0]} changes through better initial analysis")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "patterns": self.context_patterns,
            "change_triggers": self.context_change_triggers[-5:]  # Last 5 triggers
        }

class AdaptationEngine:
    """Engine for intelligent task and plan adaptation"""
    
    def __init__(self):
        self.adaptation_strategies = self._initialize_strategies()
        self.adaptation_history = deque(maxlen=100)
        self.success_patterns = {}
        
    def _initialize_strategies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize adaptation strategies"""
        return {
            "simplification": {
                "description": "Simplify task requirements while maintaining core objectives",
                "applicability": ["complexity_too_high", "repeated_failures", "resource_constraints"],
                "success_rate": 0.7,
                "implementation": self._apply_simplification_strategy
            },
            "decomposition": {
                "description": "Break down complex tasks into smaller subtasks",
                "applicability": ["single_complex_task", "unclear_requirements", "multi_step_process"],
                "success_rate": 0.8,
                "implementation": self._apply_decomposition_strategy
            },
            "reordering": {
                "description": "Reorder task execution for better efficiency",
                "applicability": ["dependency_issues", "resource_bottlenecks", "priority_conflicts"],
                "success_rate": 0.6,
                "implementation": self._apply_reordering_strategy
            },
            "context_enhancement": {
                "description": "Enhance task context with additional information",
                "applicability": ["ambiguous_requirements", "missing_context", "unclear_objectives"],
                "success_rate": 0.75,
                "implementation": self._apply_context_enhancement_strategy
            },
            "resource_optimization": {
                "description": "Optimize resource allocation and usage",
                "applicability": ["resource_constraints", "performance_issues", "efficiency_concerns"],
                "success_rate": 0.65,
                "implementation": self._apply_resource_optimization_strategy
            }
        }
    
    def recommend_adaptation(self, context: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """Recommend the best adaptation strategy"""
        applicable_strategies = []
        
        for strategy_name, strategy_info in self.adaptation_strategies.items():
            applicability_score = self._calculate_applicability_score(strategy_info["applicability"], issues)
            
            if applicability_score > 0.5:
                applicable_strategies.append({
                    "name": strategy_name,
                    "info": strategy_info,
                    "applicability_score": applicability_score,
                    "expected_success": strategy_info["success_rate"] * applicability_score
                })
        
        if not applicable_strategies:
            return {"strategy": None, "confidence": 0.0, "rationale": "No applicable strategies found"}
        
        # Select best strategy
        best_strategy = max(applicable_strategies, key=lambda x: x["expected_success"])
        
        return {
            "strategy": best_strategy["name"],
            "confidence": best_strategy["expected_success"],
            "rationale": best_strategy["info"]["description"],
            "implementation": best_strategy["info"]["implementation"]
        }
    
    def _calculate_applicability_score(self, applicability_conditions: List[str], issues: List[str]) -> float:
        """Calculate how applicable a strategy is to current issues"""
        if not issues:
            return 0.0
        
        matches = 0
        for condition in applicability_conditions:
            if any(condition.lower() in issue.lower() for issue in issues):
                matches += 1
        
        return matches / len(applicability_conditions) if applicability_conditions else 0.0
    
    def _apply_simplification_strategy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply simplification strategy"""
        # This would be implemented to actually simplify tasks
        return {
            "success": True,
            "changes": ["Simplified task requirements", "Reduced complexity"],
            "new_task_data": task_data  # Placeholder
        }
    
    def _apply_decomposition_strategy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decomposition strategy"""
        return {
            "success": True,
            "changes": ["Decomposed into subtasks", "Added dependency management"],
            "new_task_data": task_data  # Placeholder
        }
    
    def _apply_reordering_strategy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply reordering strategy"""
        return {
            "success": True,
            "changes": ["Reordered task execution", "Optimized dependencies"],
            "new_task_data": task_data  # Placeholder
        }
    
    def _apply_context_enhancement_strategy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply context enhancement strategy"""
        return {
            "success": True,
            "changes": ["Enhanced task context", "Added clarifying information"],
            "new_task_data": task_data  # Placeholder
        }
    
    def _apply_resource_optimization_strategy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resource optimization strategy"""
        return {
            "success": True,
            "changes": ["Optimized resource allocation", "Improved efficiency"],
            "new_task_data": task_data  # Placeholder
        }
    
    def record_adaptation_result(self, strategy_name: str, success: bool, context: Dict[str, Any]):
        """Record the result of an adaptation"""
        adaptation_record = {
            "timestamp": time.time(),
            "strategy": strategy_name,
            "success": success,
            "context": context
        }
        
        self.adaptation_history.append(adaptation_record)
        
        # Update strategy success rates
        if strategy_name in self.adaptation_strategies:
            strategy = self.adaptation_strategies[strategy_name]
            current_rate = strategy["success_rate"]
            
            # Simple moving average update
            new_rate = (current_rate * 0.9) + (1.0 if success else 0.0) * 0.1
            strategy["success_rate"] = new_rate
        
        logging.info(f"Recorded adaptation result: {strategy_name} - {'Success' if success else 'Failure'}")