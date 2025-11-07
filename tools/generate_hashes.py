#!/usr/bin/env python3
"""
Script para generar hashes SHA256 de los archivos de release
Uso: python generate_hashes.py
"""

import hashlib
import os
import sys
from pathlib import Path

def calculate_file_hash(file_path):
    """Calcula el hash SHA256 de un archivo"""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ Error calculando hash de {file_path}: {e}")
        return None

def generate_checksums(directory="dist"):
    """Genera archivo de hashes para los releases"""
    print("🔍 Generando hashes SHA256...")
    
    hash_file = Path("checksums.sha256")
    files_processed = 0
    
    with open(hash_file, 'w', encoding='utf-8') as f:
        for file_path in Path(directory).rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    relative_path = file_path.relative_to(directory)
                    f.write(f"{file_hash}  {relative_path}\n")
                    print(f"✅ {relative_path} - {file_hash[:16]}...")
                    files_processed += 1
        
        config_files = [
            "config/version.json",
            "config/settings.json", 
            "config/models.json"
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                file_hash = calculate_file_hash(config_path)
                if file_hash:
                    f.write(f"{file_hash}  {config_file}\n")
                    print(f"✅ {config_file} - {file_hash[:16]}...")
                    files_processed += 1
    
    print(f"\n🎉 Hashes generados correctamente!")
    print(f"📊 Archivos procesados: {files_processed}")
    print(f"📁 Archivo de hashes: {hash_file}")
    
    print(f"\n📝 Contenido de {hash_file}:")
    print("=" * 50)
    with open(hash_file, 'r') as f:
        print(f.read())

def verify_checksums(directory="dist"):
    """Verifica los hashes de los archivos"""
    print("🔍 Verificando hashes...")
    
    hash_file = Path("checksums.sha256")
    if not hash_file.exists():
        print("❌ No se encontró archivo de hashes")
        return False
    
    errors = 0
    verified = 0
    
    with open(hash_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            if len(parts) >= 2:
                expected_hash = parts[0]
                file_path = ' '.join(parts[2:]) if len(parts) > 2 else parts[1]
                
                full_path = Path(directory) / file_path
                if full_path.exists():
                    actual_hash = calculate_file_hash(full_path)
                    if actual_hash == expected_hash:
                        print(f"✅ {file_path} - VERIFICADO")
                        verified += 1
                    else:
                        print(f"❌ {file_path} - HASH INCORRECTO")
                        print(f"   Esperado: {expected_hash}")
                        print(f"   Obtenido: {actual_hash}")
                        errors += 1
                else:
                    print(f"⚠️  {file_path} - NO ENCONTRADO")
    
    print(f"\n📊 Resultado de verificación:")
    print(f"   ✅ Archivos verificados: {verified}")
    print(f"   ❌ Errores: {errors}")
    print(f"   📁 Total: {verified + errors}")
    
    return errors == 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        success = verify_checksums()
        sys.exit(0 if success else 1)
    else:
        generate_checksums()