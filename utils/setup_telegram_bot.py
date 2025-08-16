#!/usr/bin/env python3
"""
Script de configuración para el Bot de Telegram
Ayuda a configurar el token y verificar el setup
"""

import os
import requests
import sys

def check_env_file():
    """Verifica si existe el archivo .env"""
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        return True
    else:
        print("❌ Archivo .env no encontrado")
        return False

def check_telegram_token():
    """Verifica si el token de Telegram está configurado"""
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        print(f"✅ TELEGRAM_BOT_TOKEN configurado (***{token[-8:]})")
        return True
    else:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return False

def check_api_status():
    """Verifica si la API está ejecutándose"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ API ejecutándose en http://localhost:8000")
            return True
        else:
            print(f"⚠️ API responde pero con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API no disponible en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error verificando API: {e}")
        return False

def setup_telegram_token():
    """Ayuda a configurar el token de Telegram"""
    print("\n📱 Configuración del Bot de Telegram")
    print("=" * 50)
    print("1. Abre Telegram y busca @BotFather")
    print("2. Envía /newbot")
    print("3. Sigue las instrucciones para crear tu bot")
    print("4. Copia el token que te proporciona")
    print("5. Pégalo aquí abajo:")
    print()
    
    token = input("Token del bot: ").strip()
    
    if not token:
        print("❌ Token vacío. Operación cancelada.")
        return False
    
    # Agregar al archivo .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Verificar si ya existe TELEGRAM_BOT_TOKEN
    if 'TELEGRAM_BOT_TOKEN' in env_content:
        # Reemplazar
        lines = env_content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('TELEGRAM_BOT_TOKEN'):
                new_lines.append(f'TELEGRAM_BOT_TOKEN={token}')
            else:
                new_lines.append(line)
        env_content = '\n'.join(new_lines)
    else:
        # Agregar
        if env_content and not env_content.endswith('\n'):
            env_content += '\n'
        env_content += f'TELEGRAM_BOT_TOKEN={token}\n'
    
    # Guardar archivo .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Token guardado en .env")
    return True

def main():
    """Función principal del script de configuración"""
    print("🤖 Setup del Bot de Telegram - ElSol Challenge")
    print("=" * 60)
    
    # Verificar archivo .env
    env_exists = check_env_file()
    if not env_exists:
        print("\n📝 Creando archivo .env...")
        with open('.env', 'w') as f:
            f.write("# Variables de entorno para ElSol Challenge\n")
            f.write("GEMINI_API_KEY=tu_api_key_aqui\n")
            f.write("TELEGRAM_BOT_TOKEN=tu_token_aqui\n")
        print("✅ Archivo .env creado")
    
    # Verificar token de Telegram
    print("\n🔑 Verificando configuración...")
    token_configured = check_telegram_token()
    
    if not token_configured:
        print("\n❓ ¿Quieres configurar el token de Telegram ahora? (s/n)")
        response = input().lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            setup_telegram_token()
            token_configured = check_telegram_token()
    
    # Verificar API
    print("\n🌐 Verificando API...")
    api_running = check_api_status()
    
    # Resumen final
    print("\n📊 Resumen de Configuración:")
    print("=" * 40)
    print(f"📁 Archivo .env: {'✅' if env_exists else '❌'}")
    print(f"🔑 Token Telegram: {'✅' if token_configured else '❌'}")
    print(f"🌐 API ElSol: {'✅' if api_running else '❌'}")
    
    if token_configured and api_running:
        print("\n🎉 ¡Todo listo! Puedes ejecutar el bot:")
        print("   python telegram_bot.py")
    else:
        print("\n⚠️ Configuración incompleta:")
        if not token_configured:
            print("   - Configura TELEGRAM_BOT_TOKEN en .env")
        if not api_running:
            print("   - Ejecuta la API: python main.py --api")
    
    print("\n📚 Comandos del bot:")
    print("   /start - Iniciar el bot")
    print("   /help - Mostrar ayuda")
    print("   /chat <pregunta> - Consulta médica")
    print("   /stats - Estadísticas del sistema")
    print("   Enviar audio - Transcribir conversación")

if __name__ == "__main__":
    main()
