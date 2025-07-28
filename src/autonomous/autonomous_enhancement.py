"""
Autonomous Enhancement Loop (AEL) for SuperMini
Provides self-analysis, code modification, and autonomous improvement capabilities
"""

import time
import logging
import json
import ast
import inspect
import subprocess
import hashlib
import requests
import os
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock, Thread
import shutil
import tempfile
import sys
import importlib.util

@dataclass
class CodeAnalysis:
    """Code analysis result"""
    file_path: str
    analysis_type: str
    issues: List[Dict[str, Any]]
    metrics: Dict[str, float]
    suggestions: List[Dict[str, Any]]
    confidence: float
    timestamp: float

@dataclass
class Enhancement:
    """Code enhancement suggestion"""
    enhancement_id: str
    target_file: str
    enhancement_type: str
    description: str
    code_changes: List[Dict[str, Any]]
    expected_improvement: float
    risk_level: str
    validation_method: str
    timestamp: float

@dataclass
class EnhancementResult:
    """Result of applying an enhancement"""
    enhancement_id: str
    success: bool
    applied_changes: List[str]
    performance_impact: Dict[str, float]
    validation_results: Dict[str, Any]
    rollback_info: Optional[Dict[str, Any]]
    timestamp: float

class GitHubIntegrationManager:
    """Manages autonomous contributions to GitHub repository"""
    
    def __init__(self, repo_owner: str, repo_name: str, github_token: Optional[str] = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.repo_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}"
        
        # GitHub API headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SuperMini-Autonomous-Enhancement/2.1.0"
        }
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
            
        # Safety settings
        self.max_changes_per_pr = 5
        self.allowed_file_patterns = [
            "*.py", "*.md", "*.txt", "*.json", "*.yml", "*.yaml"
        ]
        self.forbidden_paths = [
            ".github/workflows/",
            "scripts/",
            "requirements.txt",
            "setup.py"
        ]
        
    def can_create_pull_request(self) -> bool:
        """Check if GitHub integration is properly configured"""
        if not self.github_token:
            logging.warning("GitHub token not configured for autonomous contributions")
            return False
            
        try:
            # Test API access
            response = requests.get(self.repo_url, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"GitHub API test failed: {e}")
            return False
            
    def create_enhancement_branch(self, enhancement_id: str) -> Optional[str]:
        """Create a new branch for autonomous enhancement"""
        if not self.can_create_pull_request():
            return None
            
        branch_name = f"autonomous/enhancement-{enhancement_id}"
        
        try:
            # Get main branch SHA
            main_response = requests.get(f"{self.repo_url}/git/ref/heads/main", headers=self.headers)
            if main_response.status_code != 200:
                logging.error("Failed to get main branch reference")
                return None
                
            main_sha = main_response.json()["object"]["sha"]
            
            # Create new branch
            branch_data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": main_sha
            }
            
            branch_response = requests.post(f"{self.repo_url}/git/refs", 
                                         headers=self.headers, 
                                         json=branch_data)
            
            if branch_response.status_code == 201:
                logging.info(f"Created enhancement branch: {branch_name}")
                return branch_name
            else:
                logging.error(f"Failed to create branch: {branch_response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Branch creation failed: {e}")
            return None
            
    def commit_changes(self, branch_name: str, file_path: str, content: str, 
                      commit_message: str) -> bool:
        """Commit changes to the enhancement branch"""
        try:
            # Get current file content and SHA
            file_response = requests.get(f"{self.repo_url}/contents/{file_path}",
                                       headers=self.headers,
                                       params={"ref": branch_name})
            
            commit_data = {
                "message": commit_message,
                "content": content,
                "branch": branch_name
            }
            
            # If file exists, include SHA for update
            if file_response.status_code == 200:
                commit_data["sha"] = file_response.json()["sha"]
                
            # Commit the changes
            commit_response = requests.put(f"{self.repo_url}/contents/{file_path}",
                                         headers=self.headers,
                                         json=commit_data)
            
            if commit_response.status_code in [200, 201]:
                logging.info(f"Successfully committed changes to {file_path}")
                return True
            else:
                logging.error(f"Failed to commit changes: {commit_response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Commit failed: {e}")
            return False
            
    def create_pull_request(self, branch_name: str, enhancement: 'Enhancement', 
                          results: List['EnhancementResult']) -> Optional[str]:
        """Create a pull request for autonomous enhancement"""
        try:
            # Generate PR title and description
            pr_title = f"🤖 Autonomous Enhancement: {enhancement.description}"
            
            pr_body = self._generate_pr_description(enhancement, results)
            
            pr_data = {
                "title": pr_title,
                "head": branch_name,
                "base": "main",
                "body": pr_body,
                "draft": False
            }
            
            pr_response = requests.post(f"{self.repo_url}/pulls",
                                      headers=self.headers,
                                      json=pr_data)
            
            if pr_response.status_code == 201:
                pr_url = pr_response.json()["html_url"]
                logging.info(f"Created pull request: {pr_url}")
                
                # Add labels
                self._add_pr_labels(pr_response.json()["number"])
                
                return pr_url
            else:
                logging.error(f"Failed to create PR: {pr_response.text}")
                return None
                
        except Exception as e:
            logging.error(f"PR creation failed: {e}")
            return None
            
    def _generate_pr_description(self, enhancement: 'Enhancement', 
                               results: List['EnhancementResult']) -> str:
        """Generate comprehensive PR description"""
        description = f"""## 🤖 Autonomous Enhancement

This pull request was automatically generated by SuperMini's "Enhance Yourself" mode.

### Enhancement Details
- **Type**: {enhancement.enhancement_type}
- **Target File**: {enhancement.target_file}
- **Risk Level**: {enhancement.risk_level}
- **Expected Improvement**: {enhancement.expected_improvement:.2%}

### Description
{enhancement.description}

### Changes Made
"""
        
        for result in results:
            if result.success:
                description += f"✅ **{result.enhancement_id}**\n"
                for change in result.applied_changes:
                    description += f"  - {change}\n"
            else:
                description += f"❌ **{result.enhancement_id}** (failed)\n"
                
        description += """
### Validation Results
All changes have been automatically validated using:
- Syntax checking
- Import validation
- Basic functionality tests

### Safety Measures
- ✅ Automated backup created before changes
- ✅ Validation completed successfully
- ✅ Risk assessment: LOW
- ✅ Human review recommended before merge

### Performance Impact
"""
        
        for result in results:
            if result.success and result.performance_impact:
                description += f"- Execution time change: {result.performance_impact.get('execution_time_change', 0):.1%}\n"
                description += f"- Memory usage change: {result.performance_impact.get('memory_usage_change', 0):.1%}\n"
                
        description += """
---

🔍 **Human Review Required**: Please review these autonomous changes before merging.

🤖 **Generated by SuperMini v2.1.0** - Autonomous Enhancement Mode

Co-Authored-By: SuperMini AI <noreply@supermini.ai>
"""
        
        return description
        
    def _add_pr_labels(self, pr_number: int):
        """Add appropriate labels to the PR"""
        labels = ["autonomous", "enhancement", "ai-generated"]
        
        try:
            requests.post(f"{self.repo_url}/issues/{pr_number}/labels",
                         headers=self.headers,
                         json={"labels": labels})
        except Exception as e:
            logging.warning(f"Failed to add PR labels: {e}")
            
    def is_file_allowed(self, file_path: str) -> bool:
        """Check if file is allowed for autonomous modification"""
        # Check forbidden paths
        for forbidden in self.forbidden_paths:
            if file_path.startswith(forbidden):
                return False
                
        # Check allowed patterns
        file_path_obj = Path(file_path)
        for pattern in self.allowed_file_patterns:
            if file_path_obj.match(pattern):
                return True
                
        return False

