"""
Servicio de búsqueda para el almacenamiento vectorial
Maneja todas las operaciones de búsqueda de pacientes y conversaciones
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class SearchService:
    """
    Servicio para búsquedas en el almacenamiento vectorial
    Maneja búsquedas por diferentes criterios
    """
    
    def __init__(self, conversations_collection, patients_collection):
        """
        Inicializa el servicio de búsqueda
        
        Args:
            conversations_collection: Colección de conversaciones de Chroma
            patients_collection: Colección de pacientes de Chroma
        """
        self.conversations_collection = conversations_collection
        self.patients_collection = patients_collection
    
    def search_similar_patients(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca pacientes similares basado en una consulta
        
        Args:
            query: Consulta de búsqueda
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de pacientes similares
        """
        try:
            print(f"Buscando pacientes similares: '{query}'")
            
            # Buscar en colección de conversaciones
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Formatear resultados
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontrados {len(formatted_results)} pacientes similares")
            return formatted_results
            
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return []
    
    def search_by_patient_name(self, patient_name: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca conversaciones de un paciente específico por nombre
        
        Args:
            patient_name: Nombre del paciente a buscar
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de conversaciones del paciente
        """
        try:
            print(f"Buscando conversaciones de: {patient_name}")
            
            # Buscar en colección de conversaciones por nombre
            results = self.conversations_collection.query(
                query_texts=[f"paciente {patient_name}"],
                n_results=n_results,
                where={
                    "patient_name": {"$contains": patient_name}
                }
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontradas {len(formatted_results)} conversaciones de {patient_name}")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando por nombre: {e}")
            return []
    
    def search_by_symptoms(self, symptoms: List[str], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca pacientes por síntomas específicos
        
        Args:
            symptoms: Lista de síntomas a buscar
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de pacientes con síntomas similares
        """
        try:
            query_text = f"Síntomas: {', '.join(symptoms)}"
            print(f"Buscando por síntomas: {symptoms}")
            
            results = self.conversations_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={
                    "symptoms": {"$contains": json.dumps(symptoms)}
                }
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontrados {len(formatted_results)} pacientes con síntomas similares")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando por síntomas: {e}")
            return []
    
    def search_by_diagnosis(self, diagnosis_keywords: List[str], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca pacientes por diagnóstico o enfermedad
        
        Args:
            diagnosis_keywords: Palabras clave del diagnóstico
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de pacientes con diagnósticos similares
        """
        try:
            query_text = f"Diagnóstico: {', '.join(diagnosis_keywords)}"
            print(f"Buscando por diagnóstico: {diagnosis_keywords}")
            
            results = self.conversations_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontrados {len(formatted_results)} pacientes con diagnósticos similares")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando por diagnóstico: {e}")
            return []
    
    def search_by_date_range(self, start_date: str, end_date: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca conversaciones en un rango de fechas
        
        Args:
            start_date: Fecha de inicio (ISO format)
            end_date: Fecha de fin (ISO format)
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de conversaciones en el rango de fechas
        """
        try:
            print(f"Buscando conversaciones entre {start_date} y {end_date}")
            
            # Buscar conversaciones en el rango de fechas
            results = self.conversations_collection.query(
                query_texts=["conversaciones en rango de fechas"],
                n_results=n_results,
                where={
                    "conversation_date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontradas {len(formatted_results)} conversaciones en el rango de fechas")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando por rango de fechas: {e}")
            return []
    
    def search_by_priority_level(self, priority: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca pacientes por nivel de prioridad
        
        Args:
            priority: Nivel de prioridad (normal, media, alta)
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de pacientes con la prioridad especificada
        """
        try:
            print(f"Buscando pacientes con prioridad: {priority}")
            
            results = self.conversations_collection.query(
                query_texts=[f"pacientes prioridad {priority}"],
                n_results=n_results,
                where={
                    "priority_level": priority
                }
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontrados {len(formatted_results)} pacientes con prioridad {priority}")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando por prioridad: {e}")
            return []
    
    def search_by_promoter(self, promoter_id: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca conversaciones por promotor específico
        
        Args:
            promoter_id: ID del promotor
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de conversaciones del promotor
        """
        try:
            print(f"Buscando conversaciones del promotor: {promoter_id}")
            
            results = self.conversations_collection.query(
                query_texts=[f"conversaciones promotor {promoter_id}"],
                n_results=n_results,
                where={
                    "promoter_id": promoter_id
                }
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontradas {len(formatted_results)} conversaciones del promotor {promoter_id}")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando por promotor: {e}")
            return []
    
    def search_complex_query(self, query: str, filters: Dict[str, Any] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Búsqueda compleja con filtros múltiples
        
        Args:
            query: Consulta de texto libre
            filters: Filtros adicionales (síntomas, prioridad, fechas, etc.)
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de resultados que coinciden con la consulta y filtros
        """
        try:
            print(f"Búsqueda compleja: '{query}' con filtros: {filters}")
            
            # Construir filtros where
            where_filters = {}
            if filters:
                if 'symptoms' in filters and filters['symptoms']:
                    where_filters["symptoms_list"] = {"$contains": json.dumps(filters['symptoms'])}
                
                if 'priority' in filters and filters['priority']:
                    where_filters["priority_level"] = filters['priority']
                
                if 'promoter_id' in filters and filters['promoter_id']:
                    where_filters["promoter_id"] = filters['promoter_id']
                
                if 'patient_name' in filters and filters['patient_name']:
                    where_filters["patient_name"] = {"$contains": filters['patient_name']}
            
            # Realizar búsqueda
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filters if where_filters else None
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontrados {len(formatted_results)} resultados para la búsqueda compleja")
            return formatted_results
            
        except Exception as e:
            print(f"Error en búsqueda compleja: {e}")
            return []
    
    def search_high_priority_patients(self, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca pacientes con alta prioridad
        
        Args:
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de pacientes con alta prioridad
        """
        try:
            print("Buscando pacientes con alta prioridad...")
            
            results = self.conversations_collection.query(
                query_texts=["paciente alta prioridad emergencia"],
                n_results=n_results,
                where={
                    "priority_level": "alta"
                }
            )
            
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i]
                }
                formatted_results.append(result)
            
            print(f"Encontrados {len(formatted_results)} pacientes con alta prioridad")
            return formatted_results
            
        except Exception as e:
            print(f"Error buscando pacientes de alta prioridad: {e}")
            return []
