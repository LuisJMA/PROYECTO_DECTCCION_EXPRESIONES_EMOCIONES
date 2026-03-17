"""
Módulo de Registro de Personas
Captura rostros y genera embeddings usando DeepFace (modelo Facenet)
"""

import cv2
import numpy as np
from deepface import DeepFace

class Registrador:
    def __init__(self):
        self.embeddings = []
        self.capturas_actuales = 0
        self.capturas_necesarias = 5
        print("✅ Registrador iniciado (modelo Facenet)")
    
    def detectar_rostro(self, frame):
        """
        Detecta un rostro en el frame
        Returns: (top, right, bottom, left) o None
        """
        try:
            rostros = DeepFace.extract_faces(
                img_path=frame,
                detector_backend='opencv',
                enforce_detection=False
            )
            
            if rostros and len(rostros) > 0:
                area = rostros[0]['facial_area']
                x, y, w, h = area['x'], area['y'], area['w'], area['h']
                return (y, x + w, y + h, x)
            return None
        except:
            return None
    
    def extraer_embedding(self, frame, face_location):
        """
        Extrae embedding del rostro usando Facenet
        """
        try:
            top, right, bottom, left = face_location
            rostro = frame[top:bottom, left:right]
            
            if rostro.size == 0:
                return None
            
            # Guardar temporalmente
            cv2.imwrite("temp_rostro.jpg", rostro)
            
            # Extraer embedding con Facenet
            embedding = DeepFace.represent(
                img_path="temp_rostro.jpg",
                model_name='VGG-Face',
                enforce_detection=False
            )
            
            if embedding and len(embedding) > 0:
                return np.array(embedding[0]['embedding'])
            return None
        except Exception as e:
            print(f"Error embedding: {e}")
            return None
    
    def capturar_desde_camara(self, frame):
        """Captura un embedding del frame actual"""
        face_loc = self.detectar_rostro(frame)
        if face_loc:
            emb = self.extraer_embedding(frame, face_loc)
            if emb is not None:
                self.embeddings.append(emb)
                self.capturas_actuales = len(self.embeddings)
                return True
        return False
    
    def obtener_embedding_promedio(self):
        if not self.embeddings:
            return None
        return np.mean(self.embeddings, axis=0)
    
    def limpiar_capturas(self):
        self.embeddings = []
        self.capturas_actuales = 0
    
    def verificar_calidad(self):
        if len(self.embeddings) < 3:
            return {"valido": False, "mensaje": "Se necesitan más capturas", "calidad": "insuficiente"}
        
        embeddings_array = np.array(self.embeddings)
        varianza = np.var(embeddings_array, axis=0).mean()
        
        if varianza < 0.1:
            return {"valido": True, "mensaje": "✅ Excelente calidad", "calidad": "excelente"}
        elif varianza < 0.15:
            return {"valido": True, "mensaje": "✅ Buena calidad", "calidad": "buena"}
        else:
            return {"valido": True, "mensaje": "⚠️ Calidad regular", "calidad": "regular"}  
    
    def dibujar_guia(self, frame, face_location=None):
        if face_location:
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, "Rostro OK", (left, top-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            cv2.putText(frame, "Buscando rostro...", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        texto = f"Capturas: {self.capturas_actuales}/{self.capturas_necesarias}"
        cv2.putText(frame, texto, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame