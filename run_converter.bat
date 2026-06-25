@echo off
:: VRoid Hair Slot Converter - one-click launcher
:: Double-click this file to open the GUI converter.

title VRoid Hair Slot Converter
cd /d "%~dp0"

:: Try launching the GUI
python vroid_hair_converter_gui.py
if errorlevel 1 (
    echo.
    echo Python not found or an error occurred.
    echo Make sure Python 3 is installed and added to PATH.
    pause
)
