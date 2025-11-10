@echo off
REM MammoViewer - Windows Setup Script
REM Automates the installation and configuration process

echo ================================================
echo MammoViewer - Setup (Windows)
echo ================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo [OK] Python is installed
echo.

REM Check pip
echo Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)
echo [OK] pip is installed
echo.

REM Create virtual environment
echo Creating Python virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
    choice /M "Remove and recreate"
    if errorlevel 2 goto skip_venv
    rmdir /s /q venv
)
python -m venv venv
echo [OK] Virtual environment created
:skip_venv
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing Python dependencies...
cd backend
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
cd ..
echo.

REM Create directories
echo Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
if not exist "slicer_scripts" mkdir slicer_scripts
echo [OK] Directories created
echo.

REM Create .env file
echo Setting up environment configuration...
if not exist ".env" (
    copy .env.example .env
    echo [OK] Created .env file from template
    echo [WARNING] Please edit .env and update SLICER_PATH
) else (
    echo [WARNING] .env file already exists
)
echo.

REM Search for 3D Slicer
echo Searching for 3D Slicer installation...
set SLICER_FOUND=0

REM Common installation paths
set "SLICER_PATH_1=C:\Program Files\Slicer 5.4.0\Slicer.exe"
set "SLICER_PATH_2=C:\Program Files\Slicer 5.2.0\Slicer.exe"
set "SLICER_PATH_3=C:\Program Files (x86)\Slicer 5.4.0\Slicer.exe"

if exist "%SLICER_PATH_1%" (
    set "SLICER_PATH=%SLICER_PATH_1%"
    set SLICER_FOUND=1
) else if exist "%SLICER_PATH_2%" (
    set "SLICER_PATH=%SLICER_PATH_2%"
    set SLICER_FOUND=1
) else if exist "%SLICER_PATH_3%" (
    set "SLICER_PATH=%SLICER_PATH_3%"
    set SLICER_FOUND=1
)

if %SLICER_FOUND%==1 (
    echo [OK] Found 3D Slicer at: %SLICER_PATH%
    echo Please update backend\config.py with this path if needed
) else (
    echo [WARNING] 3D Slicer not found automatically
    echo Please install 3D Slicer from: https://download.slicer.org/
    echo Then update SLICER_PATH in backend\config.py
)
echo.

REM Test configuration
echo Testing configuration...
cd backend
python config.py
cd ..
echo.

REM Final instructions
echo ================================================
echo [SUCCESS] Setup Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. If 3D Slicer path wasn't auto-detected:
echo    Edit backend\config.py and set SLICER_PATH
echo.
echo 2. Start the application:
echo    cd backend
echo    python app.py
echo.
echo 3. Open your browser:
echo    http://localhost:5000
echo.
echo 4. For detailed instructions, see:
echo    - QUICKSTART.md
echo    - README.md
echo.
echo ================================================
echo.

REM Ask to start server
choice /M "Start the server now"
if errorlevel 2 goto end

echo.
echo Starting server...
echo Press Ctrl+C to stop
echo.
cd backend
python app.py

:end
pause