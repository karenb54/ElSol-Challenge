#!/usr/bin/env python3
"""
Script completo para probar la API de ElSol Challenge
Incluye pruebas para todos los endpoints y tipos de preguntas
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "health": f"{BASE_URL}/",
    "process_audio": f"{BASE_URL}/process-audio",
    "chat": f"{BASE_URL}/chat"
}

def wait_for_api():
    """Espera a que la API esté lista"""
    print("Waiting for API to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(API_ENDPOINTS["health"], timeout=5)
            if response.status_code == 200:
                print("API is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    print("API not ready after 30 seconds")
    return False

def test_api_health():
    """Prueba el endpoint de salud de la API"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(API_ENDPOINTS["health"])
        if response.status_code == 200:
            data = response.json()
            print("API Health: OK")
            print(f"Message: {data.get('message', 'N/A')}")
            print(f"Documentation: {data.get('documentation', 'N/A')}")
            return True
        else:
            print(f"API Health: Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"API Health: Error - {e}")
        return False

def test_process_audio():
    """Prueba el endpoint de procesamiento de audio"""
    print("Testing Process Audio...")
    try:
        # Usar un archivo de audio de prueba
        audio_file = "pruebas/p_52015966_552.wav"
        
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(API_ENDPOINTS["process_audio"], files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("Process Audio: Success")
            print(f"Message: {data.get('message', 'N/A')}")
            print(f"File Saved: {data.get('file_saved', 'N/A')}")
            print(f"Patient: {data.get('patient_name', 'N/A')}")
            print(f"Vector ID: {data.get('vector_id', 'N/A')}")
            return True
        else:
            print(f"Process Audio: Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Process Audio: Error - {e}")
        return False

def test_chat():
    """Prueba el endpoint de chat con diferentes tipos de preguntas"""
    print("Testing Chat...")
    
    # Lista de preguntas para probar diferentes tipos
    test_questions = [
        # Preguntas básicas
        "Hola, ¿qué día es hoy?",
        
        # Preguntas sobre pacientes específicos
        "¿Qué síntomas tiene Juan Pérez?",
        "¿Qué enfermedad tiene Pepito Gómez?",
        
        # Preguntas sobre síntomas
        "¿Qué pacientes reportaron fiebre en julio?",
        "Listame los pacientes con diabetes",
        
        # Preguntas por fecha
        "Que pacientes vinieron el 05 de mayo",
        
        # Preguntas de estadísticas
        "cuantos casos de diabetes hemos tenido",
        
        # Preguntas de planes de cuidado
        "Créame un Plan de cuidado para Juan Pérez.",
        
        # Preguntas generales
        "¿Qué pacientes tenemos registrados?",
        "Muéstrame estadísticas de todos los pacientes"
    ]
    
    success_count = 0
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nPrueba {i}: {question[:50]}...")
        
        try:
            payload = {"question": question}
            response = requests.post(
                API_ENDPOINTS["chat"], 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("Chat: Success")
                print(f"Response: {data.get('response', 'N/A')[:100]}...")
                print(f"Context Used: {data.get('context_used', 0)}")
                print(f"Model: {data.get('model_used', 'N/A')}")
                success_count += 1
            else:
                print(f"Chat: Failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Chat: Error - {e}")
    
    print(f"\n Chat Tests: {success_count}/{len(test_questions)} passed")
    return success_count > 0

def print_curl_examples():
    """Imprime ejemplos de comandos curl para testing manual"""
    print("\n" + "=" * 60)
    print("CURL COMMANDS FOR MANUAL TESTING")
    print("=" * 60)
    
    print("\n1. 🏥 API Health:")
    print(f'curl -X GET "{API_ENDPOINTS["health"]}"')
    
    print("\n2. Process Audio:")
    print(f'curl -X POST "{API_ENDPOINTS["process_audio"]}" \\')
    print('     -F "file=@pruebas/p_52015966_552.wav"')
    
    print("\n3. Chat with AI:")
    print(f'curl -X POST "{API_ENDPOINTS["chat"]}" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"question": "¿Qué síntomas tiene Juan Pérez?"}\'')
    
    print("\n4. Chat - Plan de Cuidado:")
    print(f'curl -X POST "{API_ENDPOINTS["chat"]}" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"question": "Créame un Plan de cuidado para Juan Pérez"}\'')
    
    print("\n5. Chat - Estadísticas:")
    print(f'curl -X POST "{API_ENDPOINTS["chat"]}" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"question": "cuantos casos de diabetes hemos tenido"}\'')
    
    print("\n6. Chat - Búsqueda por Fecha:")
    print(f'curl -X POST "{API_ENDPOINTS["chat"]}" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"question": "Que pacientes vinieron el 05 de mayo"}\'')

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("Starting ElSol Challenge API Tests")
    print("=" * 60)
    
    # Esperar a que la API esté lista
    if not wait_for_api():
        return False
    
    # Ejecutar pruebas
    tests = [
        ("API Health", test_api_health),
        ("Process Audio", test_process_audio),
        ("Chat", test_chat)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        print()
    
    # Resultados
    print("=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed < total:
        print("Some tests failed. Check the API server and configuration.")
    
    # Mostrar ejemplos de curl
    print_curl_examples()
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
