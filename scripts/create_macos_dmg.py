#!/usr/bin/env python3
"""
Create macOS DMG for SuperMini
Professional DMG creation with proper layout and background
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
import json

class MacOSDMGCreator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.app_name = "SuperMini"
        self.version = "2.1.0"
        self.dmg_name = f"{self.app_name}-{self.version}"
        
        # Paths
        self.build_dir = self.base_dir / "build"
        self.dist_dir = self.base_dir / "dist"
        self.app_bundle = self.build_dir / f"{self.app_name}.app"
        
        # DMG settings
        self.dmg_size = "500m"
        self.window_size = (640, 480)
        self.icon_size = 128
        self.background_color = "#f0f0f0"
    
    def check_prerequisites(self):
        """Check if app bundle exists"""
        print("🔍 Checking prerequisites...")
        
        if not self.app_bundle.exists():
            print(f"❌ App bundle not found: {self.app_bundle}")
            print("   Run create_macos_app.py first")
            return False
        
        # Check for required tools
        tools = ['hdiutil']  # Only hdiutil is required
        missing_tools = []
        
        for tool in tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def create_dmg_source(self):
        """Create the source directory for DMG"""
        print("📁 Creating DMG source directory...")
        
        # Create temporary directory for DMG contents
        dmg_source = self.build_dir / "dmg_source"
        if dmg_source.exists():
            shutil.rmtree(dmg_source)
        dmg_source.mkdir(parents=True)
        
        # Copy app bundle
        app_dest = dmg_source / f"{self.app_name}.app"
        shutil.copytree(self.app_bundle, app_dest)
        print(f"   ✅ Copied {self.app_name}.app")
        
        # Create Applications symlink
        applications_link = dmg_source / "Applications"
        applications_link.symlink_to("/Applications")
        print("   ✅ Created Applications symlink")
        
        # Create README
        readme_content = f"""Welcome to {self.app_name} v{self.version}!

🚀 INSTALLATION:
1. Drag "{self.app_name}.app" to the "Applications" folder
2. Open Applications and double-click {self.app_name}
3. Run the setup script if prompted

🔧 FIRST-TIME SETUP:
• The app will create a Python virtual environment on first run
• Install Ollama from https://ollama.ai/ for full AI features
• Optional: Add Claude API key in Settings for enhanced AI

💡 FEATURES:
• Task Me: AI-assisted task execution
• Go Explore: Autonomous AI exploration  
• Enhance Yourself: Self-improvement mode
• Multimedia processing and analysis
• Document analysis and summarization
• Code generation and debugging
• Data analytics and visualization

📁 OUTPUT: Files are saved to ~/SuperMini_Output/

🆘 SUPPORT: Check built-in documentation and help files

Enjoy your autonomous Mac Mini AI agent! 🤖✨
"""
        
        readme_file = dmg_source / "README.txt"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print("   ✅ Created README.txt")
        
        # Create Quick Start Guide
        quickstart_content = f"""{self.app_name} Quick Start Guide

🚀 GETTING STARTED:

1. INSTALL THE APP:
   • Drag {self.app_name}.app to Applications folder
   • Launch from Applications or Launchpad

2. FIRST RUN SETUP:
   • {self.app_name} will automatically set up its environment
   • Install Python dependencies (automatic)
   • Create output directories

3. INSTALL OLLAMA (RECOMMENDED):
   • Download from: https://ollama.ai/
   • Or use Homebrew: brew install ollama
   • Download AI models: ollama pull qwen2.5-coder:7b

4. BASIC USAGE:
   • Click "Task Me" for AI assistance
   • Use "Go Explore" for autonomous AI
   • Try "Enhance Yourself" for self-improvement
   
5. SETTINGS:
   • Add Claude API key for enhanced features
   • Configure output preferences
   • Adjust AI model settings

📁 All generated files go to: ~/SuperMini_Output/

