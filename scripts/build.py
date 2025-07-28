#!/usr/bin/env python3
"""
SuperMini Simplified Build System
One-command build, test, package, and distribute for macOS
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
import json
import stat
from datetime import datetime

class SuperMiniBuild:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_name = "SuperMini"
        self.app_version = self._get_version()
        self.bundle_id = "com.supermini.ai-assistant"
        
        # Build directories
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
        # Core files to bundle
        self.core_files = [
            "supermini.py",  # Main entry point
            "aimm.py",       # Legacy main file
            "universal_launcher.py",
            "activity_monitor.py",
            "autonomous_agent.py",
            "autonomous_enhancement.py",
            "recursive_engine.py",
            "requirements.txt"
        ]
        
        # Directories to bundle
        self.core_dirs = [
            "assets",
            "prompts",
            "docs"
        ]
        
    def _get_version(self):
        """Extract version from main application file"""
        try:
            # Try to read version from supermini.py first
            version_file = self.project_root / "supermini.py"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'APP_VERSION' in line and '=' in line:
                            return line.split('=')[1].strip().strip('"\'')
            
            # Fallback to VERSION file
            version_file = self.project_root / "VERSION"
            if version_file.exists():
                return version_file.read_text().strip()
                
            # Final fallback
            return "2.1.0"
        except:
            return "2.1.0"
    
    def print_status(self, message, emoji="ℹ️"):
        """Print colored status message"""
        print(f"{emoji} {message}")
    
    def print_success(self, message):
        """Print success message"""
        self.print_status(message, "✅")
    
    def print_error(self, message):
        """Print error message"""
        self.print_status(message, "❌")
    
    def print_warning(self, message):
        """Print warning message"""
        self.print_status(message, "⚠️")
    
    def clean_build(self):
        """Clean previous build artifacts"""
        self.print_status("Cleaning previous builds...")
        
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                self.print_success(f"Removed {directory.name}/")
        
        # Create fresh directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def validate_environment(self):
        """Validate build environment"""
        self.print_status("Validating build environment...")
        
        # Check Python version
        if sys.version_info < (3, 9):
            self.print_error("Python 3.9+ required")
            return False
        
        # Check required tools
        required_tools = ['hdiutil', 'iconutil']
        for tool in required_tools:
            if not shutil.which(tool):
                self.print_error(f"Required tool not found: {tool}")
                return False
        
        # Check core files exist
        missing_files = []
        for file in self.core_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.print_warning(f"Optional files missing: {', '.join(missing_files)}")
        
        # Check icon
        icon_path = self.project_root / "assets" / "SuperMini.icns"
        if not icon_path.exists():
            self.print_warning("App icon not found, using default")
        
        self.print_success("Environment validated")
        return True
    
    def setup_venv(self):
        """Create and configure virtual environment"""
        self.print_status("Setting up virtual environment...")
        
        venv_path = self.build_dir / "venv"
        
        # Create venv
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True, capture_output=True)
        
        # Activate and install requirements
        pip_path = venv_path / "bin" / "pip"
        requirements_path = self.project_root / "requirements.txt"
        
        if requirements_path.exists():
            subprocess.run([
                str(pip_path), "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            subprocess.run([
                str(pip_path), "install", "-r", str(requirements_path)
            ], check=True, capture_output=True)
        
        self.print_success("Virtual environment configured")
        return venv_path
    
    def create_app_bundle(self, venv_path):
        """Create macOS app bundle"""
        self.print_status("Creating macOS app bundle...")
        
        # App bundle structure
        app_bundle = self.build_dir / f"{self.app_name}.app"
        contents_dir = app_bundle / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # Create directories
        macos_dir.mkdir(parents=True)
        resources_dir.mkdir(parents=True)
        
        # Create Info.plist
        self._create_info_plist(contents_dir)
        
        # Create launcher script
        self._create_launcher(macos_dir)
        
        # Copy application files
        self._copy_app_files(resources_dir)
        
        # Copy virtual environment
        if venv_path.exists():
            shutil.copytree(venv_path, resources_dir / "venv")
        
        # Copy icon
        self._copy_icon(resources_dir)
        
        self.print_success(f"App bundle created: {app_bundle}")
        return app_bundle
    
    def _create_info_plist(self, contents_dir):
        """Create Info.plist file"""
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{self.app_name} - AI Assistant</string>
    <key>CFBundleIdentifier</key>
    <string>{self.bundle_id}</string>
    <key>CFBundleVersion</key>
    <string>{self.app_version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.app_version}</string>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIconFile</key>
    <string>SuperMini.icns</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>NSHumanReadableCopyright</key>
    <string>© 2024 SuperMini. All rights reserved.</string>
</dict>
</plist>'''
        
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(plist_content)
    
    def _create_launcher(self, macos_dir):
        """Create launcher script"""
        launcher_content = f'''#!/bin/bash
# SuperMini Launcher
set -e

# Get bundle paths
BUNDLE_PATH="$(cd "$(dirname "$0")/.." && pwd)"
RESOURCES_PATH="$BUNDLE_PATH/Resources"

# Change to resources directory
cd "$RESOURCES_PATH"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create output directory
mkdir -p "$HOME/SuperMini_Output/{{data,logs,data/memory,data/collaboration,autonomous}}"

# Start Ollama if available and not running
if command -v ollama &> /dev/null && ! pgrep -f "ollama serve" > /dev/null; then
    echo "🤖 Starting Ollama service..."
    ollama serve &
    sleep 2
fi

# Launch application
echo "🚀 Launching {self.app_name}..."
if [ -f "supermini.py" ]; then
    python3 supermini.py
elif [ -f "universal_launcher.py" ]; then
    python3 universal_launcher.py
else
    python3 aimm.py
fi
'''
        
        launcher_file = macos_dir / self.app_name
        with open(launcher_file, 'w') as f:
            f.write(launcher_content)
        
        # Make executable
        launcher_file.chmod(0o755)
    
    def _copy_app_files(self, resources_dir):
        """Copy application files to bundle"""
        # Copy core Python files
        for file in self.core_files:
            src_file = self.project_root / file
            if src_file.exists():
                shutil.copy2(src_file, resources_dir / file)
        
        # Copy directories
        for directory in self.core_dirs:
            src_dir = self.project_root / directory
            if src_dir.exists():
                shutil.copytree(src_dir, resources_dir / directory, dirs_exist_ok=True)
    
    def _copy_icon(self, resources_dir):
        """Copy app icon"""
        # Try multiple icon locations
        icon_sources = [
            self.project_root / "assets" / "SuperMini.icns",
            self.project_root / "assets" / "icons" / "icns" / "SuperMini_neural_zen.icns",
            self.project_root / "SuperMini.icns"
        ]
        
        for icon_source in icon_sources:
            if icon_source.exists():
                shutil.copy2(icon_source, resources_dir / "SuperMini.icns")
                self.print_success(f"Icon copied from {icon_source}")
                return
        
        self.print_warning("No app icon found")
    
    def create_dmg(self, app_bundle):
        """Create DMG installer"""
        self.print_status("Creating DMG installer...")
        
        dmg_name = f"{self.app_name}-{self.app_version}"
        dmg_path = self.dist_dir / f"{dmg_name}.dmg"
        
        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            dmg_source = temp_path / "dmg_source"
            dmg_source.mkdir()
            
            # Copy app bundle
            shutil.copytree(app_bundle, dmg_source / f"{self.app_name}.app")
            
            # Create Applications symlink
            (dmg_source / "Applications").symlink_to("/Applications")
            
            # Create README
            self._create_readme(dmg_source)
            
            # Create DMG
            cmd = [
                'hdiutil', 'create',
                '-srcfolder', str(dmg_source),
                '-volname', f"{self.app_name} {self.app_version}",
                '-format', 'UDZO',
                '-imagekey', 'zlib-level=9',
                str(dmg_path)
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
        
        self.print_success(f"DMG created: {dmg_path}")
        return dmg_path
    
    def _create_readme(self, dmg_source):
        """Create README for DMG"""
        readme_content = f"""# {self.app_name} v{self.app_version}

