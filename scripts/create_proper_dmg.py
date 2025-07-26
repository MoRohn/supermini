#!/usr/bin/env python3
"""
Fixed SuperMini DMG Creator - Creates proper double-clickable DMG
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path

def create_proper_dmg():
    """Create a properly formatted DMG that opens correctly"""
    
    print("💿 Creating Proper DMG for SuperMini...")
    
    app_name = "SuperMini"
    version = "2.0.1"
    dmg_name = f"{app_name}-{version}"
    
    # Ensure we have the app bundle
    app_bundle = Path("build/SuperMini.app")
    if not app_bundle.exists():
        print("❌ App bundle not found. Run create_dmg.py first.")
        return None
    
    # Create dist directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Remove old DMG
    old_dmg = dist_dir / f"{dmg_name}.dmg"
    if old_dmg.exists():
        old_dmg.unlink()
        print(f"🗑️  Removed old DMG: {old_dmg}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dmg_source = temp_path / "dmg_contents"
        dmg_source.mkdir()
        
        print("📁 Preparing DMG contents...")
        
        # Copy app bundle
        app_dest = dmg_source / f"{app_name}.app"
        shutil.copytree(app_bundle, app_dest)
        print(f"   ✅ Copied {app_name}.app")
        
        # Create Applications symlink
        applications_link = dmg_source / "Applications"
        applications_link.symlink_to("/Applications")
        print("   ✅ Created Applications symlink")
        
        # Create enhanced README
        readme_content = f"""Welcome to {app_name} v{version}!

🚀 INSTALLATION INSTRUCTIONS:

1. Drag "{app_name}.app" to the "Applications" folder
2. Open Applications folder or Launchpad
3. Double-click {app_name} to launch

📋 FIRST-TIME SETUP:

• Install Ollama: https://ollama.ai/ (Required for AI features)
• Optional: Add Claude API key in {app_name} Settings for enhanced AI

💡 FEATURES:

• Task Me: AI-assisted task execution
• Go Explore: Autonomous AI exploration
• Enhance Yourself: Self-improvement mode
• Multimedia processing and analysis
• Document analysis and summarization
• Code generation and debugging
• Data analytics and visualization

📁 OUTPUT LOCATION: ~/SuperMini_Output/

🆘 SUPPORT: Check README files and documentation

