"""
Enhanced Discovery Engine for SuperMini
Sophisticated enhancement detection with ML-powered analysis and pattern recognition
"""

import ast
import inspect
import logging
import time
import json
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from collections import defaultdict, Counter
import sqlite3
from threading import Lock
import re

# ML and analysis imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available. Using fallback analysis methods.")

@dataclass
class CodeMetrics:
    """Comprehensive code metrics"""
    file_path: str
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    complexity_score: float
    maintainability_index: float
    technical_debt_score: float
    performance_score: float
    security_score: float
    test_coverage: float
    documentation_score: float
    code_smells: List[str]
    dependencies: List[str]
    api_usage: Dict[str, int]
    timestamp: float

@dataclass
class EnhancementOpportunity:
    """Enhanced opportunity with detailed analysis"""
    opportunity_id: str
    file_path: str
    opportunity_type: str
    title: str
    description: str
    impact_score: float
    effort_estimate: float
    risk_level: str
    confidence: float
    related_patterns: List[str]
    code_context: Dict[str, Any]
    improvement_suggestions: List[str]
    research_keywords: List[str]
    priority_rank: int
    estimated_benefit: Dict[str, float]
    timestamp: float

@dataclass
class CodeContext:
    """Detailed code context for opportunities"""
    function_name: Optional[str]
    class_name: Optional[str]
    module_name: str
    line_range: Tuple[int, int]
    ast_node_type: str
    surrounding_code: str
    dependencies_used: List[str]
    complexity_metrics: Dict[str, float]

