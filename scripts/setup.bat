@echo off
REM Change to project root directory
cd /d "%~dp0.."

echo ============================================
echo French Novel Processor - Setup
echo ============================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies...
echo This may take a few minutes...
echo.
pip install -r requirements.txt

REM Check if Tesseract is installed
echo.
echo ============================================
echo Checking for Tesseract OCR...
echo ============================================
tesseract --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Tesseract OCR is not installed!
    echo.
    echo Tesseract is required for PDF text extraction.
    echo Please download and install from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo After installation, add Tesseract to your PATH
    echo Default location: C:\Program Files\Tesseract-OCR
    echo.
) else (
    echo Tesseract OCR detected:
    tesseract --version
)

REM Check if Poppler is available (for pdf2image)
echo.
echo ============================================
echo Checking for Poppler (PDF conversion)...
echo ============================================
where pdftoppm > nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Poppler is not installed!
    echo.
    echo Poppler is required for PDF to image conversion.
    echo Please download from:
    echo https://github.com/oschwartz10612/poppler-windows/releases
    echo.
    echo Extract and add the 'bin' folder to your PATH
    echo.
) else (
    echo Poppler detected.
)

REM Create necessary directories
echo.
echo Creating directories...
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
if not exist "web_interface\uploads" mkdir web_interface\uploads
if not exist "web_interface\output" mkdir web_interface\output

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. If you saw warnings above, install Tesseract and Poppler
echo 2. Get your OpenAI API key from https://platform.openai.com
echo 3. Run run_application.bat to start the tool
echo.
pause
