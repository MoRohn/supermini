"""
Autonomous decision-making system for SuperMini task processing.
This module provides intelligent parameter determination and response analysis.
"""

import re
from typing import Dict, Tuple, List, Optional


class TaskIntelligence:
    """Autonomous decision-making for task processing"""
    
    # Task-specific temperature profiles for optimal performance
    TEMPERATURE_PROFILES = {
        'code': {'min': 0.2, 'max': 0.4, 'default': 0.3},
        'multimedia': {'min': 0.6, 'max': 0.8, 'default': 0.7},
        'rag': {'min': 0.3, 'max': 0.5, 'default': 0.4},
        'automation': {'min': 0.1, 'max': 0.3, 'default': 0.2},
        'analytics': {'min': 0.2, 'max': 0.4, 'default': 0.3},
        'exploration': {'min': 0.7, 'max': 0.9, 'default': 0.8},
        'enhancement': {'min': 0.4, 'max': 0.6, 'default': 0.5}
    }
    
    # Task-specific continuation limits
    CONTINUATION_LIMITS = {
        'code': {'min': 2, 'max': 5, 'default': 3},
        'multimedia': {'min': 1, 'max': 3, 'default': 2},
        'rag': {'min': 1, 'max': 4, 'default': 2},
        'automation': {'min': 2, 'max': 4, 'default': 3},
        'analytics': {'min': 3, 'max': 8, 'default': 5},
        'exploration': {'min': 3, 'max': 10, 'default': 6},
        'enhancement': {'min': 1, 'max': 5, 'default': 3}
    }
    
    def __init__(self):
        self.context_memory = {}
        self.success_patterns = {}
    
    def determine_optimal_temperature(self, prompt: str, task_type: str, context: dict = None) -> float:
        """Dynamically calculate optimal temperature based on task and context"""
        profile = self.TEMPERATURE_PROFILES.get(task_type, self.TEMPERATURE_PROFILES['code'])
        base_temp = profile['default']
        
        # Analyze prompt for complexity and creativity requirements
        complexity_score = self._analyze_prompt_complexity(prompt)
        creativity_score = self._analyze_creativity_requirements(prompt)
        
        # Adjust based on context
        if context:
            # Lower temperature for error recovery
            if context.get('retry_count', 0) > 0:
                base_temp = max(profile['min'], base_temp - 0.1 * context['retry_count'])
            
            # Adjust based on previous success patterns
            if context.get('previous_success', True):
                base_temp = min(profile['max'], base_temp + 0.05)
            else:
                base_temp = max(profile['min'], base_temp - 0.1)
        
        # Apply complexity and creativity adjustments
        if task_type in ['multimedia', 'exploration']:
            # For creative tasks, higher complexity and creativity increase temperature
            adjustment = (complexity_score + creativity_score) * 0.1
            base_temp = min(profile['max'], base_temp + adjustment)
        else:
            # For analytical tasks, higher complexity decreases temperature for precision
            adjustment = complexity_score * 0.1
            base_temp = max(profile['min'], base_temp - adjustment)
        
        return round(base_temp, 2)
    
    def calculate_max_iterations(self, task_type: str, complexity_score: float, prompt_length: int = 0) -> int:
        """Dynamic iteration limit calculation based on task characteristics"""
        limits = self.CONTINUATION_LIMITS.get(task_type, self.CONTINUATION_LIMITS['code'])
        base_limit = limits['default']
        
        # Adjust based on complexity
        if complexity_score > 0.7:
            base_limit = min(limits['max'], base_limit + 2)
        elif complexity_score < 0.3:
            base_limit = max(limits['min'], base_limit - 1)
        
        # Adjust based on prompt length (longer prompts may need more iterations)
        if prompt_length > 500:
            base_limit = min(limits['max'], base_limit + 1)
        
        return base_limit
    
    def get_task_specific_prompts(self, task_type: str) -> Dict[str, str]:
        """Get optimized system prompts for each task type"""
        prompts = {
            'code': """You are an expert software engineer. Focus on:
- Writing clean, efficient, and well-documented code
- Following best practices and design patterns
- Including error handling and edge cases
- Providing clear explanations of your implementation choices
- Ensuring code is production-ready and maintainable""",

            'multimedia': """You are an expert visual analyst and creative professional. Focus on:
- Providing detailed, insightful analysis of visual content
- Identifying artistic techniques, composition, and visual elements
- Explaining context, cultural significance, and creative choices
- Offering creative and imaginative interpretations
- Being thorough and descriptive in your observations""",

            'rag': """You are a research specialist and information synthesizer. Focus on:
- Accurately extracting and synthesizing information from documents
- Providing well-sourced and factual responses
- Maintaining context and relevance to the query
- Organizing information clearly and logically
- Distinguishing between facts and interpretations""",

            'automation': """You are a systems automation expert. Focus on:
- Creating reliable, robust automation scripts
- Including comprehensive error handling and logging
- Providing clear documentation and usage instructions
- Ensuring cross-platform compatibility where possible
- Building in safety checks and validation steps""",

            'analytics': """You are a data science expert and statistical analyst. Focus on:
- Providing methodical, rigorous data analysis
- Using appropriate statistical methods and visualizations
- Explaining your analytical approach and assumptions
- Identifying patterns, trends, and actionable insights
- Ensuring reproducible and well-documented analysis""",

            'exploration': """You are a creative problem-solver and innovator. Focus on:
- Exploring multiple approaches and perspectives
- Thinking outside conventional boundaries
- Generating novel ideas and creative solutions
- Connecting seemingly unrelated concepts
- Encouraging experimentation and discovery""",

            'enhancement': """You are a system improvement specialist. Focus on:
- Identifying specific, actionable improvement opportunities
- Providing practical, implementable solutions
- Considering performance, maintainability, and user experience
- Balancing innovation with stability and reliability
- Delivering incremental, measurable enhancements"""
        }
        
        return {
            'system_prompt': prompts.get(task_type, prompts['code']),
            'context_instructions': f"This is a {task_type} task. Apply {task_type}-specific expertise and approaches."
        }
    
    def _analyze_prompt_complexity(self, prompt: str) -> float:
        """Analyze prompt complexity (0.0-1.0)"""
        complexity_indicators = [
            'complex', 'detailed', 'comprehensive', 'advanced', 'sophisticated',
            'multi-step', 'elaborate', 'intricate', 'thorough', 'extensive'
        ]
        
        prompt_lower = prompt.lower()
        complexity_count = sum(1 for indicator in complexity_indicators if indicator in prompt_lower)
        
        # Factor in length and sentence complexity
        word_count = len(prompt.split())
        sentence_count = len([s for s in prompt.split('.') if s.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Normalize complexity score
        indicator_score = min(1.0, complexity_count / 5.0)
        length_score = min(1.0, word_count / 500.0)
        sentence_complexity = min(1.0, avg_sentence_length / 20.0)
        
        return (indicator_score + length_score + sentence_complexity) / 3.0
    
    def _analyze_creativity_requirements(self, prompt: str) -> float:
        """Analyze creativity requirements in prompt (0.0-1.0)"""
        creativity_indicators = [
            'creative', 'innovative', 'unique', 'original', 'artistic', 'design',
            'brainstorm', 'imagine', 'invent', 'explore', 'experiment', 'novel'
        ]
        
        prompt_lower = prompt.lower()
        creativity_count = sum(1 for indicator in creativity_indicators if indicator in prompt_lower)
        
        return min(1.0, creativity_count / 4.0)


class ResponseAnalyzer:
    """Analyze AI responses for quality and completeness"""
    
    def __init__(self):
        self.quality_patterns = {
            'completion_indicators': [
                r'(complete|finished|done|ready|final)',
                r'(here is|here are|I have|I\'ve)\s+(created|generated|built|made)',
                r'(this completes|task completed|finished with)',
            ],
            'continuation_cues': [
                r'(would you like|do you want|shall I|should I|need me to)',
                r'(next step|continue|proceed|go ahead|ready to)',
                r'(any questions|need clarification|want me to)',
                r'(let me know|please specify|if you need)',
            ],
            'error_indicators': [
                r'(error|failed|couldn\'t|unable|can\'t)',
                r'(issue|problem|trouble|difficulty)',
                r'(try again|retry|attempt|fix)',
            ],
            'code_quality': [
                r'(function|class|def |import |from )',
                r'(#.*|//.*|/\*.*\*/)',  # Comments
                r'(\{|\}|\(|\)|;)',      # Code structure
            ],
        }
    
    def analyze_completeness(self, response: str, original_prompt: str, task_type: str) -> float:
        """Score response completeness (0.0-1.0)"""
        if not response or not response.strip():
            return 0.0
        
        completeness_score = 0.0
        
        # Check for completion indicators
        completion_matches = self._count_pattern_matches(response, self.quality_patterns['completion_indicators'])
        if completion_matches > 0:
            completeness_score += 0.4
        
        # Task-specific completeness checks
        if task_type == 'code':
            completeness_score += self._analyze_code_completeness(response) * 0.6
        elif task_type == 'multimedia':
            completeness_score += self._analyze_multimedia_completeness(response) * 0.6
        elif task_type == 'analytics':
            completeness_score += self._analyze_analytics_completeness(response) * 0.6
        else:
            # General completeness based on response length and structure
            word_count = len(response.split())
            if word_count > 50:
                completeness_score += 0.3
            if word_count > 200:
                completeness_score += 0.3
        
        return min(1.0, completeness_score)
    
    def detect_continuation_cues(self, response: str) -> dict:
        """Identify specific continuation needs"""
        cues = {
            'has_question': False,
            'needs_clarification': False,
            'suggests_continuation': False,
            'has_errors': False,
            'confidence': 0.0
        }
        
        # Check for continuation patterns
        continuation_matches = self._count_pattern_matches(response, self.quality_patterns['continuation_cues'])
        error_matches = self._count_pattern_matches(response, self.quality_patterns['error_indicators'])
        
        # Question detection (more sophisticated than original)
        has_question = '?' in response.split('.')[-1] or continuation_matches > 0
        cues['has_question'] = has_question
        
        # Error detection
        cues['has_errors'] = error_matches > 0
        
        # Clarification needs
        clarification_terms = ['clarify', 'specify', 'unclear', 'ambiguous', 'which', 'what exactly']
        cues['needs_clarification'] = any(term in response.lower() for term in clarification_terms)
        
        # Continuation suggestions
        cues['suggests_continuation'] = continuation_matches > 0
        
        # Calculate overall confidence for continuation
        if cues['has_errors']:
            cues['confidence'] = 0.8  # High confidence to continue for error correction
        elif cues['needs_clarification']:
            cues['confidence'] = 0.6  # Medium confidence for clarification
        elif cues['suggests_continuation']:
            cues['confidence'] = 0.4  # Lower confidence for optional continuation
        elif cues['has_question']:
            cues['confidence'] = 0.5  # Medium confidence for questions
        
        return cues
    
    def should_continue(self, response: str, iteration: int, max_iterations: int, task_type: str, original_prompt: str) -> Tuple[bool, str]:
        """Intelligent continuation decision with reasoning"""
        if iteration >= max_iterations:
            return False, f"Reached maximum iterations ({max_iterations})"
        
        # Analyze response quality
        completeness = self.analyze_completeness(response, original_prompt, task_type)
        cues = self.detect_continuation_cues(response)
        
        # Decision logic
        if completeness >= 0.8 and not cues['has_errors'] and not cues['needs_clarification']:
            return False, "Response appears complete and high quality"
        
        if cues['has_errors'] and iteration < max_iterations - 1:
            return True, "Continuing to address errors"
        
        if cues['needs_clarification'] and iteration < max_iterations - 2:
            return True, "Continuing to provide clarification"
        
        if cues['suggests_continuation'] and completeness < 0.6:
            return True, "Continuing as suggested by AI response"
        
        if completeness < 0.4 and iteration < max_iterations - 1:
            return True, "Response appears incomplete"
        
        return False, "No clear need for continuation"
    
    def _count_pattern_matches(self, text: str, patterns: List[str]) -> int:
        """Count matches for a list of regex patterns"""
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count
    
    def _analyze_code_completeness(self, response: str) -> float:
        """Analyze code response completeness"""
        code_indicators = self._count_pattern_matches(response, self.quality_patterns['code_quality'])
        
        # Check for basic code structure
        has_functions = bool(re.search(r'def\s+\w+|function\s+\w+|class\s+\w+', response))
        has_imports = bool(re.search(r'import\s+\w+|from\s+\w+', response))
        has_comments = bool(re.search(r'#.*|//.*', response))
        
        completeness = 0.0
        if code_indicators > 0:
            completeness += 0.4
        if has_functions:
            completeness += 0.3
        if has_imports:
            completeness += 0.2
        if has_comments:
            completeness += 0.1
        
        return completeness
    
    def _analyze_multimedia_completeness(self, response: str) -> float:
        """Analyze multimedia response completeness"""
        analysis_indicators = ['description', 'analysis', 'details', 'shows', 'depicts', 'contains']
        word_count = len(response.split())
        
        completeness = 0.0
        indicator_count = sum(1 for indicator in analysis_indicators if indicator in response.lower())
        
        if indicator_count > 0:
            completeness += 0.5
        if word_count > 100:
            completeness += 0.3
        if word_count > 300:
            completeness += 0.2
        
        return completeness
    
    def _analyze_analytics_completeness(self, response: str) -> float:
        """Analyze analytics response completeness"""
        analytics_indicators = ['data', 'analysis', 'statistics', 'chart', 'graph', 'correlation', 'trend']
        code_present = bool(re.search(r'import|pandas|matplotlib|seaborn|numpy', response))
        
        completeness = 0.0
        indicator_count = sum(1 for indicator in analytics_indicators if indicator in response.lower())
        
        if indicator_count > 0:
            completeness += 0.4
        if code_present:
            completeness += 0.4
        if len(response.split()) > 200:
            completeness += 0.2
        
        return completeness