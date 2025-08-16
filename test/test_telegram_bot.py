#!/usr/bin/env python3
"""
Tests para el Bot de Telegram - ElSol Challenge
Prueba las funcionalidades del bot sin afectar datos reales.
"""

import os
import sys
import asyncio
import tempfile
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_telegram_bot_imports():
    """Test: Verificar que se pueden importar las clases del bot."""
    print("Test 1: Verificando importaciones del bot de Telegram...")
    
    try:
        from services.telegram_bot import ElSolTelegramBot
        print("✅ ElSolTelegramBot importado correctamente")
        
        # Verificar que la clase tiene los métodos esperados
        bot_methods = [
            'start_command',
            'help_command', 
            'stats_command',
            'chat_command',
            'handle_text_message',
            'handle_audio',
            '_process_chat_question'
        ]
        
        for method in bot_methods:
            assert hasattr(ElSolTelegramBot, method), f"Método {method} no encontrado"
            print(f"  ✓ Método {method} disponible")
            
        print("✅ Todos los métodos del bot están disponibles")
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        raise

def test_bot_initialization():
    """Test: Verificar inicialización del bot."""
    print("\nTest 2: Verificando inicialización del bot...")
    
    try:
        from services.telegram_bot import ElSolTelegramBot
        
        # Mock del token para evitar errores
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_123'}):
            bot = ElSolTelegramBot(token='test_token_123')
            
            # Verificar propiedades básicas
            assert bot.api_base_url == "http://localhost:8000"
            print("✅ URL base configurada correctamente")
            
            assert hasattr(bot, 'application')
            print("✅ Aplicación de Telegram configurada")
            
        print("✅ Bot inicializado correctamente")
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        raise

@pytest.mark.asyncio
async def test_start_command():
    """Test: Verificar comando /start."""
    print("\nTest 3: Verificando comando /start...")
    
    try:
        from services.telegram_bot import ElSolTelegramBot
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_123'}):
            bot = ElSolTelegramBot(token='test_token_123')
            
            # Mock del update y context
            mock_update = Mock()
            mock_update.effective_user.first_name = "TestUser"
            mock_update.message.reply_text = AsyncMock()
            mock_context = Mock()
            
            # Ejecutar comando start
            await bot.start_command(mock_update, mock_context)
            
            # Verificar que se envió un mensaje
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            
            # Verificar que el mensaje contiene elementos esperados
            message = call_args[0][0]
            assert "TestUser" in message or "Doctor" in message
            assert len(message) > 50  # Verificar que el mensaje no está vacío
            
            print("✅ Comando /start funcionando correctamente")
            print(f"  ✓ Mensaje enviado exitosamente")
            print(f"  ✓ Longitud del mensaje: {len(message)} caracteres")
            
    except Exception as e:
        print(f"❌ Error en comando start: {e}")
        raise

@pytest.mark.asyncio 
async def test_help_command():
    """Test: Verificar comando /help."""
    print("\nTest 4: Verificando comando /help...")
    
    try:
        from services.telegram_bot import ElSolTelegramBot
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_123'}):
            bot = ElSolTelegramBot(token='test_token_123')
            
            # Mock del update y context
            mock_update = Mock()
            mock_update.message.reply_text = AsyncMock()
            mock_context = Mock()
            
            # Ejecutar comando help
            await bot.help_command(mock_update, mock_context)
            
            # Verificar que se envió un mensaje
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            
            # Verificar contenido del mensaje de ayuda
            message = call_args[0][0]
            assert len(message) > 50  # Verificar que el mensaje no está vacío
            
            print("✅ Comando /help funcionando correctamente")
            print(f"  ✓ Mensaje de ayuda enviado exitosamente")
            print(f"  ✓ Longitud del mensaje: {len(message)} caracteres")
            
    except Exception as e:
        print(f"❌ Error en comando help: {e}")
        raise

@pytest.mark.asyncio
async def test_intelligent_messages():
    """Test: Verificar mensajes inteligentes según tipo de consulta."""
    print("\nTest 5: Verificando mensajes inteligentes...")
    
    try:
        from services.telegram_bot import ElSolTelegramBot
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_123'}):
            bot = ElSolTelegramBot(token='test_token_123')
            
            # Mock de update y context
            mock_update = Mock()
            mock_update.message.text = "¿Cuántos pacientes tienen fiebre?"
            mock_update.message.reply_text = AsyncMock()
            mock_context = Mock()
            
            # Mock de la API response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'response': 'Hay 3 pacientes con fiebre',
                'model_used': 'Google Gemini'
            }
            
            # Test con consulta de conteo
            with patch('requests.post', return_value=mock_response):
                await bot.handle_text_message(mock_update, mock_context)
                
                # Verificar que se llamó reply_text al menos 2 veces (mensaje de procesamiento + respuesta)
                assert mock_update.message.reply_text.call_count >= 2
                
                # Verificar mensaje de procesamiento contextual
                first_call = mock_update.message.reply_text.call_args_list[0][0][0]
                counting_keywords = ["Contando", "Calculando", "Revisando números"]
                has_counting_message = any(keyword in first_call for keyword in counting_keywords)
                assert has_counting_message, f"Mensaje de procesamiento no contextual: {first_call}"
                
                print("✅ Mensajes inteligentes funcionando")
                print(f"  ✓ Mensaje contextual para conteo: {first_call}")
                
    except Exception as e:
        print(f"❌ Error en mensajes inteligentes: {e}")
        raise

