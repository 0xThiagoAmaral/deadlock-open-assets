@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title Deadlock Asset Extractor v2.0

cd /d "%~dp0"
set "ROOT=%CD%"

reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

echo.
echo  [*] Deadlock Open Assets Extractor v2.0
echo  [*] Root: %ROOT%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found in PATH.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [+] %PYVER%

echo  [*] Checking dependencies...
python -m pip install vpk -q --disable-pip-version-check 2>nul

if not exist "%ROOT%\tools\extractor_tui.py" (
    echo  [ERROR] tools/extractor_tui.py not found.
    pause
    exit /b 1
)

echo  [*] Launching interactive extractor...
python "%ROOT%\tools\extractor_tui.py"
set EXITCODE=%ERRORLEVEL%
if not %EXITCODE%==0 pause
exit /b %EXITCODE%
