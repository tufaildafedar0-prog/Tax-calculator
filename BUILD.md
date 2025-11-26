# Building Tax Calculator

This document explains how to build and distribute the Tax Calculator application.

## Prerequisites

- Python 3.13+ (already installed in `.venv`)
- PyInstaller (automatically installed via `requirements.txt`)

## Development Build

To run the application in development mode:

```bash
cd "Tax calc"
python tax_calculator.py
```

## Running Tests

To run the comprehensive test suite (58 tests):

```bash
cd .
pytest tests/ -v
```

Tests cover:
- Individual and corporate tax calculations
- PAN validation and entity detection
- Database operations (save/retrieve)

## Creating Standalone Executable

### Option 1: Using Batch Script (Easiest - Windows only)

```cmd
build.bat
```

This will create `dist/tax_calculator.exe`

To clean previous builds first:

```cmd
build.bat /clean
```

### Option 2: Using PyInstaller Directly

```bash
python -m PyInstaller build.spec
```

Output will be in `dist/` folder.

### Option 3: Modify for One-File Executable

If you want a single `.exe` file instead of a folder, run:

```bash
python -m PyInstaller -F -w --distpath dist --workpath build -n tax_calculator "Tax calc/tax_calculator.py"
```

This creates a single `dist/tax_calculator.exe` file (slower startup, larger file).

## Build Output

After building, the `dist/` folder contains:
- **Windows Distribution-Ready Folder**: Copy entire `dist/tax_calculator/` folder to another Windows machine
- **No Dependencies Required**: The executable includes all Python libraries and dependencies

## Distribution

### To distribute to end users:

1. **Build the executable**:
   ```bash
   build.bat
   ```

2. **Zip the dist folder**:
   - Right-click `dist/tax_calculator/` → Send to → Compressed (zipped) folder
   - Or use: `tar -czf tax_calculator.zip dist/tax_calculator/`

3. **Share the ZIP file**: Users can extract and double-click `tax_calculator.exe` to run

### Minimum System Requirements:
- Windows 7 or later (x64 or x86)
- No Python installation required
- ~150-200 MB disk space

## Troubleshooting

### Build fails with "module not found"

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Executable won't start

**Solution**: Try running from command prompt to see error messages:
```cmd
dist\tax_calculator\tax_calculator.exe
```

### Build takes a long time

This is normal - PyInstaller bundles all Python dependencies. First build may take 2-5 minutes.

## Project Structure

```
Tax calc/
├── tax_calculator.py           # Main application
├── taxlib/                     # Business logic module
│   ├── __init__.py
│   ├── calculations.py         # Tax calculation engine
│   ├── pan.py                  # PAN validation
│   └── db.py                   # Database operations
├── tests/                      # Unit tests
│   ├── test_calculations.py
│   ├── test_pan.py
│   └── test_db.py
├── build.spec                  # PyInstaller configuration
├── build.bat                   # Build script (Windows)
├── build.ps1                   # Build script (PowerShell)
└── requirements.txt            # Dependencies
```

## Next Steps

- Add app icon: Modify `build.spec` to include `icon='path/to/icon.ico'`
- Create installer: Use NSIS or Inno Setup with the `dist/` folder
- Add splash screen: PyInstaller supports splash images
- CI/CD: Set up GitHub Actions to auto-build on release
