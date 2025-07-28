"""
Autonomous Continuation Engine for SuperMini
Replaces simple "Continue" prompts with intelligent enhancement decisions
"""

import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .enhancement_discovery_engine import EnhancementDiscoveryEngine
from .enhancement_decision_engine import DecisionEngine
from .quality_assessment_framework import QualityAssessmentFramework
from .safety_manager import SafetyManager
from ..core.task_intelligence import TaskIntelligence, ResponseAnalyzer


class ContinuationType(Enum):
    """Types of autonomous continuation strategies"""
    ENHANCEMENT = "enhancement"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    TASK_COMPLETION = "task_completion"
    ERROR_CORRECTION = "error_correction"
    OPTIMIZATION = "optimization"
    FEATURE_ADDITION = "feature_addition"


@dataclass
class ContinuationContext:
    """Context for continuation decisions"""
    task_type: str
    original_prompt: str
    current_response: str
    iteration_count: int
    max_iterations: int
    accumulated_results: List[str]
    generated_files: List[str]
    execution_time: float
    quality_scores: Dict[str, float]
    previous_enhancements: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    model_type: str  # "claude" or "ollama"
    quality_history: List[float] = None  # Track quality across iterations
    success_history: List[bool] = None  # Track success/failure across iterations


@dataclass
class ContinuationPlan:
    """Plan for autonomous continuation"""
    should_continue: bool
    continuation_type: ContinuationType
    enhancement_prompt: str
    reasoning: str
    expected_improvements: List[str]
    risk_level: float
    confidence_score: float
    estimated_effort: int  # 1-5 scale


