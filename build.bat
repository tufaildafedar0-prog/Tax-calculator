@echo off
REM Build script for Tax Calculator (Windows Batch)
REM Creates a standalone Windows executable using PyInstaller
REM Usage: build.bat

setlocal enabledelayedexpansion

echo.
echo ================================
echo Tax Calculator - Build Script
echo ================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "VENV_PATH=%SCRIPT_DIR%.venv"

REM Check if virtual environment exists
if not exist "%VENV_PATH%" (
    echo ERROR: Virtual environment not found at %VENV_PATH%
    echo Please create a virtual environment first:
    echo   python -m venv .venv
    pause
    exit /b 1
)

REM Get Python executable path
set "PYTHON_EXE=%VENV_PATH%\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python executable not found at %PYTHON_EXE%
    pause
    exit /b 1
)

REM Clean previous builds if /clean argument provided
if "%1"=="/clean" (
    echo Cleaning previous builds...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    echo Clean complete.
)

REM Build configuration
set "SPEC_FILE=%SCRIPT_DIR%build.spec"
echo Building with spec file: %SPEC_FILE%
echo.

REM Run PyInstaller
echo Running PyInstaller...
"%PYTHON_EXE%" -m PyInstaller --distpath "%SCRIPT_DIR%dist" --workpath "%SCRIPT_DIR%build" "%SPEC_FILE%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ================================
    echo BUILD SUCCESSFUL!
    echo ================================
    echo.
    echo Executable location:
    echo   %SCRIPT_DIR%dist\tax_calculator.exe
    echo.
    echo To run the application:
    echo   dist\tax_calculator.exe
    echo.
    echo Distribution notes:
    echo   - The executable is standalone and doesn't require Python
    echo   - You can copy the entire dist/ folder to other machines
    echo   - Each machine needs Windows to run the .exe
) else (
    echo.
    echo BUILD FAILED!
    echo Exit code: %ERRORLEVEL%
    pause
    exit /b 1
)
