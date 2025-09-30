@echo off
REM Change to project root directory
cd /d "%~dp0.."

echo ============================================
echo French Novel Processor - Starting...
echo ============================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Change to web_interface directory
cd web_interface

REM Start Flask application
echo Starting web interface...
echo Open your browser to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py

REM Return to original directory
cd ..

pause
