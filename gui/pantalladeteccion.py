# gui/pantalla_deteccion.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
from modules.reconocimiento import Reconocedor

class PantallaDeteccion(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.reconocedor = Reconocedor()
        self.detectando = False
        self.cap = None
        
        self.init_ui()
    
    def init_ui(self):
        # Panel superior - Controles
        panel_controles = tk.Frame(self, bg='#2c3e50', height=60)
        panel_controles.pack(fill='x')
        panel_controles.pack_propagate(False)
        
        self.btn_iniciar = tk.Button(panel_controles, text="▶ INICIAR", 
                                     command=self.iniciar_deteccion,
                                     bg='#27ae60', fg='white', font=('Arial', 11, 'bold'),
                                     padx=20, pady=8)
        self.btn_iniciar.pack(side='left', padx=10, pady=10)
        
        self.btn_detener = tk.Button(panel_controles, text="⏹ DETENER", 
                                     command=self.detener_deteccion,
                                     bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'),
                                     state='disabled', padx=20, pady=8)
        self.btn_detener.pack(side='left', padx=10, pady=10)
        
        # Panel de estadísticas en tiempo real
        self.frame_stats = tk.Frame(panel_controles, bg='#34495e')
        self.frame_stats.pack(side='right', padx=20, pady=5, fill='y')
        
        self.label_stats = tk.Label(self.frame_stats, text="ESTADÍSTICAS", 
                                    font=('Arial', 10, 'bold'), bg='#34495e', fg='white')
        self.label_stats.pack(anchor='w')
        
        self.label_rostros = tk.Label(self.frame_stats, text="Rostros: 0", 
                                      bg='#34495e', fg='white')
        self.label_rostros.pack(anchor='w')
        
        self.label_registrados = tk.Label(self.frame_stats, text="Registrados: 0", 
                                         bg='#34495e', fg='white')
        self.label_registrados.pack(anchor='w')
        
        # Panel de video
        panel_video = tk.Frame(self, bg='black')
        panel_video.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.label_video = tk.Label(panel_video, bg='black')
        self.label_video.pack(fill='both', expand=True)
        
        # Panel de información detallada
        panel_info = tk.Frame(self, bg='#ecf0f1', height=150)
        panel_info.pack(fill='x', side='bottom')
        panel_info.pack_propagate(False)
        
        # Tabla de últimas detecciones
        self.tree = ttk.Treeview(panel_info, columns=('Persona', 'Emoción', 'Confianza'), 
                                 show='headings', height=4)
        self.tree.heading('Persona', text='Persona')
        self.tree.heading('Emoción', text='Emoción')
        self.tree.heading('Confianza', text='Confianza')
        
        self.tree.column('Persona', width=200)
        self.tree.column('Emoción', width=150)
        self.tree.column('Confianza', width=100)
        
        scrollbar = ttk.Scrollbar(panel_info, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
    
    def iniciar_deteccion(self):
        """Inicia la detección con IP Webcam"""
        url = "http://192.168.1.103:8080/video"  # Cambia por tu IP
        self.cap = cv2.VideoCapture(url)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        if self.cap.isOpened():
            self.detectando = True
            self.btn_iniciar.config(state='disabled')
            self.btn_detener.config(state='normal')
            self.actualizar_deteccion()
        else:
            messagebox.showerror("Error", "No se pudo abrir la cámara")
    
    def detener_deteccion(self):
        """Detiene la detección"""
        self.detectando = False
        if self.cap:
            self.cap.release()
        self.btn_iniciar.config(state='normal')
        self.btn_detener.config(state='disabled')
        self.label_video.config(image='')
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def actualizar_deteccion(self):
        """Actualiza el frame de video"""
        if not self.detectando:
            return
        
        ret, frame = self.cap.read()
        if ret:
            # Procesar frame con el reconocedor
            resultado = self.reconocedor.procesar_frame(frame)
            
            # Actualizar estadísticas
            if resultado['persona']:
                self.label_registrados.config(text="Registrados: 1")
            else:
                self.label_registrados.config(text="Registrados: 0")
            
            # Dibujar información en el frame
            frame = self.reconocedor.dibujar_info(frame, resultado)
            
            # Actualizar tabla si hay rostro
            if resultado['rostro_detectado']:
                nombre = "No registrado"
                if resultado['persona']:
                    nombre = f"{resultado['persona']['nombre']} {resultado['persona']['apellido']}"
                
                # Insertar al inicio de la tabla
                self.tree.insert('', 0, values=(
                    nombre,
                    resultado['emocion'],
                    f"{resultado['confianza_emocion']:.2f}"
                ))
                # Mantener solo últimas 10 filas
                if len(self.tree.get_children()) > 10:
                    self.tree.delete(self.tree.get_children()[-1])
            
            # Convertir para tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((800, 600))
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.label_video.imgtk = imgtk
            self.label_video.configure(image=imgtk)
        
        self.after(30, self.actualizar_deteccion)
    
    def __del__(self):
        """Libera la cámara al cerrar"""
        if self.cap:
            self.cap.release()