# gui/pantalla_registro.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
from modules.registro import Registrador
from modules.database import Database

class PantallaRegistro(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.registrador = Registrador()
        self.db = Database()
        self.cap = None
        self.camara_activa = False
        self.capturando = False
        
        self.init_ui()
        self.iniciar_camara()
    
    def init_ui(self):
        # Frame izquierdo - Formulario
        frame_form = tk.Frame(self, bg='#f0f0f0', width=300)
        frame_form.pack(side='left', fill='y', padx=10, pady=10)
        frame_form.pack_propagate(False)
        
        tk.Label(frame_form, text="REGISTRO DE PERSONA", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=20)
        
        # Campos
        tk.Label(frame_form, text="Nombre:", font=('Arial', 11), bg='#f0f0f0').pack(anchor='w', pady=(10,0))
        self.entry_nombre = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.entry_nombre.pack(pady=(0,10))
        
        tk.Label(frame_form, text="Apellido:", font=('Arial', 11), bg='#f0f0f0').pack(anchor='w', pady=(10,0))
        self.entry_apellido = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.entry_apellido.pack(pady=(0,10))
        
        tk.Label(frame_form, text="Email:", font=('Arial', 11), bg='#f0f0f0').pack(anchor='w', pady=(10,0))
        self.entry_email = tk.Entry(frame_form, font=('Arial', 11), width=30)
        self.entry_email.pack(pady=(0,10))
        
        # Indicador de calidad
        self.label_calidad = tk.Label(frame_form, text="Calidad: -", font=('Arial', 10), bg='#f0f0f0')
        self.label_calidad.pack(pady=10)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(frame_form, length=200, maximum=5)
        self.progress.pack(pady=10)
        
        # Contador
        self.label_contador = tk.Label(frame_form, text="Capturas: 0/5", font=('Arial', 10), bg='#f0f0f0')
        self.label_contador.pack()
        
        # Botones
        self.btn_capturar = tk.Button(frame_form, text="📸 CAPTURAR ROSTRO", 
                                      command=self.capturar_rostro,
                                      bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                                      state='disabled', width=25, height=2)
        self.btn_capturar.pack(pady=10)
        
        self.btn_registrar = tk.Button(frame_form, text="💾 REGISTRAR PERSONA", 
                                       command=self.registrar_persona,
                                       bg='#2196F3', fg='white', font=('Arial', 11, 'bold'),
                                       state='disabled', width=25, height=2)
        self.btn_registrar.pack(pady=10)
        
        self.btn_limpiar = tk.Button(frame_form, text="🗑️ LIMPIAR CAPTURAS", 
                                     command=self.limpiar_capturas,
                                     bg='#FF9800', fg='white', font=('Arial', 10),
                                     width=25, height=1)
        self.btn_limpiar.pack(pady=5)
        
        # Frame derecho - Cámara
        frame_camara = tk.Frame(self, bg='black')
        frame_camara.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.label_camara = tk.Label(frame_camara, bg='black')
        self.label_camara.pack(fill='both', expand=True)
        
        # Mensajes
        self.label_mensaje = tk.Label(self, text="Iniciando cámara...", font=('Arial', 10), bg='#e0e0e0')
        self.label_mensaje.pack(side='bottom', fill='x', pady=5)
    
    def iniciar_camara(self):
        """Inicia la captura de video con IP Webcam"""
        # Usar IP Webcam (cambia por tu IP)
        url = "http://192.168.1.103:8080/video"
        self.cap = cv2.VideoCapture(url)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        if self.cap.isOpened():
            self.camara_activa = True
            self.actualizar_camara()
            self.btn_capturar.config(state='normal')
            self.label_mensaje.config(text="Cámara lista")
    
    def actualizar_camara(self):
        """Actualiza el frame de la cámara"""
        if self.camara_activa and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Detectar rostro para guía
                face_loc = self.registrador.detectar_rostro(frame)
                frame = self.registrador.dibujar_guia(frame, face_loc)
                
                # Convertir para tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.thumbnail((640, 480))
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.label_camara.imgtk = imgtk
                self.label_camara.configure(image=imgtk)
            
            self.after(30, self.actualizar_camara)
    
    def capturar_rostro(self):
        """Captura un rostro"""
        if not self.camara_activa:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        if self.registrador.capturar_desde_camara(frame):
            capturas = self.registrador.capturas_actuales
            self.progress['value'] = capturas
            self.label_contador.config(text=f"Capturas: {capturas}/5")
            
            if capturas >= 3:
                calidad = self.registrador.verificar_calidad()
                self.label_calidad.config(text=f"Calidad: {calidad['mensaje']}")
            
            if capturas >= 5:
                self.btn_registrar.config(state='normal')
                self.label_mensaje.config(text="¡Listo para registrar!")
            else:
                self.label_mensaje.config(text=f"Captura {capturas}/5")
        else:
            messagebox.showwarning("Atención", "No se detectó rostro")
    
    def limpiar_capturas(self):
        """Limpia las capturas actuales"""
        self.registrador.limpiar_capturas()
        self.progress['value'] = 0
        self.label_contador.config(text="Capturas: 0/5")
        self.label_calidad.config(text="Calidad: -")
        self.btn_registrar.config(state='disabled')
        self.label_mensaje.config(text="Capturas limpiadas")
    
    def registrar_persona(self):
        """Guarda la persona en la base de datos"""
        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        email = self.entry_email.get().strip()
        
        if not nombre or not apellido or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        if '@' not in email or '.' not in email:
            messagebox.showerror("Error", "Email no válido")
            return
        
        if len(self.registrador.embeddings) < 5:
            messagebox.showerror("Error", "Debes capturar al menos 5 rostros")
            return
        
        persona_id = self.db.registrar_persona(
            nombre, apellido, email, 
            self.registrador.embeddings
        )
        
        if persona_id:
            messagebox.showinfo("Éxito", f"Persona registrada con ID {persona_id}")
            self.limpiar_capturas()
            self.entry_nombre.delete(0, tk.END)
            self.entry_apellido.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "El email ya existe")
    
    def __del__(self):
        """Libera la cámara al cerrar"""
        if self.cap:
            self.cap.release()