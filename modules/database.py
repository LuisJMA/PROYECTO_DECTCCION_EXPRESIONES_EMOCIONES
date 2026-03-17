"""
Módulo de Base de Datos
Guarda y lee información usando archivos JSON
"""

import json
import os
import numpy as np
from datetime import datetime

class Database:
    def __init__(self, carpeta="database"):
        """
        Inicializa la base de datos
        Args:
            carpeta: nombre de la carpeta donde se guardan los archivos
        """
        self.carpeta = carpeta
        
        # Rutas completas de los archivos
        self.ruta_personas = os.path.join(carpeta, "personas.json")
        self.ruta_detecciones = os.path.join(carpeta, "detecciones.json")
        
        # Crear carpeta si no existe
        os.makedirs(carpeta, exist_ok=True)
        
        # Cargar datos existentes o crear nuevos
        self.personas = self._cargar_json(self.ruta_personas, [])
        self.detecciones = self._cargar_json(self.ruta_detecciones, [])
    
    def _cargar_json(self, ruta, valor_por_defecto):
        """
        Carga un archivo JSON o crea uno nuevo si no existe
        Args:
            ruta: ubicación del archivo
            valor_por_defecto: valor si el archivo no existe
        Returns:
            datos cargados o valor_por_defecto
        """
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Crear archivo vacío
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(valor_por_defecto, f, indent=2)
            return valor_por_defecto
    
    def _guardar_json(self, ruta, datos):
        """
        Guarda datos en un archivo JSON
        """
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def registrar_persona(self, nombre, apellido, email, embeddings):
        """
        Guarda una nueva persona en la base de datos
        Args:
            nombre, apellido, email: datos personales
            embeddings: lista de embeddings (arrays numpy)
        Returns:
            int: ID de la nueva persona o None si el email ya existe
        """
        # Verificar si el email ya está registrado
        for p in self.personas:
            if p['email'] == email:
                print(f"❌ El email {email} ya existe")
                return None
        
        # Convertir embeddings de numpy a lista (para JSON)
        embeddings_lista = []
        for emb in embeddings:
            if isinstance(emb, np.ndarray):
                embeddings_lista.append(emb.tolist())
            else:
                embeddings_lista.append(emb)
        
        # Crear nueva persona
        nueva_persona = {
            "id": len(self.personas) + 1,
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "fecha_registro": datetime.now().isoformat(),
            "embeddings": embeddings_lista,
            "num_capturas": len(embeddings_lista)
        }
        
        self.personas.append(nueva_persona)
        self._guardar_json(self.ruta_personas, self.personas)
        
        print(f"✅ Persona registrada con ID: {nueva_persona['id']}")
        return nueva_persona["id"]
    
    def buscar_por_embedding(self, embedding, tolerancia=0.8):
        """
        Busca una persona por su embedding facial
        Args:
            embedding: array numpy a buscar
            tolerancia: distancia máxima para considerar coincidencia
        Returns:
            dict: datos de la persona o None si no se encuentra
        """
        mejor_coincidencia = None
        menor_distancia = float('inf')
        
        for persona in self.personas:
            # Convertir embeddings guardados (listas) a numpy
            for emb_lista in persona['embeddings']:
                emb_guardado = np.array(emb_lista)
                
                # Calcular distancia (qué tan similares son)
                distancia = np.linalg.norm(emb_guardado - embedding)
                
                # Si es la mejor coincidencia hasta ahora
                if distancia < tolerancia and distancia < menor_distancia:
                    menor_distancia = distancia
                    mejor_coincidencia = {
                        "id": persona["id"],
                        "nombre": persona["nombre"],
                        "apellido": persona["apellido"],
                        "email": persona["email"],
                        "distancia": float(distancia)
                    }
        
        return mejor_coincidencia
    
    def guardar_deteccion(self, persona_id, emocion, confianza):
        """
        Guarda una detección en el historial
        Args:
            persona_id: ID de la persona detectada
            emocion: emoción detectada
            confianza: nivel de confianza (0-1)
        """
        # Buscar nombre de la persona
        nombre_persona = "Desconocido"
        for p in self.personas:
            if p["id"] == persona_id:
                nombre_persona = f"{p['nombre']} {p['apellido']}"
                break

        # Convertir confianza de float32 a float normal
        confianza = float(confianza)    
        
        deteccion = {
            "id": len(self.detecciones) + 1,
            "persona_id": persona_id,
            "nombre_persona": nombre_persona,
            "emocion": emocion,
            "confianza": round(confianza, 3),
            "timestamp": datetime.now().isoformat()
        }
        
        self.detecciones.append(deteccion)
        self._guardar_json(self.ruta_detecciones, self.detecciones)
        print(f"📝 Detección guardada: {nombre_persona} - {emocion}")
    
    def obtener_historial(self, persona_id=None):
        """
        Obtiene el historial de detecciones
        Args:
            persona_id: filtrar por persona (opcional)
        Returns:
            lista de detecciones
        """
        if persona_id:
            return [d for d in self.detecciones if d["persona_id"] == persona_id]
        return self.detecciones
    
    def obtener_estadisticas(self):
        """
        Calcula estadísticas básicas
        Returns:
            dict con estadísticas
        """
        stats = {
            "total_personas": len(self.personas),
            "total_detecciones": len(self.detecciones),
            "emociones": {},
            "personas": {}
        }
        
        # Contar emociones
        for d in self.detecciones:
            emocion = d["emocion"]
            stats["emociones"][emocion] = stats["emociones"].get(emocion, 0) + 1
        
        # Contar detecciones por persona
        for d in self.detecciones:
            nombre = d["nombre_persona"]
            stats["personas"][nombre] = stats["personas"].get(nombre, 0) + 1
        
        return stats