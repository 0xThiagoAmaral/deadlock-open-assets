@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title Umblock Deadlock Extractor v2.0

REM Always use the folder where this .bat file lives
cd /d "%~dp0"
set "ROOT=%CD%"

reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

echo.
echo  [*] Umblock Deadlock Extractor v2.0  (live progress + ETA)
echo  [*] Root: %ROOT%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found in PATH.
    echo  Install Python 3.10+ from https://python.org
    echo  Make sure "Add to PATH" is checked during install.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [+] %PYVER%

echo  [*] Checking dependencies...
python -m pip install vpk openai -q --disable-pip-version-check 2>nul
if errorlevel 1 (
    echo  [WARN] pip install failed - TUI will retry on demand.
) else (
    echo  [+] Dependencies OK
)

if not exist "%ROOT%\tools\extractor_tui.py" (
    echo.
    echo  [ERROR] extractor_tui.py not found at:
    echo          %ROOT%\tools\extractor_tui.py
    echo.
    echo  Make sure UmblockExtractor.bat stays in the umblock project root.
    echo.
    pause
    exit /b 1
)

echo  [*] Launching interactive extractor...
echo.
python "%ROOT%\tools\extractor_tui.py"
set EXITCODE=%ERRORLEVEL%

if not %EXITCODE%==0 (
    echo.
    echo  [ERROR] Extractor exited with code %EXITCODE%
    pause
    exit /b %EXITCODE%
)

endlocal
exit /b 0
