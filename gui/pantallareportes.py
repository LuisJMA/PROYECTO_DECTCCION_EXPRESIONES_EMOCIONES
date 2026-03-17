# gui/pantalla_reportes.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from modules.database import Database

class PantallaReportes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = Database()
        
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        # Panel superior - Filtros
        panel_filtros = tk.Frame(self, bg='#3498db', height=80)
        panel_filtros.pack(fill='x')
        panel_filtros.pack_propagate(False)
        
        tk.Label(panel_filtros, text="REPORTES Y ESTADÍSTICAS", 
                font=('Arial', 14, 'bold'), bg='#3498db', fg='white').pack(pady=10)
        
        # Botón actualizar
        self.btn_actualizar = tk.Button(panel_filtros, text="🔄 ACTUALIZAR", 
                                        command=self.cargar_datos,
                                        bg='#2ecc71', fg='white', font=('Arial', 10))
        self.btn_actualizar.pack(side='right', padx=10)
        
        # Botón exportar
        self.btn_exportar = tk.Button(panel_filtros, text="💾 EXPORTAR CSV", 
                                      command=self.exportar_csv,
                                      bg='#f39c12', fg='white', font=('Arial', 10))
        self.btn_exportar.pack(side='right', padx=10)
        
        # Panel principal con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña 1: Gráficos
        self.tab_graficos = tk.Frame(self.notebook)
        self.notebook.add(self.tab_graficos, text='📊 Gráficos')
        
        # Pestaña 2: Historial
        self.tab_historial = tk.Frame(self.notebook)
        self.notebook.add(self.tab_historial, text='📋 Historial')
        
        # Pestaña 3: Estadísticas
        self.tab_stats = tk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text='📈 Estadísticas')
        
        # Crear contenido de cada pestaña
        self.crear_pestana_graficos()
        self.crear_pestana_historial()
        self.crear_pestana_stats()
    
    def crear_pestana_graficos(self):
        """Crea el gráfico de emociones"""
        frame = tk.Frame(self.tab_graficos)
        frame.pack(fill='both', expand=True)
        
        # Crear figura para el gráfico
        self.fig = Figure(figsize=(10, 6))
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def crear_pestana_historial(self):
        """Crea la tabla con el historial de detecciones"""
        frame = tk.Frame(self.tab_historial)
        frame.pack(fill='both', expand=True)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame)
        scroll_y.pack(side='right', fill='y')
        
        scroll_x = ttk.Scrollbar(frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')
        
        # Treeview
        self.tree = ttk.Treeview(frame, 
                                 columns=('Persona', 'Emoción', 'Confianza', 'Fecha'),
                                 show='headings',
                                 yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set)
        
        self.tree.heading('Persona', text='Persona')
        self.tree.heading('Emoción', text='Emoción')
        self.tree.heading('Confianza', text='Confianza')
        self.tree.heading('Fecha', text='Fecha')
        
        self.tree.column('Persona', width=200)
        self.tree.column('Emoción', width=150)
        self.tree.column('Confianza', width=100)
        self.tree.column('Fecha', width=200)
        
        self.tree.pack(fill='both', expand=True)
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
    
    def crear_pestana_stats(self):
        """Crea las estadísticas generales"""
        frame = tk.Frame(self.tab_stats)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Labels para estadísticas
        self.stats_labels = {}
        stats_texts = [
            'Total Personas Registradas:',
            'Total Detecciones:',
            'Emoción Más Común:',
            'Persona Más Detectada:',
            'Confianza Promedio:'
        ]
        
        for i, text in enumerate(stats_texts):
            tk.Label(frame, text=text, font=('Arial', 11, 'bold')).grid(
                row=i, column=0, sticky='w', pady=10)
            
            self.stats_labels[text] = tk.Label(frame, text='-', font=('Arial', 11))
            self.stats_labels[text].grid(row=i, column=1, sticky='w', padx=20, pady=10)
    
    def cargar_datos(self):
        """Carga los datos de la base de datos"""
        stats = self.db.obtener_estadisticas()
        historial = self.db.obtener_historial()
        
        # Actualizar gráfico
        self.actualizar_grafico(historial)
        
        # Actualizar tabla
        self.actualizar_tabla(historial)
        
        # Actualizar estadísticas
        self.actualizar_stats(stats, historial)
    
    def actualizar_grafico(self, historial):
        """Actualiza el gráfico de emociones"""
        self.ax.clear()
        
        if not historial:
            self.ax.text(0.5, 0.5, 'No hay datos disponibles', 
                        ha='center', va='center', fontsize=14)
        else:
            # Convertir a DataFrame para facilitar el conteo
            df = pd.DataFrame(historial)
            
            # Contar emociones por persona
            emociones_por_persona = df.groupby(['nombre_persona', 'emocion']).size().unstack()
            
            if not emociones_por_persona.empty:
                emociones_por_persona.plot(kind='bar', ax=self.ax, legend=True)
                self.ax.set_title('Distribución de Emociones por Persona')
                self.ax.set_xlabel('Persona')
                self.ax.set_ylabel('Cantidad')
                self.ax.legend(title='Emoción', bbox_to_anchor=(1.05, 1))
        
        self.canvas.draw()
    
    def actualizar_tabla(self, historial):
        """Actualiza la tabla con el historial"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar datos
        for det in historial:
            self.tree.insert('', 'end', values=(
                det['nombre_persona'],
                det['emocion'],
                f"{det['confianza']:.2%}",
                det['timestamp'][:19]  # Solo fecha y hora sin milisegundos
            ))
    
    def actualizar_stats(self, stats, historial):
        """Actualiza las estadísticas"""
        self.stats_labels['Total Personas Registradas:'].config(
            text=str(stats['total_personas']))
        
        self.stats_labels['Total Detecciones:'].config(
            text=str(stats['total_detecciones']))
        
        if stats['emociones']:
            emocion_comun = max(stats['emociones'], key=stats['emociones'].get)
            self.stats_labels['Emoción Más Común:'].config(
                text=f"{emocion_comun} ({stats['emociones'][emocion_comun]} veces)")
        
        if stats['personas']:
            persona_comun = max(stats['personas'], key=stats['personas'].get)
            self.stats_labels['Persona Más Detectada:'].config(
                text=f"{persona_comun} ({stats['personas'][persona_comun]} veces)")
        
        if historial:
            confianza_prom = sum(d['confianza'] for d in historial) / len(historial)
            self.stats_labels['Confianza Promedio:'].config(
                text=f"{confianza_prom:.2%}")
    
    def exportar_csv(self):
        """Exporta el historial a CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]
        )
        
        if filename:
            historial = self.db.obtener_historial()
            if historial:
                df = pd.DataFrame(historial)
                df.to_csv(filename, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            else:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")