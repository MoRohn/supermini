#!/usr/bin/env python3
"""
SuperMini DMG Creator
Creates a professional macOS DMG installer for SuperMini
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
import json

class DMGCreator:
    def __init__(self):
        self.app_name = "SuperMini"
        self.app_version = "2.0.1"
        self.bundle_id = "com.supermini.ai-assistant"
        self.build_dir = Path("build")
        self.dist_dir = Path("dist")
        
    def create_app_bundle(self):
        """Create macOS app bundle structure"""
        
        print("📱 Creating macOS app bundle...")
        
        # Create app bundle structure
        app_bundle = self.build_dir / f"{self.app_name}.app"
        contents_dir = app_bundle / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        # Clean and create directories
        if app_bundle.exists():
            shutil.rmtree(app_bundle)
        
        macos_dir.mkdir(parents=True)
        resources_dir.mkdir(parents=True)
        
        # Create Info.plist
        info_plist = {
            "CFBundleName": self.app_name,
            "CFBundleDisplayName": "SuperMini - AI Multimedia Management",
            "CFBundleIdentifier": self.bundle_id,
            "CFBundleVersion": self.app_version,
            "CFBundleShortVersionString": self.app_version,
            "CFBundleExecutable": self.app_name,
            "CFBundleIconFile": "SuperMini.icns",
            "CFBundlePackageType": "APPL",
            "CFBundleSignature": "????",
            "LSMinimumSystemVersion": "10.15",
            "NSHighResolutionCapable": True,
            "NSAppleScriptEnabled": False,
            "LSUIElement": False,
            "CFBundleDocumentTypes": [
                {
                    "CFBundleTypeExtensions": ["txt", "md", "csv", "json"],
                    "CFBundleTypeName": "Text Documents",
                    "CFBundleTypeRole": "Viewer"
                },
                {
                    "CFBundleTypeExtensions": ["png", "jpg", "jpeg", "gif", "bmp"],
                    "CFBundleTypeName": "Image Files", 
                    "CFBundleTypeRole": "Viewer"
                }
            ]
        }
        
        # Write Info.plist
        plist_content = self._dict_to_plist(info_plist)
        with open(contents_dir / "Info.plist", 'w') as f:
            f.write(plist_content)
        
        # Copy icon
        if Path("assets/SuperMini.icns").exists():
            shutil.copy2("assets/SuperMini.icns", resources_dir)
        
        # Create main executable script
        main_script = f"""#!/bin/bash
# SuperMini Launcher
# Get the directory containing this script
APP_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# Change to app directory
cd "$RESOURCES_DIR"

# Activate virtual environment
source venv/bin/activate

# Start Ollama if not running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Launch SuperMini
python3 aimm.py
"""
        
        # Write and make executable
        main_executable = macos_dir / self.app_name
        with open(main_executable, 'w') as f:
            f.write(main_script)
        os.chmod(main_executable, 0o755)
        
        # Copy application files to Resources
        files_to_copy = [
            "aimm.py",
            "recursive_engine.py", 
            "activity_monitor.py",
            "autonomous_agent.py",
            "requirements.txt",
            "venv",
            "assets",
            "prompts"
        ]
        
        for item in files_to_copy:
            src = Path(item)
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, resources_dir / item, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, resources_dir / item)
                print(f"   ✅ Copied {item}")
        
        print(f"✅ App bundle created: {app_bundle}")
        return app_bundle
    
    def _dict_to_plist(self, d):
        """Convert dictionary to plist XML format"""
        plist = '<?xml version="1.0" encoding="UTF-8"?>\\n'
        plist += '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\\n'
        plist += '<plist version="1.0">\\n'
        plist += self._dict_to_xml(d)
        plist += '</plist>\\n'
        return plist
    
    def _dict_to_xml(self, obj, level=0):
        """Convert Python object to XML"""
        indent = "  " * level
        
        if isinstance(obj, dict):
            xml = f"{indent}<dict>\\n"
            for key, value in obj.items():
                xml += f"{indent}  <key>{key}</key>\\n"
                xml += self._dict_to_xml(value, level + 1)
            xml += f"{indent}</dict>\\n"
            return xml
        elif isinstance(obj, list):
            xml = f"{indent}<array>\\n"
            for item in obj:
                xml += self._dict_to_xml(item, level + 1)
            xml += f"{indent}</array>\\n"
            return xml
        elif isinstance(obj, bool):
            return f"{indent}<{'true' if obj else 'false'}/>\\n"
        elif isinstance(obj, (int, float)):
            return f"{indent}<real>{obj}</real>\\n"
        else:
            return f"{indent}<string>{obj}</string>\\n"
    
    def create_dmg(self, app_bundle):
        """Create DMG file from app bundle"""
        
        print("💿 Creating DMG installer...")
        
        # Ensure dist directory exists
        self.dist_dir.mkdir(exist_ok=True)
        
        # DMG settings
        dmg_name = f"{self.app_name}-{self.app_version}"
        dmg_path = self.dist_dir / f"{dmg_name}.dmg"
        
        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()
        
        # Create temporary DMG directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            dmg_source = temp_path / "dmg_source"
            dmg_source.mkdir()
            
            # Copy app bundle to DMG source
            shutil.copytree(app_bundle, dmg_source / f"{self.app_name}.app")
            
            # Create Applications symlink
            applications_link = dmg_source / "Applications"
            applications_link.symlink_to("/Applications")
            
            # Create README file
            readme_content = f"""# {self.app_name} - AI Multimedia Management

## Installation

1. Drag {self.app_name}.app to the Applications folder
2. Open {self.app_name} from Applications or Launchpad

## First Time Setup

1. **Install Ollama** (if not already installed):
   - Download from: https://ollama.ai/
   - Or install via Homebrew: `brew install ollama`

