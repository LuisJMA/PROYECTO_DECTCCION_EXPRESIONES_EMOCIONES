# PROYECTO_DECTCCION_EXPRESIONES_EMOCIONES
"Sistema de reconocimiento facial con análisis de emociones"

## 📋 Descripción General
Aplicación de escritorio que permite registrar personas mediante reconocimiento facial, identificarlas en tiempo real y analizar sus emociones (Felicidad, Tristeza, Enojo, Sorpresa, Neutral, Miedo, Disgusto). El sistema cuenta con una interfaz gráfica intuitiva de tres pantallas y utiliza modelos de deep learning para la detección facial y clasificación de emociones.

## ✅ Funcionalidades Principales

### Módulo de Registro de Personas
- [x] Capturar rostros mediante cámara web
- [x] Extraer y almacenar embeddings faciales
- [x] Registrar información personal (nombre, apellido, email)
- [x] Validar que no existan duplicados

### Módulo de Reconocimiento
- [x] Identificar personas previamente registradas en tiempo real
- [x] Mostrar información de la persona identificada
- [x] Manejar casos de "persona no registrada"
- [x] Clasificar 7 emociones básicas:
  - Felicidad, Tristeza, Enojo, Sorpresa, Neutral, Miedo, Disgusto
- [x] Mostrar nivel de confianza de cada predicción

### Módulo de Base de Datos
- [x] Almacenar registros de personas
- [x] Guardar histórico de detecciones emocionales
- [x] Permitir consultas y reportes

## 🖥️ Interfaz Gráfica

### Pantalla de Registro
- [x] Formulario para datos personales
- [x] Vista previa de cámara en tiempo real
- [x] Botón para capturar múltiples imágenes
- [x] Indicador de calidad del registro
- [x] Mensajes de confirmación/error

### Pantalla de Detección
- [x] Video en tiempo real con overlay
- [x] Información en pantalla:
  - Nombre de persona identificada
  - Emoción detectada
  - Nivel de confianza
  - Tiempo de detección
- [x] Controles: iniciar/detener detección

### Pantalla de Reportes
- [x] Gráfico de emociones por persona
- [x] Estadísticas generales
- [x] Historial de detecciones
- [x] Opciones de exportación

## 📦 Entregables

### Código Fuente
- [x] Código completo y funcional
- [x] Comentado y documentado
- [x] Organizado modularmente
- [x] Manejo de errores robusto

### Repositorio GitHub
- [x] README.md con documentación completa
- [x] requirements.txt con dependencias
- [x] .gitignore apropiado
- [x] Commits descriptivos y organizados

## 🛠️ Tecnologías Utilizadas
- Python 3.11
- OpenCV (captura de video)
- DeepFace (reconocimiento facial y emociones)
- TensorFlow (backend de DeepFace)
- Tkinter (interfaz gráfica)
- Matplotlib (gráficos)
- Pandas (manejo de datos)

## 📁 Estructura del Proyecto

IA/
├── modules/
│ ├── database.py # Manejo de archivos JSON
│ ├── registro.py # Captura de rostros y embeddings
│ └── reconocimiento.py # Identificación y análisis de emociones
├── gui/
│ ├── pantallaregistro.py
│ ├── pantalladeteccion.py
│ └── pantallareportes.py
├── database/
│ ├── personas.json # Datos de personas registradas
│ └── detecciones.json # Historial de detecciones
├── main.py # Punto de entrada
├── requirements.txt # Dependencias
├── README.md # Documentación
└── .gitignore # Archivos ignorados

-Crear entorno virtual
python -m venv venv
# Activar en Windows:
venv\Scripts\activate

-Instalar dependencias
pip install -r requirements.txt

-Configurar cámara

Si usas IP Webcam (celular):
Instala la app IP Webcam en tu celular
Abre la app y presiona "Start Server"
En el código, cambia la URL por la IP que aparece en tu celular

-Ejecutar la aplicación
python main.py


-Pantalla de Registro

Completa nombre, apellido y email

Presiona "CAPTURAR ROSTRO" 5 veces(O mas)

Verifica la calidad del registro

Presiona "REGISTRAR PERSONA"

-Pantalla de Detección

Presiona "INICIAR"

El sistema mostrará:

Rectángulo verde si la persona está registrada

Rectángulo rojo si no está registrada

Emoción detectada y nivel de confianza

-Pantalla de Reportes

Gráficos: Distribución de emociones por persona

Historial: Tabla con todas las detecciones

Estadísticas: Totales, emociones más comunes

Exportar: Guardar datos en CSV

-Ajustar tolerancia
En database.py:
tolerancia=0.6  # Menor = más estricto, Mayor = más permisivo(en el codigo esta a 0.8)


-Solución de Problemas

*No se detecta la cámara
Verifica que IP Webcam esté corriendo

Comprueba la URL en el código

*No reconoce a persona registrada

Ajusta la tolerancia (0.6 → 0.7)

Registra con más capturas (10 en lugar de 5)

Mejora la iluminación
