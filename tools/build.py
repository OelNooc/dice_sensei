#!/usr/bin/env python3
"""
Script de construcción para DiceSensei
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_executable():
    print("🎲 Construyendo DiceSensei...")
    
    for folder in ['build', 'dist']:
        if Path(folder).exists():
            shutil.rmtree(folder)
    
    opts = [
        'src/main.py',
        '--name=dicesensei',
        '--onefile',
        '--windowed',
        '--icon=assets/icons/dicesensei.ico',
        '--add-data=config;config',
        '--add-data=assets;assets',
        '--hidden-import=tkinter',
        '--hidden-import=requests',
        '--clean',
        '--noconfirm'
    ]
    
    try:
        PyInstaller.__main__.run(opts)
        print("✅ DiceSensei construido correctamente!")
        
        dist_dir = Path("dist")
        essential_folders = ['config', 'assets']
        
        for folder in essential_folders:
            if Path(folder).exists():
                shutil.copytree(folder, dist_dir / folder)
                
        print("📁 Archivos copiados a dist/")
        
    except Exception as e:
        print(f"❌ Error construyendo: {e}")

if __name__ == "__main__":
    build_executable()