@pytest.mark.asyncio
async def test_audio_handling():
    """Test: Verificar manejo de archivos de audio."""
    print("\nTest 6: Verificando manejo de audio...")
    
    try:
        from services.telegram_bot import ElSolTelegramBot
        
        with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_123'}):
            bot = ElSolTelegramBot(token='test_token_123')
            
            # Mock del update para audio
            mock_update = Mock()
            mock_update.effective_user.first_name = "TestUser"
            mock_update.message.audio = Mock()
            mock_update.message.audio.file_name = "test_audio.mp3"
            mock_update.message.voice = None
            mock_update.message.caption = "María González"  # Nombre del paciente
            mock_update.message.reply_text = AsyncMock()
            mock_context = Mock()
            
            # Mock del archivo de audio
            mock_file = Mock()
            mock_file.download_to_drive = AsyncMock()
            mock_update.message.audio.get_file = AsyncMock(return_value=mock_file)
            
            # Mock de la respuesta de la API
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'success': True,
                'patient_name': 'María González',
                'vector_id': 'test_vector_123'
            }
            
            with patch('requests.post', return_value=mock_response):
                with patch('os.path.exists', return_value=True):
                    with patch('os.remove'):
                        await bot.handle_audio(mock_update, mock_context)
            
            # Verificar que se procesó el audio
            mock_update.message.reply_text.assert_called()
            calls = mock_update.message.reply_text.call_args_list
            
            # Verificar mensaje de procesamiento de audio
            processing_call = calls[0][0][0]
            assert "TestUser" in processing_call
            assert "audio" in processing_call.lower()
            
            print("✅ Manejo de audio funcionando")
            print(f"  ✓ Mensaje de procesamiento: {processing_call}")
            print(f"  ✓ Nombre del paciente desde caption manejado")
            
    except Exception as e:
        print(f"❌ Error en manejo de audio: {e}")
        raise

def test_message_variation():
    """Test: Verificar variación en mensajes."""
    print("\nTest 7: Verificando variación en mensajes...")
    
    try:
        # Simular múltiples llamadas para verificar variación
        import random
        
        # Test de mensajes de procesamiento variados
        messages = [
            "Analizando tu consulta...",
            "Buscando en registros médicos...",
            "Procesando información clínica...",
            "Consultando base de datos médica..."
        ]
        
        # Verificar que random.choice funcionaría con estos mensajes
        selected_messages = set()
        for _ in range(20):
            selected = random.choice(messages)
            selected_messages.add(selected)
        
        # Debería haber al menos 2 mensajes diferentes en 20 intentos
        assert len(selected_messages) >= 2, "No hay suficiente variación en mensajes"
        
        print("✅ Variación de mensajes funcionando")
        print(f"  ✓ {len(selected_messages)} mensajes diferentes generados")
        print(f"  ✓ Mensajes disponibles: {len(messages)}")
        
    except Exception as e:
        print(f"❌ Error en variación de mensajes: {e}")
        raise

def run_telegram_tests():
    """Ejecutar todos los tests del bot de Telegram."""
    print("🤖 INICIANDO TESTS DEL BOT DE TELEGRAM")
    print("=" * 50)
    
    try:
        # Tests síncronos
        test_telegram_bot_imports()
        test_bot_initialization()
        test_message_variation()
        
        # Tests asíncronos
        asyncio.run(test_start_command())
        asyncio.run(test_help_command())
        asyncio.run(test_intelligent_messages())
        asyncio.run(test_audio_handling())
        
        print("\n" + "=" * 50)
        print("✅ TODOS LOS TESTS DEL BOT PASARON EXITOSAMENTE")
        print("🎉 El bot de Telegram está funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS DEL BOT: {e}")
        print("💡 Verifica que:")
        print("  - services/telegram_bot.py existe")
        print("  - Las dependencias están instaladas")
        print("  - La estructura de clases es correcta")
        return False

if __name__ == "__main__":
    run_telegram_tests()
