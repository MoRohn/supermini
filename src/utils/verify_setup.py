#!/usr/bin/env python3
"""
SuperMini Setup Verification Script
Verifies that the open-source project setup is complete and functional
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple

def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True,
            cwd=Path.cwd()
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists"""
    path = Path(file_path)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_git_setup() -> bool:
    """Verify Git repository setup"""
    print("\n🔧 Git Repository Setup")
    print("=" * 50)
    
    all_good = True
    
    # Check if it's a git repository
    if not Path('.git').exists():
        print("❌ Not a Git repository")
        return False
    
    print("✅ Git repository initialized")
    
    # Check git status
    code, stdout, stderr = run_command(['git', 'status', '--porcelain'])
    if code == 0:
        if stdout.strip():
            print(f"⚠️  Uncommitted changes: {len(stdout.strip().split())} files")
        else:
            print("✅ Working directory clean")
    else:
        print("❌ Error checking git status")
        all_good = False
    
    # Check for initial commit
    code, stdout, stderr = run_command(['git', 'log', '--oneline', '-1'])
    if code == 0:
        print("✅ Initial commit exists")
        print(f"   Latest: {stdout.strip()}")
    else:
        print("❌ No commits found")
        all_good = False
    
    # Check remote
    code, stdout, stderr = run_command(['git', 'remote', '-v'])
    if code == 0 and stdout.strip():
        print("✅ Git remote configured")
        for line in stdout.strip().split('\n'):
            print(f"   {line}")
    else:
        print("⚠️  No Git remote configured (expected for local setup)")
    
    return all_good

def check_required_files() -> bool:
    """Check for required project files"""
    print("\n📄 Required Files")
    print("=" * 50)
    
    required_files = [
        ("README.md", "Project README"),
        ("LICENSE", "MIT License"),
        ("CONTRIBUTING.md", "Contribution guidelines"),
        ("CHANGELOG.md", "Version changelog"),
        ("requirements.txt", "Python dependencies"),
        ("VERSION", "Version file"),
        (".gitignore", "Git ignore file"),
        ("supermini.py", "Main application"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_github_actions() -> bool:
    """Check GitHub Actions setup"""
    print("\n🚀 GitHub Actions")
    print("=" * 50)
    
    workflows = [
        (".github/workflows/ci.yml", "CI/CD Pipeline"),
        (".github/workflows/release.yml", "Release Automation"),
    ]
    
    templates = [
        (".github/ISSUE_TEMPLATE/bug_report.yml", "Bug report template"),
        (".github/ISSUE_TEMPLATE/feature_request.yml", "Feature request template"),
        (".github/pull_request_template.md", "Pull request template"),
    ]
    
    all_exist = True
    for file_path, description in workflows + templates:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_project_structure() -> bool:
    """Check project directory structure"""
    print("\n📁 Project Structure")
    print("=" * 50)
    
    directories = [
        ("assets/", "Assets and icons"),
        ("docs/", "Documentation"),
        ("scripts/", "Build and deployment scripts"),
        ("tests/", "Test files"),
        ("prompts/", "AI prompt templates"),
        (".github/", "GitHub configuration"),
    ]
    
    all_exist = True
    for dir_path, description in directories:
        if not check_file_exists(dir_path, description):
            all_exist = False
    
    return all_exist

def check_python_dependencies() -> bool:
    """Check Python dependencies"""
    print("\n🐍 Python Dependencies")
    print("=" * 50)
    
    # Check if requirements.txt exists and is readable
    if not Path('requirements.txt').exists():
        print("❌ requirements.txt not found")
        return False
    
    # Read requirements
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"✅ Found {len(requirements)} dependencies:")
        for req in requirements:
            print(f"   - {req}")
        
        # Check critical dependencies
        critical_deps = ['PyQt6', 'anthropic', 'requests', 'pandas', 'numpy', 'semantic-version']
        missing = []
        
        for dep in critical_deps:
            found = any(dep.lower() in req.lower() for req in requirements)
            if found:
                print(f"✅ Critical dependency found: {dep}")
            else:
                print(f"❌ Missing critical dependency: {dep}")
                missing.append(dep)
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_release_automation() -> bool:
    """Check release automation setup"""
    print("\n🤖 Release Automation")
    print("=" * 50)
    
    automation_files = [
        ("release_automation.py", "Release automation module"),
        ("release_integration.py", "Release integration module"),
        ("VERSION", "Version tracking file"),
    ]
    
    all_exist = True
    for file_path, description in automation_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    # Check VERSION file content
    if Path('VERSION').exists():
        try:
            with open('VERSION', 'r') as f:
                version = f.read().strip()
            print(f"✅ Current version: {version}")
        except Exception as e:
            print(f"❌ Error reading VERSION file: {e}")
            all_exist = False
    
    return all_exist

def check_security_setup() -> bool:
    """Check security configuration"""
    print("\n🔒 Security Setup")
    print("=" * 50)
    
    # Check .gitignore content
    if Path('.gitignore').exists():
        try:
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
            
            security_patterns = [
                '*.key',
                '*.secret',
                '.env',
                'api_keys.txt',
                '.claude_api_key',
                '.anthropic_key'
            ]
            
            all_patterns_found = True
            for pattern in security_patterns:
                if pattern in gitignore_content:
                    print(f"✅ Security pattern found: {pattern}")
                else:
                    print(f"❌ Missing security pattern: {pattern}")
                    all_patterns_found = False
            
            return all_patterns_found
            
        except Exception as e:
            print(f"❌ Error reading .gitignore: {e}")
            return False
    else:
        print("❌ .gitignore file not found")
        return False

def generate_report() -> Dict:
    """Generate comprehensive setup report"""
    print("🔍 SuperMini Open-Source Setup Verification")
    print("=" * 60)
    
    checks = {
        "Git Repository": check_git_setup(),
        "Required Files": check_required_files(),
        "GitHub Actions": check_github_actions(),
        "Project Structure": check_project_structure(),
        "Python Dependencies": check_python_dependencies(),
        "Release Automation": check_release_automation(),
        "Security Setup": check_security_setup(),
    }
    
    print("\n📊 Summary Report")
    print("=" * 50)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Congratulations! SuperMini is ready for open-source distribution!")
        print("\nNext steps:")
        print("1. Follow GITHUB_SETUP_INSTRUCTIONS.md to create GitHub repository")
        print("2. Push code to GitHub: git push origin main")
        print("3. Create initial release: git tag v2.0.0 && git push origin v2.0.0")
        print("4. Test the 'Enhance Yourself' mode to verify release automation")
    else:
        print("⚠️  Some checks failed. Please review and fix the issues above.")
        print("Run this script again after making corrections.")
    
    return checks

def main():
    """Main verification function"""
    try:
        # Change to script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Run verification
        report = generate_report()
        
        # Exit with appropriate code
        if all(report.values()):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()