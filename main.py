"""
ElSol Challenge - Medical Conversation Processing System
Main entry point for the application
"""

import os
import sys
import argparse
import asyncio
import threading
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from services.transcription_service import TranscriptionService
from services.chat_service import ChatService
from database.vector_store_service import VectorStoreService

# Pydantic models for API
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    context_used: int
    model_used: Optional[str] = None
    timestamp: str
    error: Optional[str] = None

class ProcessAudioResponse(BaseModel):
    success: bool
    message: str
    file_saved: str
    patient_name: Optional[str] = None
    vector_id: Optional[str] = None
    error: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="ElSol Challenge - Medical Conversation API",
    description="API para procesar conversaciones médicas y chatbot inteligente",
    version="1.0.0"
)

# Global services
transcription_service = None
vector_service = None
chat_service = None

def initialize_services():
    """Initialize all services"""
    global transcription_service, vector_service, chat_service
    
    print("Inicializando servicios...")
    
    # Initialize transcription service
    transcription_service = TranscriptionService()
    print("Servicio de transcripción inicializado")
    
    # Initialize vector store service
    vector_service = VectorStoreService()
    print("Servicio de almacenamiento vectorial inicializado")
    
    # Initialize chat service
    chat_service = ChatService()
    print("Servicio de chat inicializado")

@app.on_event("startup")
async def startup_event():
    initialize_services()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ElSol Challenge - Medical Conversation API",
        "version": "1.0.0",
        "endpoints": {
            "process_audio": "POST /process-audio - Procesar audio y guardar en ChromaDB",
            "chat": "POST /chat - Hacer preguntas al chatbot médico"
        },
        "documentation": "http://localhost:8000/docs"
    }

