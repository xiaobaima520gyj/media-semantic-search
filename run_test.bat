@echo off
echo Starting Media Search API Test Client...
echo.

cd /d "%~dp0"

"python.exe" test_api.py

pause
