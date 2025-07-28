"""
Advanced Enhancement Metrics Tracker for SuperMini
Comprehensive tracking and measurement of enhancement effectiveness
"""

import time
import json
import logging
import sqlite3
import asyncio
import psutil
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, deque
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import hashlib
import subprocess
import sys

@dataclass
class PerformanceMetrics:
    """Performance metrics for code execution"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    memory_peak: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    timestamp: float

@dataclass
class QualityMetrics:
    """Code quality metrics"""
    cyclomatic_complexity: float
    maintainability_index: float
    test_coverage: float
    code_duplication: float
    documentation_coverage: float
    security_score: float
    type_hint_coverage: float
    timestamp: float

@dataclass
class EnhancementImpact:
    """Impact measurement of an enhancement"""
    enhancement_id: str
    file_path: str
    enhancement_type: str
    
    # Before/after metrics
    performance_before: PerformanceMetrics
    performance_after: PerformanceMetrics
    quality_before: QualityMetrics
    quality_after: QualityMetrics
    
    # Calculated improvements
    performance_improvement: Dict[str, float] = field(default_factory=dict)
    quality_improvement: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    
    # Metadata
    implementation_time: float = 0.0
    risk_assessment: str = "unknown"
    user_satisfaction: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class LearningMetrics:
    """Machine learning and pattern recognition metrics"""
    pattern_accuracy: float
    prediction_confidence: float
    false_positive_rate: float
    false_negative_rate: float
    adaptation_rate: float
    knowledge_base_size: int
    timestamp: float

@dataclass
class SystemHealthMetrics:
    """Overall system health metrics"""
    total_enhancements: int
    successful_enhancements: int
    success_rate: float
    average_impact_score: float
    average_implementation_time: float
    cumulative_improvement: Dict[str, float]
    stability_score: float
    error_rate: float
    timestamp: float

class PerformanceBenchmarker:
    """Benchmarking system for performance measurements"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.benchmark_cache = cache_dir / "benchmarks"
        self.benchmark_cache.mkdir(parents=True, exist_ok=True)
        
    async def benchmark_code(self, file_path: str, function_name: str = None, iterations: int = 100) -> PerformanceMetrics:
        """Benchmark code performance"""
        try:
            # Setup benchmarking environment
            process = psutil.Process()
            
            # Baseline measurements
            cpu_before = process.cpu_percent()
            memory_before = process.memory_info()
            
            start_time = time.perf_counter()
            
            # Run the code under test
            if function_name:
                await self._benchmark_function(file_path, function_name, iterations)
            else:
                await self._benchmark_file(file_path, iterations)
                
            end_time = time.perf_counter()
            
            # Final measurements
            cpu_after = process.cpu_percent()
            memory_after = process.memory_info()
            
            # Calculate metrics
            execution_time = end_time - start_time
            memory_usage = memory_after.rss - memory_before.rss
            cpu_usage = cpu_after - cpu_before
            memory_peak = memory_after.peak_wset if hasattr(memory_after, 'peak_wset') else memory_after.rss
            
            # I/O metrics
            io_counters = process.io_counters()
            disk_io = {
                'read_bytes': io_counters.read_bytes,
                'write_bytes': io_counters.write_bytes
            }
            
            # Network I/O (if available)
            try:
                net_io = psutil.net_io_counters()
                network_io = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                }
            except:
                network_io = {'bytes_sent': 0, 'bytes_recv': 0}
                
            return PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                memory_peak=memory_peak,
                disk_io=disk_io,
                network_io=network_io,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Benchmarking failed: {e}")
            return self._get_default_performance_metrics()
            
    async def _benchmark_function(self, file_path: str, function_name: str, iterations: int):
        """Benchmark a specific function"""
        try:
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location("benchmark_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the function
            func = getattr(module, function_name)
            
            # Run benchmarks
            for _ in range(iterations):
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
                    
        except Exception as e:
            logging.error(f"Function benchmarking failed: {e}")
            
    async def _benchmark_file(self, file_path: str, iterations: int):
        """Benchmark entire file execution"""
        for _ in range(iterations):
            try:
                # Execute the file
                result = subprocess.run([sys.executable, file_path], 
                                      capture_output=True, 
                                      timeout=30)
                if result.returncode != 0:
                    logging.warning(f"File execution returned non-zero: {result.returncode}")
            except subprocess.TimeoutExpired:
                logging.warning("File execution timed out")
            except Exception as e:
                logging.error(f"File benchmarking failed: {e}")
                
    def _get_default_performance_metrics(self) -> PerformanceMetrics:
        """Get default performance metrics when benchmarking fails"""
        return PerformanceMetrics(
            execution_time=0.0,
            memory_usage=0.0,
            cpu_usage=0.0,
            memory_peak=0.0,
            disk_io={'read_bytes': 0, 'write_bytes': 0},
            network_io={'bytes_sent': 0, 'bytes_recv': 0},
            timestamp=time.time()
        )

class QualityAnalyzer:
    """Code quality analysis system"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.analysis_cache = cache_dir / "quality_analysis"
        self.analysis_cache.mkdir(parents=True, exist_ok=True)
        
    def analyze_code_quality(self, file_path: str) -> QualityMetrics:
        """Analyze code quality metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST for analysis
            import ast
            tree = ast.parse(content)
            
            # Calculate various quality metrics
            complexity = self._calculate_cyclomatic_complexity(tree)
            maintainability = self._calculate_maintainability_index(content, complexity)
            test_coverage = self._estimate_test_coverage(file_path)
            duplication = self._calculate_code_duplication(content)
            documentation = self._calculate_documentation_coverage(content)
            security = self._calculate_security_score(content)
            type_hints = self._calculate_type_hint_coverage(tree)
            
            return QualityMetrics(
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                test_coverage=test_coverage,
                code_duplication=duplication,
                documentation_coverage=documentation,
                security_score=security,
                type_hint_coverage=type_hints,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Quality analysis failed for {file_path}: {e}")
            return self._get_default_quality_metrics()
            
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
                
        return float(complexity)
        
    def _calculate_maintainability_index(self, content: str, complexity: float) -> float:
        """Calculate maintainability index"""
        lines = content.split('\n')
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        if loc == 0:
            return 0.0
            
        # Simplified maintainability index
        volume = loc * 4.0  # Approximation
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        comment_ratio = comment_lines / max(loc, 1)
        
        # Maintainability index formula (simplified)
        mi = max(0, (171 - 5.2 * np.log(volume) - 0.23 * complexity - 16.2 * np.log(loc) + 50 * np.sin(np.sqrt(2.4 * comment_ratio))) / 171)
        return min(1.0, mi)
        
    def _estimate_test_coverage(self, file_path: str) -> float:
        """Estimate test coverage (simplified)"""
        # Look for corresponding test files
        file_path_obj = Path(file_path)
        test_patterns = [
            file_path_obj.parent / f"test_{file_path_obj.stem}.py",
            file_path_obj.parent / f"{file_path_obj.stem}_test.py",
            file_path_obj.parent / "tests" / f"test_{file_path_obj.stem}.py"
        ]
        
        for test_file in test_patterns:
            if test_file.exists():
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        test_content = f.read()
                    
                    # Count test functions
                    test_functions = test_content.count('def test_')
                    
                    # Estimate coverage based on test function count
                    return min(1.0, test_functions / 10.0)  # Assume 10 tests = 100% coverage
                    
                except Exception:
                    continue
                    
        return 0.0  # No tests found
        
    def _calculate_code_duplication(self, content: str) -> float:
        """Calculate code duplication ratio"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return 0.0
            
        # Simple duplicate line counting
        line_counts = {}
        for line in lines:
            if len(line) > 10:  # Only consider substantial lines
                line_counts[line] = line_counts.get(line, 0) + 1
                
        duplicate_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        return duplicate_lines / len(lines)
        
    def _calculate_documentation_coverage(self, content: str) -> float:
        """Calculate documentation coverage"""
        lines = content.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        docstring_lines = content.count('"""') + content.count("'''")
        
        if total_lines == 0:
            return 0.0
            
        return (comment_lines + docstring_lines * 3) / total_lines  # Weight docstrings more
        
    def _calculate_security_score(self, content: str) -> float:
        """Calculate security score"""
        score = 1.0
        
        # Check for security anti-patterns
        security_issues = [
            ('eval(', 0.3),
            ('exec(', 0.3),
            ('os.system(', 0.2),
            ('subprocess.call(', 0.1),
            ('pickle.loads(', 0.2),
            ('password = "', 0.4),
            ('api_key = "', 0.4)
        ]
        
        for pattern, penalty in security_issues:
            if pattern in content:
                score -= penalty
                
        return max(0.0, score)
        
    def _calculate_type_hint_coverage(self, tree: ast.AST) -> float:
        """Calculate type hint coverage"""
        total_functions = 0
        typed_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                
                # Check for return type annotation
                has_return_type = node.returns is not None
                
                # Check for parameter type annotations
                has_param_types = any(arg.annotation for arg in node.args.args)
                
                if has_return_type and has_param_types:
                    typed_functions += 1
                    
        if total_functions == 0:
            return 1.0  # No functions to type
            
        return typed_functions / total_functions
        
    def _get_default_quality_metrics(self) -> QualityMetrics:
        """Get default quality metrics when analysis fails"""
        return QualityMetrics(
            cyclomatic_complexity=1.0,
            maintainability_index=0.5,
            test_coverage=0.0,
            code_duplication=0.0,
            documentation_coverage=0.0,
            security_score=0.5,
            type_hint_coverage=0.0,
            timestamp=time.time()
        )

class MetricsVisualization:
    """Visualization system for enhancement metrics"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.charts_dir = output_dir / "charts"
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def create_enhancement_dashboard(self, impacts: List[EnhancementImpact]) -> str:
        """Create comprehensive enhancement dashboard"""
        dashboard_file = self.charts_dir / f"enhancement_dashboard_{int(time.time())}.html"
        
        # Create multiple visualizations
        charts = []
        
        # Performance improvement chart
        perf_chart = self._create_performance_chart(impacts)
        charts.append(perf_chart)
        
        # Quality improvement chart
        quality_chart = self._create_quality_chart(impacts)
        charts.append(quality_chart)
        
        # Enhancement type distribution
        type_chart = self._create_type_distribution_chart(impacts)
        charts.append(type_chart)
        
        # Timeline view
        timeline_chart = self._create_timeline_chart(impacts)
        charts.append(timeline_chart)
        
        # ROI analysis
        roi_chart = self._create_roi_chart(impacts)
        charts.append(roi_chart)
        
        # Generate HTML dashboard
        html_content = self._generate_dashboard_html(charts, impacts)
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logging.info(f"Enhancement dashboard created: {dashboard_file}")
        return str(dashboard_file)
        
    def _create_performance_chart(self, impacts: List[EnhancementImpact]) -> str:
        """Create performance improvement chart"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Performance Improvements', fontsize=16, fontweight='bold')
        
        # Extract data
        execution_improvements = [impact.performance_improvement.get('execution_time', 0) for impact in impacts]
        memory_improvements = [impact.performance_improvement.get('memory_usage', 0) for impact in impacts]
        enhancement_types = [impact.enhancement_type for impact in impacts]
        
        # Execution time improvements
        axes[0, 0].bar(range(len(execution_improvements)), execution_improvements, color='skyblue')
        axes[0, 0].set_title('Execution Time Improvements')
        axes[0, 0].set_ylabel('Improvement (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Memory usage improvements
        axes[0, 1].bar(range(len(memory_improvements)), memory_improvements, color='lightgreen')
        axes[0, 1].set_title('Memory Usage Improvements')
        axes[0, 1].set_ylabel('Improvement (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Performance by enhancement type
        type_performance = defaultdict(list)
        for impact in impacts:
            type_performance[impact.enhancement_type].append(impact.overall_score)
            
        types = list(type_performance.keys())
        avg_scores = [np.mean(scores) for scores in type_performance.values()]
        
        axes[1, 0].bar(types, avg_scores, color='coral')
        axes[1, 0].set_title('Average Impact by Enhancement Type')
        axes[1, 0].set_ylabel('Average Impact Score')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Distribution of overall scores
        overall_scores = [impact.overall_score for impact in impacts]
        axes[1, 1].hist(overall_scores, bins=10, color='plum', alpha=0.7)
        axes[1, 1].set_title('Distribution of Overall Impact Scores')
        axes[1, 1].set_xlabel('Impact Score')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.charts_dir / f"performance_chart_{int(time.time())}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
        
    def _create_quality_chart(self, impacts: List[EnhancementImpact]) -> str:
        """Create quality improvement chart"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('Code Quality Improvements', fontsize=16, fontweight='bold')
        
        # Quality metrics
        metrics = ['maintainability_index', 'test_coverage', 'documentation_coverage', 
                  'security_score', 'type_hint_coverage']
        
        for i, metric in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            improvements = [impact.quality_improvement.get(metric, 0) for impact in impacts]
            
            axes[row, col].bar(range(len(improvements)), improvements, 
                             color=plt.cm.Set3(i / len(metrics)))
            axes[row, col].set_title(f'{metric.replace("_", " ").title()} Improvements')
            axes[row, col].set_ylabel('Improvement')
            axes[row, col].tick_params(axis='x', rotation=45)
            
        # Overall quality score
        if len(metrics) < 6:
            row, col = 1, 2
            overall_quality = [
                sum(impact.quality_improvement.get(m, 0) for m in metrics) / len(metrics)
                for impact in impacts
            ]
            
            axes[row, col].bar(range(len(overall_quality)), overall_quality, color='gold')
            axes[row, col].set_title('Overall Quality Improvement')
            axes[row, col].set_ylabel('Average Improvement')
            axes[row, col].tick_params(axis='x', rotation=45)
            
        plt.tight_layout()
        
        # Save chart
        chart_file = self.charts_dir / f"quality_chart_{int(time.time())}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
        
    def _create_type_distribution_chart(self, impacts: List[EnhancementImpact]) -> str:
        """Create enhancement type distribution chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Enhancement Type Analysis', fontsize=16, fontweight='bold')
        
        # Type distribution pie chart
        type_counts = defaultdict(int)
        for impact in impacts:
            type_counts[impact.enhancement_type] += 1
            
        ax1.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('Distribution by Type')
        
        # Success rate by type
        type_success = defaultdict(list)
        for impact in impacts:
            type_success[impact.enhancement_type].append(impact.overall_score > 0.5)
            
        types = list(type_success.keys())
        success_rates = [np.mean(successes) * 100 for successes in type_success.values()]
        
        ax2.bar(types, success_rates, color='lightcoral')
        ax2.set_title('Success Rate by Type')
        ax2.set_ylabel('Success Rate (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.charts_dir / f"type_distribution_{int(time.time())}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
        
    def _create_timeline_chart(self, impacts: List[EnhancementImpact]) -> str:
        """Create timeline chart of enhancements"""
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Sort by timestamp
        sorted_impacts = sorted(impacts, key=lambda x: x.timestamp)
        
        timestamps = [datetime.fromtimestamp(impact.timestamp) for impact in sorted_impacts]
        scores = [impact.overall_score for impact in sorted_impacts]
        
        # Plot timeline
        ax.plot(timestamps, scores, marker='o', linewidth=2, markersize=6)
        ax.fill_between(timestamps, scores, alpha=0.3)
        
        ax.set_title('Enhancement Impact Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Impact Score')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.charts_dir / f"timeline_chart_{int(time.time())}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
        
    def _create_roi_chart(self, impacts: List[EnhancementImpact]) -> str:
        """Create ROI analysis chart"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Return on Investment Analysis', fontsize=16, fontweight='bold')
        
        # ROI calculation (benefit vs effort)
        roi_values = []
        effort_values = []
        
        for impact in impacts:
            benefit = impact.overall_score
            effort = impact.implementation_time / 3600  # Convert to hours
            
            if effort > 0:
                roi = benefit / effort
            else:
                roi = benefit  # If no time recorded, use benefit directly
                
            roi_values.append(roi)
            effort_values.append(effort)
            
        # ROI scatter plot
        colors = [impact.overall_score for impact in impacts]
        scatter = ax1.scatter(effort_values, roi_values, c=colors, cmap='viridis', alpha=0.7)
        ax1.set_xlabel('Implementation Effort (hours)')
        ax1.set_ylabel('ROI (Benefit/Effort)')
        ax1.set_title('Effort vs ROI')
        plt.colorbar(scatter, ax=ax1, label='Impact Score')
        
        # ROI distribution
        ax2.hist(roi_values, bins=15, color='skyblue', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('ROI Value')
        ax2.set_ylabel('Frequency')
        ax2.set_title('ROI Distribution')
        ax2.axvline(np.mean(roi_values), color='red', linestyle='--', label=f'Mean: {np.mean(roi_values):.2f}')
        ax2.legend()
        
        plt.tight_layout()
        
        # Save chart
        chart_file = self.charts_dir / f"roi_chart_{int(time.time())}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(chart_file)
        
    def _generate_dashboard_html(self, chart_files: List[str], impacts: List[EnhancementImpact]) -> str:
        """Generate HTML dashboard"""
        
        # Calculate summary statistics
        total_enhancements = len(impacts)
        successful_enhancements = sum(1 for impact in impacts if impact.overall_score > 0.5)
        success_rate = (successful_enhancements / total_enhancements * 100) if total_enhancements > 0 else 0
        avg_impact = np.mean([impact.overall_score for impact in impacts]) if impacts else 0
        avg_time = np.mean([impact.implementation_time for impact in impacts]) if impacts else 0
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SuperMini Enhancement Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .header {{ text-align: center; background-color: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
                .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .stat-card {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                .stat-label {{ color: #7f8c8d; }}
                .chart-container {{ background-color: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .chart-container img {{ max-width: 100%; height: auto; }}
                .enhancement-list {{ background-color: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .enhancement-item {{ border-bottom: 1px solid #ecf0f1; padding: 10px 0; }}
                .enhancement-item:last-child {{ border-bottom: none; }}
                .enhancement-score {{ float: right; background-color: #3498db; color: white; padding: 5px 10px; border-radius: 15px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 SuperMini Enhancement Dashboard</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{total_enhancements}</div>
                    <div class="stat-label">Total Enhancements</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_impact:.2f}</div>
                    <div class="stat-label">Average Impact</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{avg_time/3600:.1f}h</div>
                    <div class="stat-label">Average Time</div>
                </div>
            </div>
        """
        
        # Add chart sections
        chart_titles = [
            "Performance Analysis",
            "Quality Improvements", 
            "Enhancement Types",
            "Timeline View",
            "ROI Analysis"
        ]
        
        for chart_file, title in zip(chart_files, chart_titles):
            html += f"""
            <div class="chart-container">
                <h2>{title}</h2>
                <img src="{Path(chart_file).name}" alt="{title}">
            </div>
            """
            
        # Add enhancement list
        html += """
        <div class="enhancement-list">
            <h2>Recent Enhancements</h2>
        """
        
        # Sort by timestamp and show recent enhancements
        recent_impacts = sorted(impacts, key=lambda x: x.timestamp, reverse=True)[:20]
        
        for impact in recent_impacts:
            timestamp_str = datetime.fromtimestamp(impact.timestamp).strftime('%Y-%m-%d %H:%M')
            html += f"""
            <div class="enhancement-item">
                <strong>{impact.enhancement_type.replace('_', ' ').title()}</strong>
                <span class="enhancement-score">{impact.overall_score:.2f}</span>
                <br>
                <small>{Path(impact.file_path).name} - {timestamp_str}</small>
            </div>
            """
            
        html += """
            </div>
        </body>
        </html>
        """
        
        return html

class EnhancementMetricsTracker:
    """Main metrics tracking system"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.benchmarker = PerformanceBenchmarker(cache_dir)
        self.quality_analyzer = QualityAnalyzer(cache_dir)
        self.visualizer = MetricsVisualization(cache_dir)
        
        # Database for metrics storage
        self.db_path = cache_dir / "metrics.db"
        self._init_database()
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitor_thread = None
        self.metrics_history = deque(maxlen=1000)
        
    def _init_database(self):
        """Initialize metrics database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enhancement_impacts (
                    enhancement_id TEXT PRIMARY KEY,
                    impact_data TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    metric_id TEXT PRIMARY KEY,
                    metric_data TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    session_id TEXT PRIMARY KEY,
                    learning_data TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
    async def measure_enhancement_impact(self, 
                                       enhancement_id: str,
                                       file_path: str,
                                       enhancement_type: str,
                                       pre_enhancement_callback: Callable = None,
                                       post_enhancement_callback: Callable = None) -> EnhancementImpact:
        """Measure the impact of an enhancement"""
        
        logging.info(f"Measuring impact for enhancement: {enhancement_id}")
        
        # Measure baseline metrics
        logging.info("Measuring baseline metrics...")
        performance_before = await self.benchmarker.benchmark_code(file_path)
        quality_before = self.quality_analyzer.analyze_code_quality(file_path)
        
        # Record start time
        start_time = time.time()
        
        # Apply enhancement (via callback)
        if pre_enhancement_callback:
            await pre_enhancement_callback()
            
        # Wait a moment for changes to take effect
        await asyncio.sleep(1)
        
        # Measure post-enhancement metrics
        logging.info("Measuring post-enhancement metrics...")
        performance_after = await self.benchmarker.benchmark_code(file_path)
        quality_after = self.quality_analyzer.analyze_code_quality(file_path)
        
        if post_enhancement_callback:
            await post_enhancement_callback()
            
        # Record completion time
        implementation_time = time.time() - start_time
        
        # Calculate improvements
        performance_improvement = self._calculate_performance_improvement(
            performance_before, performance_after
        )
        quality_improvement = self._calculate_quality_improvement(
            quality_before, quality_after
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            performance_improvement, quality_improvement
        )
        
        # Create impact record
        impact = EnhancementImpact(
            enhancement_id=enhancement_id,
            file_path=file_path,
            enhancement_type=enhancement_type,
            performance_before=performance_before,
            performance_after=performance_after,
            quality_before=quality_before,
            quality_after=quality_after,
            performance_improvement=performance_improvement,
            quality_improvement=quality_improvement,
            overall_score=overall_score,
            implementation_time=implementation_time,
            risk_assessment=self._assess_risk(performance_improvement, quality_improvement),
            timestamp=time.time()
        )
        
        # Store in database
        self._store_impact(impact)
        
        # Add to history for real-time monitoring
        self.metrics_history.append(impact)
        
        logging.info(f"Enhancement impact measured - Overall score: {overall_score:.2f}")
        return impact
        
    def _calculate_performance_improvement(self, 
                                         before: PerformanceMetrics, 
                                         after: PerformanceMetrics) -> Dict[str, float]:
        """Calculate performance improvements"""
        improvements = {}
        
        # Execution time improvement (negative change is improvement)
        if before.execution_time > 0:
            improvements['execution_time'] = (before.execution_time - after.execution_time) / before.execution_time
        else:
            improvements['execution_time'] = 0.0
            
        # Memory usage improvement (negative change is improvement)
        if before.memory_usage > 0:
            improvements['memory_usage'] = (before.memory_usage - after.memory_usage) / before.memory_usage
        else:
            improvements['memory_usage'] = 0.0
            
        # CPU usage improvement
        improvements['cpu_usage'] = before.cpu_usage - after.cpu_usage
        
        return improvements
        
    def _calculate_quality_improvement(self, 
                                     before: QualityMetrics, 
                                     after: QualityMetrics) -> Dict[str, float]:
        """Calculate quality improvements"""
        improvements = {}
        
        # Each metric improvement
        metrics = [
            'maintainability_index', 'test_coverage', 'documentation_coverage',
            'security_score', 'type_hint_coverage'
        ]
        
        for metric in metrics:
            before_value = getattr(before, metric)
            after_value = getattr(after, metric)
            
            if before_value > 0:
                improvements[metric] = (after_value - before_value) / before_value
            else:
                improvements[metric] = after_value  # If before was 0, improvement is the after value
                
        # Complexity improvement (lower is better)
        if before.cyclomatic_complexity > 0:
            improvements['cyclomatic_complexity'] = (before.cyclomatic_complexity - after.cyclomatic_complexity) / before.cyclomatic_complexity
        else:
            improvements['cyclomatic_complexity'] = 0.0
            
        # Code duplication improvement (lower is better)
        improvements['code_duplication'] = before.code_duplication - after.code_duplication
        
        return improvements
        
    def _calculate_overall_score(self, 
                               performance_improvement: Dict[str, float], 
                               quality_improvement: Dict[str, float]) -> float:
        """Calculate overall improvement score"""
        
        # Weight different types of improvements
        performance_weights = {
            'execution_time': 0.4,
            'memory_usage': 0.3,
            'cpu_usage': 0.3
        }
        
        quality_weights = {
            'maintainability_index': 0.2,
            'test_coverage': 0.15,
            'documentation_coverage': 0.15,
            'security_score': 0.25,
            'type_hint_coverage': 0.1,
            'cyclomatic_complexity': 0.1,
            'code_duplication': 0.05
        }
        
        # Calculate weighted performance score
        performance_score = sum(
            performance_improvement.get(metric, 0) * weight
            for metric, weight in performance_weights.items()
        )
        
        # Calculate weighted quality score
        quality_score = sum(
            quality_improvement.get(metric, 0) * weight
            for metric, weight in quality_weights.items()
        )
        
        # Combine scores (60% quality, 40% performance)
        overall_score = quality_score * 0.6 + performance_score * 0.4
        
        # Normalize to 0-1 range and ensure positive
        return max(0.0, min(1.0, overall_score + 0.5))  # Add 0.5 baseline
        
    def _assess_risk(self, 
                    performance_improvement: Dict[str, float], 
                    quality_improvement: Dict[str, float]) -> str:
        """Assess risk level of the enhancement"""
        
        # Check for negative impacts
        negative_performance = sum(1 for v in performance_improvement.values() if v < -0.1)
        negative_quality = sum(1 for v in quality_improvement.values() if v < -0.1)
        
        total_negative = negative_performance + negative_quality
        
        if total_negative >= 3:
            return "high"
        elif total_negative >= 2:
            return "medium"
        elif total_negative >= 1:
            return "low"
        else:
            return "minimal"
            
    def _store_impact(self, impact: EnhancementImpact):
        """Store impact in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO enhancement_impacts (enhancement_id, impact_data, timestamp) VALUES (?, ?, ?)",
                (impact.enhancement_id, json.dumps(asdict(impact), default=str), impact.timestamp)
            )
            
    def start_real_time_monitoring(self):
        """Start real-time system monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Real-time metrics monitoring started")
        
    def stop_real_time_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logging.info("Real-time metrics monitoring stopped")
        
    def _monitoring_loop(self):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Store metrics
                metric_id = f"system_{int(time.time())}"
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "INSERT INTO system_metrics (metric_id, metric_data, timestamp) VALUES (?, ?, ?)",
                        (metric_id, json.dumps(asdict(system_metrics)), time.time())
                    )
                    
                # Sleep for monitoring interval
                time.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logging.error(f"Monitoring loop error: {e}")
                time.sleep(10)  # Wait before retrying
                
    def _collect_system_metrics(self) -> SystemHealthMetrics:
        """Collect current system health metrics"""
        
        # Get recent impacts from history
        recent_impacts = [impact for impact in self.metrics_history 
                         if time.time() - impact.timestamp < 3600]  # Last hour
        
        total_enhancements = len(recent_impacts)
        successful_enhancements = sum(1 for impact in recent_impacts if impact.overall_score > 0.5)
        success_rate = (successful_enhancements / total_enhancements) if total_enhancements > 0 else 0.0
        
        avg_impact_score = np.mean([impact.overall_score for impact in recent_impacts]) if recent_impacts else 0.0
        avg_implementation_time = np.mean([impact.implementation_time for impact in recent_impacts]) if recent_impacts else 0.0
        
        # Calculate cumulative improvements
        cumulative_improvement = defaultdict(float)
        for impact in recent_impacts:
            for metric, value in impact.performance_improvement.items():
                cumulative_improvement[f"performance_{metric}"] += value
            for metric, value in impact.quality_improvement.items():
                cumulative_improvement[f"quality_{metric}"] += value
                
        # Calculate stability score (based on consistency of improvements)
        if recent_impacts:
            scores = [impact.overall_score for impact in recent_impacts]
            stability_score = 1.0 - (np.std(scores) / max(np.mean(scores), 0.1))
        else:
            stability_score = 1.0
            
        # Calculate error rate (enhancements with negative impact)
        error_rate = sum(1 for impact in recent_impacts if impact.overall_score < 0.0) / max(total_enhancements, 1)
        
        return SystemHealthMetrics(
            total_enhancements=total_enhancements,
            successful_enhancements=successful_enhancements,
            success_rate=success_rate,
            average_impact_score=avg_impact_score,
            average_implementation_time=avg_implementation_time,
            cumulative_improvement=dict(cumulative_improvement),
            stability_score=max(0.0, stability_score),
            error_rate=error_rate,
            timestamp=time.time()
        )
        
    def generate_comprehensive_report(self, days: int = 7) -> str:
        """Generate comprehensive metrics report"""
        
        # Get recent impacts
        cutoff_time = time.time() - (days * 24 * 3600)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT impact_data FROM enhancement_impacts WHERE timestamp > ? ORDER BY timestamp DESC",
                (cutoff_time,)
            )
            
            impacts = []
            for row in cursor.fetchall():
                impact_data = json.loads(row[0])
                
                # Reconstruct nested objects
                impact_data['performance_before'] = PerformanceMetrics(**impact_data['performance_before'])
                impact_data['performance_after'] = PerformanceMetrics(**impact_data['performance_after'])
                impact_data['quality_before'] = QualityMetrics(**impact_data['quality_before'])
                impact_data['quality_after'] = QualityMetrics(**impact_data['quality_after'])
                
                impacts.append(EnhancementImpact(**impact_data))
                
        if not impacts:
            logging.warning("No enhancement impacts found for report generation")
            return "No data available for report generation"
            
        # Generate dashboard
        dashboard_file = self.visualizer.create_enhancement_dashboard(impacts)
        
        logging.info(f"Comprehensive report generated: {dashboard_file}")
        return dashboard_file
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        with sqlite3.connect(self.db_path) as conn:
            # Enhancement metrics
            cursor = conn.execute("SELECT COUNT(*), AVG(json_extract(impact_data, '$.overall_score')) FROM enhancement_impacts")
            total_enhancements, avg_score = cursor.fetchone()
            
            # Recent activity
            recent_cutoff = time.time() - 86400  # Last 24 hours
            cursor = conn.execute("SELECT COUNT(*) FROM enhancement_impacts WHERE timestamp > ?", (recent_cutoff,))
            recent_enhancements = cursor.fetchone()[0]
            
            # Success rate
            cursor = conn.execute("SELECT COUNT(*) FROM enhancement_impacts WHERE json_extract(impact_data, '$.overall_score') > 0.5")
            successful_enhancements = cursor.fetchone()[0]
            
            success_rate = (successful_enhancements / max(total_enhancements, 1)) * 100
            
        return {
            'total_enhancements': total_enhancements or 0,
            'successful_enhancements': successful_enhancements or 0,
            'success_rate': success_rate,
            'average_score': avg_score or 0.0,
            'recent_activity': recent_enhancements or 0,
            'monitoring_active': self.monitoring_active,
            'metrics_history_size': len(self.metrics_history)
        }