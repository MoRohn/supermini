#!/usr/bin/env python3
"""
Create macOS App Bundle for SuperMini
Professional macOS .app bundle creation with proper structure and icons
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import json
import stat

class MacOSAppCreator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.app_name = "SuperMini"
        self.app_version = "2.1.0"
        self.bundle_id = "com.supermini.desktop"
        
        # Paths
        self.build_dir = self.base_dir / "build"
        self.app_bundle = self.build_dir / f"{self.app_name}.app"
        self.contents_dir = self.app_bundle / "Contents"
        self.macos_dir = self.contents_dir / "MacOS"
        self.resources_dir = self.contents_dir / "Resources"
        
        # Source files
        self.main_script = self.base_dir / "aimm.py"
        self.icon_file = self.base_dir / "assets" / "SuperMini.icns"
        self.requirements_file = self.base_dir / "requirements.txt"
        
        # Files to include in bundle
        self.python_files = [
            "aimm.py",
            "universal_launcher.py",
            "activity_monitor.py",
            "autonomous_agent.py",
            "autonomous_enhancement.py",
            "autonomous_orchestrator.py",
            "aimm_autonomous_integration.py",
            "dynamic_planning_components.py",
            "enhanced_memory.py",
            "enhanced_safety_framework.py",
            "enhanced_task_execution.py",
            "recursive_engine.py",
            "regression_tester.py",
            "safety_framework.py",
            "self_learning_module.py"
        ]
        
        self.data_dirs = [
            "prompts",
            "docs",
            "assets"
        ]
    
    def create_app_structure(self):
        """Create the basic app bundle structure"""
        print("🏗️  Creating app bundle structure...")
        
        # Clean and create directories
        if self.app_bundle.exists():
            shutil.rmtree(self.app_bundle)
        
        self.app_bundle.mkdir(parents=True)
        self.contents_dir.mkdir()
        self.macos_dir.mkdir()
        self.resources_dir.mkdir()
        
        print(f"   ✅ Created app bundle: {self.app_bundle}")
    
    def create_info_plist(self):
        """Create the Info.plist file"""
        print("📄 Creating Info.plist...")
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{self.app_name} - Autonomous Mac Mini AI Agent</string>
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
    <key>CFBundleSignature</key>
    <string>SMNI</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.productivity</string>
    <key>NSHumanReadableCopyright</key>
    <string>© 2024 SuperMini. All rights reserved.</string>
    <key>NSAppleScriptEnabled</key>
    <true/>
    <key>NSDocumentsFolderUsageDescription</key>
    <string>SuperMini needs access to your documents to process and analyze files.</string>
    <key>NSDesktopFolderUsageDescription</key>
    <string>SuperMini may save generated files to your desktop.</string>
    <key>NSDownloadsFolderUsageDescription</key>
    <string>SuperMini may access downloads for file processing.</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Text Document</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>txt</string>
                <string>md</string>
                <string>py</string>
                <string>js</string>
                <string>json</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
        </dict>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Image</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>png</string>
                <string>jpg</string>
                <string>jpeg</string>
                <string>gif</string>
                <string>webp</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
        </dict>
        <dict>
            <key>CFBundleTypeName</key>
            <string>PDF Document</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>pdf</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
        </dict>
    </array>
</dict>
</plist>'''
        
        plist_file = self.contents_dir / "Info.plist"
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        print(f"   ✅ Created Info.plist")
    
    def create_launcher_script(self):
        """Create the main launcher executable"""
        print("🚀 Creating launcher script...")
        
        launcher_content = f'''#!/bin/bash
# SuperMini macOS App Bundle Launcher

# Get the path to the app bundle
BUNDLE_PATH="$(dirname "$0")/.."
RESOURCES_PATH="$BUNDLE_PATH/Resources"

# Change to resources directory
cd "$RESOURCES_PATH"

# Use the universal launcher if available
if [ -f "universal_launcher.py" ]; then
    python3 universal_launcher.py
else
    # Fallback to direct launch
    echo "🚀 Launching SuperMini..."
    
    # Check for virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Create output directory
    mkdir -p "$HOME/SuperMini_Output/{{data,logs,data/memory,data/collaboration,autonomous}}"
    
    # Start Ollama if available
    if command -v ollama &> /dev/null && ! pgrep -f "ollama serve" > /dev/null; then
        echo "Starting Ollama service..."
        ollama serve &
        sleep 2
    fi
    
    # Launch the application
    python3 aimm.py
fi
'''
        
        launcher_file = self.macos_dir / self.app_name
        with open(launcher_file, 'w') as f:
            f.write(launcher_content)
        
        # Make executable
        launcher_file.chmod(launcher_file.stat().st_mode | stat.S_IEXEC)
        
        print(f"   ✅ Created launcher: {launcher_file}")
    
    def copy_application_files(self):
        """Copy Python files and resources to the bundle"""
        print("📂 Copying application files...")
        
        # Copy Python files
        for py_file in self.python_files:
            src_file = self.base_dir / py_file
            if src_file.exists():
                dst_file = self.resources_dir / py_file
                shutil.copy2(src_file, dst_file)
                print(f"   ✅ Copied {py_file}")
            else:
                print(f"   ⚠️  Skipped missing file: {py_file}")
        
        # Copy requirements.txt
        if self.requirements_file.exists():
            shutil.copy2(self.requirements_file, self.resources_dir / "requirements.txt")
            print(f"   ✅ Copied requirements.txt")
        
        # Copy data directories
        for data_dir in self.data_dirs:
            src_dir = self.base_dir / data_dir
            if src_dir.exists():
                dst_dir = self.resources_dir / data_dir
                shutil.copytree(src_dir, dst_dir)
                print(f"   ✅ Copied {data_dir}/ directory")
            else:
                print(f"   ⚠️  Skipped missing directory: {data_dir}")
        
        # Copy icon
        if self.icon_file.exists():
            shutil.copy2(self.icon_file, self.resources_dir / "SuperMini.icns")
            print(f"   ✅ Copied app icon")
        else:
            print(f"   ⚠️  App icon not found: {self.icon_file}")
    
    def create_setup_script(self):
        """Create a setup script for first-time run"""
        print("🔧 Creating setup script...")
        
        setup_content = '''#!/bin/bash
# SuperMini First-Time Setup Script

echo "🔧 Setting up SuperMini for first use..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed"
    else
        echo "❌ Some dependencies failed to install"
        echo "   SuperMini may have limited functionality"
    fi
else
    echo "⚠️  requirements.txt not found"
fi

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "🤖 Ollama AI service not found"
    echo "   Install from: https://ollama.ai/"
    echo "   Or use Homebrew: brew install ollama"
    echo "   SuperMini will work with limited AI functionality"
else
    echo "✅ Ollama found"
    
    # Check for models
    if ! ollama list 2>/dev/null | grep -q "qwen2.5-coder\\|llama"; then
        echo "🧠 No AI models found"
        read -p "Download AI models now? (y/n): " download_models
        if [[ "$download_models" == "y" || "$download_models" == "Y" ]]; then
            echo "📥 Downloading AI models (this may take several minutes)..."
            ollama pull qwen2.5-coder:7b
            ollama pull llama3.2:3b
            echo "✅ AI models downloaded"
        fi
    else
        echo "✅ AI models available"
    fi
fi

# Create output directory
OUTPUT_DIR="$HOME/SuperMini_Output"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "📁 Creating output directory..."
    mkdir -p "$OUTPUT_DIR"/{data,logs,data/memory,data/collaboration,autonomous}
    echo "✅ Output directory created: $OUTPUT_DIR"
fi

echo ""
echo "🎉 SuperMini setup complete!"
echo "   You can now launch SuperMini from your Applications folder"
echo ""
'''
        
        setup_file = self.resources_dir / "setup.sh"
        with open(setup_file, 'w') as f:
            f.write(setup_content)
        
        setup_file.chmod(setup_file.stat().st_mode | stat.S_IEXEC)
        print(f"   ✅ Created setup script")
    
    def create_uninstaller(self):
        """Create an uninstaller script"""
        print("🗑️  Creating uninstaller...")
        
        uninstall_content = '''#!/bin/bash
# SuperMini Uninstaller

echo "🗑️  SuperMini Uninstaller"
echo "=================="

read -p "Remove SuperMini output directory ($HOME/SuperMini_Output)? (y/n): " remove_output
read -p "Remove SuperMini from Applications? (y/n): " remove_app

if [[ "$remove_output" == "y" || "$remove_output" == "Y" ]]; then
    if [ -d "$HOME/SuperMini_Output" ]; then
        rm -rf "$HOME/SuperMini_Output"
        echo "✅ Removed output directory"
    fi
fi

if [[ "$remove_app" == "y" || "$remove_app" == "Y" ]]; then
    if [ -d "/Applications/SuperMini.app" ]; then
        rm -rf "/Applications/SuperMini.app"
        echo "✅ Removed SuperMini.app from Applications"
    fi
fi

echo "👋 SuperMini uninstallation complete"
'''
        
        uninstall_file = self.resources_dir / "uninstall.sh"
        with open(uninstall_file, 'w') as f:
            f.write(uninstall_content)
        
        uninstall_file.chmod(uninstall_file.stat().st_mode | stat.S_IEXEC)
        print(f"   ✅ Created uninstaller")
    
    def create_app_bundle(self):
        """Main method to create the complete app bundle"""
        print("🍎 Creating macOS App Bundle for SuperMini")
        print("=" * 50)
        
        # Create structure
        self.create_app_structure()
        
        # Create Info.plist
        self.create_info_plist()
        
        # Create launcher
        self.create_launcher_script()
        
        # Copy files
        self.copy_application_files()
        
        # Create additional scripts
        self.create_setup_script()
        self.create_uninstaller()
        
        # Set proper permissions
        self.set_permissions()
        
        print("\\n🎉 App Bundle Creation Complete!")
        print("=" * 50)
        print(f"📱 App Bundle: {self.app_bundle}")
        
        # Get bundle size
        size_result = subprocess.run(['du', '-sh', str(self.app_bundle)], 
                                   capture_output=True, text=True)
        if size_result.returncode == 0:
            size = size_result.stdout.split()[0]
            print(f"📊 Bundle Size: {size}")
        
        print("\\n📋 Next Steps:")
        print("1. Test the app bundle:")
        print(f"   open {self.app_bundle}")
        print("2. Install to Applications:")
        print(f"   cp -R {self.app_bundle} /Applications/")
        print("3. Create DMG for distribution:")
        print("   python3 create_macos_dmg.py")
        
        return True
    
    def set_permissions(self):
        """Set proper permissions for app bundle"""
        print("🔐 Setting permissions...")
        
        # Make launcher executable
        launcher = self.macos_dir / self.app_name
        if launcher.exists():
            launcher.chmod(0o755)
        
        # Make scripts executable
        for script in ["setup.sh", "uninstall.sh"]:
            script_path = self.resources_dir / script
            if script_path.exists():
                script_path.chmod(0o755)
        
        print("   ✅ Permissions set")

def main():
    """Main execution"""
    creator = MacOSAppCreator()
    
    try:
        success = creator.create_app_bundle()
        if success:
            print("\\n🚀 Ready for macOS deployment!")
            return True
        else:
            print("\\n❌ App bundle creation failed")
            return False
    except Exception as e:
        print(f"\\n❌ Error creating app bundle: {e}")
        return False

if __name__ == "__main__":
    main()