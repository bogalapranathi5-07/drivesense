@echo off
title DriveSense: Intelligent Driver Vigilance Monitoring System
color 0b

echo ===============================================================================
echo        DRIVESENSE: INTELLIGENT DRIVER VIGILANCE MONITORING SYSTEM
echo               Computer Vision & ESP32 Telemetry Dashboard
echo ===============================================================================
echo.

:: 1. Check for Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo During installation, be sure to check "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

:: 2. Check if dependencies are installed
echo [INFO] Verifying package dependencies...
python -c "import cv2, mediapipe, serial, PIL" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [NOTICE] Installing missing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Package installation failed. Please check your internet connection.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully!
) else (
    echo [OK] All dependencies are ready.
)

echo.
echo [INFO] Launching DriveSense Dashboard...
echo ===============================================================================
echo.

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] The application exited with an error code: %ERRORLEVEL%
    echo Please review the messages above to diagnose the issue.
    pause
)
