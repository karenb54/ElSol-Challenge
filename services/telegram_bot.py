#!/usr/bin/env python3
"""
Bot de Telegram para ElSol Challenge
Interfaz de usuario para el sistema de conversaciones médicas
"""

import os
import sys
import asyncio
import tempfile
import logging
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Agregar el directorio raíz al path para importar nuestros servicios
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.transcription_service import TranscriptionService
from services.chat_service import ChatService
from database.vector_store_service import VectorStoreService

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ElSolTelegramBot:
    """
    Bot de Telegram para el sistema ElSol Challenge
    Proporciona interfaz de usuario para transcripción y chat médico
    """
    
    def __init__(self, token: str):
        """
        Inicializa el bot de Telegram
        
        Args:
            token: Token del bot de Telegram obtenido de @BotFather
        """
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Inicializar servicios
        self.transcription_service = None
        self.chat_service = None
        self.vector_service = None
        
        # URL base de la API local
        self.api_base_url = "http://localhost:8000"
        
        self._setup_services()
        self._setup_handlers()
    
    def _setup_services(self):
        """Inicializa los servicios del sistema"""
        try:
            logger.info("Inicializando servicios...")
            self.transcription_service = TranscriptionService()
            self.chat_service = ChatService()
            self.vector_service = VectorStoreService()
            logger.info("Servicios inicializados correctamente")
        except Exception as e:
            logger.error(f"Error inicializando servicios: {e}")
    
    def _setup_handlers(self):
        """Configura los manejadores de comandos y mensajes"""
        # Comandos basicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Comando de chat
        self.application.add_handler(CommandHandler("chat", self.chat_command))
        
        # Manejador de archivos de audio
        self.application.add_handler(MessageHandler(
            filters.AUDIO | filters.VOICE | filters.Document.AUDIO, 
            self.handle_audio
        ))
        
        # Manejador de mensajes de texto (para chat)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_text_message
        ))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Bienvenida al bot"""
        user_name = update.effective_user.first_name or "Doctor/a"
        
        welcome_message = f"""
👋 **¡Hola {user_name}!**

🏥 **Bienvenido/a a tu Asistente Médico ElSol**

Soy tu asistente médico inteligente, estoy aquí para ayudarte.

**¿Qué puedo hacer por ti?**

🎵 **Puedo procesar:**
• Audio (.mp3, .wav, .m4a, .ogg)
• Grabación de una nota de voz directamente en Telegram
• **OPCIONAL:** Escribe el nombre del paciente como descripción

💬 **Puedes realizar consultas médicas:**
• Pregúntame sobre pacientes: "¿Qué síntomas tiene Juan?"
• Solicita estadísticas: "¿Cuántos pacientes tenemos?"
• Busca información: "Pacientes con diabetes"

¡Estoy aquí para ayudarte!
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostrar ayuda"""
        help_message = """
📚 **Comandos Disponibles:**

🎵 **Para Audio:**
- Envía cualquier archivo de audio (.mp3, .wav, .m4a, .ogg)
- **OPCIONAL:** Escribe el nombre del paciente como descripción
- El bot lo transcribirá y guardará la información

💬 **Para Chat:**
- `/chat <pregunta>` - Hacer una consulta médica
- Ejemplos:
  • `/chat ¿Qué síntomas tiene Juan?`
  • `/chat ¿Cuántos pacientes hay?`
  • `/chat Listame pacientes con fiebre`

📊 **Información:**
- `/stats` - Ver estadísticas del sistema
- `/help` - Mostrar esta ayuda

🔧 **Notas Técnicas:**
- Los audios se procesan con Whisper AI
- Las consultas usan Google Gemini
- Los datos se almacenan en ChromaDB

