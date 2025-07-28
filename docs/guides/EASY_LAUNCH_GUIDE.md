# 🚀 SuperMini - Easy Launch Guide for Non-Technical Users

Welcome! This guide shows you the **easiest** ways to start SuperMini on your Mac, no technical knowledge required.

## 📱 Method 1: Double-Click App (Recommended)

**The simplest way - just like any other Mac app:**

1. **Find the SuperMini.app file** in your SuperMini folder
2. **Double-click it** - that's it! SuperMini will start.
3. **Optional**: Drag SuperMini.app to your Applications folder or Dock for easy access

*If you don't see SuperMini.app, run the command: `python3 create_mac_app.py`*

## 🖥️ Method 2: GUI Launcher

**User-friendly launcher with automatic setup:**

1. **Find the file** called `SuperMini_Launcher.py`
2. **Double-click it** to open
3. The launcher will:
   - ✅ Check if everything is set up correctly
   - 🔧 Fix any issues automatically
   - 🚀 Launch SuperMini when ready

## 💻 Method 3: Terminal Command File

**Simple terminal launcher:**

1. **Find the file** called `launch_supermini.command`
2. **Double-click it** - a terminal window will open and start SuperMini
3. Follow any on-screen instructions

## ⚡ Quick Setup (First Time Only)

If SuperMini doesn't start immediately, it might need initial setup:

### Option A: Automatic Setup
1. Double-click `SuperMini_Launcher.py`
2. Click "Fix Issues" button
3. Wait for setup to complete
4. Click "Launch SuperMini"

### Option B: Manual Setup
1. Open Terminal (press Cmd+Space, type "Terminal", press Enter)
2. Navigate to your SuperMini folder
3. Run: `python3 setup_supermini.py`
4. Wait for completion, then use any launch method above

## 🎯 What Each Launcher Does

| File | What it does | Best for |
|------|-------------|----------|
| `SuperMini.app` | Native Mac app - just double-click | Everyone - most user-friendly |
| `SuperMini_Launcher.py` | GUI with dependency checking | First-time setup or troubleshooting |
| `launch_supermini.command` | Simple terminal launcher | Users comfortable with terminal |

## 🆘 Troubleshooting

### "Python not found" error
- Install Python 3.9+ from [python.org](https://www.python.org/downloads/)
- Restart your Mac after installation

### "Permission denied" error
1. Open Terminal
2. Navigate to SuperMini folder
3. Run: `chmod +x *.py *.command`

### Dependencies missing
- Use the GUI launcher (`SuperMini_Launcher.py`) and click "Fix Issues"
- Or run `python3 setup_supermini.py` in Terminal

### Still having issues?
- Try the GUI launcher first - it can fix most problems automatically
- Check that you're running the files from the SuperMini folder
- Make sure Python 3.9+ is installed

## 🎉 Success!

Once SuperMini starts, you'll see the main application window. You can now:
- Select task types from the dropdown
- Enter your requests in the text area  
- Click "Process Task" to get AI assistance
- Use Claude API or local Ollama models

**Tip**: For the easiest experience, drag `SuperMini.app` to your Applications folder and launch it from Launchpad like any other Mac app!