2. **Configure API Keys** (optional but recommended):
   - Get a Claude API key from: https://console.anthropic.com/
   - Add it in {self.app_name} Settings

3. **Start Using {self.app_name}**:
   - Choose from Task Me, Go Explore, or Enhance Yourself modes
   - Attach files for processing
   - Let AI help with your multimedia and management tasks

## Features

- **Code Generation**: Write, debug, and optimize code
- **Multimedia Processing**: Analyze images, process audio/video
- **Document Analysis**: Summarize and extract insights
- **Task Automation**: Generate scripts and workflows
- **Data Analytics**: Analyze CSV files and create visualizations
- **Memory System**: Context-aware responses
- **Autonomous Modes**: Self-directed exploration and enhancement

## System Requirements

- macOS 10.15 or later
- Python 3.9+ (bundled with app)
- 8GB RAM recommended
- Internet connection for Claude API (optional)

## Output Location

Generated files are saved to: `~/SuperMini_Output/`

## Support

For issues and updates, visit: https://github.com/your-username/SuperMini

Happy AI-assisted productivity! 🚀
"""
            
            with open(dmg_source / "README.txt", 'w') as f:
                f.write(readme_content)
            
            # Create background image (optional)
            self._create_dmg_background(dmg_source)
            
            # Create DMG using hdiutil
            try:
                # Create initial DMG
                temp_dmg = temp_path / "temp.dmg"
                
                cmd = [
                    'hdiutil', 'create',
                    '-srcfolder', str(dmg_source),
                    '-volname', f"{self.app_name} {self.app_version}",
                    '-format', 'UDRW',  # Read-write for customization
                    '-size', '500m',
                    str(temp_dmg)
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Mount DMG for customization
                mount_result = subprocess.run([
                    'hdiutil', 'attach', str(temp_dmg),
                    '-mountpoint', str(temp_path / 'mount')
                ], check=True, capture_output=True, text=True)
                
                mount_point = temp_path / 'mount'
                
                # Customize DMG appearance with AppleScript
                applescript = f'''
tell application "Finder"
    tell disk "{self.app_name} {self.app_version}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {{400, 100, 900, 450}}
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 128
        set background picture of theViewOptions to file ".background:dmg_background.png"
        set position of item "{self.app_name}.app" of container window to {{150, 200}}
        set position of item "Applications" of container window to {{350, 200}}
        set position of item "README.txt" of container window to {{250, 300}}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
'''
                
                # Apply AppleScript customization
                try:
                    subprocess.run(['osascript', '-e', applescript], 
                                 check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print("   ⚠️  Could not customize DMG appearance")
                
                # Unmount DMG
                subprocess.run(['hdiutil', 'detach', str(mount_point)], 
                             check=True, capture_output=True)
                
                # Convert to final compressed DMG
                cmd = [
                    'hdiutil', 'convert', str(temp_dmg),
                    '-format', 'UDZO',  # Compressed
                    '-imagekey', 'zlib-level=9',
                    '-o', str(dmg_path)
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                print(f"✅ DMG created: {dmg_path}")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Error creating DMG: {e}")
                # Fallback: create simple DMG
                cmd = [
                    'hdiutil', 'create',
                    '-srcfolder', str(dmg_source),
                    '-volname', f"{self.app_name} {self.app_version}",
                    '-format', 'UDZO',
                    str(dmg_path)
                ]
                subprocess.run(cmd, check=True)
                print(f"✅ Simple DMG created: {dmg_path}")
        
        return dmg_path
    
    def _create_dmg_background(self, dmg_source):
        """Create a background image for the DMG"""
        
        # Create .background directory
        bg_dir = dmg_source / ".background"
        bg_dir.mkdir()
        
        # Create a simple background using Python PIL if available
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create background image
            img = Image.new('RGB', (500, 350), (240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Add gradient background
            for y in range(350):
                r = int(240 - (y / 350) * 40)
                g = int(240 - (y / 350) * 40)
                b = int(240 - (y / 350) * 40)
                draw.line([(0, y), (500, y)], fill=(r, g, b))
            
            # Add instructions text
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
            except:
                font = ImageFont.load_default()
            
            draw.text((250, 50), f"Install {self.app_name}", anchor="mm", 
                     fill=(80, 80, 80), font=font)
            draw.text((250, 80), "Drag app to Applications folder", anchor="mm", 
                     fill=(120, 120, 120), font=font)
            
            # Save background
            img.save(bg_dir / "dmg_background.png", 'PNG')
            
        except ImportError:
            print("   ⚠️  PIL not available, skipping custom background")
    
    def build_distribution(self):
        """Main build process"""
        
        print(f"🚀 Building {self.app_name} v{self.app_version} Distribution")
        print("=" * 50)
        
        # Clean build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir()
        
        try:
            # Create app bundle
            app_bundle = self.create_app_bundle()
            
            # Create DMG
            dmg_path = self.create_dmg(app_bundle)
            
            print("\\n🎉 Distribution Build Complete!")
            print("=" * 50)
            print(f"📱 App Bundle: {app_bundle}")
            print(f"💿 DMG Installer: {dmg_path}")
            print(f"📊 DMG Size: {dmg_path.stat().st_size / 1024 / 1024:.1f} MB")
            print("\\n📋 Next Steps:")
            print("1. Test the DMG by double-clicking it")
            print("2. Drag the app to Applications folder")
            print("3. Launch from Applications or Launchpad")
            print("4. Distribute the DMG file to users")
            
            return dmg_path
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            raise

def main():
    """Main execution"""
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Create DMG
    creator = DMGCreator()
    dmg_path = creator.build_distribution()
    
    # Open DMG location in Finder
    subprocess.run(['open', '-R', str(dmg_path)])

if __name__ == "__main__":
    main()