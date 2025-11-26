# Build script for Tax Calculator
# Creates a standalone Windows executable using PyInstaller
# 
# Usage: .\build.ps1

param(
    [switch]$Clean
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Tax Calculator - Build Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Check if virtual environment exists
$venvPath = Join-Path $scriptDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "ERROR: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: Activation script not found" -ForegroundColor Red
    exit 1
}
& $activateScript

# Get Python executable path
$pythonExe = Join-Path $venvPath "Scripts\python.exe"

# Clean previous builds if requested
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    Write-Host "Clean complete." -ForegroundColor Green
}

# Build configuration
$specFile = Join-Path $scriptDir "build.spec"
Write-Host "Building with spec file: $specFile" -ForegroundColor Green
Write-Host ""

# Run PyInstaller
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
& $pythonExe -m PyInstaller --distpath (Join-Path $scriptDir "dist") --workpath (Join-Path $scriptDir "build") --specpath $scriptDir $specFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Yellow
    Write-Host "  $(Join-Path $scriptDir "dist\tax_calculator.exe")" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Yellow
    Write-Host "  .\dist\tax_calculator.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Distribution notes:" -ForegroundColor Yellow
    Write-Host "  - The executable in dist/ is standalone and doesn't require Python" -ForegroundColor Cyan
    Write-Host "  - You can copy the entire dist/ folder to other machines" -ForegroundColor Cyan
    Write-Host "  - Each machine needs Windows to run the .exe" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}
