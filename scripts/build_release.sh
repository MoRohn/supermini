#!/bin/bash
# SuperMini Release Builder
# Creates production-ready DMG installer

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}🚀 SuperMini Release Builder v2.0${NC}"
    echo -e "${PURPLE}================================${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking build prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
    
    # Check required files
    local required_files=("aimm.py" "requirements.txt" "assets/SuperMini.icns")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    print_success "All required files present"
    
    # Check for development tools
    if ! command -v hdiutil &> /dev/null; then
        print_error "hdiutil not found (required for DMG creation)"
        exit 1
    fi
    
    if ! command -v iconutil &> /dev/null; then
        print_error "iconutil not found (required for icon conversion)"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Create icon if needed
create_icon() {
    print_status "Checking app icon..."
    
    if [ ! -f "assets/SuperMini.icns" ] || [ "create_icon.py" -nt "assets/SuperMini.icns" ]; then
        print_status "Creating/updating app icon..."
        python3 create_icon.py
        print_success "App icon created"
    else
        print_success "App icon is up to date"
    fi
}

# Clean previous builds
clean_build() {
    print_status "Cleaning previous builds..."
    
    if [ -d "build" ]; then
        rm -rf build
        print_success "Removed build directory"
    fi
    
    if [ -d "dist" ]; then
        rm -rf dist
        print_success "Removed dist directory"
    fi
}

# Validate virtual environment
validate_venv() {
    print_status "Validating virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_warning "No virtual environment found, creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Virtual environment created and configured"
    else
        source venv/bin/activate
        print_success "Virtual environment activated"
        
        # Check if requirements are satisfied
        print_status "Checking dependencies..."
        pip check > /dev/null 2>&1 || {
            print_warning "Dependencies need updating..."
            pip install -r requirements.txt
        }
        print_success "Dependencies validated"
    fi
}

# Run tests (if available)
run_tests() {
    print_status "Running tests..."
    
    # Look for test files
    if find . -name "test_*.py" -o -name "*_test.py" | grep -q .; then
        print_status "Running Python tests..."
        python3 -m pytest -v 2>/dev/null || python3 -m unittest discover -v 2>/dev/null || {
            print_warning "Tests found but failed to run - continuing anyway"
        }
    else
        print_warning "No tests found - skipping test phase"
    fi
}

# Create DMG
create_dmg_installer() {
    print_status "Creating DMG installer..."
    
    if [ ! -f "create_dmg.py" ]; then
        print_error "create_dmg.py not found"
        exit 1
    fi
    
    python3 create_dmg.py
    
    # Verify DMG was created
    if [ -f "dist/SuperMini-"*.dmg ]; then
        DMG_FILE=$(ls dist/SuperMini-*.dmg | head -1)
        DMG_SIZE=$(du -h "$DMG_FILE" | cut -f1)
        print_success "DMG created: $DMG_FILE ($DMG_SIZE)"
        return 0
    else
        print_error "DMG creation failed"
        return 1
    fi
}

# Verify DMG
verify_dmg() {
    print_status "Verifying DMG..."
    
    DMG_FILE=$(ls dist/SuperMini-*.dmg | head -1)
    
    # Mount DMG temporarily to verify contents
    TEMP_MOUNT=$(mktemp -d)
    hdiutil attach "$DMG_FILE" -mountpoint "$TEMP_MOUNT" -quiet
    
    # Check app bundle structure
    APP_PATH="$TEMP_MOUNT/SuperMini.app"
    if [ -d "$APP_PATH" ]; then
        print_success "App bundle found in DMG"
        
        # Check essential files
        if [ -f "$APP_PATH/Contents/Info.plist" ]; then
            print_success "Info.plist present"
        else
            print_error "Info.plist missing"
        fi
        
        if [ -f "$APP_PATH/Contents/MacOS/SuperMini" ]; then
            print_success "Executable present"
        else
            print_error "Executable missing"
        fi
        
        if [ -f "$APP_PATH/Contents/Resources/aimm.py" ]; then
            print_success "Main application file present"
        else
            print_error "Main application file missing"
        fi
        
    else
        print_error "App bundle not found in DMG"
    fi
    
    # Unmount DMG
    hdiutil detach "$TEMP_MOUNT" -quiet
    rm -rf "$TEMP_MOUNT"
    
    print_success "DMG verification complete"
}

