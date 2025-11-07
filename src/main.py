#!/usr/bin/env python3
"""
DiceSensei - Asistente de Estudio Inteligente
Autor: Leonardo Catejo Almuna - OelNooc
Repo: https://github.com/OelNooc/dice_sensei
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dicesensei.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("DiceSensei")

src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from updater import DiceSenseiUpdater
from ollama_manager import OllamaManager
from ui.main_window import MainWindow

class DiceSenseiApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.updater = DiceSenseiUpdater(config_dir="config")
        self.ollama_manager = OllamaManager(progress_callback=self.update_progress)
        self.main_window = None

    def update_progress(self, message):
        """Callback para actualizar progreso desde OllamaManager"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.update_progress_text(message)
        
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title("DiceSensei 🎲 - Asistente de Estudio")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        try:
            icon_path = Path("assets/icons/dicesensei.ico")
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except:
            pass
            
        self.center_window(self.root)
    
    def center_window(self, window):
        """Centra una ventana en la pantalla"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def check_updates(self):
        """Verifica y aplica actualizaciones"""
        try:
            logger.info("Buscando actualizaciones...")
            if self.updater.check_and_apply_updates():
                messagebox.showinfo(
                    "Actualización Completada", 
                    "DiceSensei se ha actualizado correctamente.\n\n"
                    "La aplicación se reiniciará ahora."
                )
                self.restart_application()
                return False
            return True
        except Exception as e:
            logger.error(f"Error en actualización: {e}")
            return True 
            
    def initialize_ai(self):
        """Inicializa el sistema AI con warm-up interactivo"""
        def init_task():
            try:
                self.main_window.add_to_chat("⚙️", "Iniciando sistema AI...")
                
                if self.ollama_manager.setup_environment():
                    # Warm-up interactivo
                    warm_up_result = self.ollama_manager.interactive_warm_up()
                    if warm_up_result:
                        self.main_window.add_to_chat("✅", "Sistema AI listo!")
                        self.main_window.add_to_chat("🎲", "¡Hola! Soy DiceSensei, tu asistente de estudio.")
                    else:
                        self.main_window.add_to_chat("⚠️", "Sistema AI iniciado con advertencias")
                else:
                    self.main_window.add_to_chat("❌", "Error iniciando el sistema AI")
                    
            except Exception as e:
                logger.error(f"Error inicializando AI: {e}")
                self.main_window.add_to_chat("❌", f"Error: {str(e)}")        
    
        thread = threading.Thread(target=init_task)
        thread.daemon = True
        thread.start()

    def restart_application(self):
        """Reinicia la aplicación"""
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def show_splash_screen(self):
        """Muestra una pantalla de inicio simple"""
        splash = tk.Toplevel(self.root)
        splash.title("DiceSensei")
        splash.geometry("300x150")
        splash.transient(self.root)
        splash.grab_set()
        splash.resizable(False, False)
        
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        tk.Label(splash, text="🎲 DiceSensei", font=('Arial', 16, 'bold')).pack(pady=20)
        tk.Label(splash, text="Iniciando...").pack()
        
        return splash
        
    def run(self):
        """Ejecuta la aplicación principal"""
        try:
            splash = self.show_splash_screen()
            self.root.update()
            
            if not self.check_updates():
                splash.destroy()
                return
                
            splash.destroy()
            
            self.main_window = MainWindow(self.root, self.ollama_manager)
            
            self.initialize_ai()
            
            logger.info("DiceSensei iniciado correctamente")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error crítico: {e}")
            messagebox.showerror(
                "Error", 
                f"No se pudo iniciar DiceSensei:\n{str(e)}"
            )

def main():
    """Función principal"""
    try:
        app = DiceSenseiApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta pronto!")
    except Exception as e:
        logger.critical(f"Error fatal: {e}")
        messagebox.showerror(
            "Error Fatal", 
            f"DiceSensei no pudo iniciarse:\n{str(e)}"
        )

if __name__ == "__main__":
    main()