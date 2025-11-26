# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Tax Calculator
Build: pyinstaller build.spec
Output: dist/tax_calculator.exe
"""

import os
import sys

# Determine paths
if getattr(sys, 'frozen', False):
    # Running as compiled
    script_dir = os.path.dirname(sys.executable)
else:
    # Running as Python script - use current directory
    script_dir = os.getcwd()

tax_calc_dir = os.path.join(script_dir, "Tax calc")

block_cipher = None

a = Analysis(
    [os.path.join(tax_calc_dir, "tax_calculator.py")],
    pathex=[tax_calc_dir],
    binaries=[],
    datas=[],
    hiddenimports=[
        'ttkbootstrap',
        'matplotlib',
        'taxlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tax_calculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
