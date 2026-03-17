# main.py
import tkinter as tk
from gui.pantallaregistro import PantallaRegistro
from gui.pantalladeteccion import PantallaDeteccion
from gui.pantallareportes import PantallaReportes

class AplicacionPrincipal:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Reconocimiento Facial con Emociones")
        self.root.geometry("1000x600")
        
        # Barra de navegación
        self.crear_barra_navegacion()
        
        # Contenedor principal
        self.container = tk.Frame(self.root)
        self.container.pack(fill='both', expand=True)
        
        # Mostrar pantalla inicial
        self.mostrar_pantalla(PantallaDeteccion)
    
    def crear_barra_navegacion(self):
        barra = tk.Frame(self.root, bg='#34495e', height=50)
        barra.pack(side='bottom', fill='x')
        
        tk.Button(barra, text="📝 REGISTRO", 
                 command=lambda: self.mostrar_pantalla(PantallaRegistro),
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                 width=15, height=2).pack(side='left', padx=10, pady=5)
        
        tk.Button(barra, text="🎥 DETECCIÓN", 
                 command=lambda: self.mostrar_pantalla(PantallaDeteccion),
                 bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'),
                 width=15, height=2).pack(side='left', padx=10, pady=5)
        
        tk.Button(barra, text="📊 REPORTES", 
                 command=lambda: self.mostrar_pantalla(PantallaReportes),
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                 width=15, height=2).pack(side='left', padx=10, pady=5)
    
    def mostrar_pantalla(self, Pantalla):
        for widget in self.container.winfo_children():
            widget.destroy()
        pantalla = Pantalla(self.container)
        pantalla.pack(fill='both', expand=True)
    
    def ejecutar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.ejecutar()