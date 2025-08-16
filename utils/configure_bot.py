#!/usr/bin/env python3
"""
Script para configurar el token del bot de Telegram
"""

import os

def configure_telegram_token():
    """Configura el token de Telegram en el archivo .env"""
    token = "8200173365:AAE4CywZfVch4BOum8_o_E9JQTUr9XxTw5A"
    
    # Leer archivo .env actual
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Agregar token si no existe
    if 'TELEGRAM_BOT_TOKEN' not in env_content:
        if env_content and not env_content.endswith('\n'):
            env_content += '\n'
        env_content += f'TELEGRAM_BOT_TOKEN={token}\n'
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Token de Telegram configurado en .env")
        print(f"🤖 Bot: @ElSolMedicalApi_bot")
        print(f"🔗 Link: https://t.me/ElSolMedicalApi_bot")
    else:
        print("ℹ️ Token ya está configurado")

if __name__ == "__main__":
    configure_telegram_token()
