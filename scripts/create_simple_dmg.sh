#!/bin/bash
# Simple DMG Creator for SuperMini

echo "🚀 Creating Simple SuperMini DMG..."

# Clean up
rm -f dist/SuperMini-*.dmg
rm -rf /tmp/aimm_dmg

# Create temporary directory
mkdir -p /tmp/aimm_dmg

# Copy app bundle (without the large venv)
echo "📦 Copying app bundle..."
cp -R build/SuperMini.app /tmp/supermini_dmg/

# Remove the large venv from the copy and create a setup script instead
echo "🔧 Optimizing bundle size..."
rm -rf /tmp/supermini_dmg/SuperMini.app/Contents/Resources/venv

# Create setup script
cat > /tmp/supermini_dmg/SuperMini.app/Contents/Resources/setup_venv.sh << 'EOF'
#!/bin/bash
# SuperMini Virtual Environment Setup
cd "$(dirname "$0")"
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Environment setup complete!"
EOF

chmod +x /tmp/supermini_dmg/SuperMini.app/Contents/Resources/setup_venv.sh

# Create Applications symlink
ln -s /Applications /tmp/supermini_dmg/Applications

# Create README
cat > /tmp/supermini_dmg/README.txt << 'EOF'
SuperMini - AI Multimedia Management v2.0.1

INSTALLATION:
1. Drag SuperMini.app to Applications folder
2. Open Terminal and run:
   cd /Applications/SuperMini.app/Contents/Resources
   ./setup_venv.sh
3. Launch SuperMini from Applications

REQUIREMENTS:
- Python 3.9+
- Ollama (https://ollama.ai)

FIRST TIME SETUP:
- Install Ollama: brew install ollama
- Optional: Add Claude API key in settings

OUTPUT: ~/SuperMini_Output/
EOF

# Create the DMG
echo "💿 Creating DMG..."
hdiutil create -srcfolder /tmp/aimm_dmg -volname "SuperMini 2.0.1" -fs HFS+ -format UDZO -imagekey zlib-level=9 dist/SuperMini-2.0.1.dmg

# Clean up
rm -rf /tmp/aimm_dmg

# Check result
if [ -f "dist/SuperMini-2.0.1.dmg" ]; then
    echo "✅ DMG created: dist/SuperMini-2.0.1.dmg"
    ls -lh dist/SuperMini-2.0.1.dmg
    
    # Set proper file type
    if command -v SetFile &> /dev/null; then
        SetFile -t dmg -c ddsk dist/SuperMini-2.0.1.dmg
        echo "✅ Set proper file type"
    fi
    
    # Test the DMG
    echo "🧪 Testing DMG..."
    hdiutil verify dist/SuperMini-2.0.1.dmg && echo "✅ DMG verified"
    
    # Create desktop shortcut
    ln -sf "$(pwd)/dist/SuperMini-2.0.1.dmg" "$HOME/Desktop/SuperMini-Installer.dmg"
    echo "🖥️ Desktop shortcut created"
    
    echo "🎉 DMG creation complete!"
    echo "Double-click ~/Desktop/SuperMini-Installer.dmg to test"
    
else
    echo "❌ DMG creation failed"
fi