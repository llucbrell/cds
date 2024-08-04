# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['init.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('templates', 'templates'),
        ('plugins', 'plugins'),
    ],
    hiddenimports=['nltk'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cds',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Cambiar a False
    icon='static/images/cds_icon_5.ico',
    base='Win32GUI'  # Añadir esta línea
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cds'
)

app = BUNDLE(
    coll,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='cds',
    onefile=True  # Esta línea asegura que el ejecutable sea un archivo único
)
