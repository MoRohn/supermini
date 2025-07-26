"""
Regression Tester for SuperMini Autonomous Enhancements
Validates that code modifications don't break existing functionality
"""

import time
import logging
import json
import subprocess
import sys
import tempfile
import shutil
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Lock, Thread
import importlib.util
import traceback
import pickle
import ast

@dataclass
class TestCase:
    """Individual test case definition"""
    test_id: str
    name: str
    test_type: str  # unit, integration, functional, performance
    target_function: Optional[str]
    input_data: Dict[str, Any]
    expected_output: Any
    tolerance: float = 0.0
    timeout: float = 30.0
    setup_code: Optional[str] = None
    teardown_code: Optional[str] = None

@dataclass
class TestResult:
    """Test execution result"""
    test_id: str
    success: bool
    execution_time: float
    actual_output: Any
    expected_output: Any
    error_message: Optional[str]
    performance_metrics: Dict[str, float]
    timestamp: float

@dataclass
class RegressionSuite:
    """Collection of regression tests"""
    suite_id: str
    name: str
    target_files: List[str]
    test_cases: List[TestCase]
    baseline_results: List[TestResult]
    created_at: float
    last_run: Optional[float] = None

class TestGenerator:
    """Automatically generates test cases from code analysis"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.test_dir = output_dir / "tests"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_tests_for_file(self, file_path: str) -> List[TestCase]:
        """Generate test cases for a Python file"""
        logging.info(f"Generating tests for {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            test_cases = []
            
            # Generate tests for functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):  # Skip private functions
                        test_case = self._generate_function_test(file_path, node)
                        if test_case:
                            test_cases.append(test_case)
                            
            # Generate tests for classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_tests = self._generate_class_tests(file_path, node)
                    test_cases.extend(class_tests)
                    
            logging.info(f"Generated {len(test_cases)} test cases for {file_path}")
            return test_cases
            
        except Exception as e:
            logging.error(f"Test generation failed for {file_path}: {e}")
            return []
            
    def _generate_function_test(self, file_path: str, func_node: ast.FunctionDef) -> Optional[TestCase]:
        """Generate test case for a function"""
        try:
            # Analyze function signature
            func_name = func_node.name
            args = [arg.arg for arg in func_node.args.args]
            
            # Skip functions with complex signatures for now
            if len(args) > 5 or any(arg.startswith('*') for arg in args):
                return None
                
            # Generate test inputs based on argument analysis
            test_inputs = self._generate_test_inputs(func_node)
            
            test_id = f"test_{func_name}_{int(time.time() * 1000000)}"
            
            return TestCase(
                test_id=test_id,
                name=f"Test {func_name}",
                test_type="unit",
                target_function=func_name,
                input_data=test_inputs,
                expected_output=None,  # Will be captured during baseline run
                tolerance=0.01,
                timeout=10.0
            )
            
        except Exception as e:
            logging.error(f"Function test generation failed: {e}")
            return None
            
    def _generate_class_tests(self, file_path: str, class_node: ast.ClassDef) -> List[TestCase]:
        """Generate test cases for a class"""
        test_cases = []
        
        try:
            class_name = class_node.name
            
            # Find __init__ method
            init_method = None
            public_methods = []
            
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef):
                    if node.name == '__init__':
                        init_method = node
                    elif not node.name.startswith('_'):
                        public_methods.append(node)
                        
            # Generate constructor test
            if init_method:
                test_inputs = self._generate_test_inputs(init_method)
                
                test_id = f"test_{class_name}_init_{int(time.time() * 1000000)}"
                
                test_cases.append(TestCase(
                    test_id=test_id,
                    name=f"Test {class_name} constructor",
                    test_type="unit",
                    target_function=f"{class_name}.__init__",
                    input_data=test_inputs,
                    expected_output=None,
                    timeout=5.0
                ))
                
            # Generate method tests
            for method in public_methods[:3]:  # Limit to first 3 methods
                test_inputs = self._generate_test_inputs(method)
                
                test_id = f"test_{class_name}_{method.name}_{int(time.time() * 1000000)}"
                
                test_cases.append(TestCase(
                    test_id=test_id,
                    name=f"Test {class_name}.{method.name}",
                    test_type="unit",
                    target_function=f"{class_name}.{method.name}",
                    input_data=test_inputs,
                    expected_output=None,
                    timeout=10.0
                ))
                
        except Exception as e:
            logging.error(f"Class test generation failed: {e}")
            
        return test_cases
        
    def _generate_test_inputs(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Generate test inputs for a function based on its signature"""
        inputs = {}
        
        for arg in func_node.args.args:
            arg_name = arg.arg
            
            # Skip 'self' argument
            if arg_name == 'self':
                continue
                
            # Generate input based on argument name patterns
            if any(keyword in arg_name.lower() for keyword in ['id', 'count', 'num', 'size']):
                inputs[arg_name] = 42
            elif any(keyword in arg_name.lower() for keyword in ['name', 'text', 'str']):
                inputs[arg_name] = "test_string"
            elif any(keyword in arg_name.lower() for keyword in ['list', 'items']):
                inputs[arg_name] = [1, 2, 3]
            elif any(keyword in arg_name.lower() for keyword in ['dict', 'config']):
                inputs[arg_name] = {"key": "value"}
            elif any(keyword in arg_name.lower() for keyword in ['flag', 'enable', 'bool']):
                inputs[arg_name] = True
            elif any(keyword in arg_name.lower() for keyword in ['path', 'file']):
                inputs[arg_name] = "/tmp/test_file.txt"
            else:
                # Default to string
                inputs[arg_name] = f"test_{arg_name}"
                
        return inputs

