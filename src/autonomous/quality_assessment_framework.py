"""
Quality Assessment Framework for SuperMini
Comprehensive quality measurement for autonomous continuation decisions
"""

import re
import logging
import time
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import ast
import json


class QualityDimension(Enum):
    """Different dimensions of quality assessment"""
    CONTENT_QUALITY = "content_quality"
    TECHNICAL_QUALITY = "technical_quality"
    USER_VALUE = "user_value"
    CONTEXTUAL_RELEVANCE = "contextual_relevance"
    LEARNING_VALUE = "learning_value"
    INNOVATION_FACTOR = "innovation_factor"


@dataclass
class QualityMetrics:
    """Detailed quality metrics for responses"""
    content_completeness: float  # 0.0-1.0
    technical_accuracy: float    # 0.0-1.0
    clarity_score: float         # 0.0-1.0
    depth_score: float           # 0.0-1.0
    innovation_score: float      # 0.0-1.0
    practical_value: float       # 0.0-1.0
    code_quality: float          # 0.0-1.0 (for code tasks)
    documentation_quality: float # 0.0-1.0
    error_rate: float           # 0.0-1.0 (lower is better)
    consistency_score: float    # 0.0-1.0


@dataclass
class QualityAssessment:
    """Comprehensive quality assessment"""
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    detailed_metrics: QualityMetrics
    improvement_areas: List[str]
    strengths: List[str]
    quality_trend: Optional[str]  # "improving", "stable", "declining"
    confidence_level: float
    assessment_reasoning: str


