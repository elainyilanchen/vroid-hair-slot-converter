@echo off
:: VRoid Hair Slot Converter - one-click launcher
:: Double-click this file to open the GUI converter.

title VRoid Hair Slot Converter
cd /d "%~dp0"

:: Launch with pythonw (windowed Python): no console window pops up and
:: harmless startup messages (e.g. "libpng warning: iCCP ...") aren't shown.
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw vroid_hair_converter_gui.py
    goto :eof
)

:: Fallback: pythonw not found, use console python so errors stay visible.
python vroid_hair_converter_gui.py
if errorlevel 1 (
    echo.
    echo Python not found or an error occurred.
    echo Make sure Python 3 is installed and added to PATH.
    pause
)
