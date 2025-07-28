#!/usr/bin/env python3
"""
SuperMini Complete Setup & Build System
One command to rule them all: setup, icon, build, package
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def run_script(script_name, description):
    """Run a script and return success status"""
    print(f"\n🔧 {description}")
    print("-" * 60)
    
    script_path = Path(__file__).parent / script_name
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path)
        ], check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Script not found: {script_name}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SuperMini Setup & Build System")
    parser.add_argument('--icons-only', action='store_true', 
                       help='Only setup/update icons')
    parser.add_argument('--build-only', action='store_true', 
                       help='Only build (skip icon setup)')
    parser.add_argument('--quick', action='store_true', 
                       help='Quick build without extensive validation')
    
    args = parser.parse_args()
    
    print("🚀 SuperMini Complete Setup & Build System")
    print("=" * 60)
    print("This script will:")
    
    if not args.build_only:
        print("  1. Setup and validate icons")
    if not args.icons_only:
        print("  2. Build macOS app bundle")
        print("  3. Create DMG installer")
        print("  4. Generate checksums")
    
    print("\nStarting in 3 seconds...")
    
    try:
        import time
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return 1
    
    success = True
    
    # Step 1: Icon setup
    if not args.build_only:
        success &= run_script("icon_dev.py", "Icon Development & Setup")
    
    # Step 2: Build
    if not args.icons_only and success:
        success &= run_script("build.py", "Application Build & Packaging")
    
    # Final status
    print("\n" + "=" * 60)
    if success:
        print("🎉 SuperMini setup & build completed successfully!")
        print("\nNext steps:")
        print("  • Test the DMG installer in dist/")
        print("  • Install and verify the app works")
        print("  • Distribute to users")
    else:
        print("❌ Setup & build failed")
        print("\nCheck the error messages above and try again")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())