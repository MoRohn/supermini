#!/usr/bin/env python3
"""
SuperMini Icon Creator
Creates a modern, professional icon for the SuperMini application
"""

import subprocess
import sys
from pathlib import Path

def create_svg_icon():
    """Create a modern SVG icon for SuperMini"""
    
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Modern gradient background -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#764ba2;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f093fb;stop-opacity:1" />
    </linearGradient>
    
    <!-- AI circuit pattern gradient -->
    <linearGradient id="circuitGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#74c0fc;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#51cf66;stop-opacity:1" />
    </linearGradient>
    
    <!-- Inner glow -->
    <radialGradient id="innerGlow" cx="50%" cy="30%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#ffffff;stop-opacity:0" />
    </radialGradient>
    
    <!-- Drop shadow filter -->
    <filter id="dropshadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000000" flood-opacity="0.3"/>
    </filter>
    
    <!-- Glow filter -->
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Rounded rectangle background with modern gradient -->
  <rect x="64" y="64" width="896" height="896" rx="200" ry="200" 
        fill="url(#bgGradient)" filter="url(#dropshadow)"/>
  
  <!-- Inner glow overlay -->
  <rect x="64" y="64" width="896" height="896" rx="200" ry="200" 
        fill="url(#innerGlow)"/>
  
  <!-- Main AI brain/circuit design -->
  <g transform="translate(512,512)">
    
    <!-- Central AI brain circle -->
    <circle cx="0" cy="0" r="180" fill="url(#circuitGradient)" opacity="0.9" filter="url(#glow)"/>
    
    <!-- Neural network connections -->
    <g stroke="url(#circuitGradient)" stroke-width="8" fill="none" opacity="0.7">
      <!-- Main connection lines -->
      <path d="M -120,-80 Q 0,-160 120,-80"/>
      <path d="M -120,80 Q 0,160 120,80"/>
      <path d="M -160,0 Q -200,-100 -120,-160"/>
      <path d="M 160,0 Q 200,-100 120,-160"/>
      <path d="M -160,0 Q -200,100 -120,160"/>
      <path d="M 160,0 Q 200,100 120,160"/>
      
      <!-- Circuit nodes -->
      <circle cx="-120" cy="-80" r="12" fill="#74c0fc"/>
      <circle cx="120" cy="-80" r="12" fill="#74c0fc"/>
      <circle cx="-120" cy="80" r="12" fill="#74c0fc"/>
      <circle cx="120" cy="80" r="12" fill="#74c0fc"/>
      <circle cx="-120" cy="-160" r="8" fill="#51cf66"/>
      <circle cx="120" cy="-160" r="8" fill="#51cf66"/>
      <circle cx="-120" cy="160" r="8" fill="#51cf66"/>
      <circle cx="120" cy="160" r="8" fill="#51cf66"/>
    </g>
    
    <!-- Central AI symbol -->
    <g fill="#ffffff" filter="url(#glow)">
      <!-- AI letters -->
      <text x="0" y="20" text-anchor="middle" font-family="SF Pro Display, -apple-system, sans-serif" 
            font-size="120" font-weight="700" letter-spacing="-4">AI</text>
    </g>
    
    <!-- Multimedia symbols around the center -->
    <g fill="#ffffff" opacity="0.8" font-family="SF Pro Display, -apple-system, sans-serif" font-size="36">
      <!-- Code symbol -->
      <text x="-200" y="-120" text-anchor="middle">&lt;/&gt;</text>
      
      <!-- Image symbol -->
      <text x="200" y="-120" text-anchor="middle">🖼</text>
      
      <!-- Document symbol -->
      <text x="-200" y="140" text-anchor="middle">📄</text>
      
      <!-- Analytics symbol -->
      <text x="200" y="140" text-anchor="middle">📊</text>
      
      <!-- Automation symbol -->
      <text x="0" y="-240" text-anchor="middle">⚡</text>
      
      <!-- Management symbol -->
      <text x="0" y="280" text-anchor="middle">⚙️</text>
    </g>
  </g>
  
  <!-- App name at bottom -->
  <text x="512" y="900" text-anchor="middle" fill="#ffffff" opacity="0.9"
        font-family="SF Pro Display, -apple-system, sans-serif" font-size="72" font-weight="600">
    SuperMini
  </text>