class AutonomousContinuationEngine:
    """
    Main engine for intelligent autonomous continuation
    Replaces simple "Continue" with smart enhancement decisions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Set up cache directory
        import tempfile
        from pathlib import Path
        cache_dir = Path(tempfile.gettempdir()) / "supermini_autonomous"
        cache_dir.mkdir(exist_ok=True)
        
        # Initialize core components
        self.enhancement_discovery = EnhancementDiscoveryEngine(cache_dir)
        self.decision_engine = DecisionEngine()
        self.quality_framework = QualityAssessmentFramework()
        self.safety_manager = SafetyManager()
        
        # Legacy compatibility
        self.task_intelligence = TaskIntelligence()
        self.response_analyzer = ResponseAnalyzer()
        
        # Performance tracking
        self.continuation_history = []
        self.enhancement_metrics = {
            'total_continuations': 0,
            'successful_enhancements': 0,
            'quality_improvements': 0.0,
            'average_confidence': 0.0,
            'time_spent': 0.0
        }
        
        # Configuration
        self.enable_learning = self.config.get('enable_learning', True)
        self.enable_safety_checks = self.config.get('enable_safety_checks', True)
        self.max_enhancement_iterations = self.config.get('max_enhancement_iterations', 10)
        
        logging.info("AutonomousContinuationEngine initialized")
    
    def should_continue_autonomous(self, context: ContinuationContext) -> ContinuationPlan:
        """
        Main decision point - should we continue and how?
        Replaces the old should_continue logic with intelligent analysis
        """
        start_time = time.time()
        
        try:
            # Safety checks first
            if self.enable_safety_checks:
                safety_result = self.safety_manager.validate_continuation(context)
                if not safety_result.is_safe:
                    return ContinuationPlan(
                        should_continue=False,
                        continuation_type=ContinuationType.TASK_COMPLETION,
                        enhancement_prompt="",
                        reasoning=f"Safety check failed: {safety_result.reason}",
                        expected_improvements=[],
                        risk_level=1.0,
                        confidence_score=0.0,
                        estimated_effort=0
                    )
            
            # Check basic continuation limits
            if context.iteration_count >= context.max_iterations:
                return self._create_completion_plan("Maximum iterations reached")
            
            # Discover potential enhancements
            # Note: Using existing discovery engine with file-based approach
            # For response-based analysis, we'll create a simpler approach
            enhancement_opportunities = self._discover_response_enhancements(context)
            
            if not enhancement_opportunities:
                return self._create_completion_plan("No meaningful enhancements found")
            
            # Assess current quality
            quality_assessment = self.quality_framework.assess_quality(
                context.current_response,
                context.task_type,
                context.original_prompt,
                context.generated_files
            )
            
            # Make intelligent decision
            continuation_plan = self.decision_engine.make_continuation_decision(
                enhancement_opportunities,
                quality_assessment,
                context
            )
            
            # Update metrics
            self._update_metrics(continuation_plan, time.time() - start_time)
            
            # Log decision for transparency
            self._log_continuation_decision(continuation_plan, context)
            
            return continuation_plan
            
        except Exception as e:
            logging.error(f"Error in autonomous continuation decision: {e}")
            return self._create_completion_plan(f"Error in continuation logic: {str(e)}")
    
    def generate_enhancement_prompt(self, plan: ContinuationPlan, context: ContinuationContext) -> str:
        """
        Generate intelligent enhancement prompt based on continuation plan
        This replaces the simple "Continue with the task" prompt
        """
        if not plan.should_continue:
            return ""
        
        # Base enhancement prompt from the plan
        enhancement_prompt = plan.enhancement_prompt
        
        # Add context-aware enhancements
        prompt_parts = [
            f"## Autonomous Enhancement - {plan.continuation_type.value.title()}",
            f"",
            f"Previous response analysis:",
            f"- Quality score: {context.quality_scores.get('overall', 0.0):.2f}",
            f"- Iteration: {context.iteration_count + 1}/{context.max_iterations}",
            f"- Enhancement focus: {plan.continuation_type.value}",
            f"",
            f"**Enhancement objective:** {enhancement_prompt}",
            f"",
            f"**Expected improvements:**"
        ]
        
        for improvement in plan.expected_improvements:
            prompt_parts.append(f"- {improvement}")
        
        prompt_parts.extend([
            f"",
            f"**Previous response to enhance:**",
            f"```",
            context.current_response[-1000:] if len(context.current_response) > 1000 else context.current_response,
            f"```",
            f"",
            f"Please provide the enhancement focusing on {plan.continuation_type.value}. "
            f"Build upon the previous response while addressing the identified improvement opportunities."
        ])
        
        # Add task-specific guidance
        task_guidance = self._get_task_specific_enhancement_guidance(context.task_type)
        if task_guidance:
            prompt_parts.extend([f"", f"**Task-specific guidance:**", task_guidance])
        
        return "\n".join(prompt_parts)
    
    def update_from_result(self, plan: ContinuationPlan, context: ContinuationContext, 
                          new_response: str, new_files: List[str]) -> None:
        """
        Update the engine based on continuation results for learning
        """
        if not self.enable_learning:
            return
        
        try:
            # Calculate improvement achieved
            new_quality = self.quality_framework.assess_quality(
                new_response, context.task_type, context.original_prompt, new_files
            )
            
            previous_quality = context.quality_scores.get('overall', 0.0)
            improvement = new_quality.overall_score - previous_quality
            
            # Update learning data
            continuation_record = {
                'timestamp': time.time(),
                'task_type': context.task_type,
                'continuation_type': plan.continuation_type.value,
                'predicted_confidence': plan.confidence_score,
                'actual_improvement': improvement,
                'success': improvement > 0.05,  # 5% improvement threshold
                'context_features': self._extract_context_features(context)
            }
            
            self.continuation_history.append(continuation_record)
            
            # Update component learning
            self.enhancement_discovery.update_learning(continuation_record)
            self.decision_engine.update_learning(continuation_record)
            
            # Update metrics
            if improvement > 0.05:
                self.enhancement_metrics['successful_enhancements'] += 1
            
            self.enhancement_metrics['quality_improvements'] += improvement
            
            logging.info(f"Continuation learning update: improvement={improvement:.3f}, "
                        f"success={improvement > 0.05}")
            
        except Exception as e:
            logging.error(f"Error updating continuation learning: {e}")
    
    def get_continuation_status(self) -> Dict[str, Any]:
        """Get current status and metrics of the continuation engine"""
        return {
            'total_continuations': self.enhancement_metrics['total_continuations'],
            'successful_enhancements': self.enhancement_metrics['successful_enhancements'],
            'success_rate': (
                self.enhancement_metrics['successful_enhancements'] / 
                max(1, self.enhancement_metrics['total_continuations'])
            ),
            'average_quality_improvement': self.enhancement_metrics['quality_improvements'],
            'average_confidence': self.enhancement_metrics['average_confidence'],
            'learning_enabled': self.enable_learning,
            'safety_enabled': self.enable_safety_checks,
            'history_size': len(self.continuation_history)
        }
    
    def _create_completion_plan(self, reason: str) -> ContinuationPlan:
        """Create a plan to stop continuation"""
        return ContinuationPlan(
            should_continue=False,
            continuation_type=ContinuationType.TASK_COMPLETION,
            enhancement_prompt="",
            reasoning=reason,
            expected_improvements=[],
            risk_level=0.0,
            confidence_score=1.0,
            estimated_effort=0
        )
    
    def _update_metrics(self, plan: ContinuationPlan, execution_time: float) -> None:
        """Update internal metrics"""
        if plan.should_continue:
            self.enhancement_metrics['total_continuations'] += 1
            self.enhancement_metrics['average_confidence'] = (
                (self.enhancement_metrics['average_confidence'] * 
                 (self.enhancement_metrics['total_continuations'] - 1) + 
                 plan.confidence_score) / self.enhancement_metrics['total_continuations']
            )
        self.enhancement_metrics['time_spent'] += execution_time
    
    def _log_continuation_decision(self, plan: ContinuationPlan, context: ContinuationContext) -> None:
        """Log continuation decision for transparency"""
        decision_info = {
            'should_continue': plan.should_continue,
            'continuation_type': plan.continuation_type.value if plan.should_continue else None,
            'reasoning': plan.reasoning,
            'confidence': plan.confidence_score,
            'risk_level': plan.risk_level,
            'iteration': context.iteration_count,
            'task_type': context.task_type
        }
        
        logging.info(f"Autonomous continuation decision: {decision_info}")
    
    def _get_task_specific_enhancement_guidance(self, task_type: str) -> str:
        """Get task-specific enhancement guidance"""
        guidance = {
            'code': "Focus on code quality, performance, error handling, and documentation improvements.",
            'multimedia': "Enhance visual analysis depth, provide more creative interpretations, and add contextual insights.",
            'rag': "Improve information synthesis, add more comprehensive analysis, and strengthen source integration.",
            'automation': "Enhance script robustness, add better error handling, and improve cross-platform compatibility.",
            'analytics': "Deepen statistical analysis, add more visualizations, and provide actionable insights."
        }
        return guidance.get(task_type, "Focus on overall quality and completeness improvements.")
    
    def _extract_context_features(self, context: ContinuationContext) -> Dict[str, Any]:
        """Extract features from context for learning"""
        return {
            'task_type': context.task_type,
            'response_length': len(context.current_response),
            'iteration_count': context.iteration_count,
            'files_generated': len(context.generated_files),
            'execution_time': context.execution_time,
            'model_type': context.model_type
        }
    
    # Legacy compatibility methods
    def should_continue(self, response: str, iteration: int, max_iterations: int, 
                       task_type: str, original_prompt: str) -> Tuple[bool, str]:
        """
        Legacy compatibility method for existing SuperMini integration
        Maintains the same interface but uses the new autonomous system
        """
        # Create context from legacy parameters
        context = ContinuationContext(
            task_type=task_type,
            original_prompt=original_prompt,
            current_response=response,
            iteration_count=iteration,
            max_iterations=max_iterations,
            accumulated_results=[response],
            generated_files=[],
            execution_time=0.0,
            quality_scores={'overall': 0.5},  # Default neutral score
            previous_enhancements=[],
            user_preferences={},
            model_type="claude"  # Default assumption
        )
        
        # For legacy compatibility, use simple logic without full autonomous decision
        # This maintains backwards compatibility while providing basic enhancement detection
        
        # Basic continuation logic
        if iteration >= max_iterations:
            return False, f"Reached maximum iterations ({max_iterations})"
        
        # Check if response suggests continuation
        response_lower = response.lower()
        continuation_indicators = [
            'would you like', 'do you want', 'shall I', 'should I', 'need me to',
            'next step', 'continue', 'proceed', 'go ahead', 'ready to',
            'let me know', 'please specify', 'if you need'
        ]
        
        has_continuation_cues = any(indicator in response_lower for indicator in continuation_indicators)
        has_questions = '?' in response
        
        # Simple enhancement detection
        opportunities = self._discover_response_enhancements(context)
        has_enhancements = len(opportunities) > 0
        
        # Decision logic
        if has_enhancements and iteration < max_iterations - 1:
            return True, f"Found {len(opportunities)} enhancement opportunities"
        elif has_continuation_cues or has_questions:
            return True, "Response suggests continuation"
        elif len(response.split()) < 50 and iteration < max_iterations - 2:
            return True, "Response appears brief and could be expanded"
        else:
            return False, "No clear need for continuation"
    
    def _discover_response_enhancements(self, context) -> List:
        """
        Simple response-based enhancement discovery
        Creates basic enhancement opportunities from response analysis
        """
        from .enhancement_discovery_engine import EnhancementOpportunity
        
        opportunities = []
        response = context.current_response
        
        try:
            # Basic content analysis
            word_count = len(response.split())
            has_code = 'def ' in response or 'class ' in response or '```' in response
            has_examples = 'example' in response.lower() or 'for instance' in response.lower()
            
            # Content gap opportunities
            if word_count < 100:
                opportunities.append(EnhancementOpportunity(
                    opportunity_id=f"content_gap_{int(time.time())}",
                    file_path="response_analysis",
                    opportunity_type="content_expansion", 
                    title="Expand Content",
                    description="Response appears brief and could be more comprehensive",
                    impact_score=0.7,
                    effort_estimate=0.3,
                    risk_level="low",
                    confidence=0.8,
                    related_patterns=["brief_response"],
                    code_context={},
                    improvement_suggestions=["Add more details", "Provide examples", "Include explanations"],
                    research_keywords=["content expansion", "detailed explanation"],
                    priority_rank=70,
                    estimated_benefit={"comprehensiveness": 0.8, "user_value": 0.7},
                    timestamp=time.time()
                ))
            
            # Code quality opportunities (for code tasks)
            if context.task_type == 'code' and has_code:
                if 'try:' not in response or 'except' not in response:
                    opportunities.append(EnhancementOpportunity(
                        opportunity_id=f"code_quality_{int(time.time())}",
                        file_path="response_analysis",
                        opportunity_type="technical_enhancement",
                        title="Add Error Handling", 
                        description="Code could benefit from error handling",
                        impact_score=0.8,
                        effort_estimate=0.4,
                        risk_level="low",
                        confidence=0.9,
                        related_patterns=["missing_error_handling"],
                        code_context={},
                        improvement_suggestions=["Add try-except blocks", "Include error validation"],
                        research_keywords=["error handling", "code robustness"],
                        priority_rank=80,
                        estimated_benefit={"code_quality": 0.9, "reliability": 0.8},
                        timestamp=time.time()
                    ))
            
            # Example opportunities
            if not has_examples and context.task_type in ['code', 'automation']:
                opportunities.append(EnhancementOpportunity(
                    opportunity_id=f"examples_{int(time.time())}",
                    file_path="response_analysis", 
                    opportunity_type="knowledge_expansion",
                    title="Add Examples",
                    description="Response would benefit from practical examples",
                    impact_score=0.6,
                    effort_estimate=0.2,
                    risk_level="low",
                    confidence=0.7,
                    related_patterns=["missing_examples"],
                    code_context={},
                    improvement_suggestions=["Add concrete examples", "Include usage demonstrations"],
                    research_keywords=["examples", "practical demonstration"],
                    priority_rank=60,
                    estimated_benefit={"user_value": 0.8, "clarity": 0.7},
                    timestamp=time.time()
                ))
            
            # Quality improvement for all types
            if '?' in response or 'unclear' in response.lower():
                opportunities.append(EnhancementOpportunity(
                    opportunity_id=f"clarity_{int(time.time())}",
                    file_path="response_analysis",
                    opportunity_type="quality_improvement", 
                    title="Improve Clarity",
                    description="Response contains unclear elements that could be clarified",
                    impact_score=0.7,
                    effort_estimate=0.3,
                    risk_level="low",
                    confidence=0.8,
                    related_patterns=["unclear_content"],
                    code_context={},
                    improvement_suggestions=["Clarify ambiguous statements", "Provide clearer explanations"],
                    research_keywords=["clarity", "explanation improvement"],
                    priority_rank=70,
                    estimated_benefit={"clarity": 0.9, "user_value": 0.7},
                    timestamp=time.time()
                ))
            
            # Sort by priority
            opportunities.sort(key=lambda x: x.priority_rank, reverse=True)
            
            logging.info(f"Discovered {len(opportunities)} response-based enhancement opportunities")
            return opportunities
            
        except Exception as e:
            logging.error(f"Error in response enhancement discovery: {e}")
            return []