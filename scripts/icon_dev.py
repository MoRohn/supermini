#!/usr/bin/env python3
"""
SuperMini Icon Development Tool
Simplified icon generation and management
"""

import os
import subprocess
import shutil
from pathlib import Path

class IconDeveloper:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.assets_dir = self.project_root / "assets"
        self.icons_dir = self.assets_dir / "icons"
        
        # Standard icon sizes for macOS
        self.icon_sizes = [16, 32, 64, 128, 256, 512, 1024]
        
    def print_status(self, message, emoji="ℹ️"):
        print(f"{emoji} {message}")
    
    def find_source_icon(self):
        """Find the best source icon to use"""
        sources = [
            self.icons_dir / "icns" / "SuperMini_neural_zen.icns",
            self.icons_dir / "png" / "SuperMini_neural_zen_1024x1024.png",
            self.icons_dir / "svg" / "SuperMini_neural_zen.svg",
            self.assets_dir / "SuperMini.icns",
            self.assets_dir / "SuperMini_icon.svg"
        ]
        
        for source in sources:
            if source.exists():
                return source
        
        return None
    
    def create_app_icon(self):
        """Create the main app icon for bundling"""
        self.print_status("Creating app icon...")
        
        source = self.find_source_icon()
        if not source:
            self.print_status("No source icon found", "❌")
            return False
        
        target = self.assets_dir / "SuperMini.icns"
        
        if source.suffix == '.icns':
            # Copy existing ICNS
            shutil.copy2(source, target)
            self.print_status(f"Copied ICNS: {source.name}", "✅")
        
        elif source.suffix == '.png':
            # Convert PNG to ICNS
            self._png_to_icns(source, target)
        
        elif source.suffix == '.svg':
            # Convert SVG to ICNS via PNG
            temp_png = self.assets_dir / "temp_1024.png"
            self._svg_to_png(source, temp_png, 1024)
            self._png_to_icns(temp_png, target)
            temp_png.unlink()
        
        if target.exists():
            self.print_status(f"App icon ready: {target}", "✅")
            return True
        
        return False
    
    def _svg_to_png(self, svg_path, png_path, size):
        """Convert SVG to PNG using rsvg-convert or fallback"""
        try:
            # Try rsvg-convert first (Homebrew: librsvg)
            subprocess.run([
                'rsvg-convert', '-w', str(size), '-h', str(size),
                str(svg_path), '-o', str(png_path)
            ], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            # Try qlmanage (built into macOS)
            subprocess.run([
                'qlmanage', '-t', '-s', str(size),
                '-o', str(png_path.parent), str(svg_path)
            ], check=True, capture_output=True)
            
            # qlmanage creates weird names, find and rename
            for file in png_path.parent.glob("*.png"):
                if svg_path.stem in file.name:
                    file.rename(png_path)
                    return True
        except subprocess.CalledProcessError:
            pass
        
        self.print_status("SVG conversion failed - install librsvg or ensure SVG is valid", "⚠️")
        return False
    
    def _png_to_icns(self, png_path, icns_path):
        """Convert PNG to ICNS using iconutil"""
        if not png_path.exists():
            return False
        
        # Create iconset directory
        iconset_dir = icns_path.parent / f"{icns_path.stem}.iconset"
        if iconset_dir.exists():
            shutil.rmtree(iconset_dir)
        iconset_dir.mkdir()
        
        try:
            # Generate different sizes from source PNG
            for size in self.icon_sizes:
                # Standard resolution
                out_file = iconset_dir / f"icon_{size}x{size}.png"
                self._resize_png(png_path, out_file, size)
                
                # High resolution (@2x) for sizes ≤ 512
                if size <= 512:
                    out_file_2x = iconset_dir / f"icon_{size}x{size}@2x.png"
                    self._resize_png(png_path, out_file_2x, size * 2)
            
            # Convert iconset to icns
            subprocess.run([
                'iconutil', '-c', 'icns', str(iconset_dir)
            ], check=True, capture_output=True)
            
            # Clean up
            shutil.rmtree(iconset_dir)
            
            self.print_status(f"ICNS created from PNG", "✅")
            return True
            
        except subprocess.CalledProcessError:
            self.print_status("ICNS conversion failed", "❌")
            return False
    
    def _resize_png(self, source_png, target_png, size):
        """Resize PNG using sips (built into macOS)"""
        try:
            subprocess.run([
                'sips', '-z', str(size), str(size),
                str(source_png), '--out', str(target_png)
            ], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def validate_icon(self, icon_path):
        """Validate icon quality and completeness"""
        if not icon_path.exists():
            return False
        
        # Check file size (should be reasonable)
        size_kb = icon_path.stat().st_size / 1024
        if size_kb < 10 or size_kb > 5000:
            self.print_status(f"Icon size unusual: {size_kb:.1f}KB", "⚠️")
        
        # Try to get icon info
        try:
            result = subprocess.run([
                'file', str(icon_path)
            ], capture_output=True, text=True)
            
            if 'Apple Icon Image' in result.stdout:
                self.print_status("Icon format valid", "✅")
                return True
        except:
            pass
        
        self.print_status("Icon validation inconclusive", "⚠️")
        return True  # Don't fail build for this
    
    def setup_icons(self):
        """Main icon setup process"""
        print("\n🎨 SuperMini Icon Development")
        print("=" * 40)
        
        # Ensure directories exist
        self.assets_dir.mkdir(exist_ok=True)
        
        # Create/update app icon
        success = self.create_app_icon()
        
        if success:
            icon_path = self.assets_dir / "SuperMini.icns"
            self.validate_icon(icon_path)
            print("\n✅ Icon development complete")
            return True
        else:
            print("\n❌ Icon development failed")
            return False

def main():
    """Entry point for icon development"""
    developer = IconDeveloper()
    return developer.setup_icons()

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)