"""
Script para probar el chat con Gemini usando la API
"""

import requests
import json
import time

def wait_for_api():
    """Espera a que la API esté disponible"""
    print("⏳ Esperando a que la API esté disponible...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            if response.status_code == 200:
                print("✅ API disponible")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ Intento {i+1}/30...")
    
    print("❌ API no disponible después de 30 intentos")
    return False

def test_chat_question(question):
    """Prueba una pregunta específica en el chat"""
    print(f"\n📝 Pregunta: {question}")
    
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Respuesta: {result.get('response', 'Sin respuesta')}")
            print(f"🔧 Modelo usado: {result.get('model_used', 'N/A')}")
            print(f"📊 Contexto usado: {result.get('context_used', 0)} pacientes")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")

def main():
    print("🧪 Probando Chat con Gemini...")
    
    if not wait_for_api():
        return
    
    # Preguntas de prueba
    test_questions = [
        "¿Cuántos pacientes hay?",
        "¿Qué síntomas tiene Juan Pérez?",
        "¿Qué pacientes tienen fiebre?",
        "¿Cuál es el diagnóstico de María García?",
        "¿Qué hora es?",
        "Hola, ¿cómo estás?",
        "¿Qué medicamentos toma Carlos López?",
        "¿Hay pacientes con diabetes?"
    ]
    
    for question in test_questions:
        test_chat_question(question)
        time.sleep(1)  # Pausa entre preguntas
    
    print("\n✅ Prueba de Chat con Gemini completada")

if __name__ == "__main__":
    main()
