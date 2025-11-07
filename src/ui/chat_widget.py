import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import logging

logger = logging.getLogger("DiceSensei.ChatWidget")

class ChatWidget:
    def __init__(self, parent):
        self.parent = parent
        self.messages = []
        self.setup_widgets()
    
    def setup_widgets(self):
        """Configura los widgets del chat"""
        self.chat_frame = ttk.Frame(self.parent)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_message_area()
        
        self.setup_input_area()
    
    def setup_message_area(self):
        """Configura el área de mensajes"""
        message_frame = ttk.Frame(self.chat_frame)
        message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(message_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.message_text = tk.Text(
            message_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            font=('Arial', 10),
            padx=10,
            pady=5,
            spacing1=5,
            spacing3=5
        )
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.message_text.yview)
        
        self.setup_message_tags()
    
    def setup_message_tags(self):
        """Configura los estilos para diferentes tipos de mensajes"""
        self.message_text.tag_configure(
            "user",
            background="#007bff",
            foreground="white",
            justify="right",
            margin=(60, 10, 10, 10),
            relief="raised",
            spacing2=5
        )
        
        self.message_text.tag_configure(
            "bot",
            background="#e9ecef",
            foreground="black",
            justify="left",
            margin=(10, 10, 60, 10),
            relief="raised",
            spacing2=5
        )
        
        self.message_text.tag_configure(
            "system",
            foreground="#6c757d",
            justify="center",
            font=('Arial', 9, 'italic')
        )
        
        self.message_text.tag_configure(
            "timestamp",
            foreground="#6c757d",
            font=('Arial', 8)
        )
    
    def setup_input_area(self):
        """Configura el área de entrada de texto"""
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=('Arial', 11),
            relief="solid",
            bd=1
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.send_button = tk.Button(
            input_frame,
            text="Enviar",
            command=self.on_send,
            bg="#28a745",
            fg="white",
            font=('Arial', 10, 'bold'),
            padx=20,
            relief="flat"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        self.input_entry.bind('<Return>', lambda e: self.on_send())
    
    def add_message(self, sender, message, message_type="normal"):
        """Añade un mensaje al chat"""
        self.message_text.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        
        self.message_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        if sender == "user":
            prefix = "👤 Tú"
            tag = "user"
        elif sender == "bot":
            prefix = "🎲 DiceSensei"
            tag = "bot"
        else:  # system
            prefix = "⚙️ Sistema"
            tag = "system"
        
        self.message_text.insert(tk.END, f"{prefix}: ", tag)
        self.message_text.insert(tk.END, f"{message}\n\n", tag)
        
        self.message_text.see(tk.END)
        self.message_text.config(state=tk.DISABLED)
        
        self.messages.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp,
            "type": message_type
        })
    
    def on_send(self):
        """Maneja el envío de mensajes"""
        message = self.input_var.get().strip()
        if message:
            self.add_message("user", message)
            self.input_var.set("")
            if hasattr(self.parent, 'on_user_message'):
                self.parent.on_user_message(message)
    
    def clear_chat(self):
        """Limpia el historial del chat"""
        self.message_text.config(state=tk.NORMAL)
        self.message_text.delete(1.0, tk.END)
        self.message_text.config(state=tk.DISABLED)
        self.messages.clear()
    
    def enable_input(self):
        """Habilita la entrada de texto"""
        self.input_entry.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
    
    def disable_input(self):
        """Deshabilita la entrada de texto"""
        self.input_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
    
    def set_placeholder(self, text):
        """Establece un texto placeholder"""
        self.input_entry.config(fg='grey')
        self.input_var.set(text)
        
        def on_focus_in(event):
            if self.input_entry.get() == text:
                self.input_entry.delete(0, tk.END)
                self.input_entry.config(fg='black')
        
        def on_focus_out(event):
            if not self.input_entry.get():
                self.input_entry.insert(0, text)
                self.input_entry.config(fg='grey')
        
        self.input_entry.bind('<FocusIn>', on_focus_in)
        self.input_entry.bind('<FocusOut>', on_focus_out)