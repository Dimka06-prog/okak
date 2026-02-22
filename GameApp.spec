# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=['firebase_admin', 'google.cloud.firestore', 'google.auth', 'google.oauth2', 'google.auth.transport.requests', 'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'asyncio', 'typing', 'datetime', 'json', 'logging', 'uuid'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'numpy', 'scipy', 'pandas'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='GameApp',
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
)
app = BUNDLE(
    exe,
    name='GameApp.app',
    icon=None,
    bundle_identifier=None,
)