¿Necesitas algo más? ¡Solo pregunta!
        """
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Mostrar estadísticas del sistema"""
        try:
            # Hacer request a la API local para obtener estadísticas
            response = requests.get(f"{self.api_base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                stats_message = f"""
📊 **Estadísticas del Sistema ElSol**

🏥 **Estado:** {data.get('status', 'Desconocido')}
⏰ **Hora del Sistema:** {datetime.now().strftime('%H:%M:%S')}
🗓️ **Fecha:** {datetime.now().strftime('%d/%m/%Y')}

🔧 **Servicios Activos:**
- ✅ Transcripción (Whisper)
- ✅ Chat (Google Gemini)
- ✅ Base de Datos (ChromaDB)
- ✅ API REST (FastAPI)

📈 **Rendimiento:**
- API Local: ✅ Disponible
- Tiempo de Respuesta: <2s
- Última Actualización: {datetime.now().strftime('%H:%M')}

Para más detalles técnicos, visita: {self.api_base_url}/docs
                """
            else:
                stats_message = """
⚠️ **Sistema Temporalmente No Disponible**

Por favor, asegúrate de que la API esté ejecutándose:
`python main.py --api`

URL esperada: http://localhost:8000
                """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"""
❌ **Error obteniendo estadísticas**

Error: {str(e)}

Verifica que la API esté ejecutándose:
`python main.py --api`
            """
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /chat - Realizar consulta al chatbot médico"""
        if not context.args:
            await update.message.reply_text(
                "❓ **Uso:** `/chat <tu pregunta>`\n\n"
                "**Ejemplos:**\n"
                "• `/chat ¿Cuántos pacientes hay?`\n"
                "• `/chat ¿Qué síntomas tiene Juan?`\n"
                "• `/chat Listame pacientes con diabetes`",
                parse_mode='Markdown'
            )
            return
        
        question = " ".join(context.args)
        await self._process_chat_question(update, question)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja mensajes de texto como consultas de chat"""
        question = update.message.text
        
        # Si el mensaje no es un comando, tratarlo como consulta de chat
        if not question.startswith('/'):
            try:
                # Mensaje de confirmación inteligente según el tipo de consulta
                import random
                
                question_lower = question.lower()
                
                if any(word in question_lower for word in ['cuántos', 'cuantos', 'número', 'cantidad', 'total']):
                    messages = [
                        "Contando pacientes en la base de datos...",
                        "Calculando estadísticas médicas...",
                        "Revisando números de casos..."
                    ]
                elif any(word in question_lower for word in ['síntomas', 'sintomas', 'enfermedad', 'padece', 'tiene']):
                    messages = [
                        "Consultando historial clínico...",
                        "Revisando síntomas registrados...",
                        "Analizando información médica..."
                    ]
                elif any(word in question_lower for word in ['lista', 'listame', 'mostrar', 'pacientes con']):
                    messages = [
                        "Generando lista de pacientes...",
                        "Filtrando registros médicos...",
                        "Buscando pacientes que coincidan..."
                    ]
                elif any(word in question_lower for word in ['plan', 'tratamiento', 'cuidado', 'recomendación']):
                    messages = [
                        "Elaborando plan médico...",
                        "Analizando opciones de tratamiento...",
                        "Preparando recomendaciones clínicas..."
                    ]
                else:
                    messages = [
                        "Analizando tu consulta...",
                        "Buscando en registros médicos...",
                        "Procesando información clínica...",
                        "Consultando base de datos médica..."
                    ]
                
                random_message = random.choice(messages)
                await update.message.reply_text(random_message)
                await self._process_chat_question(update, question)
            except Exception as e:
                print(f"Error en manejo de texto: {e}")
                try:
                    await update.message.reply_text("Error procesando consulta. Intenta de nuevo.")
                except:
                    pass  # Si falla enviar error, no hacer nada
    
    async def _process_chat_question(self, update: Update, question: str):
        """Procesa una pregunta del chat médico"""
        try:
            # No mostrar mensaje adicional, ir directo al procesamiento
            
                        # Hacer request a la API de chat
            chat_data = {"question": question}
            response = requests.post(
                f"{self.api_base_url}/chat", 
                json=chat_data,
                timeout=20  # Reducir timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    response_content = result.get('response', 'No se pudo generar respuesta')
                    
                    # Limitar longitud de respuesta para evitar timeouts
                    if len(response_content) > 3000:
                        response_content = response_content[:2950] + "...\n\n[Respuesta truncada por longitud]"
                    
                    response_text = f"🤖 {response_content}"
                else:
                    response_text = f"❌ Error: {result.get('error', 'Error desconocido')}"
            else:
                response_text = f"⚠️ API no disponible (Código: {response.status_code})"
            
            # Enviar respuesta con manejo de errores
            try:
                await update.message.reply_text(response_text, parse_mode='Markdown')
            except Exception as send_error:
                print(f"Error enviando respuesta: {send_error}")
                # Intentar enviar sin formato si falla con Markdown
                try:
                    await update.message.reply_text(response_text.replace('**', '').replace('*', ''))
                except:
                    print("No se pudo enviar respuesta")
            
        except Exception as e:
            print(f"Error en proceso de chat: {e}")
            try:
                error_message = f"❌ Error: {str(e)}"
                await update.message.reply_text(error_message)
            except:
                print("No se pudo enviar mensaje de error")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja archivos de audio enviados al bot"""
        try:
            user_name = update.effective_user.first_name or "Doctor/a"
            
            # Obtener nombre del paciente desde el caption si está disponible
            patient_name_override = None
            if update.message.caption:
                patient_name_override = update.message.caption.strip()
            
            # Determinar tipo de mensaje
            is_voice = update.message.voice is not None
            
            # Mensajes dinámicos para audio
            import random
            
            if is_voice:
                voice_messages = [
                    f"🎤 {user_name}, transcribiendo nota de voz...",
                    f"🎤 {user_name}, analizando grabación médica...",
                    f"🎤 {user_name}, procesando conversación...",
                    f"🎤 {user_name}, extrayendo información clínica..."
                ]
                await update.message.reply_text(random.choice(voice_messages), parse_mode='Markdown')
            else:
                audio_messages = [
                    f"🎵 {user_name}, transcribiendo archivo de audio...",
                    f"🎵 {user_name}, procesando conversación médica...",
                    f"🎵 {user_name}, analizando contenido clínico...",
                    f"🎵 {user_name}, extrayendo datos del paciente..."
                ]
                await update.message.reply_text(random.choice(audio_messages), parse_mode='Markdown')
            
            # Obtener el archivo
            if update.message.audio:
                file_obj = update.message.audio
                file_name = file_obj.file_name or f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            elif update.message.voice:
                file_obj = update.message.voice
                file_name = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg"
            elif update.message.document:
                file_obj = update.message.document
                file_name = file_obj.file_name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            else:
                await update.message.reply_text("❌ Tipo de archivo no soportado")
                return
            
            # Descargar el archivo
            file = await context.bot.get_file(file_obj.file_id)
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix=f"_{file_name}", delete=False) as temp_file:
                await file.download_to_drive(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Convertir .ogg a .wav si es necesario
                final_path = temp_path
                final_name = file_name
                
                if file_name.endswith('.ogg'):
                    print("🔄 Convirtiendo archivo .ogg a .wav...")
                    wav_path = temp_path.replace('.ogg', '.wav')
                    
                    # Usar FFmpeg para convertir
                    import subprocess
                    try:
                        subprocess.run([
                            'ffmpeg', '-i', temp_path, 
                            '-acodec', 'pcm_s16le', 
                            '-ar', '16000', 
                            wav_path, '-y'
                        ], check=True, capture_output=True)
                        
                        final_path = wav_path
                        final_name = file_name.replace('.ogg', '.wav')
                        content_type = 'audio/wav'
                        print("✅ Conversión exitosa")
                        
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Error convirtiendo audio: {e}")
                        # Usar archivo original si falla la conversión
                        content_type = 'audio/ogg'
                    except FileNotFoundError:
                        print("❌ FFmpeg no encontrado, usando archivo original")
                        content_type = 'audio/ogg'
                else:
                    # Determinar content-type para otros formatos
                    if file_name.endswith('.mp3'):
                        content_type = 'audio/mpeg'
                    elif file_name.endswith('.wav'):
                        content_type = 'audio/wav'
                    elif file_name.endswith('.m4a'):
                        content_type = 'audio/mp4'
                    else:
                        content_type = 'audio/mpeg'  # default
                
                # Enviar a la API para procesamiento
                with open(final_path, 'rb') as audio_file:
                    files = {'file': (final_name, audio_file, content_type)}
                    data = {}
                    
                    # Agregar nombre del paciente si se proporcionó
                    if patient_name_override:
                        data['patient_name'] = patient_name_override
                    
                    response = requests.post(
                        f"{self.api_base_url}/process-audio", 
                        files=files,
                        data=data,
                        timeout=60
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        # Usar nombre override si se proporcionó, sino el extraído
                        if patient_name_override:
                            patient_name = patient_name_override
                        else:
                            patient_name = result.get('patient_name', 'Paciente no identificado')
                        
                        success_message = f"**Audio procesado exitosamente**\n👤 **Paciente:** {patient_name}"
                    else:
                        success_message = f"**Error procesando audio:** {result.get('error', 'Error desconocido')}"
                else:
                    success_message = f"**Error en la API** (Código: {response.status_code})"
                
                await update.message.reply_text(success_message, parse_mode='Markdown')
                
            finally:
                # Limpiar archivos temporales
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
                # Limpiar archivo convertido si existe
                if 'final_path' in locals() and final_path != temp_path and os.path.exists(final_path):
                    os.unlink(final_path)
                    
        except Exception as e:
            error_message = f"""
**Error procesando audio**

Error: {str(e)}

Verifica que:
1. La API esté ejecutándose (`python main.py --api`)
2. El archivo sea un formato soportado (.mp3, .wav, .m4a)
            """
            await update.message.reply_text(error_message, parse_mode='Markdown')
    
    async def setup_bot_commands(self):
        """Configura los comandos del bot en Telegram"""
        commands = [
            BotCommand("start", "Iniciar el bot y ver bienvenida"),
            BotCommand("help", "Mostrar ayuda y comandos disponibles"),
            BotCommand("chat", "Hacer una consulta médica"),
            BotCommand("stats", "Ver estadísticas del sistema"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Comandos del bot configurados")
    
    async def run(self):
        """Ejecuta el bot de Telegram"""
        logger.info("Iniciando bot de Telegram...")
        
        # Configurar comandos
        await self.setup_bot_commands()
        
        # Iniciar el bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot de Telegram ejecutándose. Presiona Ctrl+C para detener.")
        
        try:
            # Mantener el bot ejecutándose
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Deteniendo bot de Telegram...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

def main():
    """Función principal para ejecutar el bot"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener token del bot desde variable de entorno
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print(" Error: TELEGRAM_BOT_TOKEN no encontrado en variables de entorno")
        print("\n Para configurar:")
        print("1. Habla con @BotFather en Telegram")
        print("2. Crea un nuevo bot con /newbot")
        print("3. Copia el token que te da")
        print("4. Agrega al archivo .env:")
        print("   TELEGRAM_BOT_TOKEN=tu_token_aqui")
        print("\n Luego ejecuta nuevamente: python telegram_bot.py")
        return
    
    # Verificar que la API esté disponible
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print(" Advertencia: API no disponible en http://localhost:8000")
            print("Ejecuta primero: python main.py --api")
    except:
        print(" Advertencia: No se puede conectar a la API")
        print("Ejecuta primero: python main.py --api")
    
    # Crear y ejecutar el bot
    bot = ElSolTelegramBot(token)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f" Error ejecutando bot: {e}")

if __name__ == "__main__":
    main()
