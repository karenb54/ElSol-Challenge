"""
Servicio de chat para el sistema médico
Usa Google Gemini API REST para generar respuestas basadas en datos vectorizados
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
import re

class ChatService:
    """
    Servicio de chat médico que utiliza Google Gemini API REST.
    
    Este servicio proporciona funcionalidad de chatbot inteligente para consultas médicas,
    permitiendo que el LLM decida automáticamente si una pregunta es médica o no,
    y responda de manera contextual usando información vectorizada de pacientes.
    
    Attributes:
        gemini_api_key (str): API key para Google Gemini
        gemini_api_url (str): URL del endpoint de Gemini API REST
    """
    
    def __init__(self):
        # Cargar variables de entorno
        from dotenv import load_dotenv
        load_dotenv()
        
        # Configurar Gemini API REST
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        print(f"API Key de Gemini: {'SÍ' if self.gemini_api_key else 'NO'}")
        
        if self.gemini_api_key:
            print("Configurando Google Gemini API REST...")
            print("Google Gemini API REST configurado correctamente")
        else:
            print("No se encontró GEMINI_API_KEY")



    def generate_response(self, question: str, context_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera una respuesta contextual usando Google Gemini API REST.
        
        Args:
            question (str): Pregunta del usuario
            context_data (List[Dict[str, Any]]): Datos de contexto médico vectorizados
            
        Returns:
            Dict[str, Any]: Respuesta estructurada con:
                - success (bool): Indica si la generación fue exitosa
                - response (str): Respuesta generada por el LLM
                - context_used (int): Número de pacientes usados como contexto
                - model_used (str): Modelo utilizado para la generación
                - timestamp (str): Timestamp de la respuesta
                - error (str, optional): Mensaje de error si ocurrió alguno
        """
        try:
            # Crear prompt inteligente que le permita al LLM decidir
            prompt = self._create_smart_prompt(question, context_data)
            
            # Generar respuesta usando Gemini API REST
            if self.gemini_api_key:
                response = self._generate_gemini_response(prompt)
            else:
                response = "Lo siento, no hay modelos disponibles en este momento."
            
            return {
                "success": True,
                "response": response,
                "context_used": len(context_data),
                "model_used": "Google Gemini API REST" if self.gemini_api_key else "No Model",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error generando respuesta: {e}")
            return {
                "success": False,
                "response": "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta de nuevo.",
                "context_used": 0,
                "model_used": "Error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _create_smart_prompt(self, question: str, context_data: List[Dict[str, Any]]) -> str:
        """
        Crea un prompt inteligente que permite al LLM decidir cómo responder.
        
        Este método construye un prompt específico que instruye al LLM para:
        - Identificar si la pregunta es médica o no
        - Usar información médica solo cuando sea relevante
        - Responder de manera natural para preguntas no médicas
        - Proporcionar respuestas específicas para consultas médicas
        
        Args:
            question (str): Pregunta original del usuario
            context_data (List[Dict[str, Any]]): Datos de contexto médico
            
        Returns:
            str: Prompt estructurado para el LLM
        """
        
        # Preparar contexto médico si existe
        medical_context = ""
        if context_data:
            medical_context = self._prepare_medical_context(context_data)
        
        # Crear prompt más específico y detallado para Gemini
        prompt = f"""Eres un asistente médico inteligente. Tu trabajo es analizar la pregunta del usuario y responder de manera específica y útil usando SOLO la información médica disponible.

PREGUNTA DEL USUARIO: {question}

"""
        
        if medical_context:
            prompt += f"""
INFORMACIÓN MÉDICA DISPONIBLE EN LA BASE DE DATOS:
{medical_context}

INSTRUCCIONES ESPECÍFICAS:
1. SI la pregunta es sobre información médica:
   - Si preguntan "¿cuántos pacientes hay?" → Responde: "Actualmente hay {len(context_data)} pacientes registrados en el sistema"
   - Si preguntan por síntomas de un paciente específico → Busca ese paciente en la información disponible y lista sus síntomas exactos
   - Si preguntan por pacientes con ciertos síntomas → Lista los pacientes que tienen esos síntomas según la información disponible
   - Si preguntan por diagnósticos o medicamentos → Usa la información disponible para responder
   - SIEMPRE usa la información médica disponible para dar respuestas precisas

2. SI la pregunta NO es médica (hora, clima, saludos, etc.):
   - Responde de manera natural sin usar información médica
   - Mantén un tono conversacional y amigable

3. IMPORTANTE:
   - Responde en español
   - Mantén un tono profesional pero amigable
   - Si no encuentras información específica en los datos disponibles, indícalo claramente
   - NO inventes información que no esté en los datos proporcionados

RESPUESTA:"""
        else:
            prompt += f"""
INSTRUCCIONES:
- Si la pregunta es médica, indícalo claramente y menciona que no hay información médica disponible
- Si la pregunta NO es médica, responde de manera natural
- Mantén un tono conversacional y amigable
- Responde en español

RESPUESTA:"""
        
        return prompt

    def _prepare_medical_context(self, context_data: List[Dict[str, Any]]) -> str:
        """Prepara el contexto médico de manera estructurada"""
        if not context_data:
            return "No hay información médica disponible."
        
        context_parts = []
        for i, data in enumerate(context_data[:3]):  # Limitar a 3 pacientes
            metadata = data.get('metadata', {})
            
            patient_info = f"Paciente {i+1}: {metadata.get('patient_name', 'No especificado')}"
            if metadata.get('patient_age'):
                patient_info += f", {metadata.get('patient_age')} años"
            
            symptoms = metadata.get('symptoms_list', '[]')
            if symptoms and symptoms != '[]':
                patient_info += f", Síntomas: {symptoms}"
            
            diagnosis = metadata.get('diagnosis', '')
            if diagnosis:
                patient_info += f", Diagnóstico: {diagnosis}"
            
            medications = metadata.get('medications_list', '[]')
            if medications and medications != '[]':
                patient_info += f", Medicamentos: {medications}"
            
            context_parts.append(patient_info)
        
        return "\n".join(context_parts)

    def _generate_gemini_response(self, prompt: str) -> str:
        """Genera respuesta usando Google Gemini API REST"""
        try:
            # Preparar headers y payload para la API REST
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.gemini_api_key
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # Hacer la petición a la API REST
            response = requests.post(
                self.gemini_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extraer el texto de la respuesta
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    if parts and len(parts) > 0:
                        return parts[0].get('text', '').strip()
                
                return "No se pudo generar una respuesta."
            else:
                print(f"Error en Gemini API REST: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return "Lo siento, hubo un error procesando tu pregunta."
                
        except Exception as e:
            print(f"Error en Gemini API REST: {e}")
            return "Lo siento, hubo un error procesando tu pregunta."



def test_chat_service():
    """Función de prueba para el servicio de chat"""
    print("Probando ChatService...")
    
    chat_service = ChatService()
    
    # Probar diferentes tipos de preguntas
    test_questions = [
        "Hola, ¿cómo estás?",
        "¿Qué hora es?",
        "¿Qué síntomas tiene Juan Pérez?",
        "¿Cuántos pacientes tenemos?",
        "Gracias por tu ayuda"
    ]
    
    for question in test_questions:
        print(f"\nPregunta: {question}")
        
        # Probar generación de respuesta
        mock_context = [{
            "metadata": {
                "patient_name": "Juan Pérez",
                "patient_age": "35",
                "symptoms_list": "fiebre, tos",
                "diagnosis": "Resfriado común"
            }
        }]
        
        response = chat_service.generate_response(question, mock_context)
        print(f"Respuesta: {response['response'][:100]}...")
        print(f"Modelo usado: {response.get('model_used', 'N/A')}")
    
    print("\nPrueba de ChatService completada")

if __name__ == "__main__":
    test_chat_service()
