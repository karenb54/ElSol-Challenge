"""
Test para el servicio de transcripción de Whisper
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from services.transcription_service import TranscriptionService


class TestWhisperService:
    """Tests para el servicio de transcripción"""
    
    @pytest.fixture
    def transcription_service(self):
        """Fixture para crear instancia del servicio"""
        return TranscriptionService()
    
    def test_init(self, transcription_service):
        """Test de inicialización del servicio"""
        assert transcription_service is not None
        assert hasattr(transcription_service, 'whisper_model')
        print("✅ Servicio de transcripción inicializado correctamente")
    
    @patch('services.transcription_service.whisper.load_model')
    def test_load_whisper_model(self, mock_load_model, transcription_service):
        """Test de carga del modelo Whisper"""
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        
        # Simular carga del modelo
        transcription_service._load_whisper_model()
        
        mock_load_model.assert_called_once_with("base")
        print("✅ Modelo Whisper cargado correctamente")
    
    def test_extract_patient_info(self, transcription_service):
        """Test de extracción de información del paciente"""
        sample_text = """
        Hola, soy Juan Pérez, tengo 35 años y soy hombre.
        Me siento mal, tengo fiebre y dolor de cabeza.
        Mi teléfono es 123-456-7890.
        """
        
        result = transcription_service.extract_patient_info(sample_text)
        
        assert 'patient_info' in result
        assert 'medical_info' in result
        assert 'conversation_details' in result
        
        patient_info = result['patient_info']
        assert patient_info['name'] == 'Juan Pérez'
        assert patient_info['age'] == '35'
        assert patient_info['gender'] == 'hombre'
        
        print("✅ Extracción de información del paciente funcionando")
    
    def test_extract_symptoms(self, transcription_service):
        """Test de extracción de síntomas"""
        text = "Tengo fiebre, dolor de cabeza y tos seca"
        symptoms = transcription_service._extract_symptoms(text)
        
        expected_symptoms = ['fiebre', 'dolor de cabeza', 'tos seca']
        assert all(symptom in symptoms for symptom in expected_symptoms)
        print("✅ Extracción de síntomas funcionando")
    
    def test_extract_medications(self, transcription_service):
        """Test de extracción de medicamentos"""
        text = "Estoy tomando paracetamol e ibuprofeno"
        medications = transcription_service._extract_medications(text)
        
        expected_medications = ['paracetamol', 'ibuprofeno']
        assert all(med in medications for med in expected_medications)
        print("✅ Extracción de medicamentos funcionando")
    
    def test_determine_priority(self, transcription_service):
        """Test de determinación de prioridad"""
        # Test prioridad alta
        high_priority_text = "Me siento muy mal, tengo dolor en el pecho"
        priority = transcription_service._determine_priority(high_priority_text)
        assert priority == "alta"
        
        # Test prioridad normal
        normal_priority_text = "Tengo un resfriado leve"
        priority = transcription_service._determine_priority(normal_priority_text)
        assert priority == "normal"
        
        print("✅ Determinación de prioridad funcionando")
    
    @patch('services.transcription_service.whisper.load_model')
    def test_transcribe_audio_file(self, mock_load_model, transcription_service):
        """Test de transcripción de archivo de audio"""
        # Mock del modelo Whisper
        mock_model = Mock()
        mock_model.transcribe.return_value = {
            "text": "Hola, soy Juan Pérez, tengo 35 años y tengo fiebre."
        }
        mock_load_model.return_value = mock_model
        
        # Crear archivo de audio temporal para testing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(b'fake audio data')
            temp_audio_path = temp_audio.name
        
        try:
            # Test transcripción
            result = transcription_service.transcribe_audio(temp_audio_path)
            
            assert result is not None
            assert "text" in result
            assert "Juan Pérez" in result["text"]
            
            print("✅ Transcripción de audio funcionando")
            
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_audio_path)


def run_whisper_tests():
    """Función para ejecutar todos los tests de Whisper"""
    print("🧪 Ejecutando tests de Whisper...")
    
    service = TranscriptionService()
    
    # Test 1: Inicialización
    print("\n1. Test de inicialización:")
    assert service is not None
    print("✅ Servicio inicializado")
    
    # Test 2: Extracción de información
    print("\n2. Test de extracción de información:")
    sample_text = "Hola, soy María García, tengo 28 años y soy mujer. Tengo dolor de cabeza."
    result = service.extract_patient_info(sample_text)
    
    assert result['patient_info']['name'] == 'María García'
    assert result['patient_info']['age'] == '28'
    assert result['patient_info']['gender'] == 'mujer'
    assert 'dolor de cabeza' in result['medical_info']['symptoms']
    print("✅ Extracción de información funcionando")
    
    # Test 3: Extracción de síntomas
    print("\n3. Test de extracción de síntomas:")
    symptoms = service._extract_symptoms("Tengo fiebre, tos y dolor de garganta")
    assert 'fiebre' in symptoms
    assert 'tos' in symptoms
    assert 'dolor de garganta' in symptoms
    print("✅ Extracción de síntomas funcionando")
    
    # Test 4: Prioridad
    print("\n4. Test de determinación de prioridad:")
    high_priority = service._determine_priority("Tengo dolor en el pecho")
    normal_priority = service._determine_priority("Tengo un resfriado")
    
    assert high_priority == "alta"
    assert normal_priority == "normal"
    print("✅ Determinación de prioridad funcionando")
    
    print("\n🎉 Todos los tests de Whisper pasaron exitosamente!")


if __name__ == "__main__":
    run_whisper_tests()
