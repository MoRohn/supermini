#!/usr/bin/env python3
"""
Universal SuperMini Launcher
Cross-platform startup script with robust error handling and dependency management
"""

import os
import sys
import platform
import subprocess
import shutil
import time
from pathlib import Path
import json

class UniversalLauncher:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.system = platform.system().lower()
        self.python_exec = self.find_python()
        self.app_name = "SuperMini"
        self.main_script = self.script_dir / "aimm.py"
        
        # Output directories
        self.output_dir = Path.home() / "SuperMini_Output"
        self.log_file = self.output_dir / "logs" / "launcher.log"
        
        # Virtual environment
        self.venv_dir = self.script_dir / "venv"
        
        # Platform-specific configuration
        self.platform_config = {
            'darwin': {
                'name': 'macOS',
                'icon': '🍎',
                'ollama_install_cmd': 'brew install ollama',
                'python_install_help': 'Install from python.org or use Homebrew: brew install python'
            },
            'windows': {
                'name': 'Windows',
                'icon': '🪟',
                'ollama_install_cmd': 'Download from https://ollama.ai/download/windows',
                'python_install_help': 'Install from python.org or Microsoft Store'
            },
            'linux': {
                'name': 'Linux',
                'icon': '🐧',
                'ollama_install_cmd': 'curl -fsSL https://ollama.ai/install.sh | sh',
                'python_install_help': 'Use package manager: sudo apt install python3-pip (Ubuntu/Debian) or sudo dnf install python3-pip (Fedora)'
            }
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging directory and file"""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.touch(exist_ok=True)
        except Exception:
            pass  # Logging is not critical for startup
    
    def log(self, message, level="INFO"):
        """Log message to file and console"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(f"[{level}] {message}")
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")
        except Exception:
            pass  # Don't fail if logging fails
    
    def print_header(self):
        """Print application header"""
        config = self.platform_config.get(self.system, self.platform_config['linux'])
        
        print("=" * 60)
        print(f"{config['icon']} SuperMini - Autonomous Mac Mini AI Agent")
        print(f"Platform: {config['name']} ({platform.machine()})")
        print(f"Python: {self.python_exec}")
        print(f"Location: {self.script_dir}")
        print("=" * 60)
    
    def find_python(self):
        """Find appropriate Python executable"""
        python_candidates = ['python3', 'python']
        
        for candidate in python_candidates:
            if shutil.which(candidate):
                try:
                    # Check version
                    result = subprocess.run([candidate, '--version'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return candidate
                except Exception:
                    continue
        
        return None
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        if not self.python_exec:
            self.log("Python not found!", "ERROR")
            config = self.platform_config.get(self.system, self.platform_config['linux'])
            print(f"❌ Python 3.9+ is required but not found")
            print(f"   {config['python_install_help']}")
            return False
        
        try:
            result = subprocess.run([self.python_exec, '-c', 
                                   'import sys; print(".".join(map(str, sys.version_info[:2])))'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log(f"Python version: {version}")
                
                # Check if version is 3.9+
                major, minor = map(int, version.split('.'))
                if major >= 3 and minor >= 9:
                    print(f"✅ Python {version} (compatible)")
                    return True
                else:
                    print(f"❌ Python {version} (requires 3.9+)")
                    return False
            else:
                self.log("Failed to check Python version", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Python version check failed: {e}", "ERROR")
            return False
    
    def setup_virtual_environment(self):
        """Setup Python virtual environment if needed"""
        if self.venv_dir.exists():
            self.log("Virtual environment already exists")
            return True
        
        print("🔧 Creating Python virtual environment...")
        self.log("Creating virtual environment")
        
        try:
            result = subprocess.run([self.python_exec, '-m', 'venv', str(self.venv_dir)],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Virtual environment created")
                self.log("Virtual environment created successfully")
                return True
            else:
                self.log(f"Virtual environment creation failed: {result.stderr}", "ERROR")
                print(f"❌ Failed to create virtual environment: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Virtual environment setup error: {e}", "ERROR")
            print(f"❌ Virtual environment setup error: {e}")
            return False
    
    def get_venv_python(self):
        """Get virtual environment Python executable"""
        if self.system == 'windows':
            venv_python = self.venv_dir / "Scripts" / "python.exe"
        else:
            venv_python = self.venv_dir / "bin" / "python"
        
        return str(venv_python) if venv_python.exists() else self.python_exec
    
    def install_dependencies(self):
        """Install Python dependencies"""
        requirements_file = self.script_dir / "requirements.txt"
        
        if not requirements_file.exists():
            self.log("requirements.txt not found", "WARNING")
            print("⚠️  requirements.txt not found, skipping dependency installation")
            return True
        
        print("📦 Installing Python dependencies...")
        self.log("Installing dependencies")
        
        python_exec = self.get_venv_python()
        
        try:
            # Upgrade pip first
            subprocess.run([python_exec, '-m', 'pip', 'install', '--upgrade', 'pip'],
                          capture_output=True, text=True, check=True)
            
            # Install requirements
            result = subprocess.run([python_exec, '-m', 'pip', 'install', '-r', str(requirements_file)],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies installed")
                self.log("Dependencies installed successfully")
                return True
            else:
                self.log(f"Dependency installation failed: {result.stderr}", "ERROR")
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Dependency installation error: {e}", "ERROR")
            print(f"❌ Dependency installation error: {e}")
            return False
    
    def check_ollama(self):
        """Check Ollama installation and service"""
        print("🧠 Checking Ollama AI service...")
        
        # Check if Ollama is installed
        if not shutil.which('ollama'):
            config = self.platform_config.get(self.system, self.platform_config['linux'])
            print("❌ Ollama not found")
            print(f"   Install from: https://ollama.ai/")
            print(f"   Or use: {config['ollama_install_cmd']}")
            return False
        
        print("✅ Ollama installed")
        
        # Check if service is running
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Ollama service running")
                self.log("Ollama service is running")
                
                # Check for models
                if "qwen2.5-coder" in result.stdout or "llama" in result.stdout:
                    print("✅ AI models available")
                    return True
                else:
                    print("⚠️  No AI models found")
                    print("   Run: ollama pull qwen2.5-coder:7b")
                    return True  # Service is running, models can be installed later
            else:
                print("⚠️  Ollama service not responding")
                return self.start_ollama_service()
                
        except subprocess.TimeoutExpired:
            print("⚠️  Ollama service timeout")
            return self.start_ollama_service()
        except Exception as e:
            self.log(f"Ollama check error: {e}", "ERROR")
            print(f"⚠️  Ollama check failed: {e}")
            return False
    
    def start_ollama_service(self):
        """Start Ollama service"""
        print("🔄 Starting Ollama service...")
        self.log("Starting Ollama service")
        
        try:
            if self.system == 'windows':
                # On Windows, Ollama might be a service
                subprocess.Popen(['ollama', 'serve'], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # On Unix-like systems
                subprocess.Popen(['ollama', 'serve'])
            
            # Wait for service to start
            time.sleep(3)
            
            # Test if service is now running
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ Ollama service started")
                self.log("Ollama service started successfully")
                return True
            else:
                print("❌ Failed to start Ollama service")
                self.log("Failed to start Ollama service", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Ollama service start error: {e}", "ERROR")
            print(f"❌ Failed to start Ollama service: {e}")
            return False
    
    def setup_output_directories(self):
        """Setup output directories"""
        directories = [
            self.output_dir / "data",
            self.output_dir / "logs", 
            self.output_dir / "data" / "memory",
            self.output_dir / "data" / "collaboration",
            self.output_dir / "autonomous"
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
            
            print(f"✅ Output directories ready: {self.output_dir}")
            self.log(f"Output directories created: {self.output_dir}")
            return True
            
        except Exception as e:
            self.log(f"Directory setup error: {e}", "ERROR")
            print(f"❌ Failed to setup directories: {e}")
            return False
    
    def check_main_script(self):
        """Check if main script exists"""
        if self.main_script.exists():
            print(f"✅ Main script found: {self.main_script.name}")
            return True
        else:
            print(f"❌ Main script not found: {self.main_script}")
            self.log(f"Main script not found: {self.main_script}", "ERROR")
            return False
    
    def launch_application(self):
        """Launch the main application"""
        print("🚀 Launching SuperMini...")
        self.log("Launching main application")
        
        python_exec = self.get_venv_python()
        
        try:
            # Launch with proper error handling
            result = subprocess.run([python_exec, str(self.main_script)],
                                  cwd=str(self.script_dir))
            
            if result.returncode == 0:
                self.log("Application exited normally")
                print("👋 SuperMini closed normally")
                return True
            else:
                self.log(f"Application exited with code: {result.returncode}", "WARNING")
                print(f"⚠️  SuperMini exited with code: {result.returncode}")
                return False
                
        except KeyboardInterrupt:
            self.log("Application interrupted by user")
            print("\\n👋 SuperMini interrupted by user")
            return True
        except Exception as e:
            self.log(f"Application launch error: {e}", "ERROR")
            print(f"❌ Failed to launch SuperMini: {e}")
            return False
    
    def run_diagnostic(self):
        """Run system diagnostic"""
        print("\\n🔍 System Diagnostic:")
        print("-" * 40)
        
        diagnostics = [
            ("Python Version", self.check_python_version),
            ("Virtual Environment", lambda: self.venv_dir.exists()),
            ("Main Script", self.check_main_script),
            ("Output Directory", lambda: self.output_dir.exists()),
            ("Ollama Available", lambda: shutil.which('ollama') is not None)
        ]
        
        for name, check in diagnostics:
            try:
                result = check()
                status = "✅" if result else "❌"
                print(f"{status} {name}")
            except Exception:
                print(f"❌ {name} (error)")
    
    def main_launcher(self):
        """Main launcher workflow"""
        self.print_header()
        
        # Check basic requirements
        if not self.check_python_version():
            input("Press Enter to exit...")
            return False
        
        if not self.check_main_script():
            input("Press Enter to exit...")
            return False
        
        # Setup environment
        if not self.setup_virtual_environment():
            print("⚠️  Continuing without virtual environment...")
        
        if not self.install_dependencies():
            print("⚠️  Some dependencies may be missing...")
        
        # Setup directories
        self.setup_output_directories()
        
        # Check Ollama (optional)
        self.check_ollama()
        
        # Launch application
        print("\\n" + "=" * 60)
        return self.launch_application()

def main():
    """Main entry point"""
    launcher = UniversalLauncher()
    
    try:
        success = launcher.main_launcher()
        
        if not success:
            print("\\n" + "=" * 60)
            print("❌ Launch failed. Running diagnostic...")
            launcher.run_diagnostic()
            print("\\n📋 Check the log file for details:")
            print(f"   {launcher.log_file}")
            input("\\nPress Enter to exit...")
            
    except KeyboardInterrupt:
        print("\\n👋 Launcher interrupted")
    except Exception as e:
        print(f"\\n❌ Launcher error: {e}")
        launcher.log(f"Launcher error: {e}", "ERROR")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()