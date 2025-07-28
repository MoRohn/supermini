#!/usr/bin/env python3
"""
Dead Simple SuperMini Launcher
Just launches supermini.py - that's it!
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Simple SuperMini Launcher")
    print("=" * 30)
    
    # Find supermini.py
    script_dir = Path(__file__).parent.parent
    app_path = script_dir / "supermini.py"
    
    if not app_path.exists():
        print("❌ Error: supermini.py not found")
        print(f"   Looking in: {script_dir}")
        input("Press Enter to exit...")
        return 1
    
    print(f"✅ Found: {app_path}")
    print("🏃 Starting SuperMini...")
    
    try:
        # Just run it
        subprocess.run([sys.executable, str(app_path)])
        print("SuperMini has closed.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())