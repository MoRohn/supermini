"""
Enhancement Decision Engine for SuperMini
Intelligent decision-making for autonomous continuation strategies
"""

import logging
import time
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .enhancement_discovery_engine import EnhancementOpportunity


class EnhancementType(Enum):
    """Types of enhancements that can be discovered"""
    CONTENT_GAP = "content_gap"
    QUALITY_IMPROVEMENT = "quality_improvement"
    TECHNICAL_ENHANCEMENT = "technical_enhancement"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    ERROR_CORRECTION = "error_correction"
    OPTIMIZATION = "optimization"
    FEATURE_ADDITION = "feature_addition"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    SECURITY = "security"


class DecisionStrategy(Enum):
    """Decision strategies for continuation"""
    CONSERVATIVE = "conservative"       # Low risk, proven improvements
    BALANCED = "balanced"              # Balance of risk and reward
    AGGRESSIVE = "aggressive"          # High impact, higher risk
    QUALITY_FOCUSED = "quality_focused" # Prioritize quality improvements
    PERFORMANCE_FOCUSED = "performance_focused" # Prioritize performance


@dataclass
class DecisionContext:
    """Context for making continuation decisions"""
    task_type: str
    iteration_count: int
    max_iterations: int
    execution_time: float
    model_type: str
    user_preferences: Dict[str, Any]
    resource_constraints: Dict[str, float]
    quality_history: List[float]
    success_history: List[bool]


@dataclass
class DecisionRationale:
    """Rationale behind a decision"""
    primary_reason: str
    supporting_factors: List[str]
    risk_assessment: str
    confidence_explanation: str
    alternative_considered: Optional[str]


