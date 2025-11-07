import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("DiceSensei.ConfigManager")

class ConfigManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.settings_file = self.config_dir / "settings.json"
        self.version_file = self.config_dir / "version.json"
        self.models_file = self.config_dir / "models.json"
        
        self.default_settings = {
            "ai": {
                "model": "mistral:7b",
                "temperature": 0.7,
                "max_tokens": 1000,
                "context_window": 4096
            },
            "ui": {
                "theme": "light",
                "font_size": 11,
                "language": "es",
                "auto_save": True,
                "show_timestamps": True
            },
            "updates": {
                "auto_check": True,
                "allow_auto_update": True,
                "check_interval_hours": 24
            },
            "document": {
                "max_file_size_mb": 50,
                "supported_formats": [".txt", ".pdf", ".docx", ".md", ".rtf"],
                "auto_load_last": True,
                "chunk_size": 1000
            },
            "paths": {
                "documents_dir": "documents",
                "models_dir": "assets/models",
                "logs_dir": "logs"
            }
        }
        
        self.default_models = {
            "available_models": [
                {
                    "name": "mistral:7b",
                    "description": "Modelo equilibrado - Recomendado",
                    "size_gb": 4.1,
                    "language": "multilingual",
                    "recommended": True
                },
                {
                    "name": "llama2:7b",
                    "description": "Modelo versátil en inglés",
                    "size_gb": 3.8,
                    "language": "english",
                    "recommended": False
                },
                {
                    "name": "phi:2.7b",
                    "description": "Modelo pequeño y rápido",
                    "size_gb": 1.7,
                    "language": "english",
                    "recommended": False
                }
            ],
            "selected_model": "mistral:7b"
        }
        
        self.ensure_directories()
        self.ensure_default_files()
    
    def ensure_directories(self):
        """Asegura que los directorios necesarios existan"""
        directories = [
            self.config_dir,
            Path("documents"),
            Path("assets/models"),
            Path("logs"),
            Path("backup")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def ensure_default_files(self):
        """Crea archivos de configuración por defecto si no existen"""
        if not self.settings_file.exists():
            self.save_settings(self.default_settings)
            logger.info("Archivo de configuración creado")
        
        if not self.models_file.exists():
            self.save_models(self.default_models)
            logger.info("Archivo de modelos creado")
    
    def load_settings(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            merged_settings = self._deep_merge(self.default_settings, settings)
            return merged_settings
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Guarda la configuración en el archivo"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("Configuración guardada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def load_models(self) -> Dict[str, Any]:
        """Carga la configuración de modelos"""
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            return self.default_models.copy()
    
    def save_models(self, models_config: Dict[str, Any]) -> bool:
        """Guarda la configuración de modelos"""
        try:
            with open(self.models_file, 'w', encoding='utf-8') as f:
                json.dump(models_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
            return False
    
    def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Obtiene un valor específico de configuración"""
        try:
            settings = self.load_settings()
            keys = key_path.split('.')
            value = settings
            
            for key in keys:
                value = value[key]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set_setting(self, key_path: str, value: Any) -> bool:
        """Establece un valor específico de configuración"""
        try:
            settings = self.load_settings()
            keys = key_path.split('.')
            current = settings
            
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = value
            
            return self.save_settings(settings)
            
        except Exception as e:
            logger.error(f"Error estableciendo configuración: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Obtiene la lista de modelos disponibles"""
        models_config = self.load_models()
        return models_config.get("available_models", [])
    
    def get_selected_model(self) -> str:
        """Obtiene el modelo seleccionado"""
        models_config = self.load_models()
        return models_config.get("selected_model", "mistral:7b")
    
    def set_selected_model(self, model_name: str) -> bool:
        """Establece el modelo seleccionado"""
        models_config = self.load_models()
        models_config["selected_model"] = model_name
        return self.save_models(models_config)
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Combina recursivamente dos diccionarios"""
        result = base.copy()
        
        for key, value in update.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

_config_manager = None

def get_config_manager():
    """Obtiene la instancia global del ConfigManager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager