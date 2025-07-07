@echo off
set SCRIPT_NAME=png-premult-gui
set EXE_NAME=%SCRIPT_NAME%.exe

echo Cleaning previous build...
pyinstaller --clean "%SCRIPT_NAME%.pyw"

echo Building %EXE_NAME%...
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico:." "%SCRIPT_NAME%.pyw"

echo Moving executable and cleaning up...
IF EXIST "dist\%EXE_NAME%" (
    MOVE "dist\%EXE_NAME%" "%EXE_NAME%"
    ECHO %EXE_NAME% moved to current directory.
) ELSE (
    ECHO Error: %EXE_NAME% not found in dist.
)

RMDIR /S /Q build
RMDIR /S /Q dist
DEL /Q "%SCRIPT_NAME%.spec"

echo Build process complete.
echo.
echo Note: Windows Defender might briefly scan, flag or lock the newly built executable.
echo This is normal behavior for new or unsigned applications.
pause