class TestExecutor:
    """Executes test cases and captures results"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.execution_lock = Lock()
        
    def execute_test_case(self, test_case: TestCase, target_file: str) -> TestResult:
        """Execute a single test case"""
        start_time = time.time()
        
        try:
            # Load the target module
            module = self._load_module(target_file)
            
            if not module:
                return TestResult(
                    test_id=test_case.test_id,
                    success=False,
                    execution_time=time.time() - start_time,
                    actual_output=None,
                    expected_output=test_case.expected_output,
                    error_message="Failed to load module",
                    performance_metrics={},
                    timestamp=time.time()
                )
                
            # Execute the test
            actual_output, error_message, perf_metrics = self._execute_test(test_case, module)
            
            execution_time = time.time() - start_time
            
            # Compare results
            success = self._compare_outputs(actual_output, test_case.expected_output, test_case.tolerance)
            
            if error_message:
                success = False
                
            return TestResult(
                test_id=test_case.test_id,
                success=success,
                execution_time=execution_time,
                actual_output=actual_output,
                expected_output=test_case.expected_output,
                error_message=error_message,
                performance_metrics=perf_metrics,
                timestamp=time.time()
            )
            
        except Exception as e:
            return TestResult(
                test_id=test_case.test_id,
                success=False,
                execution_time=time.time() - start_time,
                actual_output=None,
                expected_output=test_case.expected_output,
                error_message=str(e),
                performance_metrics={},
                timestamp=time.time()
            )
            
    def _load_module(self, file_path: str):
        """Load Python module from file"""
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            if spec is None:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
            
        except Exception as e:
            logging.error(f"Failed to load module {file_path}: {e}")
            return None
            
    def _execute_test(self, test_case: TestCase, module) -> Tuple[Any, Optional[str], Dict[str, float]]:
        """Execute the actual test"""
        try:
            # Setup if needed
            if test_case.setup_code:
                exec(test_case.setup_code, module.__dict__)
                
            # Get the target function/class
            target = self._get_target_callable(test_case, module)
            
            if not target:
                return None, f"Target not found: {test_case.target_function}", {}
                
            # Measure performance
            start_time = time.time()
            
            # Call the function with test inputs
            if test_case.target_function and '.' in test_case.target_function:
                # Class method
                class_name, method_name = test_case.target_function.split('.', 1)
                
                if method_name == '__init__':
                    # Constructor
                    result = target(**test_case.input_data)
                else:
                    # Instance method - need to create instance first
                    instance = getattr(module, class_name)()
                    method = getattr(instance, method_name)
                    result = method(**test_case.input_data)
            else:
                # Regular function
                result = target(**test_case.input_data)
                
            execution_time = time.time() - start_time
            
            # Teardown if needed
            if test_case.teardown_code:
                exec(test_case.teardown_code, module.__dict__)
                
            perf_metrics = {
                "execution_time": execution_time,
                "memory_usage": self._estimate_memory_usage()
            }
            
            return result, None, perf_metrics
            
        except Exception as e:
            error_message = f"{type(e).__name__}: {str(e)}"
            return None, error_message, {}
            
    def _get_target_callable(self, test_case: TestCase, module):
        """Get the target function or class to test"""
        target_name = test_case.target_function
        
        if not target_name:
            return None
            
        if '.' in target_name:
            # Class method
            class_name = target_name.split('.')[0]
            return getattr(module, class_name, None)
        else:
            # Regular function
            return getattr(module, target_name, None)
            
    def _compare_outputs(self, actual: Any, expected: Any, tolerance: float) -> bool:
        """Compare actual and expected outputs"""
        if expected is None:
            # No expected output defined (baseline run)
            return True
            
        if actual is None and expected is None:
            return True
            
        if actual is None or expected is None:
            return False
            
        try:
            # Numeric comparison with tolerance
            if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
                return abs(actual - expected) <= tolerance
                
            # String comparison
            if isinstance(actual, str) and isinstance(expected, str):
                return actual == expected
                
            # List comparison
            if isinstance(actual, list) and isinstance(expected, list):
                if len(actual) != len(expected):
                    return False
                return all(self._compare_outputs(a, e, tolerance) for a, e in zip(actual, expected))
                
            # Dict comparison
            if isinstance(actual, dict) and isinstance(expected, dict):
                if set(actual.keys()) != set(expected.keys()):
                    return False
                return all(self._compare_outputs(actual[k], expected[k], tolerance) for k in actual.keys())
                
            # Default equality
            return actual == expected
            
        except Exception:
            return False
            
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage (placeholder)"""
        # In a real implementation, this would use memory profiling
        return 0.0

