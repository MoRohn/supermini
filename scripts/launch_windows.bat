@echo off
REM SuperMini Windows Launcher
REM Cross-platform launcher for Windows systems

title SuperMini - Autonomous Mac Mini AI Agent

echo ================================================================
echo 🪟 SuperMini - Autonomous Mac Mini AI Agent (Windows)
echo ================================================================

REM Change to script directory
cd /d "%~dp0"

REM Check if universal launcher exists
if exist "universal_launcher.py" (
    echo 🚀 Using Universal SuperMini Launcher
    python universal_launcher.py
    goto :end
)

REM Fallback method
echo ⚠️  Universal launcher not found, using fallback method

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.9+ from python.org
    echo    Or install from Microsoft Store
    pause
    exit /b 1
)

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo 🐍 Activating Python virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found, using system Python
)

REM Check for requirements.txt and install if needed
if exist "requirements.txt" (
    echo 📦 Installing/updating Python dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

REM Create output directory
if not exist "%USERPROFILE%\SuperMini_Output" (
    echo 📁 Creating output directory...
    mkdir "%USERPROFILE%\SuperMini_Output\data"
    mkdir "%USERPROFILE%\SuperMini_Output\logs"
    mkdir "%USERPROFILE%\SuperMini_Output\data\memory"
    mkdir "%USERPROFILE%\SuperMini_Output\data\collaboration"
    mkdir "%USERPROFILE%\SuperMini_Output\autonomous"
)

REM Check for Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama not found
    echo    Download from: https://ollama.ai/download/windows
    echo    SuperMini will work with limited AI functionality
) else (
    echo ✅ Ollama found
    
    REM Start Ollama service if not running
    tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
    if errorlevel 1 (
        echo ⚡ Starting Ollama service...
        start /B ollama serve
        timeout /t 3 /nobreak >nul
    ) else (
        echo ✅ Ollama service already running
    )
)

REM Check if main script exists
if not exist "aimm.py" (
    echo ❌ aimm.py not found in current directory
    echo Current directory: %CD%
    dir
    pause
    exit /b 1
)

REM Launch SuperMini
echo ================================================================
echo 🚀 Launching SuperMini...
echo ================================================================

python aimm.py

:end
if errorlevel 1 (
    echo ❌ SuperMini exited with error code: %errorlevel%
    pause
)

echo 👋 SuperMini session ended
pause