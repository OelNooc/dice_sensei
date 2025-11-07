#!/usr/bin/env python3
"""
Script para crear instaladores automáticamente
"""

import os
import sys
import shutil
from pathlib import Path
import zipfile
import json

class InstallerCreator:
    def __init__(self):
        self.build_dir = Path("dist")
        self.release_dir = Path("releases")
        self.installer_dir = Path("installer")
        
    def create_release_package(self, platform):
        """Crea un paquete de release para una plataforma específica"""
        print(f"📦 Creando paquete para {platform}...")
        
        temp_dir = Path(f"temp_{platform}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        essential_files = [
            "dicesensei.exe" if platform == "windows" else "dicesensei",
            "config/",
            "assets/",
            "README.md",
            "LICENSE"
        ]
        
        for item in essential_files:
            source = self.build_dir / item if not item.endswith('/') else self.build_dir / item[:-1]
            dest = temp_dir / item if not item.endswith('/') else temp_dir / item[:-1]
            
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, dest)
                else:
                    shutil.copytree(source, dest)
        
        self.release_dir.mkdir(exist_ok=True)
        zip_path = self.release_dir / f"dicesensei-{platform}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        shutil.rmtree(temp_dir)
        
        print(f"✅ Paquete creado: {zip_path}")
        return zip_path
    
    def create_all_platform_packages(self):
        """Crea paquetes para todas las plataformas"""
        platforms = ["windows", "linux", "macos"]
        
        print("🎲 Creando paquetes de release para todas las plataformas...")
        print("=" * 50)
        
        created_packages = []
        
        for platform in platforms:
            exe_name = "dicesensei.exe" if platform == "windows" else "dicesensei"
            exe_path = self.build_dir / exe_name
            
            if exe_path.exists():
                package_path = self.create_release_package(platform)
                created_packages.append(package_path)
            else:
                print(f"⚠️  No se encontró {exe_name} - Saltando {platform}")
        
        if created_packages:
            print("\n🔐 Generando hashes...")
            os.system("python tools/generate_hashes.py")
        
        print(f"\n🎉 Proceso completado!")
        print(f"📦 Paquetes creados: {len(created_packages)}")
        for package in created_packages:
            print(f"   📁 {package.name}")
        
        return created_packages
    
    def update_version_file(self, new_version):
        """Actualiza el archivo de versión"""
        version_file = Path("config/version.json")
        
        if version_file.exists():
            with open(version_file, 'r') as f:
                version_data = json.load(f)
        
        version_data["version"] = new_version
        version_data["build_date"] = os.environ.get('BUILD_DATE', '')
        
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        print(f"✅ Versión actualizada a {new_version}")

def main():
    """Función principal"""
    creator = InstallerCreator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "package":
            creator.create_all_platform_packages()
        elif sys.argv[1] == "version" and len(sys.argv) > 2:
            creator.update_version_file(sys.argv[2])
        else:
            print("Uso: python create_installer.py [package|version <new_version>]")
    else:
        print("🎲 DiceSensei - Creador de Instaladores")
        print("=" * 40)
        print("1. Crear paquetes para todas las plataformas")
        print("2. Actualizar versión")
        print("3. Salir")
        
        choice = input("\nSelecciona una opción (1-3): ").strip()
        
        if choice == "1":
            creator.create_all_platform_packages()
        elif choice == "2":
            new_version = input("Nueva versión (ej: 1.1.0): ").strip()
            if new_version:
                creator.update_version_file(new_version)
            else:
                print("❌ No se especificó versión")
        elif choice == "3":
            print("👋 ¡Hasta luego!")
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()