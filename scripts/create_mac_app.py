#!/usr/bin/env python3
"""
Create a proper macOS .app bundle for SuperMini
This makes the app behave like a native macOS application
"""

import os
import shutil
import subprocess
from pathlib import Path

def create_app_bundle():
    """Create a macOS .app bundle for SuperMini"""
    
    # Paths
    script_dir = Path(__file__).parent
    app_name = "SuperMini"
    app_path = script_dir / f"{app_name}.app"
    
    # Clean up existing app bundle
    if app_path.exists():
        print(f"Removing existing {app_name}.app...")
        shutil.rmtree(app_path)
    
    # Create app bundle structure
    print(f"Creating {app_name}.app bundle...")
    
    # Create directories
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    contents_dir.mkdir(parents=True)
    macos_dir.mkdir()
    resources_dir.mkdir()
    
    # Create Info.plist
    info_plist = contents_dir / "Info.plist"
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleGetInfoString</key>
    <string>SuperMini AI Assistant 1.0</string>
    <key>CFBundleIconFile</key>
    <string>icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.supermini.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleSignature</key>
    <string>SMNI</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
</dict>
</plist>"""
    
    with open(info_plist, 'w') as f:
        f.write(plist_content)
    
    # Create executable script
    executable_path = macos_dir / app_name
    executable_content = f"""#!/bin/bash
# SuperMini App Bundle Launcher

# Get the app bundle path
BUNDLE_PATH="$(dirname "$(dirname "$0")")"
APP_DIR="$(dirname "$BUNDLE_PATH")"

# Change to the application directory
cd "$APP_DIR"

# Check if GUI launcher exists
if [ -f "SuperMini_Launcher.py" ]; then
    # Use GUI launcher
    exec python3 "SuperMini_Launcher.py"
else
    # Fallback to direct launch
    exec python3 "supermini.py"
fi
"""
    
    with open(executable_path, 'w') as f:
        f.write(executable_content)
    
    # Make executable
    os.chmod(executable_path, 0o755)
    
    # Copy icon if available
    icon_sources = [
        script_dir / "assets" / "icon.icns",
        script_dir / "assets" / "icon.png",
        script_dir / "build" / "icon.icns"
    ]
    
    for icon_source in icon_sources:
        if icon_source.exists():
            icon_dest = resources_dir / "icon.icns"
            if icon_source.suffix == ".png":
                # Convert PNG to ICNS if needed
                try:
                    subprocess.run([
                        "sips", "-s", "format", "icns", 
                        str(icon_source), "--out", str(icon_dest)
                    ], check=True, capture_output=True)
                    print(f"✅ Converted {icon_source.name} to icon.icns")
                    break
                except:
                    pass
            else:
                shutil.copy2(icon_source, icon_dest)
                print(f"✅ Copied {icon_source.name} as app icon")
                break
    
    print(f"✅ Created {app_name}.app bundle")
    print(f"📁 Location: {app_path}")
    print("")
    print("To use:")
    print(f"  1. Double-click {app_name}.app to launch")
    print(f"  2. Or drag {app_name}.app to Applications folder")
    print("  3. Then launch from Launchpad or Applications")
    
    return app_path

def main():
    """Main function"""
    print("🚀 SuperMini macOS App Bundle Creator")
    print("====================================")
    print("")
    
    try:
        app_path = create_app_bundle()
        
        # Test the app bundle
        print("")
        print("🧪 Testing app bundle...")
        test_result = subprocess.run([
            "open", str(app_path)
        ], capture_output=True, text=True)
        
        if test_result.returncode == 0:
            print("✅ App bundle test successful!")
        else:
            print("⚠️ App bundle test had issues, but bundle was created")
            
    except Exception as e:
        print(f"❌ Error creating app bundle: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())