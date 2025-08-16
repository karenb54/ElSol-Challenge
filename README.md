# ElSol Challenge - Medical Conversation API

Sistema de procesamiento de conversaciones médicas que transcribe audio, extrae información estructurada y proporciona un chatbot inteligente basado en datos vectorizados.

## Características Principales

- **Transcripción de Audio**: Procesamiento automático de archivos de audio (.wav, .mp3, .m4a, .flac)
- **Extracción de Información**: Análisis automático de datos del paciente (nombre, edad, síntomas, medicamentos)
- **Base de Datos Vectorial**: Almacenamiento semántico usando ChromaDB
- **Chatbot Inteligente**: Asistente médico basado en Google Gemini que responde consultas contextuales
- **API REST**: Interfaz completa con documentación automática

## Arquitectura del Sistema

```mermaid
graph TB
    subgraph "API Layer"
        API[FastAPI Server<br/>main.py]
        DOCS[Swagger Docs<br/>/docs]
    end
    
    subgraph "Audio Processing"
        AUDIO[Audio Files<br/>.wav, .mp3, .m4a, .flac]
        FFMPEG[FFmpeg<br/>Audio Processing]
        WHISPER[Whisper Model<br/>Transcription]
    end
    
    subgraph "AI Services"
        CHAT[Chat Service<br/>Gemini API]
        TRANSCRIPT[Transcription Service<br/>OpenAI Whisper]
    end
    
    subgraph "Database Layer"
        VECTOR[Vector Store Service<br/>ChromaDB]
        SEARCH[Search Service<br/>Semantic Search]
        PATIENT[Patient Service<br/>Patient Operations]
        CHROMA[(ChromaDB<br/>Vector Database)]
    end
    
    subgraph "Utilities"
        CONFIG[Config Service<br/>Environment & Settings]
    end
    
    %% API Connections
    API --> CHAT
    API --> TRANSCRIPT
    API --> VECTOR
    
    %% Audio Flow
    AUDIO --> FFMPEG
    FFMPEG --> WHISPER
    WHISPER --> TRANSCRIPT
    TRANSCRIPT --> VECTOR
    
    %% Database Connections
    VECTOR --> SEARCH
    VECTOR --> PATIENT
    VECTOR --> CHROMA
    
    %% Service Dependencies
    CHAT --> SEARCH
    CHAT --> CONFIG
    TRANSCRIPT --> CONFIG
    VECTOR --> CONFIG
    
    %% External APIs
    CHAT -.-> GEMINI[Google Gemini API]
    
    style API fill:#e1f5fe
    style CHAT fill:#f3e5f5
    style TRANSCRIPT fill:#e8f5e8
    style VECTOR fill:#fff3e0
    style CHROMA fill:#ffebee
    style GEMINI fill:#f1f8e9
```

## Prerrequisitos

- Python 3.8+
- FFmpeg instalado y configurado
- Cuenta de Google Cloud con API de Gemini habilitada

## Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd ElSol-Challenge
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   Crear archivo `.env` en la raíz del proyecto:
   ```env
   GEMINI_API_KEY=tu_api_key_de_gemini
   ```

## Ejecución

### Modo API (Recomendado)
```bash
python main.py --api
```
- Servidor disponible en: http://localhost:8000
- Documentación automática: http://localhost:8000/docs

### Modo Consola
```bash
python main.py
```

## Endpoints de la API

### 1. Health Check
- **GET** `/`
- **Descripción**: Verifica el estado del servidor
- **Respuesta**: Información del sistema y endpoints disponibles

### 2. Procesamiento de Audio
- **POST** `/process-audio`
- **Descripción**: Sube un archivo de audio, lo transcribe y almacena la información
- **Parámetros**: `file` (archivo de audio)
- **Respuesta**: Confirmación de procesamiento exitoso

### 3. Chat Inteligente
- **POST** `/chat`
- **Descripción**: Chatbot médico que responde consultas basadas en datos vectorizados
- **Parámetros**: `question` (pregunta del usuario)
- **Respuesta**: Respuesta contextual del asistente médico

## Casos de Uso del Chatbot

### Consultas Médicas
- "¿Cuántos pacientes hay registrados?"
- "¿Qué síntomas tiene Juan Pérez?"
- "¿Qué pacientes tienen fiebre?"
- "¿Hay pacientes con diabetes?"
- "Créame un plan de cuidado para Juan Pérez"

### Consultas No Médicas
- "¿Qué hora es?"
- "Hola, ¿cómo estás?"
- El chatbot responde de manera natural sin usar información médica

## Testing

### Ejecutar Todos los Tests
```bash
# Test de transcripción
python test/test_whisper.py

# Test de base de datos
python test/test_chroma.py

# Test completo de API
python test/test_api.py

# Test del chatbot
python test/test_chat_gemini.py
```

