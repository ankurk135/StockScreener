@echo off
title Stock Screener - Setup
color 0B
cls

echo.
echo ========================================
echo   STOCK SCREENER - INITIAL SETUP
echo ========================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment and install packages
echo [3/5] Installing required packages...
echo This may take a few minutes...
call venv\Scripts\activate
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install packages
    pause
    exit /b 1
)
echo [OK] All packages installed
echo.

REM Create data directories
echo [4/5] Creating data directories...
if not exist "data" mkdir data
if not exist "data\cache" mkdir data\cache
if not exist "data\processed" mkdir data\processed
if not exist "data\exports" mkdir data\exports
if not exist "logs" mkdir logs
echo [OK] Directories created
echo.

REM Check for watchlist file
echo [5/5] Checking for watchlist.xlsx...
if not exist "watchlist.xlsx" (
    echo [WARNING] watchlist.xlsx not found
    echo.
    echo Please create an Excel file named 'watchlist.xlsx' with:
    echo - Sheet name: Master
    echo - Columns: Stock_Name, YF_Ticker, TV_Ticker, Sector, Industry
    echo.
    echo Example:
    echo   Stock_Name          YF_Ticker       TV_Ticker        Sector    Industry
    echo   Reliance Industries RELIANCE.NS     NSE:RELIANCE     Oil       Refining
    echo   TCS                 TCS.NS          NSE:TCS          IT        Software
    echo.
) else (
    echo [OK] watchlist.xlsx found
)
echo.

echo ========================================
echo   SETUP COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Make sure watchlist.xlsx exists with your stock data
echo 2. Run 'run_screener.bat' to start the application
echo.
pause