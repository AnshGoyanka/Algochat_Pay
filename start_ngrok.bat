@echo off
REM AlgoChat Pay - Quick ngrok Setup (Windows)
REM Double-click this file to start ngrok tunnel

echo ========================================
echo   AlgoChat Pay - Starting ngrok
echo ========================================
echo.

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0setup_ngrok.ps1"

pause