### Testing Manual con curl
```bash
# Health check
curl -X GET "http://localhost:8000/"

# Procesar audio
curl -X POST "http://localhost:8000/process-audio" \
     -F "file=@pruebas/p_52015966_552.wav"

# Chat médico
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "¿Qué síntomas tiene Juan Pérez?"}'
```

## Supuestos del Sistema

1. **Formato de Audio**: Soporta .wav, .mp3, .m4a, .flac
2. **Idioma**: Transcripción optimizada para español
3. **Información del Paciente**: Extracción automática de nombre, edad, género, síntomas
4. **Priorización**: Clasificación automática de urgencia (alta/normal)
5. **Persistencia**: Datos almacenados en ChromaDB con directorio `database/vector_db/`
6. **Seguridad**: Variables de entorno para API keys sensibles

## Buenas Prácticas Implementadas

### Arquitectura
- **Separación de responsabilidades**: Servicios modulares y especializados
- **Inyección de dependencias**: Configuración centralizada
- **Manejo de errores**: Try-catch robusto en todas las operaciones
- **Logging**: Registro detallado de operaciones

### Código
- **Docstrings**: Documentación completa de clases y métodos
- **Type hints**: Tipado estático para mejor mantenibilidad
- **Modularización**: Código organizado en servicios específicos
- **Tests**: Cobertura completa con tests unitarios e integración

### Seguridad
- **Variables de entorno**: API keys en archivo .env
- **Validación de entrada**: Pydantic para validación de datos
- **Manejo de archivos**: Validación de tipos y tamaños
- **Directorio temporal**: Tests sin afectar datos reales

## Estructura del Proyecto

```
ElSol-Challenge/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Documentación principal
├── .env                   # Variables de entorno (no versionado)
├── .gitignore            # Archivos excluidos del versionado
│
├── services/              # Servicios de la aplicación
│   ├── __init__.py
│   ├── transcription_service.py  # Servicio de transcripción
│   └── chat_service.py           # Servicio de chat con LLM
│
├── database/              # Capa de base de datos
│   ├── __init__.py
│   ├── vector_store_service.py   # Servicio principal de ChromaDB
│   ├── search_service.py         # Búsquedas semánticas
│   ├── patient_service.py        # Operaciones de pacientes
│   └── vector_db/               # Datos de ChromaDB (no versionado)
│
├── utils/                 # Utilidades y configuración
│   ├── __init__.py
│   └── config.py          # Configuración centralizada
│
├── test/                  # Tests del sistema
│   ├── test_api.py        # Tests de endpoints de API
│   ├── test_whisper.py    # Tests de transcripción
│   ├── test_chroma.py     # Tests de base de datos
│   └── test_chat_gemini.py # Tests del chatbot
│
└── pruebas/               # Archivos de audio de prueba (no versionado)
    ├── p_51994013_222.mp3
    └── p_52015966_552.wav
```

## Configuración Avanzada

### Variables de Entorno
```env
# Google Gemini API
GEMINI_API_KEY=tu_api_key_de_gemini

# Configuración de FFmpeg
FFMPEG_PATH=C:\Program Files\ffmpeg\bin
```

### Configuración de ChromaDB
- **Directorio de persistencia**: `database/vector_db/`
- **Colecciones**: `patients`, `conversations`, `symptoms`
- **Embeddings**: Automáticos con ChromaDB

## Troubleshooting

### Problemas Comunes

1. **Error de FFmpeg**
   - Verificar que FFmpeg esté instalado y en el PATH
   - Configurar ruta manual en `transcription_service.py`

2. **Error de API Key de Gemini**
   - Verificar que `GEMINI_API_KEY` esté en el archivo `.env`
   - Confirmar que la API key sea válida

3. **Error de transcripción**
   - Verificar formato de audio soportado
   - Confirmar que el archivo no esté corrupto

4. **Error de base de datos**
   - Verificar permisos de escritura en `database/vector_db/`
   - Eliminar directorio y reiniciar para recrear colecciones

### Logs y Debugging
- Los logs detallados se muestran en la consola
- Usar `--debug` para información adicional
- Revisar logs de ChromaDB en `database/vector_db/`

## Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

- **Proyecto**: ElSol Challenge - Medical Conversation API
- **Versión**: 1.0.0
- **Última actualización**: Agosto 2025
- **Estado**: Completado y funcional
- **Características implementadas**:
  - Transcripción de audio con Whisper
  - Almacenamiento vectorial con ChromaDB
  - Chatbot inteligente con Google Gemini
  - API REST completa con FastAPI
  - Tests unitarios e integración
  - Documentación profesional sin emojis
  - Código modular y bien documentado