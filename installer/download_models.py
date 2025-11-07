#!/usr/bin/env python3
"""
Script para descargar modelos pre-entrenados para DiceSensei
"""

import requests
import os
import sys
import time
from pathlib import Path
import subprocess
import threading

class ModelDownloader:
    def __init__(self):
        self.models_dir = Path("assets/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.available_models = {
            "phi3.5:latest": {  # CAMBIADO: modelo más rápido por defecto
                "name": "Phi 3.5 Mini",
                "size_gb": 2.2,
                "description": "Modelo rápido y eficiente - Recomendado",
                "recommended": True
            },
            "mistral:7b": {
                "name": "Mistral 7B",
                "size_gb": 4.1,
                "description": "Modelo equilibrado - Buena calidad",
                "recommended": True
            },
            "phi:2.7b": {
                "name": "Phi-2 2.7B", 
                "size_gb": 1.7,
                "description": "Modelo pequeño y rápido",
                "recommended": False
            }
        }
    
    def check_ollama_installed(self):
        """Verifica si Ollama está instalado"""
        try:
            if sys.platform == "win32":
                result = subprocess.run(["where", "ollama"], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(["which", "ollama"], 
                                      capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def download_model(self, model_name, progress_callback=None):
        """Descarga un modelo usando Ollama"""
        if not self.check_ollama_installed():
            print("❌ Ollama no está instalado")
            print("   Descarga Ollama desde: https://ollama.ai/")
            return False
        
        if model_name not in self.available_models:
            print(f"❌ Modelo no disponible: {model_name}")
            print(f"   Modelos disponibles: {list(self.available_models.keys())}")
            return False
        
        model_info = self.available_models[model_name]
        print(f"📥 Descargando {model_info['name']} ({model_info['size_gb']} GB)...")
        print(f"📝 {model_info['description']}")
        print("⏳ Esto puede tomar varios minutos...")
        
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='ignore',
                env=env
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        if progress_callback:
                            progress_callback(cleaned_line)
                        else:
                            if any(keyword in cleaned_line.lower() for keyword in 
                                  ['pulling', 'downloading', 'verifying', 'writing', 'success']):
                                print(f"   {cleaned_line}")
            
            return_code = process.poll()
            
            if return_code == 0:
                print(f"✅ {model_info['name']} descargado correctamente")
                return True
            else:
                print(f"❌ Error descargando {model_info['name']} (código: {return_code})")
                return False
                
        except Exception as e:
            print(f"❌ Error durante la descarga: {e}")
            return False
    
    def list_available_models(self):
        """Lista los modelos disponibles"""
        print("🎲 Modelos disponibles para DiceSensei:")
        print("=" * 50)
        
        for model_id, info in self.available_models.items():
            recommended = " ✅ RECOMENDADO" if info['recommended'] else ""
            print(f"🔸 {model_id}")
            print(f"   Nombre: {info['name']}")
            print(f"   Tamaño: {info['size_gb']} GB")
            print(f"   Descripción: {info['description']}{recommended}")
            print()
    
    def get_downloaded_models(self):
        """Obtiene la lista de modelos descargados"""
        try:
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='ignore',
                env=env,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Saltar línea de encabezado
                    models = []
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
                    return models
            return []
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout al verificar modelos descargados")
            return []
        except Exception as e:
            print(f"⚠️  Error verificando modelos: {e}")
            return []

def main():
    """Función principal del script"""
    downloader = ModelDownloader()
    
    print("🎲 DiceSensei - Descargador de Modelos")
    print("=" * 40)
    
    if not downloader.check_ollama_installed():
        print("❌ Ollama no está instalado en el sistema.")
        print("   Por favor, instala Ollama primero desde: https://ollama.ai/")
        print("   Luego reinicia este script.")
        sys.exit(1)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("⚠️  Ollama no está corriendo. Iniciando servidor...")
            subprocess.run(["ollama", "serve"], timeout=10)
            time.sleep(3)
    except:
        print("⚠️  Iniciando servidor Ollama...")
        try:
            subprocess.Popen(["ollama", "serve"])
            time.sleep(5)
        except:
            print("❌ No se pudo iniciar Ollama. Asegúrate de que esté instalado correctamente.")
            sys.exit(1)
    
    downloader.list_available_models()
    
    downloaded = downloader.get_downloaded_models()
    if downloaded:
        print("📂 Modelos ya descargados:")
        for model in downloaded:
            print(f"   ✅ {model}")
        print()
    
    model_choice = input("¿Qué modelo quieres descargar? (ej: phi3.5:latest): ").strip()
    
    if not model_choice:
        print("❌ No se especificó ningún modelo")
        sys.exit(1)
    
    if model_choice not in downloader.available_models:
        print(f"❌ Modelo no válido: {model_choice}")
        print("   Modelos válidos:", list(downloader.available_models.keys()))
        sys.exit(1)
    
    success = downloader.download_model(model_choice)
    
    if success:
        print("\n🎉 ¡Modelo descargado correctamente!")
        print("🚀 Ahora puedes usar DiceSensei con este modelo.")
    else:
        print("\n❌ Error descargando el modelo")
        print("💡 Sugerencias:")
        print("   - Verifica tu conexión a internet")
        print("   - Asegúrate de que Ollama esté instalado correctamente")
        print("   - Intenta ejecutar 'ollama serve' manualmente primero")
        sys.exit(1)

if __name__ == "__main__":
    main()