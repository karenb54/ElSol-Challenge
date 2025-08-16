"""
Test para ChromaDB - Base de datos vectorial
Usa directorio temporal para no afectar datos reales
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from database.vector_store_service import VectorStoreService


class TestChromaDB:
    """Tests para ChromaDB"""
    
    @pytest.fixture
    def temp_db_dir(self):
        """Fixture para crear directorio temporal de BD"""
        temp_dir = tempfile.mkdtemp(prefix="test_chroma_")
        yield temp_dir
        # Limpiar después de cada test
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def vector_service(self, temp_db_dir):
        """Fixture para crear servicio con BD temporal"""
        return VectorStoreService(persist_directory=temp_db_dir)
    
    def test_init(self, vector_service):
        """Test de inicialización del servicio"""
        assert vector_service is not None
        assert vector_service.client is not None
        assert vector_service.patients_collection is not None
        assert vector_service.conversations_collection is not None
        print("✅ Servicio de ChromaDB inicializado correctamente")
    
    def test_collections_created(self, vector_service):
        """Test de creación de colecciones"""
        # Verificar que las colecciones existen
        collections = vector_service.client.list_collections()
        collection_names = [col.name for col in collections]
        
        assert "patients" in collection_names
        assert "conversations" in collection_names
        assert "symptoms" in collection_names
        print("✅ Colecciones creadas correctamente")
    
    def test_store_patient_data(self, vector_service):
        """Test de almacenamiento de datos de paciente"""
        # Datos de prueba
        test_patient_data = {
            "conversation_id": "test_conv_001",
            "patient_info": {
                "name": "Test Patient",
                "age": "30",
                "gender": "femenino"
            },
            "medical_info": {
                "symptoms": ["fiebre", "tos"],
                "medications": ["paracetamol"],
                "allergies": [],
                "chronic_conditions": []
            },
            "transcription": {
                "full_text": "Hola, soy Test Patient, tengo 30 años y tengo fiebre y tos."
            },
            "conversation_details": {
                "conversation_date": "2024-01-01T10:00:00",
                "promoter_id": "promoter_001",
                "priority_level": "normal",
                "follow_up_needed": False,
                "conversation_type": "consulta inicial"
            }
        }
        
        # Almacenar datos
        doc_id = vector_service.store_patient_data(test_patient_data)
        
        assert doc_id is not None
        assert len(doc_id) > 0
        
        # Verificar que se almacenó en la colección
        count = vector_service.conversations_collection.count()
        assert count > 0
        
        print("✅ Almacenamiento de datos funcionando")
    
    def test_search_similar_patients(self, vector_service):
        """Test de búsqueda de pacientes similares"""
        # Primero almacenar algunos datos de prueba
        test_data = {
            "conversation_id": "test_conv_002",
            "patient_info": {
                "name": "María Test",
                "age": "25",
                "gender": "femenino"
            },
            "medical_info": {
                "symptoms": ["dolor de cabeza", "náuseas"],
                "medications": ["ibuprofeno"],
                "allergies": [],
                "chronic_conditions": []
            },
            "transcription": {
                "full_text": "Hola, soy María Test, tengo dolor de cabeza y náuseas."
            },
            "conversation_details": {
                "conversation_date": "2024-01-01T11:00:00",
                "promoter_id": "promoter_001",
                "priority_level": "normal",
                "follow_up_needed": False,
                "conversation_type": "consulta inicial"
            }
        }
        
        vector_service.store_patient_data(test_data)
        
        # Buscar pacientes similares
        query = "pacientes con dolor de cabeza"
        results = vector_service.search_similar_patients(query, n_results=5)
        
        assert results is not None
        assert len(results) > 0
        
        print("✅ Búsqueda de pacientes similares funcionando")
    
    def test_search_by_patient_name(self, vector_service):
        """Test de búsqueda por nombre de paciente"""
        # Almacenar datos de prueba
        test_data = {
            "conversation_id": "test_conv_003",
            "patient_info": {
                "name": "Juan Test",
                "age": "40",
                "gender": "masculino"
            },
            "medical_info": {
                "symptoms": ["fatiga"],
                "medications": [],
                "allergies": [],
                "chronic_conditions": []
            },
            "transcription": {
                "full_text": "Hola, soy Juan Test, tengo 40 años y me siento fatigado."
            },
            "conversation_details": {
                "conversation_date": "2024-01-01T12:00:00",
                "promoter_id": "promoter_001",
                "priority_level": "normal",
                "follow_up_needed": False,
                "conversation_type": "consulta inicial"
            }
        }
        
        vector_service.store_patient_data(test_data)
        
        # Buscar por nombre
        results = vector_service.search_by_patient_name("Juan Test", n_results=5)
        
        assert results is not None
        assert len(results) > 0
        
        # Verificar que el nombre coincide
        found_patient = results[0]
        assert "Juan Test" in found_patient['metadata']['patient_name']
        
        print("✅ Búsqueda por nombre funcionando")
    
    def test_search_by_symptoms(self, vector_service):
        """Test de búsqueda por síntomas"""
        # Almacenar datos con síntomas específicos
        test_data = {
            "conversation_id": "test_conv_004",
            "patient_info": {
                "name": "Ana Test",
                "age": "35",
                "gender": "femenino"
            },
            "medical_info": {
                "symptoms": ["fiebre", "dolor de garganta"],
                "medications": ["antibiótico"],
                "allergies": [],
                "chronic_conditions": []
            },
            "transcription": {
                "full_text": "Hola, soy Ana Test, tengo fiebre y dolor de garganta."
            },
            "conversation_details": {
                "conversation_date": "2024-01-01T13:00:00",
                "promoter_id": "promoter_001",
                "priority_level": "normal",
                "follow_up_needed": False,
                "conversation_type": "consulta inicial"
            }
        }
        
        vector_service.store_patient_data(test_data)
        
        # Buscar por síntomas
        symptoms = ["fiebre", "dolor de garganta"]
        results = vector_service.search_by_symptoms(symptoms, n_results=5)
        
        assert results is not None
        assert len(results) > 0
        
        print("✅ Búsqueda por síntomas funcionando")
    
    def test_get_collection_stats(self, vector_service):
        """Test de estadísticas de colección"""
        # Almacenar algunos datos de prueba
        for i in range(3):
            test_data = {
                "conversation_id": f"test_conv_{i+5}",
                "patient_info": {
                    "name": f"Paciente Test {i+1}",
                    "age": "30",
                    "gender": "femenino"
                },
                "medical_info": {
                    "symptoms": ["síntoma test"],
                    "medications": [],
                    "allergies": [],
                    "chronic_conditions": []
                },
                "transcription": {
                    "full_text": f"Texto de prueba {i+1}"
                },
                "conversation_details": {
                    "conversation_date": "2024-01-01T14:00:00",
                    "promoter_id": "promoter_001",
                    "priority_level": "normal",
                    "follow_up_needed": False,
                    "conversation_type": "consulta inicial"
                }
            }
            vector_service.store_patient_data(test_data)
        
        # Obtener estadísticas
        stats = vector_service.get_collection_stats()
        
        assert stats is not None
        assert "total_patients" in stats
        assert "total_conversations" in stats
        assert "vector_db_size_mb" in stats
        
        print("✅ Estadísticas de colección funcionando")


def run_chroma_tests():
    """Función para ejecutar todos los tests de ChromaDB"""
    print("🧪 Ejecutando tests de ChromaDB...")
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix="test_chroma_")
    
    try:
        # Crear servicio con BD temporal
        service = VectorStoreService(persist_directory=temp_dir)
        
        # Test 1: Inicialización
        print("\n1. Test de inicialización:")
        assert service is not None
        assert service.client is not None
        print("✅ Servicio inicializado")
        
        # Test 2: Creación de colecciones
        print("\n2. Test de colecciones:")
        collections = service.client.list_collections()
        collection_names = [col.name for col in collections]
        assert "patients" in collection_names
        assert "conversations" in collection_names
        print("✅ Colecciones creadas")
        
        # Test 3: Almacenamiento de datos
        print("\n3. Test de almacenamiento:")
        test_data = {
            "conversation_id": "test_001",
            "patient_info": {
                "name": "Test Patient",
                "age": "30",
                "gender": "femenino"
            },
            "medical_info": {
                "symptoms": ["fiebre"],
                "medications": ["paracetamol"],
                "allergies": [],
                "chronic_conditions": []
            },
            "transcription": {
                "full_text": "Hola, tengo fiebre."
            },
            "conversation_details": {
                "conversation_date": "2024-01-01T10:00:00",
                "promoter_id": "promoter_001",
                "priority_level": "normal",
                "follow_up_needed": False,
                "conversation_type": "consulta inicial"
            }
        }
        
        doc_id = service.store_patient_data(test_data)
        assert doc_id is not None
        print("✅ Almacenamiento funcionando")
        
        # Test 4: Búsqueda
        print("\n4. Test de búsqueda:")
        results = service.search_similar_patients("fiebre", n_results=5)
        assert results is not None
        assert len(results) > 0
        print("✅ Búsqueda funcionando")
        
        # Test 5: Estadísticas
        print("\n5. Test de estadísticas:")
        stats = service.get_collection_stats()
        assert stats is not None
        assert stats["total_conversations"] > 0
        print("✅ Estadísticas funcionando")
        
        print("\n🎉 Todos los tests de ChromaDB pasaron exitosamente!")
        
    finally:
        # Limpiar directorio temporal
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    run_chroma_tests()
