import os
import subprocess
import sys
import requests
import time
import logging
from pathlib import Path
import platform
import threading
import json

logger = logging.getLogger("DiceSensei.OllamaManager")

class OllamaManager:
    def __init__(self, progress_callback=None):
        self.ollama_path = self.get_ollama_path()
        self.models_dir = Path("assets/models")
        self.base_url = "http://localhost:11434"
        self.is_running = False
        self.progress_callback = progress_callback
        self.ollama_process = None
        
        self.current_model = "phi3.5:latest"
        self._model_loaded = False
        
        self._ensure_psutil_installed()
        
        self.system_cores = self._detect_cpu_cores()
        self.system_ram = self._detect_ram_gb()
        
        logger.info(f"Sistema detectado: {self.system_cores} cores, {self.system_ram}GB RAM")
        
        self._setup_encoding()
    
    def _ensure_psutil_installed(self):
        """Instala psutil automáticamente si no está disponible"""
        try:
            import psutil
            logger.info("✅ psutil ya está instalado")
            return True
        except ImportError:
            logger.warning("psutil no encontrado, instalando automáticamente...")
            if self.progress_callback:
                self.progress_callback("Instalando optimizaciones del sistema...")
            
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "psutil", "--quiet"
                ], timeout=60)
                logger.info("✅ psutil instalado correctamente")
                
                import psutil
                if self.progress_callback:
                    self.progress_callback("Optimizaciones instaladas correctamente")
                return True
                
            except Exception as e:
                logger.error(f"Error instalando psutil: {e}")
                if self.progress_callback:
                    self.progress_callback("Continuando sin optimizaciones...")
                return False
    
    def _detect_cpu_cores(self):
        """Detecta el número de cores disponibles"""
        try:
            import psutil
            cores = psutil.cpu_count(logical=False)
            return cores if cores and cores >= 1 else 4
        except:
            return 4
    
    def _detect_ram_gb(self):
        """Detecta la RAM disponible en GB"""
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024**3))
            return ram_gb if ram_gb >= 1 else 8
        except:
            return 8
    
    def _setup_encoding(self):
        """Configura la codificación para Windows"""
        if sys.platform == "win32":
            try:
                os.environ['PYTHONIOENCODING'] = 'utf-8'
            except:
                pass
    
    def get_ollama_path(self):
        """Obtiene la ruta correcta de Ollama para el sistema"""
        if sys.platform == "win32":
            possible_paths = [
                Path("ollama.exe"),
                Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Ollama" / "ollama.exe",
                Path(os.environ.get('PROGRAMFILES', '')) / "Ollama" / "ollama.exe",
                Path(os.environ.get('PROGRAMFILES(X86)', '')) / "Ollama" / "ollama.exe",
            ]
            
            for path in possible_paths:
                if path.exists():
                    logger.info(f"Ollama encontrado en: {path}")
                    return path
            
            logger.warning("Ollama no encontrado en el sistema")
            return None
        else:
            return Path("ollama")
    
    def update_progress(self, message):
        """Actualiza el progreso si hay callback"""
        if self.progress_callback:
            clean_message = message
            emoji_replacements = {
                '🔧': '[CONFIG]', '🚀': '[INICIANDO]', '📥': '[DESCARGANDO]',
                '✅': '[OK]', '❌': '[ERROR]', '⚠️': '[ADVERTENCIA]',
                '🔍': '[VERIFICANDO]', '🎲': '[DICESENSEI]', '🤖': '[AI]'
            }
            for emoji, replacement in emoji_replacements.items():
                clean_message = clean_message.replace(emoji, replacement)
            
            self.progress_callback(clean_message)
    
    def is_ollama_installed(self):
        """Verifica si Ollama está instalado en el sistema"""
        if sys.platform == "win32":
            try:
                result = subprocess.run(["where", "ollama"], 
                                      capture_output=True, text=True, timeout=10,
                                      encoding='utf-8', errors='ignore')
                return result.returncode == 0
            except:
                return self.ollama_path and self.ollama_path.exists()
        else:
            try:
                result = subprocess.run(["which", "ollama"], 
                                      capture_output=True, text=True,
                                      encoding='utf-8', errors='ignore')
                return result.returncode == 0
            except:
                return False
    
    def is_ollama_running(self):
        """Verifica si el servidor Ollama está ejecutándose"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self.is_running = response.status_code == 200
            return self.is_running
        except requests.exceptions.RequestException:
            self.is_running = False
            return False
    
    def install_ollama_windows(self):
        """Instala Ollama en Windows automáticamente"""
        try:
            self.update_progress("Iniciando instalación de Ollama...")
            
            installer_url = "https://ollama.ai/download/OllamaSetup.exe"
            installer_path = Path("ollama_setup.exe")
            
            self.update_progress("Descargando instalador de Ollama...")
            
            response = requests.get(installer_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            self.update_progress(f"Descargando Ollama... {percent:.1f}%")
            
            self.update_progress("Instalando Ollama... Esto puede tomar unos minutos.")
            
            result = subprocess.run([
                str(installer_path), "/S"
            ], capture_output=True, text=True, timeout=300,  
               encoding='utf-8', errors='ignore')
            
            if installer_path.exists():
                installer_path.unlink()
            
            if result.returncode == 0:
                self.update_progress("Ollama instalado correctamente")
                self.ollama_path = Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Ollama" / "ollama.exe"
                
                self.update_progress("Finalizando configuración...")
                time.sleep(10)
                return True
            else:
                self.update_progress("Error en la instalación de Ollama")
                logger.error(f"Error instalación: {result.stderr}")
                return False
                
        except Exception as e:
            self.update_progress("Error instalando Ollama")
            logger.error(f"Error instalando Ollama: {e}")
            return False

    def _start_ollama_terminal(self):
        """Inicia Ollama en una terminal separada que se cierra automáticamente"""
        try:
            self.update_progress("Iniciando servidor Ollama...")
            
            if sys.platform == "win32":
                if self.ollama_path and self.ollama_path.exists():
                    powershell_script = f'''
                    Start-Process "{self.ollama_path}" -ArgumentList "serve" -WindowStyle Hidden
                    Start-Sleep -Seconds 10
                    '''
                    subprocess.Popen([
                        "powershell", "-WindowStyle", "Hidden", "-Command", powershell_script
                    ])
                else:
                    subprocess.Popen([
                        "powershell", "-WindowStyle", "Hidden", "-Command",
                        "Start-Process ollama -ArgumentList serve -WindowStyle Hidden; Start-Sleep -Seconds 10"
                    ])
            else:
                subprocess.Popen([
                    "nohup", "ollama", "serve", "&"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.update_progress("Esperando que Ollama esté listo...")
            for i in range(30):
                if self.is_ollama_running():
                    self.update_progress("✅ Ollama iniciado correctamente")
                    return True
                time.sleep(1)
            
            if self._check_existing_ollama_process():
                self.update_progress("✅ Ollama ya está ejecutándose en segundo plano")
                return True
            
            self.update_progress("⚠️ Ollama iniciado pero verificando estado...")
            time.sleep(5)
            if self.is_ollama_running():
                self.update_progress("✅ Ollama confirmado en ejecución")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error iniciando Ollama en terminal: {e}")
            return False

    def _start_ollama_background(self):
        """Método alternativo: iniciar Ollama directamente en segundo plano"""
        try:
            self.update_progress("Iniciando Ollama en segundo plano...")
            
            env = os.environ.copy()
            env["OLLAMA_HOST"] = "127.0.0.1:11434"
            
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  
                
                if self.ollama_path and self.ollama_path.exists():
                    self.ollama_process = subprocess.Popen(
                        [str(self.ollama_path), "serve"],
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    self.ollama_process = subprocess.Popen(
                        ["ollama", "serve"],
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
            else:
                self.ollama_process = subprocess.Popen(
                    ["ollama", "serve"],
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
            
            self.update_progress("Esperando que Ollama esté listo...")
            for i in range(25):
                if self.is_ollama_running():
                    self.update_progress("✅ Ollama iniciado correctamente en segundo plano")
                    return True
                time.sleep(1)
            
            return False
            
        except Exception as e:
            logger.error(f"Error iniciando Ollama en segundo plano: {e}")
            return False

    def start_ollama_server(self):
        """Inicia el servidor Ollama automáticamente"""
        if self.is_ollama_running():
            logger.info("Ollama ya está ejecutándose")
            self.update_progress("Ollama ya está en ejecución")
            return True
        
        if not self.is_ollama_installed():
            self.update_progress("Ollama no está instalado. Instalando...")
            if sys.platform == "win32":
                if not self.install_ollama_windows():
                    return False
            else:
                self.update_progress("Ollama requiere instalación manual en este sistema")
                return False
        
        try:
            self.update_progress("Iniciando servidor Ollama...")
            
            if self._start_ollama_terminal():
                return True
            
            self.update_progress("Intentando método alternativo...")
            if self._start_ollama_background():
                return True
            
            if self._check_existing_ollama_process():
                self.update_progress("✅ Ollama encontrado en procesos del sistema")
                time.sleep(3)
                if self.is_ollama_running():
                    return True
            
            self.update_progress("❌ No se pudo iniciar Ollama")
            return False
            
        except Exception as e:
            logger.error(f"Error iniciando Ollama: {e}")
            self.update_progress("Error iniciando Ollama")
            return False

    def _check_existing_ollama_process(self):
        """Verifica si hay procesos Ollama existentes"""
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'exe']):
                proc_name = proc.info['name'] or ''
                proc_exe = proc.info['exe'] or ''
                
                if ('ollama' in proc_name.lower() or 
                    'ollama' in proc_exe.lower()):
                    logger.info(f"Proceso Ollama encontrado: {proc.pid} - {proc_name}")
                    return True
            return False
        except:
            return False
    
    def ensure_model_downloaded(self, model_name=None):
        """Asegura que el modelo esté disponible"""
        if model_name is None:
            model_name = self.current_model
            
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=30)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model_name == model.get("name", ""):
                        self.update_progress(f"Modelo {model_name} disponible")
                        self.current_model = model_name
                        return True
            
            self.update_progress(f"Descargando modelo {model_name}...")
            
            model_info = {
                "phi3.5:latest": "Phi 3.5 - Modelo rápido y eficiente (2.2GB)",
                "mistral:7b": "Mistral 7B - Calidad premium (4.1GB)",
                "phi:2.7b": "Phi 2.7B - Modelo ligero (1.7GB)"
            }
            
            if model_name in model_info:
                self.update_progress(model_info[model_name])
            
            process_args = []
            if self.ollama_path and self.ollama_path.exists():
                process_args = [str(self.ollama_path), "pull", model_name]
            else:
                process_args = ["ollama", "pull", model_name]
            
            result = subprocess.run(
                process_args,
                capture_output=True,
                text=True,
                timeout=3600,  
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                self.update_progress(f"✅ Modelo {model_name} descargado correctamente")
                self.current_model = model_name
                return True
            else:
                self.update_progress(f"❌ Error descargando modelo {model_name}")
                logger.error(f"Error descarga: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.update_progress("❌ Timeout descargando modelo")
            return False
        except Exception as e:
            self.update_progress(f"❌ Error con el modelo: {str(e)}")
            logger.error(f"Error con el modelo: {e}")
            return False

    def _preload_model(self):
        """Pre-carga más efectiva del modelo con timeout más corto"""
        if self._model_loaded:
            return True
            
        try:
            self.update_progress("Preparando modelo para respuestas rápidas...")
            
            test_payload = {
                "model": self.current_model,
                "prompt": "Responde únicamente con la palabra 'LISTO'",
                "stream": False,
                "options": {
                    "num_predict": 3,
                    "temperature": 0.1
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=test_payload,
                timeout=15  
            )
            
            if response.status_code == 200:
                result = response.json()
                if "LISTO" in result.get("response", ""):
                    self._model_loaded = True
                    self.update_progress("✅ Modelo cargado y listo")
                    return True
            
            return False
                
        except Exception as e:
            logger.warning(f"Pre-carga fallida (no crítico): {e}")
            return False

    def interactive_warm_up(self):
        """Warm-up interactivo del modelo - OPCIONAL, no crítico"""
        try:
            self.update_progress("Realizando warm-up del modelo...")
            
            warm_up_prompt = "Responde únicamente con 'Hola, soy DiceSensei'"
            
            payload = {
                "model": self.current_model,
                "prompt": warm_up_prompt,
                "stream": False,
                "options": {
                    "num_predict": 10,
                    "temperature": 0.3
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=20  
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                logger.info(f"Warm-up exitoso: {response_text}")
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Warm-up fallido (no crítico): {e}")
            return True  

    def _get_optimized_parameters(self):
        """Parámetros optimizados para velocidad y respuestas completas"""
        return {
            "num_ctx": 4096,  
            "num_predict": 1500, 
            "num_thread": self.system_cores,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop": ["###", "Fin del documento", "Respuesta completa"]  
        }

    def _compress_context(self, context):
        """Compresión inteligente del contexto"""
        if not context or len(context) <= 2000:
            return context
        
        compressed = context[:1200] + "\n...[contenido intermedio]...\n" + context[-800:]
        logger.info(f"Contexto comprimido: {len(context)} -> {len(compressed)} caracteres")
        return compressed

    def _ensure_complete_response(self, text, max_words=500):
        """Asegura que la respuesta esté completa y no truncada"""
        if not text:
            return text
        
        words = text.split()
        if len(words) <= max_words:
            return text
        
        truncated = words[:max_words]
        
        last_sentence_end = -1
        for i in range(len(truncated)-1, max(0, len(truncated)-50), -1):
            if (truncated[i].endswith('.') or 
                truncated[i].endswith('?') or 
                truncated[i].endswith('!')) and len(truncated[i]) > 1:
                last_sentence_end = i
                break
        
        if last_sentence_end != -1:
            complete_response = ' '.join(truncated[:last_sentence_end + 1])
        else:
            complete_response = ' '.join(truncated)
            if not complete_response.endswith(('.', '!', '?')):
                complete_response += "... [respuesta truncada por longitud]"
        
        logger.info(f"Respuesta ajustada: {len(words)} -> {len(complete_response.split())} palabras")
        return complete_response

    def generate_response(self, prompt, model=None, context=None):
        """Genera respuesta usando Ollama"""
        if model is None:
            model = self.current_model
            
        try:
            if not self.is_ollama_running():
                self.update_progress("Reiniciando conexión con Ollama...")
                if not self.start_ollama_server():
                    return "Error: El servidor AI no está disponible. Por favor reinicia la aplicación."
            
            compressed_context = self._compress_context(context) if context else None
            
            if compressed_context:
                full_prompt = f"""Basándote en el siguiente documento, responde la pregunta de manera COMPLETA y DETALLADA:

DOCUMENTO:
{compressed_context}

PREGUNTA: {prompt}

IMPORTANTE: Proporciona una respuesta completa y bien estructurada. Si es un resumen, incluye los puntos principales. 
Si es una explicación, sé claro y exhaustivo.

RESPUESTA:"""
            else:
                full_prompt = f"""Responde la siguiente pregunta de manera ÚTIL, COMPLETA y DETALLADA:

PREGUNTA: {prompt}

IMPORTANTE: Proporciona una respuesta completa y bien estructurada.

RESPUESTA:"""
            
            optimized_params = self._get_optimized_parameters()
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": optimized_params
            }
            
            logger.info(f"Generando respuesta con {model}")
            
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300  
            )
            elapsed_time = time.time() - start_time
            
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "").strip()
            
            if not response_text:
                return "No se pudo generar una respuesta útil. ¿Podrías reformular tu pregunta?"
            
            complete_response = self._ensure_complete_response(response_text, max_words=600)
            
            logger.info(f"Respuesta generada en {elapsed_time:.2f}s - {len(complete_response.split())} palabras")
            return complete_response
            
        except requests.exceptions.Timeout:
            logger.error("Timeout generando respuesta")
            return "La respuesta está tomando más tiempo de lo esperado. Intenta con una pregunta más específica."
            
        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión con Ollama")
            return "Error de conexión con el servidor AI. Verifica que Ollama esté ejecutándose."
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return f"Error temporal: {str(e)}"

    def diagnostic_check(self):
        """Verifica el estado del sistema Ollama"""
        try:
            if not self.is_ollama_running():
                return "❌ Servidor Ollama no está corriendo"
            
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code != 200:
                return f"❌ Error consultando modelos: {response.status_code}"
                
            models = response.json().get("models", [])
            if not models:
                return "❌ No hay modelos disponibles"
                
            current_model_found = any(
                model.get("name") == self.current_model for model in models
            )
            
            if not current_model_found:
                return f"❌ Modelo {self.current_model} no encontrado. Modelos disponibles: {[m.get('name') for m in models]}"
                
            return "✅ Sistema funcionando correctamente"
                
        except Exception as e:
            return f"❌ Error en diagnóstico: {str(e)}"
    
    def stop_server(self):
        """Detiene el servidor Ollama de forma segura"""
        try:
            if self.ollama_process:
                self.ollama_process.terminate()
                try:
                    self.ollama_process.wait(timeout=10)
                    logger.info("Proceso Ollama terminado correctamente")
                except subprocess.TimeoutExpired:
                    self.ollama_process.kill()
                    logger.warning("Proceso Ollama forzado a terminar")
                self.ollama_process = None
                    
        except Exception as e:
            logger.error(f"Error deteniendo Ollama: {e}")
    
    def setup_environment(self):
        """Configura todo el entorno de Ollama automáticamente"""
        try:
            logger.info("Configurando entorno AI con Ollama...")
            self.update_progress("Iniciando sistema AI...")
            
            if not self.start_ollama_server():
                logger.error("No se pudo iniciar Ollama")
                return False
            
            fast_models = ["phi3.5:latest", "phi:2.7b", "mistral:7b"]
            model_available = False
            
            for model in fast_models:
                if self.ensure_model_downloaded(model):
                    model_available = True
                    break
            
            if not model_available:
                logger.error("No se pudo descargar ningún modelo")
                return False
            
            self.interactive_warm_up()
            
            logger.info("Entorno AI configurado correctamente")
            self.update_progress("✅ Sistema AI listo para usar!")
            return True
            
        except Exception as e:
            logger.error(f"Error configurando entorno AI: {e}")
            self.update_progress("Error configurando el sistema AI")
            return False

_ollama_manager = None

def get_ollama_manager(progress_callback=None):
    """Obtiene la instancia global del OllamaManager"""
    global _ollama_manager
    if _ollama_manager is None:
        _ollama_manager = OllamaManager(progress_callback=progress_callback)
    return _ollama_manager