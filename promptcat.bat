@echo off
title promptcat
promptcat -i
if %errorlevel% neq 0 (
    python -m promptcat.cli -i
)
pause
