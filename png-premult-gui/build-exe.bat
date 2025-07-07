@echo off
set SCRIPT_NAME=png-premult-gui
set EXE_NAME=%SCRIPT_NAME%.exe

echo Activating virtual environment...
call .\.venv312\Scripts\activate.bat

echo Cleaning previous build...
IF EXIST "%SCRIPT_NAME%.build" RMDIR /S /Q "%SCRIPT_NAME%.build"
IF EXIST "%SCRIPT_NAME%.dist" RMDIR /S /Q "%SCRIPT_NAME%.dist"
IF EXIST "%SCRIPT_NAME%.onefile-build" RMDIR /S /Q "%SCRIPT_NAME%.onefile-build"
IF EXIST "%EXE_NAME%" DEL /Q "%EXE_NAME%"

echo Building %EXE_NAME% with Nuitka...
call nuitka ^
    "%SCRIPT_NAME%.pyw" ^
    --onefile ^
    --windows-icon-from-ico=icon.ico ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --include-data-file=icon.ico=icon.ico

echo Nuitka finished with errorlevel %ERRORLEVEL%.

echo Cleaning up build folders...
IF EXIST "%SCRIPT_NAME%.build" RMDIR /S /Q "%SCRIPT_NAME%.build"
IF EXIST "%SCRIPT_NAME%.dist" RMDIR /S /Q "%SCRIPT_NAME%.dist"
IF EXIST "%SCRIPT_NAME%.onefile-build" RMDIR /S /Q "%SCRIPT_NAME%.onefile-build"

echo.
echo Build complete.
echo Note: Windows Defender might flag and quarantine the built executable.
echo.
pause