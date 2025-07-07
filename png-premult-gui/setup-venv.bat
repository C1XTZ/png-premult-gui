@echo off
echo Setting up Python 3.12.x virtual environment...

if exist ".venv312" (
    echo Virtual environment already exists at .venv312
    pause
    exit /b 1
)

echo Searching for Python 3.12.x...
set PYTHON_CMD=

for %%p in (python3.12 py -3.12 python) do (
    %%p --version >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2" %%i in ('%%p --version 2^>^&1') do (
            echo %%i | findstr /r "^3\.12\." >nul
            if !errorlevel! equ 0 (
                set PYTHON_CMD=%%p
                set PYTHON_VERSION=%%i
                goto :found
            )
        )
    )
)

py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('py -3.12 --version 2^>^&1') do (
        echo %%i | findstr /r "^3\.12\." >nul
        if !errorlevel! equ 0 (
            set PYTHON_CMD=py -3.12
            set PYTHON_VERSION=%%i
            goto :found
        )
    )
)

py -0 2>nul | findstr "3.12" >nul
if %errorlevel% equ 0 (
    echo Found Python 3.12 via Python Launcher
    set PYTHON_CMD=py -3.12
    for /f "tokens=2" %%i in ('py -3.12 --version 2^>^&1') do set PYTHON_VERSION=%%i
    goto :found
)

echo Error: Python 3.12.x not found!
echo.
echo Please install Python 3.12.x or ensure it's in your PATH
echo.
pause
exit /b 1

:found
setlocal enabledelayedexpansion
echo Found Python version: %PYTHON_VERSION%
echo Using command: %PYTHON_CMD%
echo.

echo Creating virtual environment at .venv312...
%PYTHON_CMD% -m venv .venv312

if not exist ".venv312\Scripts\activate.bat" (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

echo Activating virtual environment...
call .venv312\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required packages...
echo Installing numpy...
pip install numpy

echo Installing pillow...
pip install pillow

echo Installing nuitka...
pip install nuitka

echo.
echo Setup complete!
echo Virtual environment created at: .venv312
echo Python version used: %PYTHON_VERSION%
echo Installed packages:
pip list
echo.
echo You can now run png-premult-gui.pyw or build-exe.bat to build an executable.
pause