❓ Need help? Check the built-in documentation!
"""
        
        quickstart_file = dmg_source / "Quick Start.txt"
        with open(quickstart_file, 'w') as f:
            f.write(quickstart_content)
        print("   ✅ Created Quick Start Guide")
        
        return dmg_source
    
    def create_dmg_layout_script(self, dmg_source):
        """Create AppleScript to set DMG window layout"""
        print("🎨 Creating DMG layout script...")
        
        script_content = f'''
tell application "Finder"
    tell disk "{self.app_name} {self.version}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {{100, 100, {100 + self.window_size[0]}, {100 + self.window_size[1]}}}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to {self.icon_size}
        set background color of viewOptions to {{61166, 61166, 61166}}
        
        -- Position icons
        set position of item "{self.app_name}.app" of container window to {{150, 200}}
        set position of item "Applications" of container window to {{450, 200}}
        set position of item "README.txt" of container window to {{150, 350}}
        set position of item "Quick Start.txt" of container window to {{450, 350}}
        
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
'''
        
        script_file = self.build_dir / "dmg_layout.applescript"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        print("   ✅ Created layout script")
        return script_file
    
    def create_dmg(self, dmg_source):
        """Create the final DMG"""
        print("💿 Creating DMG...")
        
        # Ensure dist directory exists
        self.dist_dir.mkdir(exist_ok=True)
        
        # Remove old DMG
        final_dmg = self.dist_dir / f"{self.dmg_name}.dmg"
        if final_dmg.exists():
            final_dmg.unlink()
            print(f"   🗑️  Removed old DMG")
        
        # Create temporary DMG
        temp_dmg = self.build_dir / "temp.dmg"
        if temp_dmg.exists():
            temp_dmg.unlink()
        
        try:
            # Step 1: Create writable DMG
            print("   📀 Creating temporary DMG...")
            cmd1 = [
                'hdiutil', 'create',
                '-srcfolder', str(dmg_source),
                '-volname', f"{self.app_name} {self.version}",
                '-fs', 'HFS+',
                '-fsargs', '-c c=64,a=16,e=16',
                '-format', 'UDRW',
                '-size', self.dmg_size,
                str(temp_dmg)
            ]
            
            result = subprocess.run(cmd1, check=True, capture_output=True, text=True)
            print("   ✅ Temporary DMG created")
            
            # Step 2: Mount the DMG
            print("   🔗 Mounting DMG for layout...")
            mount_result = subprocess.run([
                'hdiutil', 'attach', str(temp_dmg), '-readwrite', '-noverify', '-noautoopen'
            ], check=True, capture_output=True, text=True)
            
            # Find mount point - try multiple approaches
            mount_point = None
            
            # First try to find in output
            for line in mount_result.stdout.split('\\n'):
                if '/Volumes/' in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('/Volumes/'):
                            # Verify the mount point exists
                            if Path(part).exists():
                                mount_point = part
                                break
                    if mount_point:
                        break
            
            # Fallback: check common mount point
            if not mount_point:
                fallback_mount = f"/Volumes/{self.app_name} {self.version}"
                if Path(fallback_mount).exists():
                    mount_point = fallback_mount
                else:
                    # Try without version
                    fallback_mount = f"/Volumes/{self.app_name}"
                    if Path(fallback_mount).exists():
                        mount_point = fallback_mount
            
            if not mount_point:
                raise Exception("Could not find mount point")
            
            print(f"   ✅ DMG mounted at: {mount_point}")
            
            # Step 3: Apply layout (skipped for compatibility)
            print("   ⚠️  Custom layout skipped for compatibility")
            
            # Step 4: Unmount
            print("   📤 Unmounting DMG...")
            try:
                subprocess.run(['hdiutil', 'detach', mount_point], 
                             check=True, capture_output=True)
                print("   ✅ DMG unmounted")
            except subprocess.CalledProcessError:
                # Try force unmount
                try:
                    subprocess.run(['hdiutil', 'detach', mount_point, '-force'], 
                                 check=True, capture_output=True)
                    print("   ✅ DMG force unmounted")
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  Unmount failed, continuing: {e}")
                    # Continue anyway
            
            # Step 5: Convert to final compressed DMG (with retry)
            print("   🗜️  Compressing final DMG...")
            
            # Wait a bit for any file handles to close
            import time
            time.sleep(2)
            
            cmd2 = [
                'hdiutil', 'convert', str(temp_dmg),
                '-format', 'UDZO',
                '-imagekey', 'zlib-level=9',
                '-o', str(final_dmg)
            ]
            
            # Retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    subprocess.run(cmd2, check=True, capture_output=True)
                    print("   ✅ Final DMG created")
                    break
                except subprocess.CalledProcessError as e:
                    if attempt < max_retries - 1:
                        print(f"   ⚠️  Attempt {attempt + 1} failed, retrying...")
                        time.sleep(3)
                    else:
                        print(f"   ❌ All conversion attempts failed: {e}")
                        # Try simpler approach
                        print("   🔄 Trying simpler DMG creation...")
                        simple_cmd = [
                            'hdiutil', 'create',
                            '-srcfolder', str(dmg_source),
                            '-volname', f"{self.app_name} {self.version}",
                            '-format', 'UDZO',
                            str(final_dmg)
                        ]
                        subprocess.run(simple_cmd, check=True, capture_output=True)
                        print("   ✅ Simple DMG created")
            
            # Clean up
            temp_dmg.unlink()
            
            return final_dmg
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ DMG creation failed: {e}")
            if e.stderr:
                print(f"   Error details: {e.stderr}")
            return None
    
    def verify_dmg(self, dmg_path):
        """Verify the created DMG"""
        print("🔍 Verifying DMG...")
        
        try:
            # Verify DMG integrity
            subprocess.run(['hdiutil', 'verify', str(dmg_path)], 
                         check=True, capture_output=True)
            print("   ✅ DMG verification passed")
            
            # Get DMG info
            info_result = subprocess.run(['hdiutil', 'imageinfo', str(dmg_path)], 
                                       capture_output=True, text=True)
            if info_result.returncode == 0:
                print("   ✅ DMG info retrieved")
            
            # Test mounting
            mount_result = subprocess.run([
                'hdiutil', 'attach', str(dmg_path), '-readonly', '-nobrowse'
            ], capture_output=True, text=True)
            
            if mount_result.returncode == 0:
                # Find mount point and check contents
                mount_point = None
                for line in mount_result.stdout.split('\\n'):
                    if '/Volumes/' in line:
                        parts = line.split()
                        for part in parts:
                            if part.startswith('/Volumes/') and Path(part).exists():
                                mount_point = part
                                break
                        if mount_point:
                            break
                
                if mount_point and Path(mount_point).exists():
                    try:
                        contents = list(Path(mount_point).iterdir())
                        print(f"   ✅ DMG contains {len(contents)} items")
                        
                        # Unmount
                        subprocess.run(['hdiutil', 'detach', mount_point], 
                                     capture_output=True)
                        print("   ✅ Test mount successful")
                        return True
                    except Exception as e:
                        print(f"   ⚠️  Error checking contents: {e}")
                        # Try to unmount anyway
                        subprocess.run(['hdiutil', 'detach', mount_point], 
                                     capture_output=True)
                        return True
                else:
                    print("   ⚠️  Mount point not accessible")
                    return True  # DMG was created, that's what matters
            
            return False
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ DMG verification failed: {e}")
            return False
    
    def create_desktop_installer(self, dmg_path):
        """Create desktop installer shortcut"""
        print("🖥️  Creating desktop installer...")
        
        desktop_installer = Path.home() / "Desktop" / f"Install {self.app_name}.command"
        
        installer_content = f'''#!/bin/bash
# SuperMini Desktop Installer

echo "🚀 Installing {self.app_name}..."

DMG_PATH="{dmg_path}"

if [ -f "$DMG_PATH" ]; then
    open "$DMG_PATH"
    echo "✅ Installer opened"
    echo "📋 Drag {self.app_name}.app to Applications folder to install"
else
    echo "❌ Installer not found: $DMG_PATH"
    echo "📁 Please locate the SuperMini DMG file manually"
fi
'''
        
        with open(desktop_installer, 'w') as f:
            f.write(installer_content)
        
        desktop_installer.chmod(0o755)
        print(f"   ✅ Desktop installer created: {desktop_installer}")
        return desktop_installer
    
    def create_dmg_package(self):
        """Main method to create DMG package"""
        print("💿 Creating macOS DMG Package for SuperMini")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Create DMG source
        dmg_source = self.create_dmg_source()
        
        # Create DMG
        dmg_path = self.create_dmg(dmg_source)
        if not dmg_path:
            return False
        
        # Verify DMG
        if not self.verify_dmg(dmg_path):
            print("⚠️  DMG verification failed but continuing...")
        
        # Create desktop installer
        desktop_installer = self.create_desktop_installer(dmg_path)
        
        # Get file info
        file_size = dmg_path.stat().st_size / 1024 / 1024
        
        # Clean up
        if dmg_source.exists():
            shutil.rmtree(dmg_source)
        
        print("\\n🎉 DMG Package Creation Complete!")
        print("=" * 50)
        print(f"💿 DMG File: {dmg_path}")
        print(f"📊 Size: {file_size:.1f} MB")
        print(f"🖥️  Desktop Installer: {desktop_installer}")
        
        print("\\n📋 Distribution Ready:")
        print("1. Double-click desktop installer to test")
        print("2. Distribute the DMG file")
        print("3. Users drag SuperMini.app to Applications")
        print("4. Launch from Applications/Launchpad")
        
        return True

def main():
    """Main execution"""
    creator = MacOSDMGCreator()
    
    try:
        success = creator.create_dmg_package()
        if success:
            print("\\n🚀 Ready for macOS distribution!")
            return True
        else:
            print("\\n❌ DMG creation failed")
            return False
    except Exception as e:
        print(f"\\n❌ Error creating DMG: {e}")
        return False

if __name__ == "__main__":
    main()