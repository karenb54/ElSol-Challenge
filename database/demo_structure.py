"""
Demo de la estructura de datos en Chroma
Muestra exactamente cómo se almacena la información
"""

def show_chroma_structure():
    """Muestra la estructura de datos que se almacena en Chroma"""
    
    print("🗄️ ESTRUCTURA DE ALMACENAMIENTO EN CHROMA")
    print("=" * 60)
    
    print("\n📊 1. INFORMACIÓN ESTRUCTURADA (Metadatos)")
    print("-" * 50)
    structured_info = {
        # Información del paciente
        "patient_name": "Juana De La Torre",
        "patient_age": 45,
        "patient_gender": "femenino",
        "patient_phone": "+1234567890",
        
        # Información médica estructurada
        "diagnosis": "Posible resfriado común (basado en síntomas)",
        "symptoms_list": '["fiebre", "dolor de cabeza", "tos"]',
        "medications_list": '[]',
        "allergies_list": '[]',
        "chronic_conditions": '[]',
        
        # Información de la conversación
        "conversation_id": "conv_20250815_204723",
        "conversation_date": "2025-08-15T20:47:23.867442",
        "promoter_id": "promoter_001",
        "priority_level": "normal",
        "follow_up_needed": True,
        
        # Metadatos técnicos
        "stored_at": "2025-08-15T20:47:23.867442",
        "conversation_type": "initial_contact"
    }
    
    for key, value in structured_info.items():
        print(f"  📋 {key}: {value}")
    
    print("\n💬 2. INFORMACIÓN NO ESTRUCTURADA (Documento Vectorizado)")
    print("-" * 50)
    unstructured_text = """
    INFORMACIÓN DEL PACIENTE:
    Paciente Juana De La Torre de 45 años, género femenino.
    
    SÍNTOMAS Y CONTEXTO CONVERSACIONAL:
    El paciente presenta: fiebre, dolor de cabeza, tos
    
    CONTEXTO MÉDICO:
    Medicamentos mencionados: ninguno mencionado
    Alergias conocidas: no mencionadas
    Condiciones crónicas: no mencionadas
    
    TRANSCRIPCIÓN COMPLETA DE LA CONVERSACIÓN:
    Hola, mi nombre es Juana de la Torre tengo 45 años y desde hace tres días 
    tengo fiebre, dolor de cabeza y tengo muchatos. Tuve contacto con una persona 
    que estaba enferma pero no sé qué tenía. Y pues quiero saber cómo puedo cuidarme.
    
    OBSERVACIONES Y CONTEXTO:
    Prioridad de atención: normal
    Tipo de conversación: contacto inicial
    Necesita seguimiento: Sí
    Promotor: promoter_001
    Fecha de la conversación: 2025-08-15T20:47:23.867442
    
    ANÁLISIS CONTEXTUAL:
    Este paciente se encuentra en una consulta de contacto inicial con síntomas 
    que sugieren Posible resfriado común (basado en síntomas).
    """
    
    print(unstructured_text)
    
    print("\n🔍 3. CAPACIDADES DE BÚSQUEDA")
    print("-" * 50)
    search_capabilities = [
        "🔎 Búsqueda por síntomas específicos",
        "🔎 Búsqueda por nombre de paciente",
        "🔎 Búsqueda por rango de edad",
        "🔎 Búsqueda por prioridad médica",
        "🔎 Búsqueda semántica (contexto natural)",
        "🔎 Búsqueda por fecha de conversación",
        "🔎 Búsqueda por promotor",
        "🔎 Búsqueda por necesidad de seguimiento",
        "🔎 Búsqueda por diagnóstico",
        "🔎 Búsqueda vectorial similar"
    ]
    
    for capability in search_capabilities:
        print(f"  {capability}")
    
    print("\n💡 4. VENTAJAS DE ESTA ESTRUCTURA")
    print("-" * 50)
    advantages = [
        "✅ Información estructurada para filtros rápidos",
        "✅ Información no estructurada para búsquedas semánticas",
        "✅ Búsquedas vectoriales por similitud",
        "✅ Contexto completo de la conversación",
        "✅ Metadatos médicos organizados",
        "✅ Escalable y eficiente",
        "✅ Sin dependencias de bases de datos externas",
        "✅ Búsquedas inteligentes basadas en IA"
    ]
    
    for advantage in advantages:
        print(f"  {advantage}")
    
    print("\n🎯 5. EJEMPLOS DE CONSULTAS POSIBLES")
    print("-" * 50)
    example_queries = [
        'Buscar pacientes con "fiebre y dolor de cabeza"',
        'Encontrar casos similares al paciente actual',
        'Pacientes que necesitan seguimiento urgente',
        'Conversaciones de alta prioridad del último mes',
        'Casos con síntomas de resfriado',
        'Pacientes atendidos por promoter_001',
        'Mujeres de 40-50 años con síntomas respiratorios'
    ]
    
    for query in example_queries:
        print(f"  🔍 {query}")

if __name__ == "__main__":
    show_chroma_structure()
