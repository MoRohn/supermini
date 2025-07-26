#!/usr/bin/env python3
"""
Universal Icon Creator for SuperMini
Generates all icon formats needed for cross-platform deployment
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
import json

class UniversalIconCreator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.assets_dir = self.base_dir / "assets"
        self.output_dir = self.base_dir / "icons_generated"
        self.svg_source = self.assets_dir / "SuperMini_icon.svg"
        
        # Icon sizes for different platforms
        self.icon_sizes = {
            'common': [16, 20, 24, 32, 40, 48, 64, 96, 128, 256, 512, 1024],
            'windows': [16, 24, 32, 48, 64, 96, 128, 256],
            'macos': [16, 20, 29, 32, 40, 44, 48, 50, 55, 58, 60, 64, 72, 76, 80, 87, 88, 100, 114, 120, 128, 144, 152, 167, 172, 180, 196, 216, 234, 256, 512, 1024],
            'linux': [16, 22, 24, 32, 36, 48, 64, 72, 96, 128, 192, 256, 512]
        }
    
    def setup_directories(self):
        """Create necessary directories"""
        print("📁 Setting up directory structure...")
        
        # Clean and create output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        
        # Create platform-specific directories
        directories = [
            "png/common",
            "png/windows", 
            "png/macos",
            "png/linux",
            "ico/windows",
            "icns/macos",
            "desktop/linux"
        ]
        
        for dir_path in directories:
            (self.output_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        print(f"   ✅ Created directories in {self.output_dir}")
    
    def check_dependencies(self):
        """Check for required tools"""
        print("🔍 Checking dependencies...")
        
        tools = {
            'inkscape': 'SVG to PNG conversion',
            'convert': 'ImageMagick for ICO creation', 
            'iconutil': 'macOS ICNS creation (Mac only)',
            'optipng': 'PNG optimization (optional)'
        }
        
        available_tools = {}
        
        for tool, description in tools.items():
            if shutil.which(tool):
                available_tools[tool] = True
                print(f"   ✅ {tool} - {description}")
            else:
                available_tools[tool] = False
                if tool == 'iconutil' and os.name != 'darwin':
                    print(f"   ⚠️  {tool} - {description} (not available on this platform)")
                else:
                    print(f"   ❌ {tool} - {description} (missing)")
        
        return available_tools
    
    def generate_png_icons(self, tools):
        """Generate PNG icons in all required sizes"""
        print("🎨 Generating PNG icons...")
        
        if not self.svg_source.exists():
            print(f"   ❌ SVG source not found: {self.svg_source}")
            return False
        
        # Generate all sizes for all platforms
        all_sizes = set()
        for platform_sizes in self.icon_sizes.values():
            all_sizes.update(platform_sizes)
        
        for size in sorted(all_sizes):
            png_file = self.output_dir / "png" / "common" / f"supermini_{size}x{size}.png"
            
            if tools['inkscape']:
                # Use Inkscape for high-quality conversion
                cmd = [
                    'inkscape',
                    '--export-type=png',
                    f'--export-filename={png_file}',
                    f'--export-width={size}',
                    f'--export-height={size}',
                    str(self.svg_source)
                ]
            elif tools['convert']:
                # Fallback to ImageMagick
                cmd = [
                    'convert',
                    '-background', 'transparent',
                    '-size', f'{size}x{size}',
                    str(self.svg_source),
                    str(png_file)
                ]
            else:
                print("   ❌ No SVG conversion tool available")
                return False
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"   ✅ Generated {size}x{size} PNG")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to generate {size}x{size} PNG: {e}")
                return False
        
        # Optimize PNGs if optipng is available
        if tools['optipng']:
            print("   🔧 Optimizing PNG files...")
            png_files = list((self.output_dir / "png" / "common").glob("*.png"))
            for png_file in png_files:
                try:
                    subprocess.run(['optipng', '-quiet', str(png_file)], check=True)
                except subprocess.CalledProcessError:
                    pass  # Optimization failure is not critical
        
        return True
    
    def copy_platform_specific_pngs(self):
        """Copy PNGs to platform-specific directories"""
        print("📋 Organizing platform-specific PNG files...")
        
        common_dir = self.output_dir / "png" / "common"
        
        for platform, sizes in self.icon_sizes.items():
            if platform == 'common':
                continue
                
            platform_dir = self.output_dir / "png" / platform
            
            for size in sizes:
                src_file = common_dir / f"supermini_{size}x{size}.png"
                dst_file = platform_dir / f"supermini_{size}x{size}.png"
                
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    print(f"   ✅ Copied {size}x{size} for {platform}")
    
    def create_windows_ico(self, tools):
        """Create Windows ICO files"""
        print("🪟 Creating Windows ICO files...")
        
        if not tools['convert']:
            print("   ❌ ImageMagick not available for ICO creation")
            return False
        
        ico_dir = self.output_dir / "ico" / "windows"
        png_dir = self.output_dir / "png" / "windows"
        
        # Create multi-resolution ICO
        ico_files = []
        for size in self.icon_sizes['windows']:
            png_file = png_dir / f"supermini_{size}x{size}.png"
            if png_file.exists():
                ico_files.append(str(png_file))
        
        if ico_files:
            ico_output = ico_dir / "supermini.ico"
            cmd = ['convert'] + ico_files + [str(ico_output)]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"   ✅ Created multi-resolution ICO: {ico_output}")
                
                # Also create single-size ICOs for compatibility
                for size in [16, 32, 48, 256]:
                    png_file = png_dir / f"supermini_{size}x{size}.png"
                    if png_file.exists():
                        single_ico = ico_dir / f"supermini_{size}.ico"
                        subprocess.run(['convert', str(png_file), str(single_ico)], 
                                     check=True, capture_output=True)
                        print(f"   ✅ Created {size}px ICO")
                
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to create ICO: {e}")
                return False
        
        return False
    
    def create_macos_icns(self, tools):
        """Create macOS ICNS files"""
        print("🍎 Creating macOS ICNS files...")
        
        if not tools['iconutil']:
            print("   ⚠️  iconutil not available (macOS required)")
            return False
        
        icns_dir = self.output_dir / "icns" / "macos"
        png_dir = self.output_dir / "png" / "macos"
        
        # Create iconset directory
        iconset_dir = icns_dir / "supermini.iconset"
        iconset_dir.mkdir(exist_ok=True)
        
        # macOS iconset naming convention
        iconset_mapping = {
            16: "icon_16x16.png",
            32: "icon_16x16@2x.png",
            32: "icon_32x32.png", 
            64: "icon_32x32@2x.png",
            128: "icon_128x128.png",
            256: "icon_128x128@2x.png",
            256: "icon_256x256.png",
            512: "icon_256x256@2x.png",
            512: "icon_512x512.png",
            1024: "icon_512x512@2x.png"
        }
        
        # Copy files with correct names
        for size, iconset_name in iconset_mapping.items():
            src_file = png_dir / f"supermini_{size}x{size}.png"
            dst_file = iconset_dir / iconset_name
            
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"   ✅ Added {iconset_name}")
        
        # Create ICNS file
        icns_output = icns_dir / "supermini.icns"
        cmd = ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_output)]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"   ✅ Created ICNS: {icns_output}")
            
            # Clean up iconset directory
            shutil.rmtree(iconset_dir)
            
            # Copy to assets directory for immediate use
            assets_icns = self.assets_dir / "SuperMini.icns"
            shutil.copy2(icns_output, assets_icns)
            print(f"   ✅ Updated assets: {assets_icns}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create ICNS: {e}")
            return False
    
    def create_linux_desktop_files(self):
        """Create Linux desktop integration files"""
        print("🐧 Creating Linux desktop files...")
        
        desktop_dir = self.output_dir / "desktop" / "linux"
        
        # Create .desktop file
        desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=SuperMini
GenericName=Autonomous Mac Mini AI Agent
Comment=Autonomous AI agent for Mac Mini systems
Exec=supermini
Icon=supermini
Terminal=false
Categories=Office;Productivity;AudioVideo;Graphics;Development;
Keywords=AI;assistant;multimedia;automation;productivity;
StartupNotify=true
StartupWMClass=supermini
MimeType=text/plain;image/png;image/jpeg;application/pdf;
"""
        
        desktop_file = desktop_dir / "supermini.desktop"
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        print(f"   ✅ Created desktop file: {desktop_file}")
        
        # Create installation script for Linux
        install_script = desktop_dir / "install_linux_icons.sh"
        install_content = """#!/bin/bash
# SuperMini Linux Icon Installation Script

echo "Installing SuperMini icons and desktop integration..."

# Create icon directories
mkdir -p ~/.local/share/icons/hicolor/{16x16,22x22,24x24,32x32,36x36,48x48,64x64,72x72,96x96,128x128,192x192,256x256,512x512}/apps

# Copy icons
for size in 16 22 24 32 36 48 64 72 96 128 192 256 512; do
    if [ -f "../png/linux/supermini_${size}x${size}.png" ]; then
        cp "../png/linux/supermini_${size}x${size}.png" "~/.local/share/icons/hicolor/${size}x${size}/apps/supermini.png"
        echo "✅ Installed ${size}x${size} icon"
    fi
done

# Install desktop file
mkdir -p ~/.local/share/applications
cp supermini.desktop ~/.local/share/applications/
echo "✅ Installed desktop file"

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache ~/.local/share/icons/hicolor/
    echo "✅ Updated icon cache"
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database ~/.local/share/applications
    echo "✅ Updated desktop database"
fi

echo "🎉 SuperMini Linux integration installed!"
echo "   You can now launch SuperMini from your application menu"
"""
        
        with open(install_script, 'w') as f:
            f.write(install_content)
        
        os.chmod(install_script, 0o755)
        print(f"   ✅ Created installation script: {install_script}")
        
        return True
    
    def create_icon_manifest(self):
        """Create manifest with icon information"""
        print("📋 Creating icon manifest...")
        
        manifest = {
            "created_by": "SuperMini Universal Icon Creator",
            "source_file": str(self.svg_source.relative_to(self.base_dir)),
            "platforms": {
                "windows": {
                    "formats": ["ico", "png"],
                    "primary_file": "ico/windows/supermini.ico",
                    "sizes": self.icon_sizes['windows']
                },
                "macos": {
                    "formats": ["icns", "png"],
                    "primary_file": "icns/macos/supermini.icns", 
                    "sizes": self.icon_sizes['macos']
                },
                "linux": {
                    "formats": ["png", "desktop"],
                    "primary_file": "png/linux/supermini_48x48.png",
                    "sizes": self.icon_sizes['linux']
                }
            },
            "usage_instructions": {
                "windows": "Use ico/windows/supermini.ico in your build process",
                "macos": "Use icns/macos/supermini.icns for app bundles",
                "linux": "Run desktop/linux/install_linux_icons.sh for system integration"
            }
        }
        
        manifest_file = self.output_dir / "icon_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"   ✅ Created manifest: {manifest_file}")
        return True
    
    def generate_all_icons(self):
        """Main method to generate all icon formats"""
        print("🎨 SuperMini Universal Icon Creator")
        print("=" * 50)
        
        # Setup
        self.setup_directories()
        tools = self.check_dependencies()
        
        # Generate base PNG files
        if not self.generate_png_icons(tools):
            print("❌ Failed to generate PNG icons")
            return False
        
        # Organize platform-specific PNGs
        self.copy_platform_specific_pngs()
        
        # Create platform-specific formats
        windows_success = self.create_windows_ico(tools)
        macos_success = self.create_macos_icns(tools)
        linux_success = self.create_linux_desktop_files()
        
        # Create manifest
        self.create_icon_manifest()
        
        # Summary
        print("\n🎉 Icon Generation Complete!")
        print("=" * 50)
        
        total_files = len(list(self.output_dir.rglob("*")))
        print(f"📊 Generated {total_files} files in {self.output_dir}")
        
        # Platform status
        platforms = {
            "Windows": windows_success,
            "macOS": macos_success, 
            "Linux": linux_success
        }
        
        for platform, success in platforms.items():
            status = "✅" if success else "❌"
            print(f"   {status} {platform}")
        
        print(f"\n📁 Output directory: {self.output_dir}")
        print("📋 Check icon_manifest.json for usage instructions")
        
        return all(platforms.values())

def main():
    """Main execution"""
    creator = UniversalIconCreator()
    success = creator.generate_all_icons()
    
    if success:
        print("\n🚀 Ready for cross-platform deployment!")
    else:
        print("\n⚠️  Some icon formats failed to generate")
        print("   Check dependencies and try again")
    
    return success

if __name__ == "__main__":
    main()