class CodePatternMatcher:
    """Advanced pattern matching for code analysis"""
    
    def __init__(self):
        self.patterns = {
            'performance_antipatterns': [
                {
                    'name': 'nested_loop_with_append',
                    'pattern': self._detect_nested_loop_append,
                    'severity': 'high',
                    'description': 'Nested loops with list append operations'
                },
                {
                    'name': 'string_concatenation_in_loop',
                    'pattern': self._detect_string_concat_loop,
                    'severity': 'medium',
                    'description': 'String concatenation inside loops'
                },
                {
                    'name': 'inefficient_data_structure',
                    'pattern': self._detect_inefficient_data_structures,
                    'severity': 'medium',
                    'description': 'Use of inefficient data structures'
                },
                {
                    'name': 'repeated_computation',
                    'pattern': self._detect_repeated_computation,
                    'severity': 'high',
                    'description': 'Repeated expensive computations'
                }
            ],
            'maintainability_issues': [
                {
                    'name': 'long_parameter_list',
                    'pattern': self._detect_long_parameter_list,
                    'severity': 'medium',
                    'description': 'Functions with too many parameters'
                },
                {
                    'name': 'deep_nesting',
                    'pattern': self._detect_deep_nesting,
                    'severity': 'high',
                    'description': 'Deeply nested code structures'
                },
                {
                    'name': 'large_class',
                    'pattern': self._detect_large_class,
                    'severity': 'medium',
                    'description': 'Classes with too many methods or lines'
                },
                {
                    'name': 'duplicate_code',
                    'pattern': self._detect_duplicate_code,
                    'severity': 'high',
                    'description': 'Duplicate or similar code blocks'
                }
            ],
            'security_vulnerabilities': [
                {
                    'name': 'dangerous_eval',
                    'pattern': self._detect_dangerous_eval,
                    'severity': 'critical',
                    'description': 'Use of eval() or exec() with untrusted input'
                },
                {
                    'name': 'sql_injection_risk',
                    'pattern': self._detect_sql_injection_risk,
                    'severity': 'critical',
                    'description': 'Potential SQL injection vulnerabilities'
                },
                {
                    'name': 'hardcoded_secrets',
                    'pattern': self._detect_hardcoded_secrets,
                    'severity': 'critical',
                    'description': 'Hardcoded passwords or API keys'
                },
                {
                    'name': 'unsafe_deserialization',
                    'pattern': self._detect_unsafe_deserialization,
                    'severity': 'high',
                    'description': 'Unsafe deserialization operations'
                }
            ],
            'modern_improvements': [
                {
                    'name': 'missing_type_hints',
                    'pattern': self._detect_missing_type_hints,
                    'severity': 'low',
                    'description': 'Functions without type hints'
                },
                {
                    'name': 'old_string_formatting',
                    'pattern': self._detect_old_string_formatting,
                    'severity': 'low',
                    'description': 'Old-style string formatting'
                },
                {
                    'name': 'missing_async_opportunities',
                    'pattern': self._detect_async_opportunities,
                    'severity': 'medium',
                    'description': 'I/O operations that could be async'
                },
                {
                    'name': 'outdated_patterns',
                    'pattern': self._detect_outdated_patterns,
                    'severity': 'low',
                    'description': 'Usage of outdated coding patterns'
                }
            ]
        }
        
    def analyze_patterns(self, file_path: str, ast_tree: ast.AST) -> List[Dict[str, Any]]:
        """Analyze code for all patterns"""
        detected_patterns = []
        
        for category, patterns in self.patterns.items():
            for pattern_info in patterns:
                try:
                    matches = pattern_info['pattern'](file_path, ast_tree)
                    for match in matches:
                        detected_patterns.append({
                            'category': category,
                            'name': pattern_info['name'],
                            'severity': pattern_info['severity'],
                            'description': pattern_info['description'],
                            'location': match['location'],
                            'context': match['context'],
                            'suggestions': match.get('suggestions', [])
                        })
                except Exception as e:
                    logging.error(f"Pattern detection failed for {pattern_info['name']}: {e}")
                    
        return detected_patterns
        
    def _detect_nested_loop_append(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect nested loops with append operations"""
        matches = []
        
        class NestedLoopVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.found_patterns = []
                
            def visit_For(self, node):
                self.loop_depth += 1
                self.generic_visit(node)
                self.loop_depth -= 1
                
            def visit_While(self, node):
                self.loop_depth += 1
                self.generic_visit(node)
                self.loop_depth -= 1
                
            def visit_Call(self, node):
                if (self.loop_depth >= 2 and 
                    isinstance(node.func, ast.Attribute) and 
                    node.func.attr == 'append'):
                    
                    self.found_patterns.append({
                        'location': {'line': getattr(node, 'lineno', 0)},
                        'context': {'loop_depth': self.loop_depth},
                        'suggestions': [
                            'Consider using list comprehensions',
                            'Pre-allocate list size if known',
                            'Use numpy arrays for numerical data'
                        ]
                    })
                    
                self.generic_visit(node)
                
        visitor = NestedLoopVisitor()
        visitor.visit(tree)
        return visitor.found_patterns
        
    def _detect_string_concat_loop(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect string concatenation in loops"""
        matches = []
        
        class StringConcatVisitor(ast.NodeVisitor):
            def __init__(self):
                self.in_loop = False
                self.found_patterns = []
                
            def visit_For(self, node):
                old_in_loop = self.in_loop
                self.in_loop = True
                self.generic_visit(node)
                self.in_loop = old_in_loop
                
            def visit_While(self, node):
                old_in_loop = self.in_loop
                self.in_loop = True
                self.generic_visit(node)
                self.in_loop = old_in_loop
                
            def visit_AugAssign(self, node):
                if (self.in_loop and 
                    isinstance(node.op, ast.Add) and
                    self._is_string_operation(node)):
                    
                    self.found_patterns.append({
                        'location': {'line': getattr(node, 'lineno', 0)},
                        'context': {'operation': 'string_concatenation'},
                        'suggestions': [
                            'Use str.join() for better performance',
                            'Use list.append() then join',
                            'Consider using StringIO for complex cases'
                        ]
                    })
                    
                self.generic_visit(node)
                
            def _is_string_operation(self, node):
                # Simple heuristic - could be more sophisticated
                return True
                
        visitor = StringConcatVisitor()
        visitor.visit(tree)
        return visitor.found_patterns
        
    def _detect_inefficient_data_structures(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect use of inefficient data structures"""
        matches = []
        
        class DataStructureVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found_patterns = []
                
            def visit_Call(self, node):
                # Check for list operations that should use sets
                if (isinstance(node.func, ast.Attribute) and
                    node.func.attr == 'remove' and
                    isinstance(node.func.value, ast.Name)):
                    
                    self.found_patterns.append({
                        'location': {'line': getattr(node, 'lineno', 0)},
                        'context': {'operation': 'list_remove'},
                        'suggestions': [
                            'Consider using set for O(1) removal',
                            'Use collections.deque for frequent removals',
                            'Pre-filter data to avoid removals'
                        ]
                    })
                    
                self.generic_visit(node)
                
        visitor = DataStructureVisitor()
        visitor.visit(tree)
        return visitor.found_patterns
        
    def _detect_repeated_computation(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect repeated expensive computations"""
        matches = []
        
        # This would require more sophisticated analysis
        # For now, detect obvious patterns like repeated function calls
        
        class RepeatedComputationVisitor(ast.NodeVisitor):
            def __init__(self):
                self.function_calls = defaultdict(list)
                self.found_patterns = []
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    self.function_calls[func_name].append(getattr(node, 'lineno', 0))
                    
                self.generic_visit(node)
                
            def analyze_patterns(self):
                for func_name, lines in self.function_calls.items():
                    if len(lines) > 3:  # Called more than 3 times
                        self.found_patterns.append({
                            'location': {'line': min(lines)},
                            'context': {'function': func_name, 'call_count': len(lines)},
                            'suggestions': [
                                'Consider caching the result',
                                'Move computation outside loop if possible',
                                'Use memoization decorator'
                            ]
                        })
                        
        visitor = RepeatedComputationVisitor()
        visitor.visit(tree)
        visitor.analyze_patterns()
        return visitor.found_patterns
        
    def _detect_long_parameter_list(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect functions with too many parameters"""
        matches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)
                if param_count > 5:  # Threshold for too many parameters
                    matches.append({
                        'location': {'line': node.lineno},
                        'context': {'function': node.name, 'param_count': param_count},
                        'suggestions': [
                            'Use a configuration object or dataclass',
                            'Group related parameters into structs',
                            'Consider using **kwargs for optional parameters'
                        ]
                    })
                    
        return matches
        
    def _detect_deep_nesting(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect deeply nested code"""
        matches = []
        
        class NestingVisitor(ast.NodeVisitor):
            def __init__(self):
                self.nesting_level = 0
                self.max_nesting = 0
                self.found_patterns = []
                
            def visit_If(self, node):
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)
                
                if self.nesting_level > 4:  # Deep nesting threshold
                    self.found_patterns.append({
                        'location': {'line': node.lineno},
                        'context': {'nesting_level': self.nesting_level},
                        'suggestions': [
                            'Extract nested logic into separate functions',
                            'Use early returns to reduce nesting',
                            'Consider using guard clauses'
                        ]
                    })
                    
                self.generic_visit(node)
                self.nesting_level -= 1
                
            def visit_For(self, node):
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)
                self.generic_visit(node)
                self.nesting_level -= 1
                
            def visit_While(self, node):
                self.nesting_level += 1
                self.max_nesting = max(self.max_nesting, self.nesting_level)
                self.generic_visit(node)
                self.nesting_level -= 1
                
        visitor = NestingVisitor()
        visitor.visit(tree)
        return visitor.found_patterns
        
    def _detect_large_class(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect classes that are too large"""
        matches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                
                if method_count > 15:  # Too many methods
                    matches.append({
                        'location': {'line': node.lineno},
                        'context': {'class': node.name, 'method_count': method_count},
                        'suggestions': [
                            'Split class into smaller, focused classes',
                            'Extract related methods into mixins',
                            'Use composition instead of inheritance'
                        ]
                    })
                    
        return matches
        
    def _detect_duplicate_code(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect duplicate code blocks"""
        matches = []
        
        # This is a simplified implementation
        # A full implementation would use more sophisticated similarity detection
        
        function_bodies = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Convert function body to string for comparison
                body_str = ast.dump(node)
                function_bodies.append({
                    'name': node.name,
                    'line': node.lineno,
                    'body': body_str
                })
                
        # Look for similar function bodies
        for i, func1 in enumerate(function_bodies):
            for j, func2 in enumerate(function_bodies[i+1:], i+1):
                similarity = self._calculate_similarity(func1['body'], func2['body'])
                if similarity > 0.8:  # High similarity threshold
                    matches.append({
                        'location': {'line': func1['line']},
                        'context': {
                            'function1': func1['name'],
                            'function2': func2['name'],
                            'similarity': similarity
                        },
                        'suggestions': [
                            'Extract common code into shared function',
                            'Use template method pattern',
                            'Consider parameterizing the differences'
                        ]
                    })
                    
        return matches
        
    def _detect_dangerous_eval(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect dangerous use of eval/exec"""
        matches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    matches.append({
                        'location': {'line': getattr(node, 'lineno', 0)},
                        'context': {'function': node.func.id},
                        'suggestions': [
                            'Use ast.literal_eval for safe evaluation',
                            'Consider using a whitelist of allowed operations',
                            'Validate and sanitize input before evaluation'
                        ]
                    })
                    
        return matches
        
    def _detect_sql_injection_risk(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect SQL injection risks"""
        matches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Look for string formatting in SQL-like contexts
                if (isinstance(node.func, ast.Attribute) and
                    node.func.attr in ['execute', 'query']):
                    
                    # Check if using string formatting
                    for arg in node.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                            matches.append({
                                'location': {'line': getattr(node, 'lineno', 0)},
                                'context': {'method': node.func.attr},
                                'suggestions': [
                                    'Use parameterized queries',
                                    'Use ORM query builders',
                                    'Validate and escape input parameters'
                                ]
                            })
                            
        return matches
        
    def _detect_hardcoded_secrets(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect hardcoded secrets"""
        matches = []
        
        # Read file content to check for patterns
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for common secret patterns
            secret_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', 'hardcoded password'),
                (r'api_key\s*=\s*["\'][^"\']+["\']', 'hardcoded API key'),
                (r'secret\s*=\s*["\'][^"\']+["\']', 'hardcoded secret'),
                (r'token\s*=\s*["\'][^"\']+["\']', 'hardcoded token')
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern, description in secret_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append({
                            'location': {'line': i},
                            'context': {'type': description},
                            'suggestions': [
                                'Use environment variables',
                                'Use configuration files not in version control',
                                'Use secure credential management systems'
                            ]
                        })
                        
        except Exception as e:
            logging.error(f"Error reading file for secret detection: {e}")
            
        return matches
        
    def _detect_unsafe_deserialization(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect unsafe deserialization"""
        matches = []
        
        unsafe_functions = ['pickle.loads', 'pickle.load', 'yaml.load']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    func_name = f"{node.func.value.id if isinstance(node.func.value, ast.Name) else 'unknown'}.{node.func.attr}"
                    if func_name in unsafe_functions:
                        matches.append({
                            'location': {'line': getattr(node, 'lineno', 0)},
                            'context': {'function': func_name},
                            'suggestions': [
                                'Use safe_load for YAML',
                                'Validate data before deserialization',
                                'Use JSON instead of pickle when possible'
                            ]
                        })
                        
        return matches
        
    def _detect_missing_type_hints(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect functions without type hints"""
        matches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_return_annotation = node.returns is not None
                has_arg_annotations = any(arg.annotation for arg in node.args.args)
                
                if not has_return_annotation or not has_arg_annotations:
                    matches.append({
                        'location': {'line': node.lineno},
                        'context': {'function': node.name},
                        'suggestions': [
                            'Add type hints for better code clarity',
                            'Use typing module for complex types',
                            'Consider using mypy for type checking'
                        ]
                    })
                    
        return matches
        
    def _detect_old_string_formatting(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect old-style string formatting"""
        matches = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
                if isinstance(node.left, ast.Str):  # Old-style % formatting
                    matches.append({
                        'location': {'line': getattr(node, 'lineno', 0)},
                        'context': {'type': 'percent_formatting'},
                        'suggestions': [
                            'Use f-strings for better performance and readability',
                            'Use str.format() for complex formatting',
                            'Consider using template strings for user-facing text'
                        ]
                    })
                    
        return matches
        
    def _detect_async_opportunities(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect I/O operations that could be async"""
        matches = []
        
        io_functions = ['open', 'requests.get', 'requests.post', 'urlopen', 'read', 'write']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                    
                if func_name in io_functions:
                    matches.append({
                        'location': {'line': getattr(node, 'lineno', 0)},
                        'context': {'function': func_name},
                        'suggestions': [
                            'Consider using async/await for I/O operations',
                            'Use aiohttp for HTTP requests',
                            'Use aiofiles for file operations'
                        ]
                    })
                    
        return matches
        
    def _detect_outdated_patterns(self, file_path: str, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detect usage of outdated patterns"""
        matches = []
        
        # This would be extended with more patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'range':
                    # Check for range with only one argument in a for loop
                    parent = getattr(node, 'parent', None)
                    if (parent and isinstance(parent, ast.For) and 
                        len(node.args) == 1):
                        matches.append({
                            'location': {'line': getattr(node, 'lineno', 0)},
                            'context': {'pattern': 'range_one_arg'},
                            'suggestions': [
                                'Consider using enumerate() when you need both index and value',
                                'Use direct iteration when index is not needed'
                            ]
                        })
                        
        return matches
        
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple similarity calculation
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        if not set1 or not set2:
            return 0.0
            
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)

class MLEnhancedAnalyzer:
    """Machine learning enhanced code analysis"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.model_cache = cache_dir / "ml_models"
        self.model_cache.mkdir(parents=True, exist_ok=True)
        
        # Initialize ML components if available
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.clusterer = None
            self.is_trained = False
        else:
            self.vectorizer = None
            self.clusterer = None
            self.is_trained = False
            
    def analyze_code_patterns(self, code_samples: List[str]) -> Dict[str, Any]:
        """Analyze code patterns using ML techniques"""
        if not ML_AVAILABLE or not code_samples:
            return self._fallback_analysis(code_samples)
            
        try:
            # Vectorize code samples
            vectors = self.vectorizer.fit_transform(code_samples)
            
            # Cluster similar code patterns
            optimal_clusters = min(5, max(2, len(code_samples) // 3))
            self.clusterer = KMeans(n_clusters=optimal_clusters, random_state=42)
            cluster_labels = self.clusterer.fit_predict(vectors)
            
            # Analyze clusters
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[label].append(i)
                
            patterns = {}
            for cluster_id, sample_indices in clusters.items():
                # Get representative features for this cluster
                cluster_vectors = vectors[sample_indices]
                centroid = cluster_vectors.mean(axis=0)
                
                # Find most important features
                feature_names = self.vectorizer.get_feature_names_out()
                top_features = np.argsort(centroid.A1)[-10:]  # Top 10 features
                
                patterns[f"cluster_{cluster_id}"] = {
                    'sample_count': len(sample_indices),
                    'key_features': [feature_names[i] for i in top_features],
                    'samples': sample_indices
                }
                
            self.is_trained = True
            return {
                'patterns': patterns,
                'total_samples': len(code_samples),
                'cluster_count': len(clusters),
                'analysis_type': 'ml_enhanced'
            }
            
        except Exception as e:
            logging.error(f"ML analysis failed: {e}")
            return self._fallback_analysis(code_samples)
            
    def _fallback_analysis(self, code_samples: List[str]) -> Dict[str, Any]:
        """Fallback analysis when ML is not available"""
        patterns = {
            'pattern_frequency': Counter(),
            'common_keywords': Counter(),
            'total_samples': len(code_samples)
        }
        
        for sample in code_samples:
            # Simple keyword extraction
            keywords = re.findall(r'\b\w+\b', sample.lower())
            patterns['common_keywords'].update(keywords)
            
            # Basic pattern detection
            if 'def ' in sample:
                patterns['pattern_frequency']['function_definition'] += 1
            if 'class ' in sample:
                patterns['pattern_frequency']['class_definition'] += 1
            if 'for ' in sample:
                patterns['pattern_frequency']['loop'] += 1
            if 'if ' in sample:
                patterns['pattern_frequency']['conditional'] += 1
                
        return {
            'patterns': dict(patterns['pattern_frequency']),
            'common_keywords': dict(patterns['common_keywords'].most_common(20)),
            'total_samples': patterns['total_samples'],
            'analysis_type': 'fallback'
        }
        
    def predict_enhancement_priority(self, opportunities: List[EnhancementOpportunity]) -> List[EnhancementOpportunity]:
        """Use ML to predict enhancement priorities"""
        if not ML_AVAILABLE or not self.is_trained:
            return self._fallback_priority_ranking(opportunities)
            
        try:
            # Extract features from opportunities
            feature_vectors = []
            for opp in opportunities:
                features = [
                    opp.impact_score,
                    opp.effort_estimate,
                    1.0 if opp.risk_level == 'low' else 0.5 if opp.risk_level == 'medium' else 0.0,
                    opp.confidence,
                    len(opp.improvement_suggestions),
                    len(opp.research_keywords)
                ]
                feature_vectors.append(features)
                
            # Use clustering to group similar opportunities
            if len(feature_vectors) > 1:
                vectors = np.array(feature_vectors)
                
                # Calculate priority scores based on multiple factors
                for i, opp in enumerate(opportunities):
                    # Composite score combining multiple factors
                    priority_score = (
                        opp.impact_score * 0.4 +
                        (1.0 - opp.effort_estimate) * 0.3 +  # Lower effort = higher priority
                        opp.confidence * 0.2 +
                        (1.0 if opp.risk_level == 'low' else 0.5) * 0.1
                    )
                    opp.priority_rank = int(priority_score * 100)
                    
            return sorted(opportunities, key=lambda x: x.priority_rank, reverse=True)
            
        except Exception as e:
            logging.error(f"ML priority prediction failed: {e}")
            return self._fallback_priority_ranking(opportunities)
            
    def _fallback_priority_ranking(self, opportunities: List[EnhancementOpportunity]) -> List[EnhancementOpportunity]:
        """Fallback priority ranking without ML"""
        for opp in opportunities:
            # Simple scoring algorithm
            risk_multiplier = {'low': 1.0, 'medium': 0.7, 'high': 0.4, 'critical': 0.2}.get(opp.risk_level, 0.5)
            priority_score = (opp.impact_score * 0.5 + opp.confidence * 0.3 + (1.0 - opp.effort_estimate) * 0.2) * risk_multiplier
            opp.priority_rank = int(priority_score * 100)
            
        return sorted(opportunities, key=lambda x: x.priority_rank, reverse=True)

class EnhancementDiscoveryEngine:
    """Enhanced discovery engine with sophisticated analysis capabilities"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.pattern_matcher = CodePatternMatcher()
        self.ml_analyzer = MLEnhancedAnalyzer(cache_dir)
        
        # Discovery state
        self.analysis_history = []
        self.discovered_opportunities = []
        self.lock = Lock()
        
        # Database for persistent storage
        self.db_path = cache_dir / "discovery_cache.db"
        self._init_database()
        
    def _init_database(self):
        """Initialize discovery database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS code_metrics (
                    file_path TEXT PRIMARY KEY,
                    metrics_data TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enhancement_opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    opportunity_data TEXT NOT NULL,
                    priority_rank INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'discovered',
                    timestamp REAL NOT NULL
                )
            """)
            
    def discover_enhancement_opportunities(self, 
                                         target_files: List[str], 
                                         context: Dict[str, Any] = None) -> List[EnhancementOpportunity]:
        """Discover enhancement opportunities with sophisticated analysis"""
        
        logging.info(f"Starting enhancement discovery for {len(target_files)} files")
        
        all_opportunities = []
        code_samples = []
        
        with self.lock:
            for file_path in target_files:
                try:
                    # Analyze individual file
                    opportunities = self._analyze_file_for_opportunities(file_path, context)
                    all_opportunities.extend(opportunities)
                    
                    # Collect code samples for ML analysis
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_samples.append(f.read())
                        
                except Exception as e:
                    logging.error(f"Failed to analyze {file_path}: {e}")
                    
            # Perform ML-enhanced analysis
            if code_samples:
                ml_insights = self.ml_analyzer.analyze_code_patterns(code_samples)
                self._incorporate_ml_insights(all_opportunities, ml_insights)
                
            # Rank opportunities using ML
            ranked_opportunities = self.ml_analyzer.predict_enhancement_priority(all_opportunities)
            
            # Store opportunities in database
            self._store_opportunities(ranked_opportunities)
            
        logging.info(f"Discovered {len(ranked_opportunities)} enhancement opportunities")
        return ranked_opportunities
        
    def _analyze_file_for_opportunities(self, 
                                      file_path: str, 
                                      context: Dict[str, Any] = None) -> List[EnhancementOpportunity]:
        """Analyze single file for enhancement opportunities"""
        opportunities = []
        
        try:
            # Read and parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Calculate comprehensive metrics
            metrics = self._calculate_comprehensive_metrics(file_path, content, tree)
            
            # Pattern-based analysis
            detected_patterns = self.pattern_matcher.analyze_patterns(file_path, tree)
            
            # Convert patterns to opportunities
            for pattern in detected_patterns:
                opportunity = self._pattern_to_opportunity(file_path, pattern, metrics)
                if opportunity:
                    opportunities.append(opportunity)
                    
            # Metric-based opportunities
            metric_opportunities = self._metrics_to_opportunities(file_path, metrics)
            opportunities.extend(metric_opportunities)
            
            # Store metrics
            self._store_metrics(file_path, metrics)
            
        except Exception as e:
            logging.error(f"File analysis failed for {file_path}: {e}")
            
        return opportunities
        
    def _calculate_comprehensive_metrics(self, file_path: str, content: str, tree: ast.AST) -> CodeMetrics:
        """Calculate comprehensive code metrics"""
        lines = content.split('\n')
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = total_lines - blank_lines - comment_lines
        
        # Calculate complexity metrics
        complexity_visitor = ComplexityCalculator()
        complexity_visitor.visit(tree)
        
        # Calculate maintainability index (simplified)
        maintainability_index = self._calculate_maintainability_index(
            code_lines, complexity_visitor.cyclomatic_complexity, comment_lines
        )
        
        # Calculate other scores
        performance_score = self._calculate_performance_score(tree)
        security_score = self._calculate_security_score(tree, content)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(tree)
        
        # Detect code smells
        code_smells = self._detect_code_smells(tree, content)
        
        return CodeMetrics(
            file_path=file_path,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            complexity_score=complexity_visitor.cyclomatic_complexity,
            maintainability_index=maintainability_index,
            technical_debt_score=len(code_smells) / max(code_lines, 1),
            performance_score=performance_score,
            security_score=security_score,
            test_coverage=0.0,  # Would need external tool integration
            documentation_score=comment_lines / max(code_lines, 1),
            code_smells=code_smells,
            dependencies=dependencies,
            api_usage={},  # Would be populated by more detailed analysis
            timestamp=time.time()
        )
        
    def _calculate_maintainability_index(self, loc: int, complexity: float, comments: int) -> float:
        """Calculate maintainability index"""
        if loc == 0:
            return 0.0
            
        # Simplified maintainability index calculation
        volume = loc * 4.0  # Approximation
        comment_ratio = comments / max(loc, 1)
        
        mi = max(0, (171 - 5.2 * np.log(volume) - 0.23 * complexity - 16.2 * np.log(loc) + 50 * np.sin(np.sqrt(2.4 * comment_ratio))) / 171)
        return min(1.0, mi)
        
    def _calculate_performance_score(self, tree: ast.AST) -> float:
        """Calculate performance score based on code patterns"""
        score = 1.0
        
        # Deduct points for performance anti-patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Nested loops penalty
                nested_loops = sum(1 for child in ast.walk(node) if isinstance(child, (ast.For, ast.While)))
                if nested_loops > 2:
                    score -= 0.1
                    
            elif isinstance(node, ast.Call):
                # Inefficient operations
                if isinstance(node.func, ast.Attribute) and node.func.attr in ['append', 'insert']:
                    score -= 0.02
                    
        return max(0.0, score)
        
    def _calculate_security_score(self, tree: ast.AST, content: str) -> float:
        """Calculate security score"""
        score = 1.0
        
        # Check for security anti-patterns
        dangerous_functions = ['eval', 'exec', 'compile']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in dangerous_functions:
                    score -= 0.3
                    
        # Check for hardcoded secrets (simplified)
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            score -= 0.5
            
        return max(0.0, score)
        
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract dependencies from import statements"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)
                    
        return list(set(dependencies))
        
    def _detect_code_smells(self, tree: ast.AST, content: str) -> List[str]:
        """Detect code smells"""
        smells = []
        
        # Long method smell
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and node.end_lineno:
                    method_length = node.end_lineno - node.lineno
                    if method_length > 50:
                        smells.append(f"Long method: {node.name} ({method_length} lines)")
                        
        # Large class smell
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                method_count = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))
                if method_count > 20:
                    smells.append(f"Large class: {node.name} ({method_count} methods)")
                    
        return smells
        
    def _pattern_to_opportunity(self, 
                              file_path: str, 
                              pattern: Dict[str, Any], 
                              metrics: CodeMetrics) -> Optional[EnhancementOpportunity]:
        """Convert detected pattern to enhancement opportunity"""
        
        # Map severity to impact score
        severity_impact = {
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5,
            'low': 0.3
        }
        
        # Map category to effort estimate
        category_effort = {
            'security_vulnerabilities': 0.6,  # Higher effort for security fixes
            'performance_antipatterns': 0.4,
            'maintainability_issues': 0.3,
            'modern_improvements': 0.2
        }
        
        opportunity_id = f"{pattern['category']}_{pattern['name']}_{int(time.time() * 1000)}"
        
        # Generate research keywords
        research_keywords = [
            pattern['name'].replace('_', ' '),
            pattern['category'].replace('_', ' '),
            'python best practices',
            'code optimization'
        ]
        
        # Create code context
        code_context = CodeContext(
            function_name=None,  # Would be extracted from AST analysis
            class_name=None,
            module_name=Path(file_path).stem,
            line_range=(pattern['location'].get('line', 0), pattern['location'].get('line', 0)),
            ast_node_type='unknown',
            surrounding_code='',  # Would be extracted from file
            dependencies_used=metrics.dependencies,
            complexity_metrics={'complexity': metrics.complexity_score}
        )
        
        # Estimate benefits
        estimated_benefit = {
            'performance': 0.2 if 'performance' in pattern['category'] else 0.0,
            'maintainability': 0.3 if 'maintainability' in pattern['category'] else 0.1,
            'security': 0.8 if 'security' in pattern['category'] else 0.0,
            'readability': 0.4 if 'modern' in pattern['category'] else 0.1
        }
        
        return EnhancementOpportunity(
            opportunity_id=opportunity_id,
            file_path=file_path,
            opportunity_type=pattern['category'],
            title=f"{pattern['name'].replace('_', ' ').title()}",
            description=pattern['description'],
            impact_score=severity_impact.get(pattern['severity'], 0.3),
            effort_estimate=category_effort.get(pattern['category'], 0.3),
            risk_level=pattern['severity'],
            confidence=0.8,  # High confidence for pattern-detected issues
            related_patterns=[pattern['name']],
            code_context=asdict(code_context),
            improvement_suggestions=pattern.get('suggestions', []),
            research_keywords=research_keywords,
            priority_rank=0,  # Will be calculated later
            estimated_benefit=estimated_benefit,
            timestamp=time.time()
        )
        
    def _metrics_to_opportunities(self, file_path: str, metrics: CodeMetrics) -> List[EnhancementOpportunity]:
        """Generate opportunities based on metrics"""
        opportunities = []
        
        # Low maintainability opportunity
        if metrics.maintainability_index < 0.5:
            opportunities.append(EnhancementOpportunity(
                opportunity_id=f"maintainability_{int(time.time() * 1000)}",
                file_path=file_path,
                opportunity_type='maintainability',
                title='Improve Code Maintainability',
                description=f'File has low maintainability index: {metrics.maintainability_index:.2f}',
                impact_score=0.6,
                effort_estimate=0.4,
                risk_level='medium',
                confidence=0.9,
                related_patterns=['maintainability_index'],
                code_context={},
                improvement_suggestions=[
                    'Reduce code complexity',
                    'Add more documentation',
                    'Break down large functions',
                    'Improve variable naming'
                ],
                research_keywords=['code maintainability', 'refactoring techniques', 'clean code'],
                priority_rank=0,
                estimated_benefit={'maintainability': 0.7, 'readability': 0.5},
                timestamp=time.time()
            ))
            
        # High technical debt opportunity
        if metrics.technical_debt_score > 0.3:
            opportunities.append(EnhancementOpportunity(
                opportunity_id=f"technical_debt_{int(time.time() * 1000)}",
                file_path=file_path,
                opportunity_type='technical_debt',
                title='Reduce Technical Debt',
                description=f'File has high technical debt: {len(metrics.code_smells)} code smells detected',
                impact_score=0.5,
                effort_estimate=0.6,
                risk_level='medium',
                confidence=0.8,
                related_patterns=['code_smells'],
                code_context={},
                improvement_suggestions=[
                    'Address identified code smells',
                    'Refactor complex code sections',
                    'Add unit tests',
                    'Improve error handling'
                ],
                research_keywords=['technical debt', 'code smells', 'refactoring'],
                priority_rank=0,
                estimated_benefit={'maintainability': 0.6, 'quality': 0.7},
                timestamp=time.time()
            ))
            
        # Low documentation opportunity
        if metrics.documentation_score < 0.1:
            opportunities.append(EnhancementOpportunity(
                opportunity_id=f"documentation_{int(time.time() * 1000)}",
                file_path=file_path,
                opportunity_type='documentation',
                title='Improve Documentation',
                description=f'File has low documentation coverage: {metrics.documentation_score:.1%}',
                impact_score=0.4,
                effort_estimate=0.2,
                risk_level='low',
                confidence=0.9,
                related_patterns=['missing_documentation'],
                code_context={},
                improvement_suggestions=[
                    'Add docstrings to functions and classes',
                    'Include inline comments for complex logic',
                    'Add module-level documentation',
                    'Use type hints for better clarity'
                ],
                research_keywords=['python documentation', 'docstrings', 'code comments'],
                priority_rank=0,
                estimated_benefit={'maintainability': 0.5, 'readability': 0.8},
                timestamp=time.time()
            ))
            
        return opportunities
        
    def _incorporate_ml_insights(self, opportunities: List[EnhancementOpportunity], ml_insights: Dict[str, Any]):
        """Incorporate ML insights into opportunities"""
        
        if ml_insights.get('analysis_type') == 'ml_enhanced':
            patterns = ml_insights.get('patterns', {})
            
            # Adjust confidence based on cluster analysis
            for opp in opportunities:
                # Find related cluster
                for cluster_id, cluster_info in patterns.items():
                    if any(keyword in ' '.join(cluster_info.get('key_features', [])) 
                          for keyword in opp.research_keywords):
                        # Boost confidence for opportunities in well-defined clusters
                        sample_count = cluster_info.get('sample_count', 1)
                        confidence_boost = min(0.2, sample_count / 10)
                        opp.confidence = min(1.0, opp.confidence + confidence_boost)
                        
    def _store_opportunities(self, opportunities: List[EnhancementOpportunity]):
        """Store opportunities in database"""
        with sqlite3.connect(self.db_path) as conn:
            for opp in opportunities:
                conn.execute(
                    "INSERT OR REPLACE INTO enhancement_opportunities (opportunity_id, opportunity_data, priority_rank, timestamp) VALUES (?, ?, ?, ?)",
                    (opp.opportunity_id, json.dumps(asdict(opp)), opp.priority_rank, opp.timestamp)
                )
                
    def _store_metrics(self, file_path: str, metrics: CodeMetrics):
        """Store code metrics in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO code_metrics (file_path, metrics_data, timestamp) VALUES (?, ?, ?)",
                (file_path, json.dumps(asdict(metrics)), metrics.timestamp)
            )
            
    def get_cached_opportunities(self, 
                               file_path: str = None, 
                               opportunity_type: str = None,
                               min_priority: int = 0) -> List[EnhancementOpportunity]:
        """Get cached enhancement opportunities"""
        opportunities = []
        
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT opportunity_data FROM enhancement_opportunities WHERE priority_rank >= ?"
            params = [min_priority]
            
            if file_path:
                query += " AND opportunity_data LIKE ?"
                params.append(f'%"file_path": "{file_path}"%')
                
            if opportunity_type:
                query += " AND opportunity_data LIKE ?"
                params.append(f'%"opportunity_type": "{opportunity_type}"%')
                
            query += " ORDER BY priority_rank DESC"
            
            cursor = conn.execute(query, params)
            for row in cursor.fetchall():
                opp_data = json.loads(row[0])
                opportunities.append(EnhancementOpportunity(**opp_data))
                
        return opportunities
        
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get discovery engine statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Opportunity statistics
            cursor = conn.execute("SELECT COUNT(*), AVG(priority_rank) FROM enhancement_opportunities")
            opp_count, avg_priority = cursor.fetchone()
            
            # Opportunity types
            cursor = conn.execute("""
                SELECT opportunity_data, COUNT(*) 
                FROM enhancement_opportunities 
                GROUP BY json_extract(opportunity_data, '$.opportunity_type')
            """)
            
            type_distribution = {}
            for row in cursor.fetchall():
                opp_data = json.loads(row[0])
                opp_type = opp_data.get('opportunity_type', 'unknown')
                type_distribution[opp_type] = row[1]
                
            # Metrics statistics
            cursor = conn.execute("SELECT COUNT(*) FROM code_metrics")
            metrics_count = cursor.fetchone()[0]
            
        return {
            'total_opportunities': opp_count or 0,
            'average_priority': avg_priority or 0.0,
            'opportunity_types': type_distribution,
            'analyzed_files': metrics_count or 0,
            'ml_analysis_available': ML_AVAILABLE,
            'patterns_detected': len(self.pattern_matcher.patterns)
        }

class ComplexityCalculator(ast.NodeVisitor):
    """Calculate cyclomatic complexity"""
    
    def __init__(self):
        self.cyclomatic_complexity = 1  # Base complexity
        
    def visit_If(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)
        
    def visit_BoolOp(self, node):
        self.cyclomatic_complexity += len(node.values) - 1
        self.generic_visit(node)