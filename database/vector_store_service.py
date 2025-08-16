"""
Servicio de almacenamiento vectorial usando Chroma
Almacena y busca información de pacientes de forma vectorial
"""

import os
import chromadb
from chromadb.config import Settings
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib
import re

from .search_service import SearchService
from .patient_service import PatientService

class VectorStoreService:
    """
    Servicio de almacenamiento vectorial usando ChromaDB.
    
    Este servicio proporciona funcionalidad completa para almacenar y buscar
    información médica de manera vectorial. Utiliza ChromaDB para crear
    embeddings semánticos que permiten búsquedas inteligentes por similitud.
    
    Attributes:
        persist_directory (str): Directorio donde se almacenan los datos de ChromaDB
        client: Cliente de ChromaDB
        patients_collection: Colección para datos de pacientes
        conversations_collection: Colección para conversaciones
        symptoms_collection: Colección para síntomas
        search_service: Servicio de búsquedas semánticas
        patient_service: Servicio de operaciones de pacientes
    """
    
    def __init__(self, persist_directory: str = "database/vector_db"):
        """
        Inicializa el servicio de almacenamiento vectorial
        
        Args:
            persist_directory: Directorio donde persistir los datos
        """
        self.persist_directory = persist_directory
        self.client = None
        self.patients_collection = None
        self.conversations_collection = None
        self.symptoms_collection = None
        
        # Servicios modulares
        self.search_service = None
        self.patient_service = None
        
        self._setup_chroma()
        self._setup_services()
    
    def _setup_chroma(self):
        """Configura Chroma y crea las colecciones necesarias"""
        try:
            print(f"Configurando Chroma en: {self.persist_directory}")
            
            # Crear directorio si no existe
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Inicializar cliente Chroma
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,  # Desactivar telemetría
                    allow_reset=True
                )
            )
            
            # Crear o obtener colecciones
            self._create_collections()
            
            print("Chroma configurado correctamente")
            
        except Exception as e:
            print(f"Error configurando Chroma: {e}")
            raise
    
    def _create_collections(self):
        """Crea las colecciones necesarias"""
        try:
            # Colección de pacientes
            self.patients_collection = self.client.get_or_create_collection(
                name="patients",
                metadata={"description": "Información vectorial de pacientes"}
            )
            
            # Colección de conversaciones
            self.conversations_collection = self.client.get_or_create_collection(
                name="conversations",
                metadata={"description": "Transcripciones y conversaciones vectoriales"}
            )
            
            # Colección de síntomas
            self.symptoms_collection = self.client.get_or_create_collection(
                name="symptoms",
                metadata={"description": "Síntomas médicos vectorizados"}
            )
            
            print("Colecciones creadas/obtenidas correctamente")
            
        except Exception as e:
            print(f"Error creando colecciones: {e}")
            raise
    
    def _setup_services(self):
        """Configura los servicios modulares"""
        try:
            self.search_service = SearchService(
                self.conversations_collection, 
                self.patients_collection
            )
            self.patient_service = PatientService(
                self.conversations_collection, 
                self.patients_collection,
                self.persist_directory
            )
            print("Servicios modulares configurados")
        except Exception as e:
            print(f"Error configurando servicios: {e}")
            raise
    
    def _generate_embedding_text(self, patient_data: Dict[str, Any]) -> str:
        """
        Genera texto para embeddings: INFORMACIÓN NO ESTRUCTURADA
        Este texto será vectorizado para búsquedas semánticas
        """
        patient_info = patient_data.get('patient_info', {})
        medical_info = patient_data.get('medical_info', {})
        transcription = patient_data.get('transcription', {})
        conversation_details = patient_data.get('conversation_details', {})
        
        # INFORMACIÓN NO ESTRUCTURADA - Texto natural para vectorización
        embedding_text = f"""
        INFORMACIÓN DEL PACIENTE:
        Paciente {patient_info.get('name', 'no identificado')} de {patient_info.get('age', 'edad no especificada')} años, 
        género {patient_info.get('gender', 'no especificado')}.
        
        SÍNTOMAS Y CONTEXTO CONVERSACIONAL:
        El paciente presenta: {', '.join(medical_info.get('symptoms', ['sin síntomas específicos']))}
        
        CONTEXTO MÉDICO:
        Medicamentos mencionados: {', '.join(medical_info.get('medications', ['ninguno mencionado']))}
        Alergias conocidas: {', '.join(medical_info.get('allergies', ['no mencionadas']))}
        Condiciones crónicas: {', '.join(medical_info.get('chronic_conditions', ['no mencionadas']))}
        
        TRANSCRIPCIÓN COMPLETA DE LA CONVERSACIÓN:
        {transcription.get('full_text', 'Sin transcripción disponible')}
        
        OBSERVACIONES Y CONTEXTO:
        Prioridad de atención: {conversation_details.get('priority_level', 'normal')}
        Tipo de conversación: {conversation_details.get('conversation_type', 'contacto inicial')}
        Necesita seguimiento: {'Sí' if conversation_details.get('follow_up_needed') else 'No'}
        Promotor: {conversation_details.get('promoter_id', 'no especificado')}
        Fecha de la conversación: {conversation_details.get('conversation_date', 'no especificada')}
        
        ANÁLISIS CONTEXTUAL:
        Este paciente se encuentra en una consulta de {conversation_details.get('conversation_type', 'tipo no especificado')} 
        con síntomas que sugieren {self._extract_diagnosis(transcription.get('full_text', ''))}.
        """
        
        return embedding_text.strip()
    
    def _extract_diagnosis(self, transcription_text: str) -> str:
        """
        Extrae posible diagnóstico de la transcripción
        """
        if not transcription_text:
            return ""
        
        text_lower = transcription_text.lower()
        
        # Patrones de diagnóstico comunes
        diagnosis_patterns = [
            r'diagnóstico\s*:?\s*([^.]+)',
            r'diagnosis\s*:?\s*([^.]+)',
            r'parece\s+(ser|que\s+es|tener)\s+([^.]+)',
            r'posible\s+([^.]+)',
            r'probable\s+([^.]+)',
            r'sospecha\s+de\s+([^.]+)',
            r'indicativo\s+de\s+([^.]+)',
        ]
        
        # Diagnósticos médicos comunes basados en síntomas
        symptom_based_diagnosis = {
            'fiebre': ['resfriado común', 'gripe', 'infección viral'],
            'dolor de cabeza': ['migraña', 'cefalea tensional', 'sinusitis'],
            'tos': ['bronquitis', 'resfriado', 'irritación respiratoria'],
            'dolor de garganta': ['faringitis', 'amigdalitis', 'infección viral'],
            'náuseas': ['gastroenteritis', 'intoxicación alimentaria', 'virus estomacal'],
            'diarrea': ['gastroenteritis', 'intoxicación alimentaria', 'virus estomacal']
        }
        
        # Buscar diagnóstico explícito
        for pattern in diagnosis_patterns:
            match = re.search(pattern, text_lower)
            if match:
                diagnosis = match.group(1).strip()
                if len(diagnosis) > 3:
                    return diagnosis.title()
        
        # Si no hay diagnóstico explícito, sugerir basado en síntomas
        for symptom, possible_diagnoses in symptom_based_diagnosis.items():
            if symptom in text_lower:
                return f"Posible {possible_diagnoses[0]} (basado en síntomas)"
        
        return "Diagnóstico pendiente"
    
    def _generate_id(self, patient_data: Dict[str, Any]) -> str:
        """Genera un ID único para el documento"""
        conversation_id = patient_data.get('conversation_id', '')
        patient_name = patient_data.get('patient_info', {}).get('name', '')
        timestamp = datetime.now().isoformat()
        
        # Crear hash único
        unique_string = f"{conversation_id}_{patient_name}_{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def store_patient_data(self, patient_data: Dict[str, Any]) -> str:
        """
        Almacena los datos del paciente en el almacenamiento vectorial.
        
        Este método procesa los datos del paciente y los almacena tanto de manera
        estructurada (metadatos) como no estructurada (texto para embeddings).
        Permite búsquedas tanto por filtros exactos como por similitud semántica.
        
        Args:
            patient_data (Dict[str, Any]): Datos del paciente con estructura:
                - patient_info: Información personal del paciente
                - medical_info: Información médica (síntomas, medicamentos, etc.)
                - transcription: Transcripción completa de la conversación
                - conversation_details: Detalles de la conversación
                
        Returns:
            str: ID único del documento almacenado
            
        Raises:
            Exception: Si hay error en el almacenamiento
        """
        try:
            print(f"Almacenando datos vectoriales para: {patient_data.get('conversation_id', 'N/A')}")
            
            # Generar ID único
            doc_id = self._generate_id(patient_data)
            
            # Generar texto para embeddings
            embedding_text = self._generate_embedding_text(patient_data)
            
            # INFORMACIÓN ESTRUCTURADA (Metadatos para búsqueda rápida)
            metadata = {
                # Información del paciente
                "patient_name": patient_data.get('patient_info', {}).get('name') or " ",
                "patient_age": patient_data.get('patient_info', {}).get('age') or 0,
                "patient_gender": patient_data.get('patient_info', {}).get('gender') or " ",
                "patient_phone": patient_data.get('patient_info', {}).get('contact_info', {}).get('phone') or " ",
                
                # Información médica estructurada
                "diagnosis": self._extract_diagnosis(patient_data.get('transcription', {}).get('full_text', '')) or " ",
                "symptoms_list": json.dumps(patient_data.get('medical_info', {}).get('symptoms', [])),
                "medications_list": json.dumps(patient_data.get('medical_info', {}).get('medications', [])),
                "allergies_list": json.dumps(patient_data.get('medical_info', {}).get('allergies', [])),
                "chronic_conditions": json.dumps(patient_data.get('medical_info', {}).get('chronic_conditions', [])),
                
                # Información de la conversación
                "conversation_id": patient_data.get('conversation_id') or " ",
                "conversation_date": patient_data.get('conversation_details', {}).get('conversation_date') or datetime.now().isoformat(),
                "promoter_id": patient_data.get('conversation_details', {}).get('promoter_id') or " ",
                "priority_level": patient_data.get('conversation_details', {}).get('priority_level') or " ",
                "follow_up_needed": bool(patient_data.get('conversation_details', {}).get('follow_up_needed', False)),
                
                # Metadatos técnicos
                "stored_at": datetime.now().isoformat(),
                "conversation_type": patient_data.get('conversation_details', {}).get('conversation_type') or " "
            }
            
            # Almacenar en colección de conversaciones
            self.conversations_collection.add(
                documents=[embedding_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            # También almacenar en colección de pacientes (si es nuevo paciente)
            self.patient_service.store_patient_summary(patient_data, doc_id)
            
            print(f"Datos vectoriales almacenados con ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            print(f"Error almacenando datos vectoriales: {e}")
            raise
    
    # Métodos delegados a los servicios modulares
    def search_similar_patients(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_similar_patients(query, n_results)
    
    def search_by_patient_name(self, patient_name: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_by_patient_name(patient_name, n_results)
    
    def search_by_symptoms(self, symptoms: List[str], n_results: int = 5) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_by_symptoms(symptoms, n_results)
    
    def search_by_diagnosis(self, diagnosis_keywords: List[str], n_results: int = 5) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_by_diagnosis(diagnosis_keywords, n_results)
    
    def search_by_date_range(self, start_date: str, end_date: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_by_date_range(start_date, end_date, n_results)
    
    def search_by_priority_level(self, priority: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_by_priority_level(priority, n_results)
    
    def search_by_promoter(self, promoter_id: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_by_promoter(promoter_id, n_results)
    
    def search_complex_query(self, query: str, filters: Dict[str, Any] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_complex_query(query, filters, n_results)
    
    def search_high_priority_patients(self, n_results: int = 10) -> List[Dict[str, Any]]:
        """Delega al SearchService"""
        return self.search_service.search_high_priority_patients(n_results)
    
    def get_patient_summary(self, patient_name: str) -> Dict[str, Any]:
        """Delega al PatientService"""
        return self.patient_service.get_patient_summary(patient_name)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Delega al PatientService"""
        return self.patient_service.get_collection_stats()
    
    def export_collection_to_json(self, collection_name: str, file_path: str = None) -> str:
        """Delega al PatientService"""
        return self.patient_service.export_collection_to_json(collection_name, file_path)
    
    def get_patient_conversation_history(self, patient_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Delega al PatientService"""
        return self.patient_service.get_patient_conversation_history(patient_name, limit)
    
    def get_patients_by_priority(self, priority: str = "alta") -> List[Dict[str, Any]]:
        """Delega al PatientService"""
        return self.patient_service.get_patients_by_priority(priority)

def test_vector_store():
    """Función de prueba para verificar el almacenamiento vectorial"""
    try:
        print("Probando almacenamiento vectorial con Chroma...")
        
        # Crear instancia del servicio
        vector_service = VectorStoreService()
        
        # Obtener estadísticas
        stats = vector_service.get_collection_stats()
        print(f"Estadísticas del almacenamiento vectorial: {stats}")
        
        print("Prueba de almacenamiento vectorial completada")
        return True
        
    except Exception as e:
        print(f"Error en la prueba de almacenamiento vectorial: {e}")
        return False

if __name__ == "__main__":
    test_vector_store()