@app.post("/process-audio", response_model=ProcessAudioResponse)
async def process_audio_direct(file: UploadFile = File(...), patient_name: Optional[str] = Form(None)):
    """
    Procesa archivo de audio directamente:
    1. Guarda el archivo en la carpeta pruebas/
    2. Procesa la transcripción
    3. Extrae información del paciente (usar patient_name si se proporciona)
    4. Almacena en ChromaDB
    5. Retorna confirmación de guardado exitoso
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg')):
            return ProcessAudioResponse(
                success=False,
                message="Error: Solo se permiten archivos de audio (.wav, .mp3, .m4a, .flac, .ogg)",
                file_saved="",
                error="Tipo de archivo no soportado"
            )
        
        # Create pruebas directory if it doesn't exist
        pruebas_dir = "pruebas"
        os.makedirs(pruebas_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"audio_{timestamp}{file_extension}"
        file_path = os.path.join(pruebas_dir, new_filename)
        
        # Save file to pruebas directory
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"Archivo guardado en: {file_path}")
        
        # Process transcription using the file path
        try:
            print(f"Iniciando transcripción del archivo: {file_path}")
            transcription_result = transcription_service.transcribe_audio(file_path)
            
            print(f"Transcripción completada:")
            print(f"   Texto transcrito: {transcription_result['text'][:200]}...")
            print(f"   Idioma detectado: {transcription_result['language']}")
            print(f"   Duración: {transcription_result['duration']:.2f} segundos")
            
            # Extract patient information from transcription
            print("Extrayendo información del paciente...")
            patient_data = transcription_service.extract_patient_info(transcription_result['text'])
            
            # Override patient name if provided from bot
            if patient_name:
                patient_data['patient_info']['name'] = patient_name.strip()
                print(f"Nombre del paciente override desde bot: {patient_name}")
            
            # Log detailed patient information
            final_patient_name = patient_data.get('patient_info', {}).get('name', 'No detectado')
            print("INFORMACIÓN EXTRAÍDA DEL PACIENTE:")
            print(f"   Nombre: {final_patient_name}")
            print(f"   Edad: {patient_data.get('patient_info', {}).get('age', 'No detectada')}")
            print(f"   Género: {patient_data.get('patient_info', {}).get('gender', 'No detectado')}")
            print(f"   Teléfono: {patient_data.get('patient_info', {}).get('contact_info', {}).get('phone', 'No detectado')}")
            print(f"   Síntomas: {', '.join(patient_data.get('medical_info', {}).get('symptoms', [])) or 'No detectados'}")
            print(f"   Medicamentos: {', '.join(patient_data.get('medical_info', {}).get('medications', [])) or 'No detectados'}")
            print(f"   Prioridad: {patient_data.get('conversation_details', {}).get('priority_level', 'Normal')}")
            print(f"   Seguimiento necesario: {'Sí' if patient_data.get('conversation_details', {}).get('follow_up_needed', False) else 'No'}")
            
            # Store in vector database
            print("Almacenando en base de datos vectorial...")
            vector_id = vector_service.store_patient_data(patient_data)
            print(f"Almacenado exitosamente con ID: {vector_id}")
            
            # Extract patient name for response message
            response_patient_name = patient_data.get('patient_info', {}).get('name', 'Paciente')
            
        except Exception as e:
            return ProcessAudioResponse(
                success=False,
                message="Error en la transcripción del audio",
                file_saved=new_filename,
                error=str(e)
            )
        
        return ProcessAudioResponse(
            success=True,
            message=f"Audio de la paciente {response_patient_name} guardado exitosamente",
            file_saved=new_filename,
            patient_name=response_patient_name,
            vector_id=vector_id
        )
        
    except Exception as e:
        print(f"Error en process-audio: {e}")
        return ProcessAudioResponse(
            success=False,
            message="Error procesando el audio",
            file_saved="",
            error=str(e)
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chatbot médico inteligente que:
    1. Busca información relevante en ChromaDB de manera semántica
    2. Permite que el LLM decida si la pregunta es médica o no
    3. Genera respuestas naturales y contextuales
    
    El LLM decide automáticamente:
    - Si la pregunta es médica → usa información de la base de datos
    - Si la pregunta NO es médica → responde de manera natural (hora, saludos, etc.)
    """
    try:
        print(f"Chatbot recibió pregunta: {request.question}")
        
        # Buscar información relevante de manera simple
        print("Buscando información relevante...")
        context_data = vector_service.search_similar_patients(
            request.question, 
            n_results=5
        )
        
        print(f"Contexto obtenido: {len(context_data)} pacientes")
        
        # Dejar que el LLM decida cómo responder
        response = chat_service.generate_response(request.question, context_data)
        
        print(f"Respuesta generada usando modelo: {response.get('model_used', 'N/A')}")
        
        return ChatResponse(
            success=response['success'],
            response=response['response'],
            context_used=response['context_used'],
            model_used=response.get('model_used'),
            timestamp=response['timestamp'],
            error=response.get('error')
        )
        
    except Exception as e:
        print(f"Error en endpoint chat: {e}")
        return ChatResponse(
            success=False,
            response="Lo siento, hubo un error procesando tu pregunta. Por favor, intenta de nuevo.",
            context_used=0,
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

def main():
    """Main function to run the application"""
    parser = argparse.ArgumentParser(description="ElSol Challenge - Medical Conversation Processing")
    parser.add_argument("--api", action="store_true", help="Run as API server")
    parser.add_argument("--host", default="localhost", help="Host for API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server")

    args = parser.parse_args()

    if args.api:
        print("Starting ElSol Challenge API Server")
        print(f"Server will be available at: http://{args.host}:{args.port}")
        print(f"API Documentation: http://{args.host}:{args.port}/docs")
        
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="info"
        )
    else:
        # Console mode - process test files
        print("Inicializando servicios para modo consola...")
        
        # Initialize services
        transcription_service = TranscriptionService()
        vector_service = VectorStoreService()
        
        # Process test files
        test_files = [
            "pruebas/p_52015966_552.wav",
            "pruebas/p_51994013_222.mp3"
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\nProcesando archivo de prueba: {test_file}")
                
                try:
                    # Transcribe
                    result = transcription_service.transcribe_audio_file(test_file)
                    
                    if result['success']:
                        print("Transcripción exitosa")
                        print(f"Texto: {result['transcription']['text'][:100]}...")
                        
                        # Store in vector database
                        vector_id = vector_service.store_patient_data(result['patient_data'])
                        print(f"Almacenado en vector DB con ID: {vector_id}")
                        
                        # Show patient info
                        patient_info = result['patient_data']['patient_info']
                        print(f"Paciente: {patient_info.get('name', 'No identificado')}")
                        print(f"Edad: {patient_info.get('age', 'No especificada')}")
                        
                    else:
                        print(f"Error en transcripción: {result['error']}")
                        
                except Exception as e:
                    print(f"Error procesando {test_file}: {e}")
            else:
                print(f"Archivo de prueba no encontrado: {test_file}")
        
        print("\nProcesamiento de archivos de prueba completado")

def start_telegram_bot_delayed():
    """Inicia el bot de Telegram con delay para esperar que la API se levante"""
    def run_bot():
        print("⏰ Esperando 10 segundos para que la API se inicialice...")
        time.sleep(10)
        
        try:
            print("🤖 Iniciando Bot de Telegram...")
            from services.telegram_bot import main as bot_main
            bot_main()
        except ImportError:
            print("❌ Error: No se pudo importar services/telegram_bot.py")
            print("   Asegúrate de que telegram_bot.py esté en la carpeta services/")
        except Exception as e:
            print(f"❌ Error ejecutando bot: {e}")
    
    # Ejecutar el bot en un hilo separado
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    return bot_thread

def run_api_with_bot():
    """Ejecuta la API y el bot de Telegram juntos"""
    print("🚀 Iniciando ElSol Challenge - API + Bot de Telegram")
    print("=" * 60)
    
    # Inicializar servicios
    try:
        initialize_services()
        print("✅ Servicios inicializados correctamente")
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        return
    
    # Iniciar bot en hilo separado
    bot_thread = start_telegram_bot_delayed()
    
    print("🌐 Iniciando servidor FastAPI...")
    print("📱 El bot de Telegram se iniciará en 10 segundos...")
    print("\n🔗 URLs disponibles:")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Bot: @ElSolMedicalApi_bot")
    print("\n⚠️  Para detener ambos servicios: Ctrl+C")
    print("=" * 60)
    
    try:
        # Ejecutar FastAPI
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Deteniendo servicios...")
    except Exception as e:
        print(f"❌ Error en servidor: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ElSol Challenge - Sistema de Conversaciones Médicas")
    parser.add_argument("--api", action="store_true", help="Ejecutar solo la API")
    parser.add_argument("--bot", action="store_true", help="Ejecutar API + Bot de Telegram")
    parser.add_argument("--full", action="store_true", help="Ejecutar API + Bot (igual que --bot)")
    
    args = parser.parse_args()
    
    if args.api:
        # Solo API (comportamiento original)
        main()
    elif args.bot or args.full:
        # API + Bot de Telegram
        run_api_with_bot()
    else:
        # Por defecto: API + Bot
        run_api_with_bot()