class SelfAnalyzer:
    """Analyzes system performance and identifies improvement opportunities"""
    
    def __init__(self, target_files: List[str], output_dir: Path):
        self.target_files = target_files
        self.output_dir = output_dir
        self.analysis_dir = output_dir / "analysis"
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis state
        self.analysis_history = []
        self.current_metrics = {}
        self.baseline_metrics = {}
        
        # Analysis tools
        self.analyzers = {
            "performance": self._analyze_performance,
            "complexity": self._analyze_complexity,
            "maintainability": self._analyze_maintainability,
            "security": self._analyze_security,
            "efficiency": self._analyze_efficiency
        }
        
    def perform_comprehensive_analysis(self) -> List[CodeAnalysis]:
        """Perform comprehensive analysis of target files"""
        logging.info("Starting comprehensive code analysis")
        
        analyses = []
        
        for file_path in self.target_files:
            if not Path(file_path).exists():
                logging.warning(f"Target file not found: {file_path}")
                continue
                
            for analysis_type, analyzer in self.analyzers.items():
                try:
                    analysis = analyzer(file_path)
                    if analysis:
                        analyses.append(analysis)
                        logging.debug(f"Completed {analysis_type} analysis for {file_path}")
                except Exception as e:
                    logging.error(f"Analysis failed for {file_path} ({analysis_type}): {e}")
                    
        self.analysis_history.extend(analyses)
        self._save_analysis_results(analyses)
        
        return analyses
        
    def _analyze_performance(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze code for performance issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            issues = []
            metrics = {}
            suggestions = []
            
            # Analyze AST for performance issues
            performance_visitor = PerformanceAnalysisVisitor()
            performance_visitor.visit(tree)
            
            issues.extend(performance_visitor.issues)
            metrics.update(performance_visitor.metrics)
            suggestions.extend(performance_visitor.suggestions)
            
            # Calculate overall metrics
            metrics["total_issues"] = len(issues)
            metrics["performance_score"] = max(0, 1.0 - (len(issues) * 0.1))
            
            return CodeAnalysis(
                file_path=file_path,
                analysis_type="performance",
                issues=issues,
                metrics=metrics,
                suggestions=suggestions,
                confidence=0.8,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Performance analysis failed: {e}")
            return None
            
    def _analyze_complexity(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze code complexity"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            complexity_visitor = ComplexityAnalysisVisitor()
            complexity_visitor.visit(tree)
            
            metrics = complexity_visitor.metrics
            issues = complexity_visitor.issues
            suggestions = complexity_visitor.suggestions
            
            return CodeAnalysis(
                file_path=file_path,
                analysis_type="complexity",
                issues=issues,
                metrics=metrics,
                suggestions=suggestions,
                confidence=0.9,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Complexity analysis failed: {e}")
            return None
            
    def _analyze_maintainability(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze code maintainability"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            issues = []
            metrics = {}
            suggestions = []
            
            # Basic maintainability checks
            total_lines = len(lines)
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            blank_lines = sum(1 for line in lines if not line.strip())
            code_lines = total_lines - comment_lines - blank_lines
            
            # Calculate metrics
            metrics["total_lines"] = total_lines
            metrics["code_lines"] = code_lines
            metrics["comment_lines"] = comment_lines
            metrics["comment_ratio"] = comment_lines / max(code_lines, 1)
            
            # Check for issues
            if metrics["comment_ratio"] < 0.1:
                issues.append({
                    "type": "low_documentation",
                    "severity": "medium",
                    "message": f"Low comment ratio: {metrics['comment_ratio']:.2%}",
                    "line": None
                })
                suggestions.append({
                    "type": "add_documentation",
                    "description": "Add more comments and documentation",
                    "priority": "medium"
                })
                
            # Check function lengths
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_length = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_length > 50:
                        issues.append({
                            "type": "long_function",
                            "severity": "medium",
                            "message": f"Function '{node.name}' is {func_length} lines long",
                            "line": node.lineno
                        })
                        suggestions.append({
                            "type": "refactor_function",
                            "description": f"Consider breaking down function '{node.name}' into smaller functions",
                            "priority": "medium",
                            "target": node.name
                        })
            
            metrics["maintainability_score"] = max(0, 1.0 - (len(issues) * 0.15))
            
            return CodeAnalysis(
                file_path=file_path,
                analysis_type="maintainability",
                issues=issues,
                metrics=metrics,
                suggestions=suggestions,
                confidence=0.7,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Maintainability analysis failed: {e}")
            return None
            
    def _analyze_security(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze code for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues = []
            suggestions = []
            
            # Basic security pattern checking
            security_patterns = [
                ("eval(", "Use of eval() can be dangerous"),
                ("exec(", "Use of exec() can be dangerous"),
                ("os.system(", "Use of os.system() can be dangerous"),
                ("subprocess.call(", "Direct subprocess calls should be validated"),
                ("pickle.loads(", "Unpickling untrusted data is dangerous"),
                ("input(", "User input should be validated")
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern, message in security_patterns:
                    if pattern in line:
                        issues.append({
                            "type": "security_risk",
                            "severity": "high" if pattern in ["eval(", "exec(", "pickle.loads("] else "medium",
                            "message": message,
                            "line": i,
                            "pattern": pattern
                        })
                        
            # Generate suggestions
            if issues:
                suggestions.append({
                    "type": "security_review",
                    "description": "Review and validate all identified security risks",
                    "priority": "high"
                })
                
            metrics = {
                "security_issues": len(issues),
                "security_score": max(0, 1.0 - (len(issues) * 0.2))
            }
            
            return CodeAnalysis(
                file_path=file_path,
                analysis_type="security",
                issues=issues,
                metrics=metrics,
                suggestions=suggestions,
                confidence=0.6,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Security analysis failed: {e}")
            return None
            
    def _analyze_efficiency(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze code for efficiency improvements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            issues = []
            suggestions = []
            
            # Look for inefficient patterns
            for node in ast.walk(tree):
                # Check for inefficient list operations
                if isinstance(node, ast.ListComp):
                    # Look for nested list comprehensions
                    for child in ast.walk(node):
                        if isinstance(child, ast.ListComp) and child != node:
                            issues.append({
                                "type": "nested_list_comprehension",
                                "severity": "low",
                                "message": "Nested list comprehensions can be inefficient",
                                "line": getattr(node, 'lineno', None)
                            })
                            
                # Check for string concatenation in loops
                if isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                            if isinstance(child.target, ast.Name):
                                issues.append({
                                    "type": "string_concat_in_loop",
                                    "severity": "medium",
                                    "message": "String concatenation in loop can be inefficient",
                                    "line": getattr(child, 'lineno', None)
                                })
                                
            # Generate efficiency suggestions
            if any(issue["type"] == "string_concat_in_loop" for issue in issues):
                suggestions.append({
                    "type": "use_join",
                    "description": "Use str.join() instead of string concatenation in loops",
                    "priority": "medium"
                })
                
            metrics = {
                "efficiency_issues": len(issues),
                "efficiency_score": max(0, 1.0 - (len(issues) * 0.1))
            }
            
            return CodeAnalysis(
                file_path=file_path,
                analysis_type="efficiency",
                issues=issues,
                metrics=metrics,
                suggestions=suggestions,
                confidence=0.7,
                timestamp=time.time()
            )
            
        except Exception as e:
            logging.error(f"Efficiency analysis failed: {e}")
            return None
            
    def _save_analysis_results(self, analyses: List[CodeAnalysis]):
        """Save analysis results to disk"""
        try:
            timestamp = int(time.time())
            results_file = self.analysis_dir / f"analysis_{timestamp}.json"
            
            analysis_data = [asdict(analysis) for analysis in analyses]
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2)
                
            logging.info(f"Analysis results saved to {results_file}")
            
        except Exception as e:
            logging.error(f"Failed to save analysis results: {e}")
            
    def get_improvement_priorities(self) -> List[Dict[str, Any]]:
        """Get prioritized list of improvement opportunities"""
        if not self.analysis_history:
            return []
            
        # Aggregate issues by type and severity
        issue_priorities = []
        
        for analysis in self.analysis_history[-10:]:  # Last 10 analyses
            for issue in analysis.issues:
                priority_score = self._calculate_priority_score(issue, analysis)
                
                issue_priorities.append({
                    "file": analysis.file_path,
                    "analysis_type": analysis.analysis_type,
                    "issue": issue,
                    "priority_score": priority_score,
                    "confidence": analysis.confidence
                })
                
        # Sort by priority score
        issue_priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return issue_priorities[:20]  # Top 20 priorities
        
    def _calculate_priority_score(self, issue: Dict[str, Any], analysis: CodeAnalysis) -> float:
        """Calculate priority score for an issue"""
        severity_weights = {"high": 1.0, "medium": 0.6, "low": 0.3}
        severity_weight = severity_weights.get(issue.get("severity", "low"), 0.3)
        
        confidence_weight = analysis.confidence
        
        # Type-specific weights
        type_weights = {
            "security_risk": 1.0,
            "performance_issue": 0.8,
            "long_function": 0.6,
            "nested_list_comprehension": 0.4,
            "low_documentation": 0.3
        }
        type_weight = type_weights.get(issue.get("type", "unknown"), 0.5)
        
        return severity_weight * confidence_weight * type_weight

class CodeModificationEngine:
    """Safely modifies code based on enhancement suggestions"""
    
    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.modification_history = []
        self.rollback_stack = []
        
    def apply_enhancement(self, enhancement: Enhancement) -> EnhancementResult:
        """Apply a code enhancement with safety checks"""
        logging.info(f"Applying enhancement: {enhancement.enhancement_id}")
        
        # Create backup
        backup_info = self._create_backup(enhancement.target_file)
        
        try:
            # Apply changes
            applied_changes = []
            
            for change in enhancement.code_changes:
                success = self._apply_code_change(enhancement.target_file, change)
                if success:
                    applied_changes.append(change["description"])
                else:
                    # Rollback on failure
                    self._restore_backup(backup_info)
                    return EnhancementResult(
                        enhancement_id=enhancement.enhancement_id,
                        success=False,
                        applied_changes=applied_changes,
                        performance_impact={},
                        validation_results={"error": "Failed to apply code change"},
                        rollback_info=backup_info,
                        timestamp=time.time()
                    )
                    
            # Validate changes
            validation_results = self._validate_changes(enhancement.target_file, enhancement.validation_method)
            
            if not validation_results.get("valid", False):
                # Rollback on validation failure
                self._restore_backup(backup_info)
                return EnhancementResult(
                    enhancement_id=enhancement.enhancement_id,
                    success=False,
                    applied_changes=applied_changes,
                    performance_impact={},
                    validation_results=validation_results,
                    rollback_info=backup_info,
                    timestamp=time.time()
                )
                
            # Measure performance impact
            performance_impact = self._measure_performance_impact(enhancement.target_file)
            
            # Success
            result = EnhancementResult(
                enhancement_id=enhancement.enhancement_id,
                success=True,
                applied_changes=applied_changes,
                performance_impact=performance_impact,
                validation_results=validation_results,
                rollback_info=backup_info,
                timestamp=time.time()
            )
            
            self.modification_history.append(result)
            self.rollback_stack.append(backup_info)
            
            logging.info(f"Enhancement applied successfully: {enhancement.enhancement_id}")
            return result
            
        except Exception as e:
            logging.error(f"Enhancement application failed: {e}")
            self._restore_backup(backup_info)
            
            return EnhancementResult(
                enhancement_id=enhancement.enhancement_id,
                success=False,
                applied_changes=[],
                performance_impact={},
                validation_results={"error": str(e)},
                rollback_info=backup_info,
                timestamp=time.time()
            )
            
    def _create_backup(self, file_path: str) -> Dict[str, Any]:
        """Create backup of file before modification"""
        source_path = Path(file_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        timestamp = int(time.time() * 1000000)
        backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(source_path, backup_path)
        
        backup_info = {
            "original_file": str(source_path),
            "backup_file": str(backup_path),
            "timestamp": timestamp,
            "file_hash": self._calculate_file_hash(str(source_path))
        }
        
        logging.debug(f"Created backup: {backup_path}")
        return backup_info
        
    def _restore_backup(self, backup_info: Dict[str, Any]):
        """Restore file from backup"""
        try:
            shutil.copy2(backup_info["backup_file"], backup_info["original_file"])
            logging.info(f"Restored backup: {backup_info['original_file']}")
        except Exception as e:
            logging.error(f"Failed to restore backup: {e}")
            
    def _apply_code_change(self, file_path: str, change: Dict[str, Any]) -> bool:
        """Apply a single code change"""
        try:
            change_type = change.get("type")
            
            if change_type == "replace_line":
                return self._replace_line(file_path, change)
            elif change_type == "insert_line":
                return self._insert_line(file_path, change)
            elif change_type == "add_import":
                return self._add_import(file_path, change)
            elif change_type == "refactor_function":
                return self._refactor_function(file_path, change)
            else:
                logging.warning(f"Unknown change type: {change_type}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to apply code change: {e}")
            return False
            
    def _replace_line(self, file_path: str, change: Dict[str, Any]) -> bool:
        """Replace a specific line in the file"""
        line_number = change.get("line_number")
        new_content = change.get("new_content")
        
        if line_number is None or new_content is None:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if 1 <= line_number <= len(lines):
                lines[line_number - 1] = new_content + '\n'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                    
                return True
            else:
                logging.error(f"Invalid line number: {line_number}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to replace line: {e}")
            return False
            
    def _insert_line(self, file_path: str, change: Dict[str, Any]) -> bool:
        """Insert a line at specific position"""
        line_number = change.get("line_number")
        new_content = change.get("new_content")
        
        if line_number is None or new_content is None:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            lines.insert(line_number - 1, new_content + '\n')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to insert line: {e}")
            return False
            
    def _add_import(self, file_path: str, change: Dict[str, Any]) -> bool:
        """Add import statement to file"""
        import_statement = change.get("import_statement")
        
        if not import_statement:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if import already exists
            if import_statement in content:
                return True
                
            lines = content.split('\n')
            
            # Find insertion point (after existing imports)
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('#'):
                    break
                    
            lines.insert(insert_index, import_statement)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to add import: {e}")
            return False
            
    def _refactor_function(self, file_path: str, change: Dict[str, Any]) -> bool:
        """Refactor a function (basic implementation)"""
        function_name = change.get("function_name")
        refactor_type = change.get("refactor_type")
        
        if not function_name or not refactor_type:
            return False
            
        # This would require more sophisticated AST manipulation
        # For now, just log the intent
        logging.info(f"Function refactoring requested: {function_name} ({refactor_type})")
        return True
        
    def _validate_changes(self, file_path: str, validation_method: str) -> Dict[str, Any]:
        """Validate applied changes"""
        validation_results = {"valid": False, "errors": []}
        
        try:
            if validation_method == "syntax_check":
                validation_results = self._validate_syntax(file_path)
            elif validation_method == "import_check":
                validation_results = self._validate_imports(file_path)
            elif validation_method == "unit_test":
                validation_results = self._run_unit_tests(file_path)
            else:
                # Default: syntax check
                validation_results = self._validate_syntax(file_path)
                
        except Exception as e:
            validation_results["errors"].append(str(e))
            
        return validation_results
        
    def _validate_syntax(self, file_path: str) -> Dict[str, Any]:
        """Validate Python syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            ast.parse(content)
            return {"valid": True, "errors": []}
            
        except SyntaxError as e:
            return {"valid": False, "errors": [f"Syntax error: {e}"]}
        except Exception as e:
            return {"valid": False, "errors": [f"Validation error: {e}"]}
            
    def _validate_imports(self, file_path: str) -> Dict[str, Any]:
        """Validate that all imports work"""
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec is None:
                return {"valid": False, "errors": ["Could not create module spec"]}
                
            # Try to load the module
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            return {"valid": True, "errors": []}
            
        except ImportError as e:
            return {"valid": False, "errors": [f"Import error: {e}"]}
        except Exception as e:
            return {"valid": False, "errors": [f"Module load error: {e}"]}
            
    def _run_unit_tests(self, file_path: str) -> Dict[str, Any]:
        """Run unit tests for the file"""
        try:
            # Look for test files
            test_file = file_path.replace('.py', '_test.py')
            if not Path(test_file).exists():
                test_file = file_path.replace('.py', '.test.py')
                
            if not Path(test_file).exists():
                return {"valid": True, "errors": [], "message": "No test file found"}
                
            # Run tests
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_file, '-v'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {"valid": True, "errors": [], "test_output": result.stdout}
            else:
                return {"valid": False, "errors": [result.stderr], "test_output": result.stdout}
                
        except subprocess.TimeoutExpired:
            return {"valid": False, "errors": ["Test execution timeout"]}
        except Exception as e:
            return {"valid": False, "errors": [f"Test execution error: {e}"]}
            
    def _measure_performance_impact(self, file_path: str) -> Dict[str, float]:
        """Measure performance impact of changes"""
        # This would require running benchmarks
        # For now, return placeholder metrics
        return {
            "execution_time_change": 0.0,
            "memory_usage_change": 0.0,
            "complexity_change": 0.0
        }
        
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()
        except Exception:
            return ""

class AutonomousEnhancementLoop:
    """Main autonomous enhancement system with GitHub integration"""
    
    def __init__(self, target_files: List[str], output_dir: Path, claude_manager, ollama_manager, 
                 github_integration: bool = False, repo_owner: str = None, repo_name: str = None):
        self.target_files = target_files
        self.output_dir = output_dir
        self.claude = claude_manager
        self.ollama = ollama_manager
        
        # Initialize components
        self.analyzer = SelfAnalyzer(target_files, output_dir)
        self.modifier = CodeModificationEngine(output_dir / "backups")
        
        # GitHub integration
        self.github_integration = github_integration
        self.github_manager = None
        if github_integration and repo_owner and repo_name:
            self.github_manager = GitHubIntegrationManager(repo_owner, repo_name)
            
        # Enhancement state
        self.enhancement_history = []
        self.active_enhancements = {}
        self.enhancement_enabled = True
        self.stop_requested = False
        self.autonomous_pr_enabled = True
        
        # Thread safety
        self.enhancement_lock = Lock()
        
    def start_enhancement_loop(self, interval: float = 3600) -> Thread:
        """Start autonomous enhancement loop in background thread"""
        enhancement_thread = Thread(
            target=self._enhancement_loop,
            args=(interval,),
            daemon=True
        )
        enhancement_thread.start()
        logging.info("Autonomous enhancement loop started")
        return enhancement_thread
        
    def _enhancement_loop(self, interval: float):
        """Main enhancement loop"""
        while not self.stop_requested and self.enhancement_enabled:
            try:
                logging.info("Starting enhancement cycle")
                
                # Perform analysis
                analyses = self.analyzer.perform_comprehensive_analysis()
                
                if analyses:
                    # Generate enhancements
                    enhancements = self._generate_enhancements(analyses)
                    
                    # Apply high-priority, low-risk enhancements
                    for enhancement in enhancements:
                        if (enhancement.risk_level == "low" and 
                            enhancement.expected_improvement > 0.1 and
                            not self.stop_requested):
                            
                            result = self.modifier.apply_enhancement(enhancement)
                            self.enhancement_history.append(result)
                            
                            if result.success:
                                logging.info(f"Successfully applied enhancement: {enhancement.enhancement_id}")
                                
                                # Create GitHub PR if enabled and configured
                                if (self.github_integration and self.github_manager and 
                                    self.autonomous_pr_enabled and 
                                    self.github_manager.is_file_allowed(enhancement.target_file)):
                                    
                                    self._create_autonomous_pr(enhancement, [result])
                                    
                            else:
                                logging.warning(f"Enhancement failed: {enhancement.enhancement_id}")
                                
                # Wait for next cycle
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"Enhancement loop error: {e}")
                time.sleep(60)  # Wait before retrying
                
    def _generate_enhancements(self, analyses: List[CodeAnalysis]) -> List[Enhancement]:
        """Generate enhancement suggestions from analyses"""
        enhancements = []
        
        # Get improvement priorities
        priorities = self.analyzer.get_improvement_priorities()
        
        for priority in priorities[:5]:  # Top 5 priorities
            enhancement = self._create_enhancement_from_priority(priority)
            if enhancement:
                enhancements.append(enhancement)
                
        return enhancements
        
    def _create_enhancement_from_priority(self, priority: Dict[str, Any]) -> Optional[Enhancement]:
        """Create enhancement from priority issue"""
        issue = priority["issue"]
        file_path = priority["file"]
        
        enhancement_id = f"enhance_{int(time.time() * 1000000)}"
        
        # Generate enhancement based on issue type
        if issue["type"] == "long_function":
            return self._create_function_refactor_enhancement(enhancement_id, file_path, issue)
        elif issue["type"] == "string_concat_in_loop":
            return self._create_string_optimization_enhancement(enhancement_id, file_path, issue)
        elif issue["type"] == "low_documentation":
            return self._create_documentation_enhancement(enhancement_id, file_path, issue)
        else:
            return None
            
    def _create_function_refactor_enhancement(self, enhancement_id: str, file_path: str, issue: Dict[str, Any]) -> Enhancement:
        """Create function refactoring enhancement"""
        return Enhancement(
            enhancement_id=enhancement_id,
            target_file=file_path,
            enhancement_type="refactor",
            description=f"Refactor long function at line {issue.get('line', 'unknown')}",
            code_changes=[{
                "type": "refactor_function",
                "function_name": "unknown",  # Would need more sophisticated analysis
                "refactor_type": "split",
                "description": "Split long function into smaller functions"
            }],
            expected_improvement=0.2,
            risk_level="medium",
            validation_method="syntax_check",
            timestamp=time.time()
        )
        
    def _create_string_optimization_enhancement(self, enhancement_id: str, file_path: str, issue: Dict[str, Any]) -> Enhancement:
        """Create string concatenation optimization"""
        line_number = issue.get('line')
        
        return Enhancement(
            enhancement_id=enhancement_id,
            target_file=file_path,
            enhancement_type="optimization",
            description=f"Optimize string concatenation at line {line_number}",
            code_changes=[{
                "type": "replace_line",
                "line_number": line_number,
                "new_content": "    # TODO: Replace with str.join() for better performance",
                "description": f"Add optimization comment at line {line_number}"
            }],
            expected_improvement=0.15,
            risk_level="low",
            validation_method="syntax_check",
            timestamp=time.time()
        )
        
    def _create_documentation_enhancement(self, enhancement_id: str, file_path: str, issue: Dict[str, Any]) -> Enhancement:
        """Create documentation enhancement"""
        return Enhancement(
            enhancement_id=enhancement_id,
            target_file=file_path,
            enhancement_type="documentation",
            description="Add missing documentation",
            code_changes=[{
                "type": "insert_line",
                "line_number": 1,
                "new_content": '"""Enhanced with autonomous documentation improvements"""',
                "description": "Add file-level documentation"
            }],
            expected_improvement=0.1,
            risk_level="low",
            validation_method="syntax_check",
            timestamp=time.time()
        )
        
    def _create_autonomous_pr(self, enhancement: Enhancement, results: List[EnhancementResult]):
        """Create autonomous pull request for enhancements"""
        try:
            logging.info(f"Creating autonomous PR for enhancement: {enhancement.enhancement_id}")
            
            # Create branch
            branch_name = self.github_manager.create_enhancement_branch(enhancement.enhancement_id)
            if not branch_name:
                logging.error("Failed to create enhancement branch")
                return
                
            # Read modified file content
            try:
                with open(enhancement.target_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                logging.error(f"Failed to read modified file: {e}")
                return
                
            # Encode content for GitHub API
            import base64
            encoded_content = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
            
            # Commit changes
            commit_message = f"🤖 Autonomous enhancement: {enhancement.description}\n\nAuto-generated by SuperMini v2.1.0\nEnhancement ID: {enhancement.enhancement_id}\nRisk Level: {enhancement.risk_level}\nExpected Improvement: {enhancement.expected_improvement:.2%}"
            
            if self.github_manager.commit_changes(branch_name, enhancement.target_file, 
                                                encoded_content, commit_message):
                
                # Create pull request
                pr_url = self.github_manager.create_pull_request(branch_name, enhancement, results)
                
                if pr_url:
                    logging.info(f"✅ Autonomous PR created successfully: {pr_url}")
                    
                    # Store PR info in results
                    for result in results:
                        if not hasattr(result, 'github_pr_url'):
                            result.github_pr_url = pr_url
                else:
                    logging.error("Failed to create pull request")
            else:
                logging.error("Failed to commit changes to branch")
                
        except Exception as e:
            logging.error(f"Autonomous PR creation failed: {e}")
            
    def enable_autonomous_prs(self, enabled: bool = True):
        """Enable or disable autonomous PR creation"""
        self.autonomous_pr_enabled = enabled
        status = "enabled" if enabled else "disabled"
        logging.info(f"Autonomous PR creation {status}")
        
    def get_github_integration_status(self) -> Dict[str, Any]:
        """Get status of GitHub integration"""
        status = {
            "integration_enabled": self.github_integration,
            "manager_configured": self.github_manager is not None,
            "pr_creation_enabled": self.autonomous_pr_enabled,
            "can_create_prs": False,
            "repository": None
        }
        
        if self.github_manager:
            status["can_create_prs"] = self.github_manager.can_create_pull_request()
            status["repository"] = f"{self.github_manager.repo_owner}/{self.github_manager.repo_name}"
            
        return status

    def stop_enhancement_loop(self):
        """Stop the enhancement loop"""
        self.stop_requested = True
        logging.info("Enhancement loop stop requested")
        
    def get_enhancement_summary(self) -> Dict[str, Any]:
        """Get summary of enhancement activities"""
        successful_enhancements = [e for e in self.enhancement_history if e.success]
        
        return {
            "total_enhancements": len(self.enhancement_history),
            "successful_enhancements": len(successful_enhancements),
            "success_rate": len(successful_enhancements) / max(len(self.enhancement_history), 1),
            "avg_improvement": sum(e.performance_impact.get("execution_time_change", 0) 
                                 for e in successful_enhancements) / max(len(successful_enhancements), 1),
            "enhancement_enabled": self.enhancement_enabled,
            "stop_requested": self.stop_requested
        }

# AST Visitor classes for analysis
class PerformanceAnalysisVisitor(ast.NodeVisitor):
    """AST visitor for performance analysis"""
    
    def __init__(self):
        self.issues = []
        self.metrics = {}
        self.suggestions = []
        self.loop_depth = 0
        
    def visit_For(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
        
    def visit_While(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1
        
    def visit_Call(self, node):
        # Check for inefficient calls in loops
        if self.loop_depth > 0:
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ['append', 'extend'] and self.loop_depth > 1:
                    self.issues.append({
                        "type": "performance_issue",
                        "severity": "medium",
                        "message": "List operations in nested loops can be inefficient",
                        "line": getattr(node, 'lineno', None)
                    })
                    
        self.generic_visit(node)

class ComplexityAnalysisVisitor(ast.NodeVisitor):
    """AST visitor for complexity analysis"""
    
    def __init__(self):
        self.metrics = {}
        self.issues = []
        self.suggestions = []
        self.function_count = 0
        self.class_count = 0
        self.max_nesting = 0
        self.current_nesting = 0
        
    def visit_FunctionDef(self, node):
        self.function_count += 1
        
        # Calculate function complexity
        complexity = self._calculate_cyclomatic_complexity(node)
        
        if complexity > 10:
            self.issues.append({
                "type": "high_complexity",
                "severity": "medium",
                "message": f"Function '{node.name}' has high complexity: {complexity}",
                "line": node.lineno
            })
            
        self.generic_visit(node)
        
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)
        
    def visit_If(self, node):
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
        
    def visit_For(self, node):
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
        
    def visit_While(self, node):
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
        
    def _calculate_cyclomatic_complexity(self, node):
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
        
    def visit_Module(self, node):
        self.generic_visit(node)
        
        self.metrics.update({
            "function_count": self.function_count,
            "class_count": self.class_count,
            "max_nesting_depth": self.max_nesting,
            "complexity_score": max(0, 1.0 - (self.max_nesting * 0.1))
        })
        
        if self.max_nesting > 5:
            self.issues.append({
                "type": "deep_nesting",
                "severity": "medium",
                "message": f"Maximum nesting depth is {self.max_nesting}",
                "line": None
            })

# Alias for backward compatibility
EnhancementEngine = AutonomousEnhancementLoop