class TaskSpecificAssessor:
    """Task-specific quality assessment logic"""
    
    @staticmethod
    def assess_code_quality(response: str, files: List[str]) -> Dict[str, float]:
        """Assess quality for code tasks"""
        metrics = {}
        
        # Check for code presence
        has_code = bool(re.search(r'```[a-zA-Z]*\n.*?```', response, re.DOTALL))
        if not has_code:
            has_code = bool(re.search(r'(def |class |import |from )', response))
        
        metrics['has_code'] = 1.0 if has_code else 0.0
        
        if has_code:
            # Code structure analysis
            metrics['has_functions'] = 1.0 if 'def ' in response else 0.0
            metrics['has_classes'] = 1.0 if 'class ' in response else 0.0
            metrics['has_imports'] = 1.0 if ('import ' in response or 'from ' in response) else 0.0
            metrics['has_comments'] = 1.0 if '#' in response else 0.0
            metrics['has_docstrings'] = 1.0 if '"""' in response or "'''" in response else 0.0
            
            # Error handling
            metrics['has_error_handling'] = 1.0 if ('try:' in response and 'except' in response) else 0.0
            
            # Code complexity (simplified)
            code_lines = [line for line in response.split('\n') if line.strip() and not line.strip().startswith('#')]
            metrics['code_complexity'] = min(1.0, len(code_lines) / 100.0)  # Normalize to reasonable range
            
            # Syntax validation (basic)
            try:
                # Extract code blocks
                code_blocks = re.findall(r'```python\n(.*?)```', response, re.DOTALL)
                if not code_blocks:
                    code_blocks = re.findall(r'```\n(.*?)```', response, re.DOTALL)
                
                syntax_valid = True
                for code_block in code_blocks:
                    try:
                        ast.parse(code_block)
                    except SyntaxError:
                        syntax_valid = False
                        break
                
                metrics['syntax_valid'] = 1.0 if syntax_valid else 0.0
            except:
                metrics['syntax_valid'] = 0.5  # Uncertain
        else:
            # No code detected, set code-specific metrics to 0
            for key in ['has_functions', 'has_classes', 'has_imports', 'has_comments', 
                       'has_docstrings', 'has_error_handling', 'code_complexity', 'syntax_valid']:
                metrics[key] = 0.0
        
        return metrics
    
    @staticmethod
    def assess_multimedia_quality(response: str, files: List[str]) -> Dict[str, float]:
        """Assess quality for multimedia tasks"""
        metrics = {}
        
        # Analysis depth
        word_count = len(response.split())
        metrics['analysis_depth'] = min(1.0, word_count / 300.0)  # Normalize to 300 words
        
        # Visual analysis indicators
        visual_terms = ['color', 'composition', 'lighting', 'texture', 'style', 'perspective', 
                       'contrast', 'balance', 'focal point', 'artistic', 'visual', 'aesthetic']
        visual_term_count = sum(1 for term in visual_terms if term.lower() in response.lower())
        metrics['visual_analysis_richness'] = min(1.0, visual_term_count / 8.0)
        
        # Cultural/contextual analysis
        context_terms = ['cultural', 'historical', 'context', 'significance', 'meaning', 
                        'symbolism', 'interpretation', 'influence', 'movement', 'period']
        context_term_count = sum(1 for term in context_terms if term.lower() in response.lower())
        metrics['contextual_analysis'] = min(1.0, context_term_count / 5.0)
        
        # Technical analysis
        tech_terms = ['technique', 'medium', 'method', 'process', 'tool', 'material']
        tech_term_count = sum(1 for term in tech_terms if term.lower() in response.lower())
        metrics['technical_analysis'] = min(1.0, tech_term_count / 3.0)
        
        return metrics
    
    @staticmethod
    def assess_rag_quality(response: str, files: List[str]) -> Dict[str, float]:
        """Assess quality for RAG tasks"""
        metrics = {}
        
        # Information synthesis
        word_count = len(response.split())
        metrics['synthesis_depth'] = min(1.0, word_count / 200.0)
        
        # Source references
        has_references = bool(re.search(r'(source|reference|according to|based on)', response, re.IGNORECASE))
        metrics['has_source_references'] = 1.0 if has_references else 0.0
        
        # Factual indicators
        factual_patterns = [r'\d{4}', r'\d+%', r'\d+\.\d+', r'study', r'research', r'findings']
        factual_count = sum(1 for pattern in factual_patterns if re.search(pattern, response))
        metrics['factual_content'] = min(1.0, factual_count / 4.0)
        
        # Analysis quality
        analysis_terms = ['analysis', 'conclusion', 'implication', 'significance', 'impact', 'insight']
        analysis_count = sum(1 for term in analysis_terms if term.lower() in response.lower())
        metrics['analysis_quality'] = min(1.0, analysis_count / 3.0)
        
        return metrics
    
    @staticmethod
    def assess_automation_quality(response: str, files: List[str]) -> Dict[str, float]:
        """Assess quality for automation tasks"""
        metrics = {}
        
        # Script presence
        has_script = bool(re.search(r'(#!/bin/bash|python|\.sh|\.py)', response))
        metrics['has_script'] = 1.0 if has_script else 0.0
        
        # Error handling
        has_error_handling = bool(re.search(r'(try|except|if.*error|error.*handling)', response, re.IGNORECASE))
        metrics['has_error_handling'] = 1.0 if has_error_handling else 0.0
        
        # Logging
        has_logging = bool(re.search(r'(log|print|echo)', response, re.IGNORECASE))
        metrics['has_logging'] = 1.0 if has_logging else 0.0
        
        # Documentation
        has_documentation = bool(re.search(r'(#.*|""".*""")', response))
        metrics['has_documentation'] = 1.0 if has_documentation else 0.0
        
        # Platform considerations
        has_platform_checks = bool(re.search(r'(os\.name|platform|sys\.platform)', response))
        metrics['platform_awareness'] = 1.0 if has_platform_checks else 0.0
        
        return metrics
    
    @staticmethod
    def assess_analytics_quality(response: str, files: List[str]) -> Dict[str, float]:
        """Assess quality for analytics tasks"""
        metrics = {}
        
        # Data analysis indicators
        analysis_libs = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy', 'sklearn']
        lib_count = sum(1 for lib in analysis_libs if lib in response.lower())
        metrics['uses_analysis_libraries'] = min(1.0, lib_count / 3.0)
        
        # Visualization
        viz_terms = ['plot', 'chart', 'graph', 'histogram', 'scatter', 'bar', 'visualization']
        viz_count = sum(1 for term in viz_terms if term.lower() in response.lower())
        metrics['has_visualizations'] = min(1.0, viz_count / 3.0)
        
        # Statistical analysis
        stat_terms = ['mean', 'median', 'std', 'correlation', 'regression', 'distribution', 'statistical']
        stat_count = sum(1 for term in stat_terms if term.lower() in response.lower())
        metrics['statistical_analysis'] = min(1.0, stat_count / 4.0)
        
        # Data insights
        insight_terms = ['insight', 'trend', 'pattern', 'finding', 'conclusion', 'recommendation']
        insight_count = sum(1 for term in insight_terms if term.lower() in response.lower())
        metrics['provides_insights'] = min(1.0, insight_count / 3.0)
        
        return metrics