Enjoy your AI-powered productivity assistant! 🤖✨
"""
        
        readme_file = dmg_source / "README.txt"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print("   ✅ Created README.txt")
        
        # Method 1: Try creating DMG with better compatibility
        print("💿 Creating DMG (Method 1: Simple)...")
        
        try:
            cmd = [
                'hdiutil', 'create',
                '-srcfolder', str(dmg_source),
                '-volname', f"{app_name} {version}",
                '-fs', 'HFS+',  # Use HFS+ for better compatibility
                '-format', 'UDZO',  # Compressed
                '-imagekey', 'zlib-level=9',
                str(old_dmg)
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ DMG created successfully: {old_dmg}")
            
            # Verify the DMG
            print("🔍 Verifying DMG...")
            verify_cmd = ['hdiutil', 'verify', str(old_dmg)]
            subprocess.run(verify_cmd, check=True, capture_output=True)
            print("✅ DMG verification passed")
            
            return old_dmg
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Method 1 failed: {e}")
            print("📝 Trying Method 2: Two-step process...")
            
            # Method 2: Two-step process for better compatibility
            try:
                temp_dmg = temp_path / "temp.dmg"
                
                # Step 1: Create writable DMG
                cmd1 = [
                    'hdiutil', 'create',
                    '-srcfolder', str(dmg_source),
                    '-volname', f"{app_name} {version}",
                    '-fs', 'HFS+',
                    '-format', 'UDRW',  # Read-write
                    '-size', '300m',
                    str(temp_dmg)
                ]
                
                subprocess.run(cmd1, check=True, capture_output=True)
                print("   ✅ Created temporary DMG")
                
                # Step 2: Convert to compressed final DMG
                cmd2 = [
                    'hdiutil', 'convert', str(temp_dmg),
                    '-format', 'UDZO',
                    '-imagekey', 'zlib-level=9',
                    '-o', str(old_dmg)
                ]
                
                subprocess.run(cmd2, check=True, capture_output=True)
                print("   ✅ Converted to final compressed DMG")
                
                # Verify the final DMG
                verify_cmd = ['hdiutil', 'verify', str(old_dmg)]
                subprocess.run(verify_cmd, check=True, capture_output=True)
                print("✅ Final DMG verification passed")
                
                return old_dmg
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Method 2 also failed: {e}")
                return None

def fix_dmg_attributes(dmg_path):
    """Fix DMG file attributes for proper double-click behavior"""
    
    print("🔧 Fixing DMG attributes...")
    
    try:
        # Set proper file type and creator
        subprocess.run([
            'SetFile', '-t', 'dmg', '-c', 'ddsk', str(dmg_path)
        ], check=True, capture_output=True)
        print("   ✅ Set file type and creator")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ⚠️  SetFile not available, using alternative method")
        
        # Alternative: Use xattr to set proper attributes
        try:
            # Set Finder info
            subprocess.run([
                'xattr', '-w', 'com.apple.FinderInfo',
                '646D672020200000000000000000000000000000000000000000000000000000',
                str(dmg_path)
            ], check=True, capture_output=True)
            print("   ✅ Set Finder attributes")
            
        except subprocess.CalledProcessError:
            print("   ⚠️  Could not set file attributes")

def create_desktop_shortcut(dmg_path):
    """Create a proper desktop shortcut"""
    
    print("🖥️  Creating desktop shortcut...")
    
    desktop_shortcut = Path.home() / "Desktop" / "SuperMini-Installer.dmg"
    
    # Remove old shortcut
    if desktop_shortcut.exists():
        desktop_shortcut.unlink()
    
    # Create new shortcut
    desktop_shortcut.symlink_to(dmg_path.absolute())
    
    # Set shortcut to open with DiskImageMounter
    try:
        subprocess.run([
            'xattr', '-w', 'com.apple.LaunchServices.OpenWith',
            'com.apple.DiskImageMounter',
            str(desktop_shortcut)
        ], capture_output=True)
        print("   ✅ Set to open with DiskImageMounter")
        
    except subprocess.CalledProcessError:
        print("   ⚠️  Could not set open-with attribute")
    
    print(f"   ✅ Desktop shortcut created: {desktop_shortcut}")
    return desktop_shortcut

def test_dmg_functionality(dmg_path):
    """Test DMG mounting and functionality"""
    
    print("🧪 Testing DMG functionality...")
    
    try:
        # Test mounting
        result = subprocess.run([
            'hdiutil', 'attach', str(dmg_path), '-readonly', '-nobrowse'
        ], check=True, capture_output=True, text=True)
        
        # Find mount point
        mount_point = None
        for line in result.stdout.split('\n'):
            if '/Volumes/' in line and 'SuperMini' in line:
                # Extract the path after /Volumes/
                parts = line.split()
                for part in parts:
                    if part.startswith('/Volumes/'):
                        mount_point = part
                        break
                if mount_point:
                    break
        
        if mount_point:
            print(f"   ✅ DMG mounted at: {mount_point}")
            
            # Check contents
            contents = list(Path(mount_point).iterdir())
            print(f"   ✅ Contains {len(contents)} items:")
            for item in contents:
                print(f"      - {item.name}")
            
            # Unmount
            subprocess.run(['hdiutil', 'detach', mount_point], 
                         check=True, capture_output=True)
            print("   ✅ DMG unmounted successfully")
            
            return True
        else:
            print("   ❌ Could not find mount point")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ DMG test failed: {e}")
        return False

def main():
    """Main execution"""
    
    print("🚀 SuperMini Proper DMG Creator")
    print("=" * 40)
    
    # Create proper DMG
    dmg_path = create_proper_dmg()
    if not dmg_path:
        print("❌ Failed to create DMG")
        return False
    
    # Fix DMG attributes
    fix_dmg_attributes(dmg_path)
    
    # Test DMG
    if test_dmg_functionality(dmg_path):
        print("✅ DMG functionality test passed")
    else:
        print("⚠️  DMG functionality test failed")
    
    # Create desktop shortcut
    desktop_shortcut = create_desktop_shortcut(dmg_path)
    
    # Get file info
    file_size = dmg_path.stat().st_size / 1024 / 1024
    
    print("\\n🎉 DMG Creation Complete!")
    print("=" * 40)
    print(f"📦 DMG File: {dmg_path}")
    print(f"📊 Size: {file_size:.1f} MB")
    print(f"🖥️  Desktop Shortcut: {desktop_shortcut}")
    print("\\n📋 Testing Instructions:")
    print("1. Double-click the desktop shortcut")
    print("2. Verify DMG opens in Finder")
    print("3. Drag SuperMini.app to Applications")
    print("4. Launch from Applications/Launchpad")
    
    return True

if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)
    main()