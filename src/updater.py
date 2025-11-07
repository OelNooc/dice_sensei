import requests
import json
import os
import sys
import shutil
import tempfile
from pathlib import Path
import hashlib
import zipfile
import logging
from datetime import datetime

logger = logging.getLogger("DiceSensei.Updater")

class DiceSenseiUpdater:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)  
        
        self.repo_url = "https://api.github.com/repos/OelNooc/dice_sensei/releases/latest"
        self.current_version = self.get_current_version()
        self.update_dir = Path("updates")
        
    def get_current_version(self):
        """Obtiene la versión actual instalada"""
        version_file = self.config_dir / "version.json"
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("version", "1.0.0")
            except Exception as e:
                logger.error(f"Error leyendo versión: {e}")
                return "1.0.0"
        return "1.0.0"
    
    def check_and_apply_updates(self):
        """Verifica y aplica actualizaciones si las hay"""
        try:
            latest_release = self.get_latest_release()
            if not latest_release:
                return False
                
            latest_version = latest_release["tag_name"]
            
            if self.is_newer_version(latest_version, self.current_version):
                logger.info(f"Nueva versión disponible: {latest_version}")
                
                if self.ask_user_update(latest_release):
                    return self.download_and_install(latest_release)
                    
            return False
            
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
            return False
    
    def get_latest_release(self):
        """Obtiene información del último release"""
        try:
            response = requests.get(self.repo_url, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo release: {e}")
            return None
    
    def is_newer_version(self, latest, current):
        """Compara versiones semánticas"""
        try:
            def parse_version(ver):
                return list(map(int, ver.lstrip('v').split('.')))
                
            latest_ver = parse_version(latest)
            current_ver = parse_version(current)
            
            return latest_ver > current_ver
            
        except:
            return False
    
    def ask_user_update(self, release_data):
        """Pregunta al usuario si quiere actualizar"""
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        release_notes = release_data.get("body", "Mejoras generales y correcciones de errores.")
        if len(release_notes) > 500:
            release_notes = release_notes[:500] + "..."
            
        response = messagebox.askyesno(
            "🎲 Actualización Disponible",
            f"DiceSensei v{release_data['tag_name']} está disponible!\n\n"
            f"¿Quieres actualizar ahora?\n\n"
            f"📝 Cambios:\n{release_notes}\n\n"
            f"La actualización tomará unos momentos..."
        )
        
        root.destroy()
        return response
    
    def download_and_install(self, release_data):
        """Descarga e instala la actualización"""
        try:
            asset = self.find_correct_asset(release_data)
            if not asset:
                logger.error("No se encontró asset compatible")
                return False
            
            temp_file = self.download_asset(asset)
            if not temp_file:
                return False
                
            if not self.verify_download(temp_file, asset, release_data):
                logger.error("Verificación fallida")
                return False
                
            if self.install_update(temp_file, release_data["tag_name"]):
                logger.info("Actualización instalada correctamente")
                return True
            else:
                logger.error("Error en instalación")
                return False
                
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
            return False
    
    def find_correct_asset(self, release_data):
        """Encuentra el asset correcto para el sistema operativo"""
        system_map = {
            'win32': 'windows',
            'darwin': 'macos',
            'linux': 'linux'
        }
        
        current_system = system_map.get(sys.platform)
        if not current_system:
            return None
            
        for asset in release_data.get("assets", []):
            asset_name = asset["name"].lower()
            if current_system in asset_name and asset_name.endswith('.zip'):
                return asset
                
        return None
    
    def download_asset(self, asset):
        """Descarga el asset del release"""
        try:
            temp_dir = Path(tempfile.gettempdir()) / "dicesensei_update"
            temp_dir.mkdir(exist_ok=True)
            
            zip_path = temp_dir / asset["name"]
            
            logger.info(f"Descargando {asset['name']}...")
            response = requests.get(asset["browser_download_url"], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
            logger.info("Descarga completada")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error descargando: {e}")
            return None
    
    def verify_download(self, file_path, asset, release_data):
        """Verificación híbrida del archivo descargado"""
        # 1. Verificar tamaño
        if not self.verify_file_size(file_path, asset):
            return False
            
        # 2. Verificar integridad del zip
        if not self.verify_zip_integrity(file_path):
            return False
            
        # 3. Intentar verificación con hash
        expected_hash = self.get_expected_hash(asset["name"], release_data)
        if expected_hash:
            actual_hash = self.calculate_hash(file_path)
            if actual_hash == expected_hash:
                logger.info("✅ Hash verificado correctamente")
                return True
            else:
                logger.error("❌ Hash no coincide")
                return False
                
        # 4. Si no hay hash, confiar en las verificaciones anteriores
        logger.info("✅ Archivo verificado (métodos alternativos)")
        return True
    
    def verify_file_size(self, file_path, asset):
        """Verifica que el tamaño del archivo coincida"""
        actual_size = os.path.getsize(file_path)
        expected_size = asset["size"]
        
        if actual_size == expected_size:
            return True
        else:
            logger.error(f"Tamaño incorrecto: {actual_size} vs {expected_size}")
            return False
    
    def verify_zip_integrity(self, file_path):
        """Verifica que el ZIP sea válido"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                bad_file = zip_ref.testzip()
                if bad_file is not None:
                    logger.error(f"Archivo ZIP corrupto: {bad_file}")
                    return False
                return True
        except zipfile.BadZipFile as e:
            logger.error(f"ZIP inválido: {e}")
            return False
    
    def get_expected_hash(self, filename, release_data):
        """Obtiene el hash esperado del archivo de hashes"""
        try:
            for asset in release_data.get("assets", []):
                if asset["name"] == "checksums.sha256":
                    response = requests.get(asset["browser_download_url"])
                    hash_content = response.text
                    
                    for line in hash_content.split('\n'):
                        if filename in line:
                            return line.split()[0]
            return None
        except:
            return None
    
    def calculate_hash(self, file_path):
        """Calcula SHA256 del archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def install_update(self, zip_path, new_version):
        """Instala la actualización"""
        try:
            backup_dir = Path("backup") / f"v{self.current_version}"
            self.create_backup(backup_dir)
            
            extract_dir = Path("update_temp")
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
                
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            self.replace_files(extract_dir)
            
            self.update_version_file(new_version)
            
            shutil.rmtree(extract_dir)
            os.remove(zip_path)
            
            logger.info(f"Actualizado a v{new_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error instalando: {e}")
            self.restore_backup(backup_dir)
            return False
    
    def create_backup(self, backup_dir):
        """Crea backup de la instalación actual"""
        try:
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                
            backup_dir.mkdir(parents=True)
            
            exclude = ['backup', 'updates', 'temp', 'logs', '__pycache__']
            
            for item in Path(".").iterdir():
                if item.name not in exclude and item.is_file():
                    shutil.copy2(item, backup_dir / item.name)
                    
            logger.info("Backup creado correctamente")
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
    
    def restore_backup(self, backup_dir):
        """Restaura desde backup"""
        try:
            if backup_dir.exists():
                for item in backup_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, Path(".") / item.name)
                logger.info("Backup restaurado")
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
    
    def replace_files(self, source_dir):
        """Reemplaza archivos con la nueva versión"""
        for item in source_dir.iterdir():
            dest_path = Path(".") / item.name
            
            if item.is_file():
                if dest_path.exists():
                    os.remove(dest_path)
                shutil.copy2(item, dest_path)
            elif item.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(item, dest_path)
    
    def update_version_file(self, new_version):
        """Actualiza el archivo de versión"""
        try:
            version_data = {
                "version": new_version,
                "last_update": datetime.now().isoformat(),
                "name": "DiceSensei"
            }
            
            self.config_dir.mkdir(exist_ok=True)
            version_file = self.config_dir / "version.json"
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error actualizando versión: {e}")