class RegressionTester:
    """Main regression testing system"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.test_data_dir = output_dir / "regression_tests"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.test_generator = TestGenerator(output_dir)
        self.test_executor = TestExecutor(output_dir)
        
        # Test state
        self.test_suites = {}
        self.baseline_results = {}
        self.test_history = []
        
        # Load existing test data
        self._load_test_data()
        
    def create_regression_suite(self, name: str, target_files: List[str]) -> str:
        """Create a new regression test suite"""
        suite_id = f"suite_{int(time.time() * 1000000)}"
        
        logging.info(f"Creating regression suite '{name}' for {len(target_files)} files")
        
        # Generate test cases for all target files
        all_test_cases = []
        
        for file_path in target_files:
            if Path(file_path).exists():
                test_cases = self.test_generator.generate_tests_for_file(file_path)
                all_test_cases.extend(test_cases)
            else:
                logging.warning(f"Target file not found: {file_path}")
                
        # Create suite
        suite = RegressionSuite(
            suite_id=suite_id,
            name=name,
            target_files=target_files,
            test_cases=all_test_cases,
            baseline_results=[],
            created_at=time.time()
        )
        
        self.test_suites[suite_id] = suite
        
        logging.info(f"Created regression suite with {len(all_test_cases)} test cases")
        
        # Save test data
        self._save_test_data()
        
        return suite_id
        
    def establish_baseline(self, suite_id: str) -> bool:
        """Establish baseline results for a test suite"""
        if suite_id not in self.test_suites:
            logging.error(f"Test suite not found: {suite_id}")
            return False
            
        suite = self.test_suites[suite_id]
        
        logging.info(f"Establishing baseline for suite '{suite.name}'")
        
        baseline_results = []
        
        for test_case in suite.test_cases:
            # Find target file for this test
            target_file = self._find_target_file(test_case, suite.target_files)
            
            if target_file:
                result = self.test_executor.execute_test_case(test_case, target_file)
                
                # Update test case with captured output as expected
                if result.success and test_case.expected_output is None:
                    test_case.expected_output = result.actual_output
                    
                baseline_results.append(result)
            else:
                logging.warning(f"No target file found for test: {test_case.test_id}")
                
        suite.baseline_results = baseline_results
        self.baseline_results[suite_id] = baseline_results
        
        # Save updated data
        self._save_test_data()
        
        success_rate = sum(1 for r in baseline_results if r.success) / max(len(baseline_results), 1)
        logging.info(f"Baseline established with {success_rate:.1%} success rate")
        
        return True
        
    def run_regression_tests(self, suite_id: str) -> Dict[str, Any]:
        """Run regression tests and compare with baseline"""
        if suite_id not in self.test_suites:
            return {"error": "Test suite not found"}
            
        suite = self.test_suites[suite_id]
        baseline = self.baseline_results.get(suite_id, [])
        
        if not baseline:
            return {"error": "No baseline established for this suite"}
            
        logging.info(f"Running regression tests for suite '{suite.name}'")
        
        current_results = []
        
        for test_case in suite.test_cases:
            target_file = self._find_target_file(test_case, suite.target_files)
            
            if target_file:
                result = self.test_executor.execute_test_case(test_case, target_file)
                current_results.append(result)
                
        # Compare with baseline
        comparison = self._compare_with_baseline(current_results, baseline)
        
        # Update suite
        suite.last_run = time.time()
        
        # Record test run
        test_run = {
            "suite_id": suite_id,
            "timestamp": time.time(),
            "results": current_results,
            "comparison": comparison
        }
        
        self.test_history.append(test_run)
        
        # Save data
        self._save_test_data()
        
        return {
            "suite_name": suite.name,
            "total_tests": len(current_results),
            "passed": sum(1 for r in current_results if r.success),
            "failed": sum(1 for r in current_results if not r.success),
            "regressions": comparison["regressions"],
            "improvements": comparison["improvements"],
            "new_failures": comparison["new_failures"],
            "success_rate": sum(1 for r in current_results if r.success) / max(len(current_results), 1),
            "baseline_success_rate": sum(1 for r in baseline if r.success) / max(len(baseline), 1),
            "detailed_results": current_results
        }
        
    def validate_enhancement(self, enhancement_id: str, target_file: str) -> Dict[str, Any]:
        """Validate that an enhancement doesn't introduce regressions"""
        # Find relevant test suites
        relevant_suites = [
            suite for suite in self.test_suites.values()
            if target_file in suite.target_files
        ]
        
        if not relevant_suites:
            # Create a quick test suite for this file
            suite_id = self.create_regression_suite(f"Enhancement validation for {Path(target_file).name}", [target_file])
            self.establish_baseline(suite_id)
            relevant_suites = [self.test_suites[suite_id]]
            
        validation_results = {}
        
        for suite in relevant_suites:
            result = self.run_regression_tests(suite.suite_id)
            validation_results[suite.suite_id] = result
            
        # Aggregate results
        total_regressions = sum(r.get("regressions", 0) for r in validation_results.values())
        total_tests = sum(r.get("total_tests", 0) for r in validation_results.values())
        
        overall_success = total_regressions == 0
        
        return {
            "enhancement_id": enhancement_id,
            "target_file": target_file,
            "validation_success": overall_success,
            "total_regressions": total_regressions,
            "total_tests": total_tests,
            "suite_results": validation_results,
            "recommendation": "Safe to apply" if overall_success else "Regressions detected - review required"
        }
        
    def _find_target_file(self, test_case: TestCase, target_files: List[str]) -> Optional[str]:
        """Find the target file for a test case"""
        # For now, assume the first file that exists
        for file_path in target_files:
            if Path(file_path).exists():
                return file_path
        return None
        
    def _compare_with_baseline(self, current_results: List[TestResult], baseline_results: List[TestResult]) -> Dict[str, Any]:
        """Compare current results with baseline"""
        baseline_dict = {r.test_id: r for r in baseline_results}
        
        regressions = 0
        improvements = 0
        new_failures = 0
        
        for current in current_results:
            baseline = baseline_dict.get(current.test_id)
            
            if baseline:
                if baseline.success and not current.success:
                    regressions += 1
                elif not baseline.success and current.success:
                    improvements += 1
            else:
                if not current.success:
                    new_failures += 1
                    
        return {
            "regressions": regressions,
            "improvements": improvements,
            "new_failures": new_failures,
            "baseline_count": len(baseline_results),
            "current_count": len(current_results)
        }
        
    def _save_test_data(self):
        """Save test data to disk"""
        try:
            # Save test suites
            suites_file = self.test_data_dir / "test_suites.json"
            suites_data = {}
            
            for suite_id, suite in self.test_suites.items():
                suite_dict = asdict(suite)
                # Convert test cases to dicts
                suite_dict["test_cases"] = [asdict(tc) for tc in suite.test_cases]
                suite_dict["baseline_results"] = [asdict(br) for br in suite.baseline_results]
                suites_data[suite_id] = suite_dict
                
            with open(suites_file, 'w', encoding='utf-8') as f:
                json.dump(suites_data, f, indent=2)
                
            # Save baseline results
            baseline_file = self.test_data_dir / "baseline_results.pkl"
            with open(baseline_file, 'wb') as f:
                pickle.dump(self.baseline_results, f)
                
            # Save test history
            history_file = self.test_data_dir / "test_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                # Convert TestResult objects to dicts for JSON serialization
                serializable_history = []
                for run in self.test_history[-100:]:  # Keep last 100 runs
                    serializable_run = run.copy()
                    serializable_run["results"] = [asdict(r) for r in run["results"]]
                    serializable_history.append(serializable_run)
                    
                json.dump(serializable_history, f, indent=2)
                
            logging.debug("Test data saved successfully")
            
        except Exception as e:
            logging.error(f"Failed to save test data: {e}")
            
    def _load_test_data(self):
        """Load existing test data from disk"""
        try:
            # Load test suites
            suites_file = self.test_data_dir / "test_suites.json"
            if suites_file.exists():
                with open(suites_file, 'r', encoding='utf-8') as f:
                    suites_data = json.load(f)
                    
                for suite_id, suite_dict in suites_data.items():
                    # Convert back to objects
                    test_cases = [TestCase(**tc) for tc in suite_dict["test_cases"]]
                    baseline_results = [TestResult(**br) for br in suite_dict["baseline_results"]]
                    
                    suite_dict["test_cases"] = test_cases
                    suite_dict["baseline_results"] = baseline_results
                    
                    suite = RegressionSuite(**suite_dict)
                    self.test_suites[suite_id] = suite
                    
            # Load baseline results
            baseline_file = self.test_data_dir / "baseline_results.pkl"
            if baseline_file.exists():
                with open(baseline_file, 'rb') as f:
                    self.baseline_results = pickle.load(f)
                    
            # Load test history
            history_file = self.test_data_dir / "test_history.json"
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    
                # Convert back to TestResult objects
                for run in history_data:
                    run["results"] = [TestResult(**r) for r in run["results"]]
                    
                self.test_history = history_data
                
            logging.info(f"Loaded {len(self.test_suites)} test suites and {len(self.test_history)} test runs")
            
        except Exception as e:
            logging.error(f"Failed to load test data: {e}")
            
    def get_testing_summary(self) -> Dict[str, Any]:
        """Get summary of testing system status"""
        total_test_cases = sum(len(suite.test_cases) for suite in self.test_suites.values())
        
        recent_runs = [run for run in self.test_history if time.time() - run["timestamp"] < 86400]  # Last 24 hours
        
        return {
            "total_suites": len(self.test_suites),
            "total_test_cases": total_test_cases,
            "recent_runs": len(recent_runs),
            "baselines_established": len(self.baseline_results),
            "last_run": max([suite.last_run for suite in self.test_suites.values() if suite.last_run], default=None)
        }