## Installation
1. Drag {self.app_name}.app to Applications folder
2. Launch from Applications or Launchpad

## Requirements
- macOS 10.15 or later
- Ollama (install from https://ollama.ai/)

## Optional
- Claude API key for enhanced AI features

## Support
Generated files saved to: ~/SuperMini_Output/

Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(dmg_source / "README.txt", 'w') as f:
            f.write(readme_content)
    
    def run_tests(self):
        """Run available tests"""
        self.print_status("Running tests...")
        
        test_files = list(self.project_root.glob("test_*.py"))
        if test_files:
            try:
                subprocess.run([
                    sys.executable, "-m", "pytest", "-v"
                ], check=True, capture_output=True, cwd=self.project_root)
                self.print_success("All tests passed")
            except subprocess.CalledProcessError:
                self.print_warning("Some tests failed, continuing build")
        else:
            self.print_warning("No tests found")
    
    def create_checksum(self, dmg_path):
        """Create SHA256 checksum"""
        self.print_status("Creating checksum...")
        
        result = subprocess.run([
            'shasum', '-a', '256', dmg_path.name
        ], cwd=dmg_path.parent, capture_output=True, text=True, check=True)
        
        checksum_file = dmg_path.with_suffix('.dmg.sha256')
        with open(checksum_file, 'w') as f:
            f.write(result.stdout)
        
        self.print_success(f"Checksum: {checksum_file}")
    
    def build(self):
        """Main build process"""
        start_time = datetime.now()
        
        print(f"\n🚀 SuperMini Build System v{self.app_version}")
        print("=" * 60)
        
        try:
            # Build steps
            if not self.validate_environment():
                return False
            
            self.clean_build()
            self.run_tests()
            venv_path = self.setup_venv()
            app_bundle = self.create_app_bundle(venv_path)
            dmg_path = self.create_dmg(app_bundle)
            self.create_checksum(dmg_path)
            
            # Build summary
            build_time = datetime.now() - start_time
            dmg_size = dmg_path.stat().st_size / (1024 * 1024)
            
            print("\n🎉 Build Complete!")
            print("=" * 60)
            print(f"📱 App Bundle: {app_bundle}")
            print(f"💿 DMG Installer: {dmg_path}")
            print(f"📊 Size: {dmg_size:.1f} MB")
            print(f"⏱️  Build Time: {build_time.total_seconds():.1f}s")
            print("\n📋 Next Steps:")
            print("1. Test the DMG installer")
            print("2. Distribute to users")
            
            # Open in Finder
            subprocess.run(['open', '-R', str(dmg_path)])
            
            return True
            
        except Exception as e:
            self.print_error(f"Build failed: {e}")
            return False

def main():
    """Entry point"""
    builder = SuperMiniBuild()
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()