class QualityAssessmentFramework:
    """
    Comprehensive quality assessment framework
    Evaluates responses across multiple quality dimensions
    """
    
    def __init__(self):
        self.task_assessors = {
            'code': TaskSpecificAssessor.assess_code_quality,
            'multimedia': TaskSpecificAssessor.assess_multimedia_quality,
            'rag': TaskSpecificAssessor.assess_rag_quality,
            'automation': TaskSpecificAssessor.assess_automation_quality,
            'analytics': TaskSpecificAssessor.assess_analytics_quality
        }
        
        # Quality history for trend analysis
        self.quality_history = []
        
        # Dimension weights for different task types
        self.dimension_weights = {
            'code': {
                QualityDimension.TECHNICAL_QUALITY: 0.4,
                QualityDimension.CONTENT_QUALITY: 0.3,
                QualityDimension.USER_VALUE: 0.2,
                QualityDimension.CONTEXTUAL_RELEVANCE: 0.1
            },
            'multimedia': {
                QualityDimension.CONTENT_QUALITY: 0.35,
                QualityDimension.LEARNING_VALUE: 0.25,
                QualityDimension.CONTEXTUAL_RELEVANCE: 0.2,
                QualityDimension.INNOVATION_FACTOR: 0.2
            },
            'rag': {
                QualityDimension.CONTENT_QUALITY: 0.4,
                QualityDimension.CONTEXTUAL_RELEVANCE: 0.25,
                QualityDimension.TECHNICAL_QUALITY: 0.2,
                QualityDimension.USER_VALUE: 0.15
            },
            'automation': {
                QualityDimension.TECHNICAL_QUALITY: 0.4,
                QualityDimension.USER_VALUE: 0.3,
                QualityDimension.CONTENT_QUALITY: 0.2,
                QualityDimension.CONTEXTUAL_RELEVANCE: 0.1
            },
            'analytics': {
                QualityDimension.TECHNICAL_QUALITY: 0.35,
                QualityDimension.CONTENT_QUALITY: 0.25,
                QualityDimension.USER_VALUE: 0.25,
                QualityDimension.LEARNING_VALUE: 0.15
            }
        }
        
        logging.info("QualityAssessmentFramework initialized")
    
    def assess_quality(self, 
                      response: str, 
                      task_type: str, 
                      original_prompt: str,
                      generated_files: List[str] = None) -> QualityAssessment:
        """
        Main quality assessment method
        Returns comprehensive quality assessment
        """
        if generated_files is None:
            generated_files = []
        
        try:
            # Get base quality metrics
            detailed_metrics = self._calculate_detailed_metrics(response, task_type, generated_files)
            
            # Calculate dimension scores
            dimension_scores = self._calculate_dimension_scores(
                response, task_type, original_prompt, detailed_metrics
            )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(dimension_scores, task_type)
            
            # Identify strengths and improvement areas
            strengths, improvement_areas = self._identify_strengths_and_improvements(
                dimension_scores, detailed_metrics, task_type
            )
            
            # Determine quality trend
            quality_trend = self._determine_quality_trend(overall_score)
            
            # Generate assessment reasoning
            reasoning = self._generate_assessment_reasoning(
                overall_score, dimension_scores, strengths, improvement_areas
            )
            
            # Create final assessment
            assessment = QualityAssessment(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                detailed_metrics=detailed_metrics,
                improvement_areas=improvement_areas,
                strengths=strengths,
                quality_trend=quality_trend,
                confidence_level=self._calculate_confidence_level(detailed_metrics),
                assessment_reasoning=reasoning
            )
            
            # Store for trend analysis
            self._store_quality_data(assessment)
            
            return assessment
            
        except Exception as e:
            logging.error(f"Error in quality assessment: {e}")
            return self._create_fallback_assessment(response)
    
    def _calculate_detailed_metrics(self, 
                                   response: str, 
                                   task_type: str,
                                   generated_files: List[str]) -> QualityMetrics:
        """Calculate detailed quality metrics"""
        
        # Base metrics applicable to all task types
        word_count = len(response.split())
        sentence_count = len([s for s in response.split('.') if s.strip()])
        
        # Content completeness (based on length and structure)
        content_completeness = min(1.0, word_count / 150.0)  # Normalize to 150 words
        if sentence_count > 1:
            content_completeness = min(1.0, content_completeness * 1.2)
        
        # Clarity score (based on sentence length and complexity)
        avg_sentence_length = word_count / max(sentence_count, 1)
        clarity_score = max(0.0, 1.0 - (avg_sentence_length - 15) / 50.0)  # Optimal around 15 words
        clarity_score = max(0.2, min(1.0, clarity_score))  # Clamp between 0.2 and 1.0
        
        # Depth score (based on content richness)
        depth_indicators = ['because', 'therefore', 'however', 'furthermore', 'specifically', 
                           'detailed', 'comprehensive', 'analysis', 'example', 'instance']
        depth_count = sum(1 for indicator in depth_indicators if indicator.lower() in response.lower())
        depth_score = min(1.0, depth_count / 5.0)
        
        # Innovation score (based on creative language and concepts)
        innovation_indicators = ['innovative', 'creative', 'novel', 'unique', 'advanced', 
                               'sophisticated', 'alternative', 'optimize', 'enhance', 'improve']
        innovation_count = sum(1 for indicator in innovation_indicators if indicator.lower() in response.lower())
        innovation_score = min(1.0, innovation_count / 4.0)
        
        # Practical value (based on actionable content)
        practical_indicators = ['step', 'process', 'method', 'approach', 'solution', 'implementation',
                              'example', 'guide', 'instruction', 'recommendation']
        practical_count = sum(1 for indicator in practical_indicators if indicator.lower() in response.lower())
        practical_value = min(1.0, practical_count / 4.0)
        
        # Documentation quality (based on explanations and comments)
        doc_indicators = ['explanation', 'describe', 'explain', 'reason', 'purpose', 'why', 'how']
        doc_count = sum(1 for indicator in doc_indicators if indicator.lower() in response.lower())
        documentation_quality = min(1.0, doc_count / 3.0)
        
        # Error rate (based on inconsistencies and unclear statements)
        error_indicators = ['unclear', 'confusing', 'ambiguous', 'incorrect', 'wrong', 'error']
        error_count = sum(1 for indicator in error_indicators if indicator.lower() in response.lower())
        error_rate = min(1.0, error_count / 2.0)  # Higher error count = higher error rate
        
        # Consistency score (based on coherent flow)
        consistency_score = 1.0  # Default high consistency
        # Check for contradictory statements (simplified)
        if 'but' in response.lower() and 'however' in response.lower():
            consistency_score *= 0.9  # Small penalty for potential contradictions
        
        # Task-specific metrics
        task_metrics = {}
        if task_type in self.task_assessors:
            task_metrics = self.task_assessors[task_type](response, generated_files)
        
        # Code quality (specific calculation for code tasks)
        if task_type == 'code':
            code_quality = self._calculate_code_quality_score(task_metrics)
        else:
            code_quality = 0.0  # Not applicable for non-code tasks
        
        # Technical accuracy (based on task-specific metrics)
        technical_accuracy = self._calculate_technical_accuracy(task_metrics, task_type)
        
        return QualityMetrics(
            content_completeness=content_completeness,
            technical_accuracy=technical_accuracy,
            clarity_score=clarity_score,
            depth_score=depth_score,
            innovation_score=innovation_score,
            practical_value=practical_value,
            code_quality=code_quality,
            documentation_quality=documentation_quality,
            error_rate=error_rate,
            consistency_score=consistency_score
        )
    
    def _calculate_code_quality_score(self, task_metrics: Dict[str, float]) -> float:
        """Calculate code quality score from task-specific metrics"""
        if not task_metrics:
            return 0.0
        
        # Weight different code quality factors
        weights = {
            'has_code': 0.3,
            'syntax_valid': 0.25,
            'has_functions': 0.15,
            'has_error_handling': 0.1,
            'has_comments': 0.1,
            'has_docstrings': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in task_metrics:
                total_score += task_metrics[metric] * weight
                total_weight += weight
        
        return total_score / max(total_weight, 0.1)
    
    def _calculate_technical_accuracy(self, task_metrics: Dict[str, float], task_type: str) -> float:
        """Calculate technical accuracy based on task-specific metrics"""
        if not task_metrics:
            return 0.5  # Default neutral score
        
        # Task-specific technical accuracy calculation
        if task_type == 'code':
            key_metrics = ['syntax_valid', 'has_imports', 'has_error_handling']
        elif task_type == 'analytics':
            key_metrics = ['uses_analysis_libraries', 'statistical_analysis', 'provides_insights']
        elif task_type == 'automation':
            key_metrics = ['has_script', 'has_error_handling', 'has_documentation']
        else:
            # For other task types, use available metrics
            key_metrics = list(task_metrics.keys())[:3]
        
        if not key_metrics:
            return 0.5
        
        scores = [task_metrics.get(metric, 0.0) for metric in key_metrics]
        return sum(scores) / len(scores)
    
    def _calculate_dimension_scores(self, 
                                   response: str, 
                                   task_type: str,
                                   original_prompt: str,
                                   detailed_metrics: QualityMetrics) -> Dict[QualityDimension, float]:
        """Calculate scores for each quality dimension"""
        
        dimension_scores = {}
        
        # Content Quality
        dimension_scores[QualityDimension.CONTENT_QUALITY] = (
            detailed_metrics.content_completeness * 0.4 +
            detailed_metrics.depth_score * 0.3 +
            detailed_metrics.clarity_score * 0.3
        )
        
        # Technical Quality
        dimension_scores[QualityDimension.TECHNICAL_QUALITY] = (
            detailed_metrics.technical_accuracy * 0.5 +
            detailed_metrics.code_quality * 0.3 +
            (1.0 - detailed_metrics.error_rate) * 0.2
        )
        
        # User Value
        dimension_scores[QualityDimension.USER_VALUE] = (
            detailed_metrics.practical_value * 0.6 +
            detailed_metrics.clarity_score * 0.4
        )
        
        # Contextual Relevance
        relevance_score = self._assess_contextual_relevance(response, original_prompt)
        dimension_scores[QualityDimension.CONTEXTUAL_RELEVANCE] = relevance_score
        
        # Learning Value
        dimension_scores[QualityDimension.LEARNING_VALUE] = (
            detailed_metrics.documentation_quality * 0.5 +
            detailed_metrics.depth_score * 0.3 +
            detailed_metrics.innovation_score * 0.2
        )
        
        # Innovation Factor
        dimension_scores[QualityDimension.INNOVATION_FACTOR] = (
            detailed_metrics.innovation_score * 0.7 +
            detailed_metrics.practical_value * 0.3
        )
        
        return dimension_scores
    
    def _assess_contextual_relevance(self, response: str, original_prompt: str) -> float:
        """Assess how well the response addresses the original prompt"""
        
        # Extract key terms from prompt
        prompt_words = set(original_prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        prompt_keywords = prompt_words - common_words
        response_keywords = response_words - common_words
        
        if not prompt_keywords:
            return 0.5  # Neutral if no keywords to match
        
        # Calculate keyword overlap
        keyword_overlap = len(prompt_keywords.intersection(response_keywords))
        relevance_score = min(1.0, keyword_overlap / len(prompt_keywords))
        
        # Boost score if response length is appropriate
        if len(response.split()) > 50:  # Substantial response
            relevance_score = min(1.0, relevance_score * 1.2)
        
        return relevance_score
    
    def _calculate_overall_score(self, 
                                dimension_scores: Dict[QualityDimension, float],
                                task_type: str) -> float:
        """Calculate weighted overall quality score"""
        
        weights = self.dimension_weights.get(task_type, {
            QualityDimension.CONTENT_QUALITY: 0.3,
            QualityDimension.TECHNICAL_QUALITY: 0.25,
            QualityDimension.USER_VALUE: 0.25,
            QualityDimension.CONTEXTUAL_RELEVANCE: 0.2
        })
        
        total_score = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = weights.get(dimension, 0.0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / max(total_weight, 0.1)
    
    def _identify_strengths_and_improvements(self, 
                                           dimension_scores: Dict[QualityDimension, float],
                                           detailed_metrics: QualityMetrics,
                                           task_type: str) -> Tuple[List[str], List[str]]:
        """Identify strengths and areas for improvement"""
        
        strengths = []
        improvements = []
        
        # Analyze dimension scores
        for dimension, score in dimension_scores.items():
            dimension_name = dimension.value.replace('_', ' ').title()
            
            if score >= 0.8:
                strengths.append(f"Excellent {dimension_name.lower()}")
            elif score >= 0.6:
                strengths.append(f"Good {dimension_name.lower()}")
            elif score < 0.4:
                improvements.append(f"Improve {dimension_name.lower()}")
        
        # Analyze detailed metrics
        if detailed_metrics.content_completeness < 0.5:
            improvements.append("Provide more comprehensive content")
        
        if detailed_metrics.clarity_score < 0.6:
            improvements.append("Improve clarity and readability")
        
        if detailed_metrics.technical_accuracy < 0.7:
            improvements.append("Enhance technical accuracy")
        
        if detailed_metrics.error_rate > 0.3:
            improvements.append("Reduce errors and inconsistencies")
        
        if detailed_metrics.practical_value < 0.5:
            improvements.append("Increase practical applicability")
        
        # Task-specific recommendations
        if task_type == 'code':
            if detailed_metrics.code_quality < 0.7:
                improvements.append("Improve code quality and best practices")
            if detailed_metrics.documentation_quality < 0.5:
                improvements.append("Add more code documentation")
        
        # Ensure we have at least one strength if overall quality is decent
        if not strengths and len(improvements) <= 2:
            strengths.append("Addresses the core requirements")
        
        return strengths, improvements
    
    def _determine_quality_trend(self, current_score: float) -> Optional[str]:
        """Determine quality trend based on history"""
        
        if len(self.quality_history) < 2:
            return None
        
        recent_scores = [entry['overall_score'] for entry in self.quality_history[-3:]]
        recent_scores.append(current_score)
        
        if len(recent_scores) >= 3:
            # Calculate trend
            first_half = sum(recent_scores[:len(recent_scores)//2]) / (len(recent_scores)//2)
            second_half = sum(recent_scores[len(recent_scores)//2:]) / (len(recent_scores) - len(recent_scores)//2)
            
            difference = second_half - first_half
            
            if difference > 0.1:
                return "improving"
            elif difference < -0.1:
                return "declining"
            else:
                return "stable"
        
        return None
    
    def _calculate_confidence_level(self, metrics: QualityMetrics) -> float:
        """Calculate confidence level in the assessment"""
        
        # Base confidence on consistency and completeness of metrics
        confidence_factors = [
            metrics.consistency_score,
            1.0 - metrics.error_rate,  # Lower error rate = higher confidence
            min(1.0, metrics.content_completeness * 1.2)  # Boost for complete content
        ]
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _generate_assessment_reasoning(self, 
                                     overall_score: float,
                                     dimension_scores: Dict[QualityDimension, float],
                                     strengths: List[str],
                                     improvements: List[str]) -> str:
        """Generate human-readable assessment reasoning"""
        
        reasoning_parts = []
        
        # Overall assessment
        if overall_score >= 0.8:
            reasoning_parts.append("Response demonstrates high quality across multiple dimensions.")
        elif overall_score >= 0.6:
            reasoning_parts.append("Response shows good quality with room for improvement.")
        elif overall_score >= 0.4:
            reasoning_parts.append("Response meets basic requirements but needs enhancement.")
        else:
            reasoning_parts.append("Response requires significant improvement to meet quality standards.")
        
        # Highlight top performing dimension
        best_dimension = max(dimension_scores.items(), key=lambda x: x[1])
        reasoning_parts.append(f"Strongest aspect: {best_dimension[0].value.replace('_', ' ')} "
                             f"({best_dimension[1]:.1%})")
        
        # Mention primary improvement area
        if improvements:
            reasoning_parts.append(f"Primary improvement opportunity: {improvements[0]}")
        
        return " ".join(reasoning_parts)
    
    def _store_quality_data(self, assessment: QualityAssessment) -> None:
        """Store quality data for trend analysis"""
        
        quality_entry = {
            'timestamp': time.time(),
            'overall_score': assessment.overall_score,
            'dimension_scores': {dim.value: score for dim, score in assessment.dimension_scores.items()},
            'confidence': assessment.confidence_level
        }
        
        self.quality_history.append(quality_entry)
        
        # Keep only recent history (last 20 assessments)
        if len(self.quality_history) > 20:
            self.quality_history = self.quality_history[-20:]
    
    def _create_fallback_assessment(self, response: str) -> QualityAssessment:
        """Create a basic fallback assessment when full assessment fails"""
        
        # Simple fallback metrics
        word_count = len(response.split())
        basic_score = min(1.0, word_count / 100.0)  # Very basic scoring
        
        fallback_metrics = QualityMetrics(
            content_completeness=basic_score,
            technical_accuracy=0.5,
            clarity_score=0.5,
            depth_score=basic_score,
            innovation_score=0.3,
            practical_value=0.4,
            code_quality=0.0,
            documentation_quality=0.3,
            error_rate=0.2,
            consistency_score=0.8
        )
        
        dimension_scores = {dim: 0.5 for dim in QualityDimension}
        
        return QualityAssessment(
            overall_score=basic_score,
            dimension_scores=dimension_scores,
            detailed_metrics=fallback_metrics,
            improvement_areas=["Unable to perform detailed assessment"],
            strengths=["Response provided"],
            quality_trend=None,
            confidence_level=0.3,
            assessment_reasoning="Fallback assessment due to processing error"
        )
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality assessment statistics"""
        
        if not self.quality_history:
            return {
                'total_assessments': 0,
                'average_quality': 0.0,
                'quality_trend': None,
                'confidence_level': 0.0
            }
        
        scores = [entry['overall_score'] for entry in self.quality_history]
        confidences = [entry['confidence'] for entry in self.quality_history]
        
        return {
            'total_assessments': len(self.quality_history),
            'average_quality': sum(scores) / len(scores),
            'latest_quality': scores[-1],
            'quality_trend': self._determine_quality_trend(scores[-1]) if len(scores) > 1 else None,
            'average_confidence': sum(confidences) / len(confidences),
            'quality_range': {
                'min': min(scores),
                'max': max(scores)
            }
        }