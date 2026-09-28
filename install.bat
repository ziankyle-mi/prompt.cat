@echo off
title promptcat installer
echo ==============================================
echo        Installing promptcat CLI globally
echo ==============================================
echo.
python -m pip install -e .
if %errorlevel% equ 0 (
    echo.
    echo ==============================================
    echo [OK] promptcat successfully installed!
    echo You can now open ANY terminal and type:
    echo.
    echo    promptcat "your idea here"
    echo    promptcat -i
    echo.
    echo ==============================================
) else (
    echo.
    echo [ERROR] Installation failed.
    echo Please make sure Python 3.11+ is installed and added to PATH.
)
echo.
pause
