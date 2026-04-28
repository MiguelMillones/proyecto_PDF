# main.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

APP_NAME = 'DocTriX'
APP_VERSION = '2.1.0'

# Determinar plataforma
is_windows = sys.platform == 'win32'
is_macos = sys.platform == 'darwin'

# Configurar icono según plataforma
if is_windows:
    ICON_PATH = 'assets/icon.ico'
elif is_macos:
    ICON_PATH = 'assets/icon.icns' if os.path.exists('assets/icon.icns') else 'assets/icon.png'
else:
    ICON_PATH = 'assets/icon.png'

# Archivos adicionales a incluir (datas)
added_files = [
    ('assets', 'assets'),
    ('src/pdf', 'pdf'),
    ('src/utils', 'utils'),
]

# Script principal
main_script = 'src/main.py'

# ========== IMPORTANTE: Forzar inclusión completa de ReportLab ==========
import PyInstaller.utils.hooks

# Obtener todos los submódulos de ReportLab
try:
    reportlab_datas = PyInstaller.utils.hooks.collect_data_files('reportlab')
    reportlab_hidden = PyInstaller.utils.hooks.collect_submodules('reportlab')
except:
    reportlab_datas = []
    reportlab_hidden = [
        'reportlab.pdfgen.canvas',
        'reportlab.pdfgen',
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'reportlab.lib',
        'reportlab.lib.utils',
    ]

# Análisis
a = Analysis(
    [main_script],
    pathex=['.'],
    binaries=[],
    datas=added_files + reportlab_datas,
    hiddenimports=[
        'PyPDF2',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',      # ← Importante
        'reportlab.pdfbase',
        'reportlab.pdfbase.ttfonts',
        'reportlab.lib',
        'reportlab.lib.utils',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PIL',
        'PIL.Image',
        'pdf.extraer',
        'pdf.unir',
        'pdf.foliar',
        'utils.path_utils',
    ] + reportlab_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'test',
        'pytest',
        'numpy',
        'matplotlib',
        'scipy',
        'jupyter',
        'IPython',
    ],
    noarchive=False,
)

# Colección de módulos Python
pyz = PYZ(a.pure)

# Ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
)

# Para macOS: crear bundle .app
if is_macos:
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=APP_NAME,
    )
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
        bundle_identifier='com.doctrix.app',
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleVersion': APP_VERSION,
            'CFBundleShortVersionString': APP_VERSION,
            'NSHighResolutionCapable': True,
        },
    )