class DecisionEngine:
    """
    Intelligent decision engine for autonomous continuation
    Uses multi-criteria analysis to make optimal continuation decisions
    """
    
    def __init__(self):
        # Decision weights for different criteria
        self.decision_weights = {
            DecisionStrategy.CONSERVATIVE: {
                'impact_score': 0.3,
                'confidence': 0.4,
                'effort_estimate': 0.2,
                'risk_level': 0.1
            },
            DecisionStrategy.BALANCED: {
                'impact_score': 0.35,
                'confidence': 0.25,
                'effort_estimate': 0.25,
                'risk_level': 0.15
            },
            DecisionStrategy.AGGRESSIVE: {
                'impact_score': 0.5,
                'confidence': 0.2,
                'effort_estimate': 0.15,
                'risk_level': 0.15
            },
            DecisionStrategy.QUALITY_FOCUSED: {
                'impact_score': 0.4,
                'confidence': 0.3,
                'effort_estimate': 0.15,
                'risk_level': 0.15
            },
            DecisionStrategy.PERFORMANCE_FOCUSED: {
                'impact_score': 0.45,
                'confidence': 0.25,
                'effort_estimate': 0.2,
                'risk_level': 0.1
            }
        }
        
        # Learning data
        self.decision_history = []
        self.strategy_performance = {strategy: {'successes': 0, 'attempts': 0} for strategy in DecisionStrategy}
        
        # Task-specific strategy preferences
        self.task_strategy_preferences = {
            'code': DecisionStrategy.QUALITY_FOCUSED,
            'multimedia': DecisionStrategy.BALANCED,
            'rag': DecisionStrategy.CONSERVATIVE,
            'automation': DecisionStrategy.QUALITY_FOCUSED,
            'analytics': DecisionStrategy.PERFORMANCE_FOCUSED
        }
        
        # Risk tolerance thresholds
        self.risk_thresholds = {
            'low': 0.8,      # Continue if confidence > 80%
            'medium': 0.6,   # Continue if confidence > 60%  
            'high': 0.4,     # Continue if confidence > 40%
            'critical': 0.2  # Continue if confidence > 20%
        }
        
        logging.info("DecisionEngine initialized")
    
    def make_continuation_decision(self, 
                                 enhancement_opportunities: List[EnhancementOpportunity],
                                 quality_assessment: Any,
                                 context) -> Any:  # Returns ContinuationPlan
        """
        Main decision-making method
        Returns a ContinuationPlan with continuation decision and strategy
        """
        try:
            # Import here to avoid circular imports
            from .autonomous_continuation_engine import ContinuationPlan, ContinuationType
            
            # If no opportunities, stop continuation
            if not enhancement_opportunities:
                return self._create_stop_plan(ContinuationPlan, ContinuationType, 
                                            "No enhancement opportunities identified")
            
            # Determine optimal strategy for this context
            strategy = self._select_decision_strategy(context)
            
            # Score and rank opportunities using the selected strategy
            scored_opportunities = self._score_opportunities(enhancement_opportunities, strategy)
            
            # Select best opportunity
            best_opportunity = scored_opportunities[0] if scored_opportunities else None
            
            if not best_opportunity:
                return self._create_stop_plan(ContinuationPlan, ContinuationType, 
                                            "No suitable enhancement opportunities found")
            
            # Make final continuation decision
            should_continue, rationale = self._make_final_decision(
                best_opportunity, quality_assessment, context, strategy
            )
            
            if should_continue:
                continuation_plan = self._create_continuation_plan(
                    ContinuationPlan, ContinuationType, best_opportunity, rationale, context
                )
                
                # Log decision for learning
                self._log_decision(strategy, continuation_plan, context)
                
                return continuation_plan
            else:
                return self._create_stop_plan(ContinuationPlan, ContinuationType, rationale.primary_reason)
                
        except Exception as e:
            logging.error(f"Error in continuation decision: {e}")
            # Import here for error case
            from .autonomous_continuation_engine import ContinuationPlan, ContinuationType
            return self._create_stop_plan(ContinuationPlan, ContinuationType, 
                                        f"Decision error: {str(e)}")
    
    def _select_decision_strategy(self, context) -> DecisionStrategy:
        """Select optimal decision strategy based on context"""
        
        # Start with task-specific preference
        base_strategy = self.task_strategy_preferences.get(
            context.task_type, DecisionStrategy.BALANCED
        )
        
        # Adjust based on context factors
        strategy_adjustments = []
        
        # If we're early in iterations, be more aggressive
        if context.iteration_count < context.max_iterations * 0.3:
            strategy_adjustments.append(DecisionStrategy.AGGRESSIVE)
        
        # If we're near the end, be more conservative
        elif context.iteration_count > context.max_iterations * 0.8:
            strategy_adjustments.append(DecisionStrategy.CONSERVATIVE)
        
        # If execution time is high, be more conservative
        if context.execution_time > 30.0:  # 30 seconds
            strategy_adjustments.append(DecisionStrategy.CONSERVATIVE)
        
        # If recent quality has been declining, be more conservative
        if len(context.quality_history) >= 2:
            recent_quality = context.quality_history[-2:]
            if len(recent_quality) == 2 and recent_quality[1] < recent_quality[0]:
                strategy_adjustments.append(DecisionStrategy.CONSERVATIVE)
        
        # If recent successes have been low, be more conservative
        if len(context.success_history) >= 3:
            recent_successes = sum(context.success_history[-3:])
            if recent_successes < 2:  # Less than 2 successes in last 3
                strategy_adjustments.append(DecisionStrategy.CONSERVATIVE)
        
        # Apply strategy adjustments
        if DecisionStrategy.CONSERVATIVE in strategy_adjustments:
            final_strategy = DecisionStrategy.CONSERVATIVE
        elif DecisionStrategy.AGGRESSIVE in strategy_adjustments and len(strategy_adjustments) == 1:
            final_strategy = DecisionStrategy.AGGRESSIVE
        else:
            final_strategy = base_strategy
        
        logging.info(f"Selected decision strategy: {final_strategy.value} for task: {context.task_type}")
        return final_strategy
    
    def _score_opportunities(self, 
                           opportunities: List[EnhancementOpportunity], 
                           strategy: DecisionStrategy) -> List[EnhancementOpportunity]:
        """Score and rank opportunities using the selected strategy"""
        
        weights = self.decision_weights[strategy]
        
        for opportunity in opportunities:
            # Calculate composite score
            impact_component = opportunity.impact_score * weights['impact_score']
            confidence_component = opportunity.confidence * weights['confidence']
            
            # Invert effort estimate (lower effort = higher score)
            effort_component = (1.0 - opportunity.effort_estimate) * weights['effort_estimate']
            
            # Risk level scoring (lower risk = higher score)
            risk_scores = {'low': 1.0, 'medium': 0.7, 'high': 0.4, 'critical': 0.2}
            risk_component = risk_scores.get(opportunity.risk_level, 0.5) * weights['risk_level']
            
            # Calculate total score
            total_score = impact_component + confidence_component + effort_component + risk_component
            
            # Apply strategy-specific bonuses
            if strategy == DecisionStrategy.QUALITY_FOCUSED:
                if opportunity.opportunity_type in [EnhancementType.QUALITY_IMPROVEMENT, 
                                      EnhancementType.DOCUMENTATION]:
                    total_score *= 1.2
            
            elif strategy == DecisionStrategy.PERFORMANCE_FOCUSED:
                if opportunity.opportunity_type in [EnhancementType.OPTIMIZATION, 
                                      EnhancementType.TECHNICAL_ENHANCEMENT]:
                    total_score *= 1.3
            
            # Store score for ranking
            opportunity.priority = total_score
        
        # Sort by score (highest first)
        return sorted(opportunities, key=lambda x: x.priority, reverse=True)
    
    def _make_final_decision(self, 
                           opportunity: EnhancementOpportunity,
                           quality_assessment: Any,
                           context,
                           strategy: DecisionStrategy) -> Tuple[bool, DecisionRationale]:
        """Make final continuation decision based on top opportunity"""
        
        # Check risk tolerance
        risk_threshold = self.risk_thresholds.get(opportunity.risk_level, 0.5)
        
        # Base decision factors
        factors = {
            'confidence_sufficient': opportunity.confidence >= risk_threshold,
            'within_iteration_limit': context.iteration_count < context.max_iterations,
            'reasonable_effort': opportunity.effort_estimate <= 0.8,
            'high_impact': opportunity.impact_score >= 0.5
        }
        
        # Additional context factors
        factors['not_too_slow'] = context.execution_time < 60.0  # 1 minute limit
        factors['quality_acceptable'] = (hasattr(quality_assessment, 'overall_score') and 
                                       quality_assessment.overall_score < 0.9)  # Room for improvement
        
        # Count positive factors
        positive_factors = sum(factors.values())
        total_factors = len(factors)
        
        # Decision logic based on strategy
        if strategy == DecisionStrategy.CONSERVATIVE:
            should_continue = positive_factors >= total_factors - 1  # Almost all factors positive
        elif strategy == DecisionStrategy.AGGRESSIVE:
            should_continue = positive_factors >= total_factors // 2  # At least half positive
        else:  # BALANCED, QUALITY_FOCUSED, PERFORMANCE_FOCUSED
            should_continue = positive_factors >= (total_factors * 2) // 3  # At least 2/3 positive
        
        # Override: Never continue if critical risk without very high confidence
        if opportunity.risk_level == 'critical' and opportunity.confidence < 0.9:
            should_continue = False
        
        # Create rationale
        rationale = self._create_decision_rationale(
            should_continue, opportunity, factors, strategy, positive_factors, total_factors
        )
        
        return should_continue, rationale
    
    def _create_decision_rationale(self, 
                                 should_continue: bool,
                                 opportunity: EnhancementOpportunity,
                                 factors: Dict[str, bool],
                                 strategy: DecisionStrategy,
                                 positive_factors: int,
                                 total_factors: int) -> DecisionRationale:
        """Create detailed rationale for the decision"""
        
        if should_continue:
            primary_reason = f"Selected {opportunity.opportunity_type} enhancement with {opportunity.confidence:.1%} confidence"
            
            supporting_factors = []
            for factor, is_positive in factors.items():
                if is_positive:
                    supporting_factors.append(factor.replace('_', ' ').title())
            
            risk_assessment = f"Risk level {opportunity.risk_level} is acceptable for {strategy.value} strategy"
            confidence_explanation = (f"Confidence {opportunity.confidence:.1%} exceeds threshold for "
                                    f"{opportunity.risk_level} risk level")
            alternative_considered = None
            
        else:
            primary_reason = f"Enhancement not suitable: {positive_factors}/{total_factors} criteria met"
            
            supporting_factors = []
            for factor, is_positive in factors.items():
                if not is_positive:
                    supporting_factors.append(f"Failed: {factor.replace('_', ' ')}")
            
            risk_assessment = f"Risk level {opportunity.risk_level} too high for current context"
            confidence_explanation = (f"Confidence {opportunity.confidence:.1%} insufficient for "
                                    f"{opportunity.risk_level} risk level")
            alternative_considered = "Consider stopping or adjusting strategy"
        
        return DecisionRationale(
            primary_reason=primary_reason,
            supporting_factors=supporting_factors,
            risk_assessment=risk_assessment,
            confidence_explanation=confidence_explanation,
            alternative_considered=alternative_considered
        )
    
    def _create_continuation_plan(self, ContinuationPlan, ContinuationType, 
                                opportunity: EnhancementOpportunity, 
                                rationale: DecisionRationale,
                                context) -> Any:
        """Create a continuation plan from the selected opportunity"""
        
        # Map enhancement type to continuation type
        type_mapping = {
            EnhancementType.CONTENT_GAP: ContinuationType.KNOWLEDGE_EXPANSION,
            EnhancementType.QUALITY_IMPROVEMENT: ContinuationType.ENHANCEMENT,
            EnhancementType.TECHNICAL_ENHANCEMENT: ContinuationType.OPTIMIZATION,
            EnhancementType.KNOWLEDGE_EXPANSION: ContinuationType.KNOWLEDGE_EXPANSION,
            EnhancementType.ERROR_CORRECTION: ContinuationType.ERROR_CORRECTION,
            EnhancementType.OPTIMIZATION: ContinuationType.OPTIMIZATION,
            EnhancementType.FEATURE_ADDITION: ContinuationType.FEATURE_ADDITION,
            EnhancementType.DOCUMENTATION: ContinuationType.ENHANCEMENT,
            EnhancementType.TESTING: ContinuationType.ENHANCEMENT,
            EnhancementType.SECURITY: ContinuationType.ERROR_CORRECTION
        }
        
        continuation_type = type_mapping.get(opportunity.opportunity_type, ContinuationType.ENHANCEMENT)
        
        # Create enhancement prompt
        enhancement_prompt = self._generate_enhancement_prompt(opportunity, context)
        
        # Estimate effort (1-5 scale)
        estimated_effort = max(1, min(5, int(opportunity.effort_estimate * 5)))
        
        return ContinuationPlan(
            should_continue=True,
            continuation_type=continuation_type,
            enhancement_prompt=enhancement_prompt,
            reasoning=rationale.primary_reason,
            expected_improvements=opportunity.specific_improvements,
            risk_level=self._convert_risk_to_float(opportunity.risk_level),
            confidence_score=opportunity.confidence,
            estimated_effort=estimated_effort
        )
    
    def _create_stop_plan(self, ContinuationPlan, ContinuationType, reason: str) -> Any:
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
    
    def _generate_enhancement_prompt(self, opportunity: EnhancementOpportunity, context) -> str:
        """Generate specific enhancement prompt for the opportunity"""
        
        base_prompt = f"**Enhancement Focus: {opportunity.opportunity_type.replace('_', ' ').title()}**\n\n"
        base_prompt += f"{opportunity.description}\n\n"
        
        if opportunity.specific_improvements:
            base_prompt += "**Specific Improvements:**\n"
            for improvement in opportunity.specific_improvements:
                base_prompt += f"- {improvement}\n"
            base_prompt += "\n"
        
        # Add task-specific guidance
        task_guidance = self._get_task_specific_guidance(context.task_type, opportunity.opportunity_type)
        if task_guidance:
            base_prompt += f"**Task-Specific Guidance:**\n{task_guidance}\n\n"
        
        # Add strategy context
        base_prompt += ("Please implement these enhancements while maintaining the existing "
                       "functionality and ensuring the improvements are meaningful and practical.")
        
        return base_prompt
    
    def _get_task_specific_guidance(self, task_type: str, enhancement_type: EnhancementType) -> str:
        """Get task and enhancement type specific guidance"""
        
        guidance_map = {
            ('code', EnhancementType.TECHNICAL_ENHANCEMENT): 
                "Focus on code efficiency, best practices, and maintainability. Ensure backward compatibility.",
            
            ('code', EnhancementType.OPTIMIZATION):
                "Optimize algorithms and data structures. Profile before and after changes when possible.",
            
            ('code', EnhancementType.TESTING):
                "Add comprehensive test cases covering edge cases and error conditions.",
            
            ('multimedia', EnhancementType.KNOWLEDGE_EXPANSION):
                "Provide deeper artistic and cultural context. Include technical analysis of visual elements.",
            
            ('analytics', EnhancementType.OPTIMIZATION):
                "Optimize data processing and visualization performance. Use appropriate statistical methods.",
            
            ('automation', EnhancementType.ERROR_CORRECTION):
                "Add robust error handling and recovery mechanisms. Include logging and monitoring.",
            
            ('rag', EnhancementType.QUALITY_IMPROVEMENT):
                "Improve information accuracy and source attribution. Enhance synthesis quality."
        }
        
        return guidance_map.get((task_type, enhancement_type), "")
    
    def _convert_risk_to_float(self, risk_level: str) -> float:
        """Convert risk level string to float"""
        risk_values = {'low': 0.2, 'medium': 0.5, 'high': 0.7, 'critical': 0.9}
        return risk_values.get(risk_level, 0.5)
    
    def _log_decision(self, strategy: DecisionStrategy, plan: Any, context) -> None:
        """Log decision for learning purposes"""
        decision_record = {
            'timestamp': time.time(),
            'strategy': strategy.value,
            'should_continue': plan.should_continue,
            'continuation_type': plan.continuation_type.value if plan.should_continue else None,
            'confidence': plan.confidence_score,
            'risk_level': plan.risk_level,
            'task_type': context.task_type,
            'iteration': context.iteration_count,
            'execution_time': context.execution_time
        }
        
        self.decision_history.append(decision_record)
        
        # Update strategy tracking
        self.strategy_performance[strategy]['attempts'] += 1
        
        logging.info(f"Decision logged: {strategy.value} -> {'continue' if plan.should_continue else 'stop'}")
    
    def update_learning(self, continuation_record: Dict[str, Any]) -> None:
        """Update learning based on continuation results"""
        
        strategy_name = continuation_record.get('strategy')
        success = continuation_record.get('success', False)
        
        if strategy_name:
            try:
                strategy = DecisionStrategy(strategy_name)
                if success:
                    self.strategy_performance[strategy]['successes'] += 1
                
                # Adjust strategy preferences based on success
                task_type = continuation_record.get('task_type')
                if task_type and success:
                    # Slightly favor successful strategies for task types
                    current_strategy = self.task_strategy_preferences.get(task_type)
                    if strategy != current_strategy and self._strategy_success_rate(strategy) > 0.7:
                        self.task_strategy_preferences[task_type] = strategy
                        logging.info(f"Updated preferred strategy for {task_type}: {strategy.value}")
                
            except ValueError:
                logging.warning(f"Unknown strategy in learning update: {strategy_name}")
    
    def _strategy_success_rate(self, strategy: DecisionStrategy) -> float:
        """Calculate success rate for a strategy"""
        performance = self.strategy_performance[strategy]
        if performance['attempts'] == 0:
            return 0.0
        return performance['successes'] / performance['attempts']
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get decision engine statistics"""
        
        total_decisions = len(self.decision_history)
        if total_decisions == 0:
            return {
                'total_decisions': 0,
                'continuation_rate': 0.0,
                'strategy_performance': {},
                'average_confidence': 0.0
            }
        
        # Calculate statistics
        continuations = sum(1 for d in self.decision_history if d['should_continue'])
        continuation_rate = continuations / total_decisions
        
        confidence_scores = [d['confidence'] for d in self.decision_history]
        average_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Strategy performance
        strategy_stats = {}
        for strategy, performance in self.strategy_performance.items():
            if performance['attempts'] > 0:
                strategy_stats[strategy.value] = {
                    'attempts': performance['attempts'],
                    'successes': performance['successes'],
                    'success_rate': performance['successes'] / performance['attempts']
                }
        
        return {
            'total_decisions': total_decisions,
            'continuation_rate': continuation_rate,
            'strategy_performance': strategy_stats,
            'average_confidence': average_confidence,
            'task_strategy_preferences': {k: v.value for k, v in self.task_strategy_preferences.items()}
        }