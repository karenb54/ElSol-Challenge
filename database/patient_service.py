"""
Servicio para manejo de pacientes en el almacenamiento vectorial
Maneja resúmenes, estadísticas y operaciones específicas de pacientes
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

class PatientService:
    """
    Servicio para operaciones específicas de pacientes
    Maneja resúmenes, estadísticas y operaciones de pacientes
    """
    
    def __init__(self, conversations_collection, patients_collection, persist_directory: str = "database/vector_db"):
        """
        Inicializa el servicio de pacientes
        
        Args:
            conversations_collection: Colección de conversaciones de Chroma
            patients_collection: Colección de pacientes de Chroma
            persist_directory: Directorio de persistencia
        """
        self.conversations_collection = conversations_collection
        self.patients_collection = patients_collection
        self.persist_directory = persist_directory
    
    def get_patient_summary(self, patient_name: str) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de un paciente específico
        
        Args:
            patient_name: Nombre del paciente
            
        Returns:
            Resumen completo del paciente con todas sus conversaciones
        """
        try:
            print(f"📋 Generando resumen para: {patient_name}")
            
            # Buscar todas las conversaciones del paciente
            from .search_service import SearchService
            search_service = SearchService(self.conversations_collection, self.patients_collection)
            conversations = search_service.search_by_patient_name(patient_name, n_results=50)
            
            if not conversations:
                return {
                    "patient_name": patient_name,
                    "found": False,
                    "message": f"No se encontraron conversaciones para {patient_name}"
                }
            
            # Extraer información del paciente de la primera conversación
            first_conv = conversations[0]
            metadata = first_conv['metadata']
            
            # Procesar todas las conversaciones
            all_symptoms = set()
            all_medications = set()
            all_diagnoses = set()
            conversation_dates = []
            
            for conv in conversations:
                conv_metadata = conv['metadata']
                
                # Agregar síntomas
                symptoms = json.loads(conv_metadata.get('symptoms_list', '[]'))
                all_symptoms.update(symptoms)
                
                # Agregar medicamentos
                medications = json.loads(conv_metadata.get('medications_list', '[]'))
                all_medications.update(medications)
                
                # Agregar diagnósticos
                diagnosis = conv_metadata.get('diagnosis', '')
                if diagnosis and diagnosis != ' ':
                    all_diagnoses.add(diagnosis)
                
                # Agregar fechas
                conv_date = conv_metadata.get('conversation_date', '')
                if conv_date:
                    conversation_dates.append(conv_date)
            
            # Crear resumen
            summary = {
                "patient_name": patient_name,
                "found": True,
                "patient_info": {
                    "age": metadata.get('patient_age', 'No especificada'),
                    "gender": metadata.get('patient_gender', 'No especificado'),
                    "phone": metadata.get('patient_phone', 'No especificado')
                },
                "medical_summary": {
                    "total_conversations": len(conversations),
                    "all_symptoms": list(all_symptoms),
                    "all_medications": list(all_medications),
                    "all_diagnoses": list(all_diagnoses),
                    "conversation_dates": sorted(conversation_dates),
                    "last_conversation": max(conversation_dates) if conversation_dates else None,
                    "first_conversation": min(conversation_dates) if conversation_dates else None
                },
                "priority_levels": list(set(conv['metadata'].get('priority_level', 'normal') for conv in conversations)),
                "follow_up_needed": any(conv['metadata'].get('follow_up_needed', False) for conv in conversations),
                "conversations": conversations
            }
            
            print(f"✅ Resumen generado para {patient_name}")
            return summary
            
        except Exception as e:
            print(f"❌ Error generando resumen del paciente: {e}")
            return {
                "patient_name": patient_name,
                "found": False,
                "error": str(e)
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de las colecciones"""
        try:
            patients_count = self.patients_collection.count()
            conversations_count = self.conversations_collection.count()
            
            return {
                "total_patients": patients_count,
                "total_conversations": conversations_count,
                "vector_db_size_mb": self._get_db_size()
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def _get_db_size(self) -> float:
        """Calcula el tamaño de la base de datos vectorial"""
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.persist_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            return total_size / (1024 * 1024)  # Convertir a MB
        except Exception:
            return 0.0
    
    def export_collection_to_json(self, collection_name: str, file_path: str = None) -> str:
        """Exporta una colección a JSON"""
        try:
            if collection_name == "patients":
                collection = self.patients_collection
            elif collection_name == "conversations":
                collection = self.conversations_collection
            else:
                raise ValueError(f"Colección no válida: {collection_name}")
            
            # Obtener todos los datos
            results = collection.get()
            
            if not file_path:
                file_path = f"exports/{collection_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Preparar datos para exportación
            export_data = {
                "collection_name": collection_name,
                "export_date": datetime.now().isoformat(),
                "total_documents": len(results['ids']),
                "documents": []
            }
            
            for i in range(len(results['ids'])):
                doc = {
                    "id": results['ids'][i],
                    "metadata": results['metadatas'][i],
                    "document": results['documents'][i]
                }
                export_data["documents"].append(doc)
            
            # Guardar a JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Colección exportada a: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error exportando colección: {e}")
            raise
    
    def store_patient_summary(self, patient_data: Dict[str, Any], doc_id: str):
        """Almacena un resumen del paciente"""
        try:
            patient_name = patient_data.get('patient_info', {}).get('name')
            if not patient_name:
                return
            
            # Crear resumen del paciente
            summary_text = f"""
            Paciente: {patient_name}
            Edad: {patient_data.get('patient_info', {}).get('age', 'No especificada')} años
            Género: {patient_data.get('patient_info', {}).get('gender', 'No especificado')}
            Síntomas principales: {', '.join(patient_data.get('medical_info', {}).get('symptoms', []))}
            Medicamentos: {', '.join(patient_data.get('medical_info', {}).get('medications', []))}
            Última conversación: {patient_data.get('conversation_details', {}).get('conversation_date', '')}
            """
            
            patient_metadata = {
                "patient_name": patient_name or " ",
                "patient_age": patient_data.get('patient_info', {}).get('age') or 0,
                "patient_gender": patient_data.get('patient_info', {}).get('gender') or " ",
                "last_conversation_id": patient_data.get('conversation_id') or " ",
                "total_conversations": 1,
                "updated_at": datetime.now().isoformat()
            }
            
            # Usar nombre del paciente como ID
            import hashlib
            patient_id = f"patient_{hashlib.md5(patient_name.encode()).hexdigest()}"
            
            # Verificar si el paciente ya existe
            existing = self.patients_collection.get(ids=[patient_id])
            if existing['ids']:
                # Actualizar paciente existente
                self.patients_collection.update(
                    ids=[patient_id],
                    documents=[summary_text],
                    metadatas=[patient_metadata]
                )
                print(f"✅ Paciente actualizado: {patient_name}")
            else:
                # Crear nuevo paciente
                self.patients_collection.add(
                    documents=[summary_text],
                    metadatas=[patient_metadata],
                    ids=[patient_id]
                )
                print(f"✅ Nuevo paciente creado: {patient_name}")
                
        except Exception as e:
            print(f"❌ Error almacenando resumen del paciente: {e}")
    
    def get_patient_conversation_history(self, patient_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de conversaciones de un paciente
        
        Args:
            patient_name: Nombre del paciente
            limit: Número máximo de conversaciones a retornar
            
        Returns:
            Lista de conversaciones ordenadas por fecha
        """
        try:
            from .search_service import SearchService
            search_service = SearchService(self.conversations_collection, self.patients_collection)
            conversations = search_service.search_by_patient_name(patient_name, n_results=limit)
            
            # Ordenar por fecha de conversación
            conversations.sort(
                key=lambda x: x['metadata'].get('conversation_date', ''),
                reverse=True
            )
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error obteniendo historial de conversaciones: {e}")
            return []
    
    def get_patients_by_priority(self, priority: str = "alta") -> List[Dict[str, Any]]:
        """
        Obtiene todos los pacientes con una prioridad específica
        
        Args:
            priority: Nivel de prioridad (normal, media, alta)
            
        Returns:
            Lista de pacientes con la prioridad especificada
        """
        try:
            from .search_service import SearchService
            search_service = SearchService(self.conversations_collection, self.patients_collection)
            return search_service.search_by_priority_level(priority, n_results=50)
            
        except Exception as e:
            print(f"❌ Error obteniendo pacientes por prioridad: {e}")
            return []