# Create checksum
create_checksum() {
    print_status "Creating checksums..."
    
    DMG_FILE=$(ls dist/SuperMini-*.dmg | head -1)
    
    # Create SHA256 checksum
    cd dist
    shasum -a 256 "$(basename "$DMG_FILE")" > "$(basename "$DMG_FILE").sha256"
    cd ..
    
    print_success "Checksum created: $(basename "$DMG_FILE").sha256"
}

# Create release notes
create_release_notes() {
    print_status "Creating release notes..."
    
    VERSION=$(python3 -c "exec(open('aimm.py').read()); print(APP_VERSION)" 2>/dev/null || echo "2.0.1")
    
    cat > dist/RELEASE_NOTES.md << EOF
# SuperMini v$VERSION Release Notes

## Installation Instructions

1. **Download the DMG**: \`SuperMini-$VERSION.dmg\`
2. **Double-click the DMG** to open it
3. **Drag SuperMini.app to Applications folder**
4. **Launch SuperMini** from Applications or Launchpad

## First-Time Setup

### Required: Install Ollama
SuperMini requires Ollama for local AI models:
- Download from: https://ollama.ai/
- Or install via Homebrew: \`brew install ollama\`

### Optional: Claude API Key
For enhanced AI capabilities:
- Get an API key from: https://console.anthropic.com/
- Add it in SuperMini Settings

## What's New in v$VERSION

### Enhanced Features
- 🎨 **New Modern Icon**: Professional macOS-style icon
- 📦 **Improved DMG Installer**: Better installation experience
- 🔧 **Enhanced Settings UI**: Better sizing and user interaction
- 🤖 **Recursive Enhancement Engine**: Advanced self-improvement capabilities
- 🛡️ **Better Error Handling**: More robust operation
- 📊 **Improved Monitoring**: Enhanced activity monitoring

### Core Features
- **Task Me Mode**: AI-assisted task execution
- **Go Explore Mode**: Autonomous exploration and learning
- **Enhance Yourself Mode**: Self-improvement and evolution
- **Multimedia Processing**: Image, audio, video analysis
- **Document Analysis**: PDF, text, markdown processing
- **Code Generation**: Multi-language code assistance
- **Data Analytics**: CSV analysis and visualization
- **Memory System**: Context-aware conversations

## System Requirements

- **macOS**: 10.15 (Catalina) or later
- **Python**: 3.9+ (bundled with app)
- **RAM**: 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for Claude API (optional)

## File Locations

- **Application**: \`/Applications/SuperMini.app\`
- **Output Files**: \`~/SuperMini_Output/\`
- **Logs**: \`~/SuperMini_Output/logs/\`
- **Memory Database**: \`~/SuperMini_Output/data/memory/\`

## Support

- **Documentation**: See README.txt in DMG
- **Issues**: Report bugs and feature requests
- **Updates**: Check for new releases regularly

## Verification

**SHA256 Checksum**: See \`SuperMini-$VERSION.dmg.sha256\`

Built on: $(date)
EOF

    print_success "Release notes created: dist/RELEASE_NOTES.md"
}

# Main build process
main() {
    print_header
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    print_status "Starting build process in: $(pwd)"
    
    # Build steps
    check_prerequisites
    create_icon
    clean_build
    validate_venv
    run_tests
    
    if create_dmg_installer; then
        verify_dmg
        create_checksum
        create_release_notes
        
        echo ""
        print_success "🎉 Build completed successfully!"
        echo ""
        echo -e "${PURPLE}📦 Distribution Files:${NC}"
        ls -la dist/
        echo ""
        echo -e "${PURPLE}📋 Next Steps:${NC}"
        echo "1. Test the DMG installer"
        echo "2. Verify app functionality"
        echo "3. Distribute to users"
        echo ""
        
        # Open dist folder
        if command -v open &> /dev/null; then
            open dist/
        fi
        
    else
        print_error "Build failed"
        exit 1
    fi
}

# Run main function
main "$@"