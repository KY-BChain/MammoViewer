@echo off
REM MammoViewer Setup Script for Windows
REM This script automates the installation and configuration of MammoViewer

setlocal enabledelayedexpansion

echo ============================================
echo   MammoViewer - DICOM to STL Converter
echo   Setup Script v1.0
echo ============================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Check Python version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo [ERROR] Python version too old
    echo Python 3.8 or higher is required
    pause
    exit /b 1
)

if %MAJOR% EQU 3 if %MINOR% LSS 8 (
    echo [ERROR] Python version too old
    echo Python 3.8 or higher is required
    pause
    exit /b 1
)

REM Check pip
echo.
echo Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed
    echo Installing pip...
    python -m ensurepip --upgrade
)
echo [OK] pip is installed

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    set /p RECREATE="Do you want to recreate it? (y/n): "
    if /i "!RECREATE!"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Virtual environment recreated
    )
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded

REM Install dependencies
echo.
echo Installing Python dependencies...
echo This may take several minutes...
python -m pip install -r backend\requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully

REM Create necessary directories
echo.
echo Creating project directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "slicer_scripts" mkdir slicer_scripts
echo [OK] Directories created

REM Check for 3D Slicer
echo.
echo Checking for 3D Slicer installation...

set SLICER_FOUND=0
set SLICER_PATH=

REM Common Slicer locations on Windows
set PATHS[0]="C:\Program Files\Slicer 5.4.0\Slicer.exe"
set PATHS[1]="C:\Program Files\Slicer 5.2.2\Slicer.exe"
set PATHS[2]="C:\Program Files (x86)\Slicer 5.4.0\Slicer.exe"
set PATHS[3]="C:\Slicer\Slicer.exe"

for /l %%i in (0,1,3) do (
    if exist !PATHS[%%i]! (
        set SLICER_PATH=!PATHS[%%i]!
        set SLICER_FOUND=1
        goto :slicer_found
    )
)

:slicer_found
if %SLICER_FOUND% equ 1 (
    echo [OK] 3D Slicer found at: %SLICER_PATH%
) else (
    echo [WARNING] 3D Slicer not found in common locations
    echo You will need to install 3D Slicer and set SLICER_PATH in .env
    echo Download from: https://www.slicer.org/
)

REM Create .env file if it doesn't exist
echo.
echo Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env >nul

    if %SLICER_FOUND% equ 1 (
        REM Update .env with Slicer path (escape backslashes)
        set ESCAPED_PATH=%SLICER_PATH:\=\\%
        powershell -Command "(gc .env) -replace '#SLICER_PATH=C:\\Program Files\\Slicer 5.4.0\\Slicer.exe', 'SLICER_PATH=%ESCAPED_PATH%' | Set-Content .env"
    )

    echo [OK] .env file created
    echo Please review and customize .env as needed
) else (
    echo [WARNING] .env file already exists, skipping
)

REM Test installation
echo.
echo Testing installation...
python test_installation.py
if %errorlevel% neq 0 (
    echo [WARNING] Installation test had some warnings
)

REM Summary
echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next steps:
echo.
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.

if %SLICER_FOUND% equ 0 (
    echo 2. Install 3D Slicer from https://www.slicer.org/
    echo.
    echo 3. Set SLICER_PATH in .env file:
    echo    notepad .env
    echo.
    echo 4. Start the application:
) else (
    echo 2. Start the application:
)
echo    python backend\app.py
echo.
echo 3. Open your browser:
echo    http://localhost:5000
echo.
echo For more information, see README.md and QUICKSTART.md
echo.
echo ============================================
echo.

pause