</svg>'''
    
    # Write SVG file
    svg_path = Path("assets/SuperMini_icon.svg")
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    return svg_path

def create_icns_from_svg(svg_path):
    """Convert SVG to ICNS format with multiple resolutions"""
    
    # Create iconset directory
    iconset_dir = Path("assets/SuperMini.iconset")
    iconset_dir.mkdir(exist_ok=True)
    
    # Icon sizes for macOS
    sizes = [
        (16, 'icon_16x16.png'),
        (32, 'icon_16x16@2x.png'),
        (32, 'icon_32x32.png'),
        (64, 'icon_32x32@2x.png'),
        (128, 'icon_128x128.png'),
        (256, 'icon_128x128@2x.png'),
        (256, 'icon_256x256.png'),
        (512, 'icon_256x256@2x.png'),
        (512, 'icon_512x512.png'),
        (1024, 'icon_512x512@2x.png')
    ]
    
    # Check if we have the necessary tools
    tools_available = True
    
    # Try to use rsvg-convert (from librsvg)
    try:
        subprocess.run(['which', 'rsvg-convert'], check=True, capture_output=True)
        converter = 'rsvg-convert'
    except subprocess.CalledProcessError:
        try:
            # Try inkscape as fallback
            subprocess.run(['which', 'inkscape'], check=True, capture_output=True)
            converter = 'inkscape'
        except subprocess.CalledProcessError:
            print("Warning: Neither rsvg-convert nor inkscape found.")
            print("Installing librsvg for icon conversion...")
            try:
                # Try to install librsvg via homebrew
                subprocess.run(['brew', 'install', 'librsvg'], check=True)
                converter = 'rsvg-convert'
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Could not install librsvg. Trying alternative method...")
                tools_available = False
    
    if tools_available:
        # Generate PNG files at different resolutions
        for size, filename in sizes:
            output_path = iconset_dir / filename
            
            if converter == 'rsvg-convert':
                cmd = [
                    'rsvg-convert',
                    '--width', str(size),
                    '--height', str(size),
                    '--output', str(output_path),
                    str(svg_path)
                ]
            else:  # inkscape
                cmd = [
                    'inkscape',
                    '--export-type=png',
                    '--export-width', str(size),
                    '--export-height', str(size),
                    '--export-filename', str(output_path),
                    str(svg_path)
                ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"Generated {filename} ({size}x{size})")
            except subprocess.CalledProcessError as e:
                print(f"Failed to generate {filename}: {e}")
        
        # Convert iconset to ICNS
        try:
            subprocess.run([
                'iconutil',
                '--convert', 'icns',
                '--output', 'assets/SuperMini.icns',
                str(iconset_dir)
            ], check=True)
            print("Successfully created SuperMini.icns")
            
            # Clean up iconset directory
            import shutil
            shutil.rmtree(iconset_dir)
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create ICNS file: {e}")
    
    else:
        print("Using Python PIL as fallback for icon generation...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create a simple icon using PIL
            for size, filename in sizes:
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Create a gradient background
                for y in range(size):
                    r = int(102 + (126 - 102) * y / size)
                    g = int(126 + (234 - 126) * y / size)
                    b = int(234 + (162 - 234) * y / size)
                    draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
                
                # Add AI text
                try:
                    font_size = max(size // 4, 8)
                    # Try to use system font
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                except:
                    font = ImageFont.load_default()
                
                text = "AI"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size - text_width) // 2
                y = (size - text_height) // 2
                
                # Add text with shadow
                draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 128))
                draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
                
                # Save PNG
                img.save(iconset_dir / filename, 'PNG')
                print(f"Generated {filename} ({size}x{size}) using PIL")
            
            print("Note: Generated basic icon with PIL. For best quality, install librsvg or inkscape.")
            
        except ImportError:
            print("PIL not available. Please install Pillow: pip install Pillow")

def main():
    """Main function to create the app icon"""
    
    print("🎨 Creating SuperMini Application Icon...")
    print("=" * 40)
    
    # Ensure assets directory exists
    Path("assets").mkdir(exist_ok=True)
    
    # Create SVG icon
    print("📝 Creating SVG icon...")
    svg_path = create_svg_icon()
    print(f"✅ SVG icon created: {svg_path}")
    
    # Convert to ICNS
    print("\n🔄 Converting to ICNS format...")
    create_icns_from_svg(svg_path)
    
    print("\n✅ Icon creation complete!")
    print("📁 Icon files created in assets/")
    print("🖼️  Preview the SVG: open assets/SuperMini_icon.svg")
    print("🍎  macOS icon: assets/SuperMini.icns")

if __name__ == "__main__":
    main()