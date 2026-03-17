"""
Módulo de Reconocimiento Facial
Identifica personas y detecta emociones usando DeepFace (mismo modelo que registro)
"""

import cv2
import numpy as np
from deepface import DeepFace
from modules.database import Database

class Reconocedor:
    def __init__(self):
        self.db = Database()
        print("✅ Reconocedor iniciado (modelo Facenet)")
    
    def detectar_rostro(self, frame):
        """Detecta un rostro en el frame"""
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
        Extrae embedding del rostro usando Facenet (IGUAL que en registro)
        """
        try:
            top, right, bottom, left = face_location
            rostro = frame[top:bottom, left:right]
            
            if rostro.size == 0:
                return None
            
            cv2.imwrite("temp_rostro.jpg", rostro)
            
            embedding = DeepFace.represent(
                img_path="temp_rostro.jpg",
                model_name='VGG-Face',  # MISMO modelo que en registro
                enforce_detection=False
            )
            
            if embedding and len(embedding) > 0:
                return np.array(embedding[0]['embedding'])
            return None
        except Exception as e:
            print(f"Error embedding: {e}")
            return None
    
    def analizar_emocion(self, frame, face_location):
        """Analiza la emoción del rostro"""
        try:
            top, right, bottom, left = face_location
            rostro = frame[top:bottom, left:right]
            cv2.imwrite("temp_emo.jpg", rostro)
            
            resultado = DeepFace.analyze(
                img_path="temp_emo.jpg",
                actions=['emotion'],
                enforce_detection=False
            )
            
            if resultado and len(resultado) > 0:
                emocion_ing = resultado[0]['dominant_emotion']
                confianza = resultado[0]['emotion'][emocion_ing] / 100.0
                
                traduccion = {
                    'angry': 'Enojo', 'disgust': 'Disgusto', 'fear': 'Miedo',
                    'happy': 'Felicidad', 'sad': 'Tristeza',
                    'surprise': 'Sorpresa', 'neutral': 'Neutral'
                }
                return traduccion.get(emocion_ing, emocion_ing), confianza
            return "Neutral", 0.5
        except:
            return "Neutral", 0.5
    
    def identificar_persona(self, embedding):
        """Busca la persona en la base de datos"""
        return self.db.buscar_por_embedding(embedding)
    
    def procesar_frame(self, frame):
        """Procesa un frame completo"""
        resultado = {
            'rostro_detectado': False,
            'persona': None,
            'emocion': None,
            'confianza_emocion': 0.0,
            'ubicacion': None
        }
        
        # 1. Detectar rostro
        face_loc = self.detectar_rostro(frame)
        if not face_loc:
            return resultado
        
        resultado['rostro_detectado'] = True
        resultado['ubicacion'] = face_loc
        
        # 2. Extraer embedding
        embedding = self.extraer_embedding(frame, face_loc)

        # 🔍 DEPURACIÓN
        if embedding is not None:
            print(f"🔍 Embedding generado - forma: {embedding.shape}")
            print(f"   Primeros valores: {embedding[:5]}")

            # Comparar con el primer embedding guardado
            if len(self.db.personas) > 0:
                primer_emb = np.array(self.db.personas[0]['embeddings'][0])
                distancia = np.linalg.norm(primer_emb - embedding)
                print(f"📊 Distancia con persona 1: {distancia:.4f}")

        
        # 3. Identificar persona
        if embedding is not None:
            persona = self.identificar_persona(embedding)
            resultado['persona'] = persona
        
        # 4. Analizar emoción
        emocion, confianza = self.analizar_emocion(frame, face_loc)
        resultado['emocion'] = emocion
        resultado['confianza_emocion'] = confianza
        
        # 5. Guardar historial
        if resultado['persona']:
            self.db.guardar_deteccion(
                resultado['persona']['id'],
                emocion,
                confianza
            )
        
        return resultado
    
    def dibujar_info(self, frame, resultado):
        """Dibuja la información en el frame"""
        if not resultado['rostro_detectado']:
            cv2.putText(frame, "Buscando rostro...", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame
        
        top, right, bottom, left = resultado['ubicacion']
        color = (0, 255, 0) if resultado['persona'] else (0, 0, 255)
        
        if resultado['persona']:
            nombre = f"{resultado['persona']['nombre']} {resultado['persona']['apellido']}"
        else:
            nombre = "No registrado"
        
        # Rectángulo
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Fondo para texto
        cv2.rectangle(frame, (left, top-60), (right, top), (0, 0, 0), -1)
        
        # Textos
        cv2.putText(frame, f"Nombre: {nombre}", (left+5, top-40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Emocion: {resultado['emocion']} ({resultado['confianza_emocion']:.2f})",
                   (left+5, top-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame