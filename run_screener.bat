@echo off
title Stock Screener - Running
color 0A
cls

echo.
echo ========================================
echo   STOCK SCREENER - STARTING
echo ========================================
echo.

REM Check if setup was run
if not exist "venv" (
    echo [ERROR] Virtual environment not found
    echo Please run 'setup_screener.bat' first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check for watchlist
if not exist "watchlist.xlsx" (
    echo [WARNING] watchlist.xlsx not found
    echo The app will start but you need to create your Excel file
    echo.
)

REM Start the application
echo Starting Stock Screener...
echo.
echo Web interface: http://localhost:5000
echo Press Ctrl+C to stop
echo.

python app.py

echo.
echo Stock Screener stopped
pause