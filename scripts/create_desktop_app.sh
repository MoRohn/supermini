#!/bin/bash
# Create a proper desktop app to launch the DMG

echo "🖥️ Creating Desktop App for SuperMini DMG..."

# Remove old shortcut
rm -f ~/Desktop/SuperMini-Installer.dmg

# Create app bundle for desktop
APP_NAME="Install SuperMini"
DESKTOP_APP="$HOME/Desktop/$APP_NAME.app"

# Remove existing
rm -rf "$DESKTOP_APP"

# Create app structure
mkdir -p "$DESKTOP_APP/Contents/MacOS"
mkdir -p "$DESKTOP_APP/Contents/Resources"

# Create Info.plist
cat > "$DESKTOP_APP/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Install SuperMini</string>
    <key>CFBundleDisplayName</key>
    <string>Install SuperMini</string>
    <key>CFBundleIdentifier</key>
    <string>com.supermini.installer</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>install_aimm</string>
    <key>CFBundleIconFile</key>
    <string>SuperMini.icns</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Copy icon
cp assets/SuperMini.icns "$DESKTOP_APP/Contents/Resources/"

# Create executable
cat > "$DESKTOP_APP/Contents/MacOS/install_aimm" << EOF
#!/bin/bash
# SuperMini Installer Launcher

DMG_PATH="$(dirname "\$(dirname "\$(dirname "\$0")")")/SuperMini/dist/SuperMini-2.0.1.dmg"

if [ -f "\$DMG_PATH" ]; then
    open "\$DMG_PATH"
else
    osascript -e 'display dialog "SuperMini installer not found. Please download SuperMini-2.0.1.dmg" buttons {"OK"} default button "OK"'
fi
EOF

# Make executable
chmod +x "$DESKTOP_APP/Contents/MacOS/install_aimm"

echo "✅ Desktop app created: $DESKTOP_APP"

# Also create a simple DMG opener script
cat > ~/Desktop/Open\ SuperMini\ Installer.command << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
DMG_PATH="../SuperMini/dist/SuperMini-2.0.1.dmg"
if [ -f "\$DMG_PATH" ]; then
    open "\$DMG_PATH"
else
    echo "❌ SuperMini installer not found at: \$DMG_PATH"
    echo "📁 Current directory: \$(pwd)"
    echo "🔍 Looking for DMG files..."
    find .. -name "*.dmg" -type f 2>/dev/null | head -5
    read -p "Press any key to continue..."
fi
EOF

chmod +x ~/Desktop/Open\ SuperMini\ Installer.command

echo "✅ Command script created: ~/Desktop/Open SuperMini Installer.command"
echo "🎉 Desktop shortcuts ready!"
echo ""
echo "📋 Test Options:"
echo "1. Double-click 'Install SuperMini.app' on desktop"
echo "2. Double-click 'Open SuperMini Installer.command' on desktop"
echo "3. Or directly: open dist/SuperMini-2.0.1.dmg"