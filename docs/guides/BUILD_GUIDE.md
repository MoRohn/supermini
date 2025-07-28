# SuperMini Build & Distribution Guide

## Overview

This guide covers the simplified build system for SuperMini, consolidating all build, packaging, and distribution tasks into easy-to-use scripts.

## Quick Start

### One-Command Build
```bash
# Complete setup and build
python3 setup_supermini.py

# Or make it executable and run directly
chmod +x setup_supermini.py
./setup_supermini.py
```

### Build Options
```bash
# Icons only (update app icons)
python3 setup_supermini.py --icons-only

# Build only (skip icon setup)
python3 setup_supermini.py --build-only

# Quick build (minimal validation)
python3 setup_supermini.py --quick
```

## Build System Components

### 1. Master Setup Script: `setup_supermini.py`
- **Purpose**: Orchestrates the complete build pipeline
- **Features**: Icon setup → App bundling → DMG creation
- **Usage**: Entry point for all build operations

### 2. Build System: `build.py`
- **Purpose**: Core build logic for macOS app bundle and DMG
- **Features**: 
  - Environment validation
  - Virtual environment setup
  - App bundle creation
  - DMG installer generation
  - Checksum creation

### 3. Icon Development: `icon_dev.py`
- **Purpose**: Icon management and preparation
- **Features**:
  - Auto-detects best available icon source
  - Converts SVG/PNG to ICNS format
  - Validates icon quality
  - Prepares icon for app bundling

## Build Process Details

### Step 1: Environment Validation
- Checks Python 3.9+ requirement
- Validates macOS build tools (hdiutil, iconutil)
- Verifies essential application files exist
- Reports any missing optional components

### Step 2: Icon Preparation
- Searches for icons in priority order:
  1. `assets/icons/icns/SuperMini_neural_zen.icns`
  2. `assets/icons/png/SuperMini_neural_zen_1024x1024.png`
  3. `assets/icons/svg/SuperMini_neural_zen.svg`
  4. `assets/SuperMini.icns`
  5. `assets/SuperMini_icon.svg`
- Converts source format to final ICNS as needed
- Validates icon format and size

### Step 3: Virtual Environment Setup
- Creates isolated Python environment in `build/venv/`
- Installs all requirements from `requirements.txt`
- Ensures consistent dependency versions

### Step 4: App Bundle Creation
- Creates proper macOS `.app` bundle structure
- Generates `Info.plist` with app metadata
- Creates launcher script with Ollama integration
- Copies all application files and assets
- Bundles virtual environment for portability

### Step 5: DMG Installer Creation
- Creates professional DMG with app and Applications symlink
- Includes README with installation instructions
- Compresses DMG for optimal size
- Generates SHA256 checksum for verification

## File Structure

### Build Artifacts
```
build/                          # Temporary build files
├── SuperMini.app/             # macOS app bundle
└── venv/                      # Bundled Python environment

dist/                          # Distribution files
├── SuperMini-{version}.dmg    # Main installer
├── SuperMini-{version}.dmg.sha256  # Checksum
└── README.txt                 # Installation guide
```

### Source Files (Bundled)
```
SuperMini.app/Contents/Resources/
├── supermini.py              # Main application
├── aimm.py                   # Legacy main file
├── universal_launcher.py     # Cross-platform launcher
├── activity_monitor.py       # System monitoring
├── autonomous_agent.py       # AI agent system
├── requirements.txt          # Python dependencies
├── venv/                     # Virtual environment
├── assets/                   # Icons and resources
├── prompts/                  # AI prompts
└── docs/                     # Documentation
```

## Icon Development Workflow

### Available Icon Sources
- **Neural Zen Collection**: Professional icon set with multiple variants
  - Dark mode: `SuperMini_neural_zen.icns`
  - Light mode: `SuperMini_neural_zen_light.icns`
  - Monochrome: `SuperMini_neural_zen_mono.icns`
- **Multiple formats**: SVG (source), PNG (web), ICNS (macOS)
- **Multiple sizes**: 16px to 1024px optimized for each use case

### Icon Conversion Process
1. **Source Detection**: Automatically finds best available icon
2. **Format Conversion**: SVG → PNG → ICNS using system tools
3. **Size Generation**: Creates full iconset with @2x variants
4. **Quality Validation**: Verifies final icon format and size

### Icon Tools Used
- `rsvg-convert`: SVG to PNG conversion (if available)
- `iconutil`: macOS ICNS creation
- `sips`: Image resizing (built into macOS)
- `file`: Format validation

## Dependencies

### Required (System)
- **macOS 10.15+**: Build target platform
- **Python 3.9+**: Minimum Python version
- **Xcode Command Line Tools**: Provides hdiutil, iconutil

### Optional (Enhanced Features)
- **librsvg**: Better SVG to PNG conversion
  ```bash
  brew install librsvg
  ```
- **pytest**: For running tests before build
  ```bash
  pip install pytest
  ```

### Python Packages
All Python dependencies are automatically installed from `requirements.txt`:
- PyQt6: GUI framework
- anthropic: Claude API client
- requests: HTTP client
- pandas: Data analysis
- chromadb: Vector database
- psutil: System monitoring

## Troubleshooting

### Common Issues

**Build fails with "hdiutil not found"**
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

**Icon conversion fails**
```bash
# Install SVG support
brew install librsvg

# Or manually copy an ICNS file to assets/SuperMini.icns
cp path/to/icon.icns assets/SuperMini.icns
```

**Virtual environment creation fails**
```bash
# Ensure Python 3.9+ is installed
python3 --version

# Update Python if needed
brew install python@3.11
```

**DMG creation fails**
```bash
# Check disk space (need ~500MB free)
df -h

# Clear previous builds
rm -rf build/ dist/
```

### Build Logs
All build output is displayed in real-time. For debugging:
- Check environment validation output
- Verify all required files are found
- Monitor icon conversion process
- Watch DMG creation progress

### Testing Builds
1. **DMG Installer**: Double-click generated DMG
2. **App Installation**: Drag to Applications folder
3. **App Launch**: Open from Applications or Launchpad
4. **Functionality**: Test core features work properly

## Distribution

### Release Checklist
- [ ] All tests pass
- [ ] Icons are properly generated
- [ ] App bundle launches successfully
- [ ] DMG installs correctly
- [ ] Checksum file generated
- [ ] README includes current version info

### Distribution Files
Upload these files for user download:
- `SuperMini-{version}.dmg` - Main installer
- `SuperMini-{version}.dmg.sha256` - Verification checksum
- `README.txt` - Installation instructions

### Version Management
Version is automatically detected from:
1. `supermini.py` APP_VERSION variable
2. `VERSION` file in project root
3. Fallback to "2.1.0"

Update version by modifying the APP_VERSION in your main application file.

## Advanced Usage

### Custom Build Configurations
Modify `build.py` for custom build settings:
- Change app bundle identifier
- Modify included files list
- Adjust DMG appearance
- Add custom installation scripts

### CI/CD Integration
The build system is designed for automation:
```bash
# Automated build (no user interaction)
python3 setup_supermini.py --build-only

# Check exit code for CI systems
echo $?  # 0 = success, 1 = failure
```

### Legacy Script Migration
Old scripts remain available but deprecated:
- `scripts/build_release.sh` → Use `setup_supermini.py`
- `scripts/create_macos_app.py` → Use `build.py`
- `scripts/create_dmg.py` → Use `build.py`

The new unified system provides better error handling, validation, and user experience.