"""
Script integrado para procesar conversaciones: transcripción + almacenamiento vectorial
"""

import os
from transcription_service import TranscriptionService
from vector_store_service import VectorStoreService
from typing import Dict, Any, Optional

class ConversationProcessor:
    """
    Procesador integrado de conversaciones
    Combina transcripción con almacenamiento vectorial
    """
    
    def __init__(self, promoter_id: str = None):
        """
        Inicializa el procesador de conversaciones
        
        Args:
            promoter_id: ID del promotor que realiza la conversación
        """
        self.promoter_id = promoter_id or "promoter_001"
        self.transcription_service = TranscriptionService()
        self.vector_service = None
        
        # Conectar al almacenamiento vectorial
        try:
            self.vector_service = VectorStoreService()
            print("Almacenamiento vectorial (Chroma) conectado correctamente")
        except Exception as e:
            print(f"No se pudo conectar al almacenamiento vectorial: {e}")
            raise
        
        print("Servicios inicializados correctamente")
    
    def process_audio_file(self, audio_path: str, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Procesa un archivo de audio completo: transcripción + almacenamiento
        
        Args:
            audio_path: Ruta al archivo de audio
            save_to_db: Si guardar en base de datos
            
        Returns:
            Diccionario con toda la información procesada
        """
        try:
            print("Iniciando procesamiento completo de conversación")
            print("=" * 60)
            
            # Paso 1: Transcribir audio
            print("Paso 1: Transcribiendo audio...")
            transcription_result = self.transcription_service.transcribe_audio(audio_path)
            
            if not transcription_result or not transcription_result.get('text'):
                raise ValueError("No se pudo transcribir el audio")
            
            # Paso 2: Extraer información del paciente
            print("🔍 Paso 2: Extrayendo información del paciente...")
            patient_data = self.transcription_service.extract_patient_info(
                transcription_result['text']
            )
            
            # Agregar información del promotor
            patient_data['conversation_details']['promoter_id'] = self.promoter_id
            
            # Paso 3: Guardar en almacenamiento vectorial
            if save_to_db and self.vector_service:
                print("Paso 3: Guardando en almacenamiento vectorial (Chroma)...")
                vector_id = self.vector_service.store_patient_data(patient_data)
                patient_data['vector_id'] = vector_id
                print(f"Guardado en Chroma con ID: {vector_id}")
            else:
                print("Paso 3: Omitiendo guardado en almacenamiento vectorial")
                patient_data['vector_id'] = None
            
            # Crear resultado final
            result = {
                "success": True,
                "transcription": transcription_result,
                "patient_data": patient_data,
                "processing_timestamp": transcription_result['transcription_time']
            }
            
            print("\nProcesamiento completado exitosamente!")
            return result
            
        except Exception as e:
            print(f"Error en el procesamiento: {e}")
            return {
                "success": False,
                "error": str(e),
                "transcription": None,
                "patient_data": None
            }
    
    def get_conversation_summary(self, patient_data: Dict[str, Any]) -> str:
        """Genera un resumen de la conversación"""
        if not patient_data:
            return "No hay datos disponibles"
        
        patient_info = patient_data.get('patient_info', {})
        medical_info = patient_data.get('medical_info', {})
        conversation_details = patient_data.get('conversation_details', {})
        
        summary = f"""
RESUMEN DE CONVERSACIÓN
==========================
ID: {patient_data.get('conversation_id', 'N/A')}
Paciente: {patient_info.get('name', 'No identificado')}
Edad: {patient_info.get('age', 'No especificada')} años
Género: {patient_info.get('gender', 'No especificado')}
Teléfono: {patient_info.get('contact_info', {}).get('phone', 'No proporcionado')}

Síntomas detectados: {', '.join(medical_info.get('symptoms', [])) or 'Ninguno'}
Medicamentos: {', '.join(medical_info.get('medications', [])) or 'Ninguno'}
Prioridad: {conversation_details.get('priority_level', 'Normal')}
Seguimiento: {'Sí' if conversation_details.get('follow_up_needed') else 'No'}

Transcripción: {patient_data.get('transcription', {}).get('full_text', 'No disponible')[:100]}...
        """
        
        return summary
    
    def close_services(self):
        """Cierra las conexiones de los servicios"""
        # Chroma no requiere cierre explícito de conexión
        pass

def process_single_conversation(audio_file: str, promoter_id: str = "promoter_001"):
    """
    Función de conveniencia para procesar una sola conversación
    
    Args:
        audio_file: Ruta al archivo de audio
        promoter_id: ID del promotor
    """
    processor = ConversationProcessor(promoter_id)
    
    try:
        # Procesar la conversación
        result = processor.process_audio_file(audio_file)
        
        if result['success']:
            # Mostrar resumen
            summary = processor.get_conversation_summary(result['patient_data'])
            print(summary)
            
            # Mostrar estadísticas del almacenamiento vectorial
            if processor.vector_service:
                vector_stats = processor.vector_service.get_collection_stats()
                print(f"\n Estadísticas del Almacenamiento Vectorial (Chroma):")
                print(f"   Total pacientes: {vector_stats.get('total_patients', 0)}")
                print(f"   Total conversaciones: {vector_stats.get('total_conversations', 0)}")
                print(f"   Tamaño de la BD: {vector_stats.get('vector_db_size_mb', 0):.2f} MB")
            
            return result
        else:
            print(f"Error en el procesamiento: {result.get('error', 'Error desconocido')}")
            return None
            
    finally:
        processor.close_services()

def main():
    """Función principal para procesar el archivo de ejemplo"""
    print("PROCESADOR DE CONVERSACIONES - ElSol Challenge")
    print("=" * 60)
    
    # Archivo de audio de ejemplo
    audio_file = "pruebas/p_51994013_222.mp3"
    
    if not os.path.exists(audio_file):
        print(f"Archivo no encontrado: {audio_file}")
        return
    
    # Procesar la conversación
    result = process_single_conversation(audio_file, "promoter_001")
    
    if result and result['success']:
        print("\nProcesamiento completado exitosamente!")
        print("Los datos están almacenados en Chroma y listos para el chatbot")
        
        # Guardar el texto transcrito en una variable como solicitaste
        texto_transcrito = result['transcription']['text']
        print(f"\nVariable 'texto_transcrito' disponible:")
        print(f"   Contenido: {texto_transcrito}")
        print(f"   Longitud: {len(texto_transcrito)} caracteres")
        
    else:
        print("\nEl procesamiento falló")

if __name__ == "__main__":
    main()
