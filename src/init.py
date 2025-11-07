"""
DiceSensei - Asistente de Estudio Inteligente
"""

__version__ = "0.1.0"
__author__ = "Leonardo Catejo Almuna - OelNooc"
__email__ = "leo.catejoa@gmail.com - leo.catejoa@dadosoluciones.cl"
__repository__ = "https://github.com/OelNooc/dice_sensei"

from .main import DiceSenseiApp
from .updater import DiceSenseiUpdater
from .ollama_manager import OllamaManager, get_ollama_manager
from .config_manager import ConfigManager, get_config_manager

__all__ = [
    'DiceSenseiApp',
    'DiceSenseiUpdater', 
    'OllamaManager',
    'get_ollama_manager',
    'ConfigManager',
    'get_config_manager'
]