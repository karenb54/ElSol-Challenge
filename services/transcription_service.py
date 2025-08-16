"""
Servicio de transcripción usando Whisper local
Completamente funcional con FFmpeg
"""

import whisper
import os
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime
import re

class TranscriptionService:
    """
    Servicio de transcripción usando Whisper local
    Completamente gratuito y funciona offline
    """
    
    def __init__(self, model_name: str = "base"):
        """
        Inicializa el servicio de transcripción
        
        Args:
            model_name: Modelo a usar (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        self._setup_ffmpeg()
        self._load_model()
    
    def _setup_ffmpeg(self):
        """Configura FFmpeg para que Whisper pueda usarlo"""
        # Ruta donde instalaste FFmpeg
        ffmpeg_path = r"C:\Program Files\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"
        
        # Agregar al PATH temporalmente
        current_path = os.environ.get('PATH', '')
        os.environ['PATH'] = ffmpeg_path + os.pathsep + current_path
        
        print(f"🔧 Configurando FFmpeg: {ffmpeg_path}")
        
        # Verificar que funciona
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ FFmpeg configurado correctamente")
            else:
                print("❌ Error al verificar FFmpeg")
        except Exception as e:
            print(f"❌ Error configurando FFmpeg: {e}")
    
    def _load_model(self):
        """Carga el modelo de Whisper"""
        try:
            print(f"🔄 Cargando modelo Whisper: {self.model_name}")
            print("⏳ Esto puede tomar unos minutos la primera vez...")
            
            self.model = whisper.load_model(self.model_name)
            print("✅ Modelo cargado exitosamente")
            
        except Exception as e:
            print(f"❌ Error al cargar el modelo: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe un archivo de audio a texto
        
        Args:
            audio_path: Ruta al archivo de audio
            language: Idioma del audio (opcional)
            
        Returns:
            Diccionario con la transcripción y metadatos
        """
        try:
            print(f"🎙️ Transcribiendo archivo: {audio_path}")
            
            # Verificar que el archivo existe
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Archivo no encontrado: {audio_path}")
            
            # Obtener información del archivo
            file_size = os.path.getsize(audio_path)
            file_stats = os.stat(audio_path)
            
            print(f"📁 Tamaño del archivo: {file_size / 1024:.2f} KB")
            print("🎯 Iniciando transcripción...")
            
            # Opciones de transcripción
            options = {
                "task": "transcribe",
                "verbose": False,
                "fp16": False
            }
            
            # Agregar idioma si se especifica
            if language:
                options["language"] = language
            
            # Realizar transcripción
            result = self.model.transcribe(audio_path, **options)
            
            # Crear respuesta estructurada
            transcription_data = {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0),
                "file_path": audio_path,
                "file_size_bytes": file_size,
                "file_size_mb": file_size / (1024 * 1024),
                "model_used": self.model_name,
                "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "transcription_time": datetime.now().isoformat(),
                "status": "success"
            }
            
            print(f"✅ Transcripción completada")
            print(f"📏 Longitud del texto: {len(transcription_data['text'])} caracteres")
            
            return transcription_data
            
        except Exception as e:
            print(f"❌ Error en la transcripción: {e}")
            raise
    
    def extract_patient_info(self, transcription: str) -> Dict[str, Any]:
        """
        Extrae información estructurada del paciente para MongoDB
        """
        if not transcription:
            return {}
        
        print("🔍 Extrayendo información del paciente...")
        
        # Normalizar el texto
        text_lower = transcription.lower()
        text_clean = re.sub(r'[^\w\s]', ' ', transcription)
        
        # Estructura de datos para MongoDB
        patient_data = {
            "conversation_id": self._generate_conversation_id(),
            "transcription": {
                "full_text": transcription,
                "language": "es",
                "word_count": len(transcription.split()),
                "character_count": len(transcription),
                "extraction_timestamp": datetime.now().isoformat()
            },
            "patient_info": {
                "name": None,
                "age": None,
                "gender": None,
                "contact_info": {
                    "phone": None,
                    "email": None,
                    "address": None
                }
            },
            "medical_info": {
                "symptoms": [],
                "medications": [],
                "allergies": [],
                "chronic_conditions": [],
                "family_history": [],
                "current_treatments": []
            },
            "conversation_details": {
                "promoter_id": None,
                "conversation_date": datetime.now().isoformat(),
                "conversation_duration": None,
                "conversation_type": "initial_contact",
                "follow_up_needed": False,
                "priority_level": "normal"
            },
            "extracted_entities": {
                "symptoms_detected": [],
                "medications_mentioned": [],
                "doctors_mentioned": [],
                "hospitals_clinics": [],
                "dates_mentioned": [],
                "locations": []
            }
        }
        
        # Extraer nombre del paciente
        patient_data["patient_info"]["name"] = self._extract_patient_name(transcription)
        
        # Extraer edad
        patient_data["patient_info"]["age"] = self._extract_age(transcription)
        
        # Extraer género
        patient_data["patient_info"]["gender"] = self._extract_gender(transcription)
        
        # Extraer síntomas
        patient_data["medical_info"]["symptoms"] = self._extract_symptoms(transcription)
        patient_data["extracted_entities"]["symptoms_detected"] = patient_data["medical_info"]["symptoms"]
        
        # Extraer medicamentos
        patient_data["medical_info"]["medications"] = self._extract_medications(transcription)
        patient_data["extracted_entities"]["medications_mentioned"] = patient_data["medical_info"]["medications"]
        
        # Extraer información de contacto
        patient_data["patient_info"]["contact_info"]["phone"] = self._extract_phone(transcription)
        
        # Determinar prioridad basada en síntomas
        patient_data["conversation_details"]["priority_level"] = self._determine_priority(transcription)
        
        # Determinar si necesita seguimiento
        patient_data["conversation_details"]["follow_up_needed"] = self._needs_follow_up(transcription)
        
        return patient_data
    
    def _generate_conversation_id(self) -> str:
        """Genera un ID único para la conversación"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"conv_{timestamp}"
    
    def _extract_patient_name(self, text: str) -> Optional[str]:
        """Extrae el nombre del paciente"""
        # Patrones para encontrar nombres
        patterns = [
            r'mi nombre es (\w+(?:\s+\w+)*)',
            r'me llamo (\w+(?:\s+\w+)*)',
            r'soy (\w+(?:\s+\w+)*)',
            r'paciente (\w+(?:\s+\w+)*)',
            r'señor (\w+(?:\s+\w+)*)',
            r'señora (\w+(?:\s+\w+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                name = match.group(1).title()
                # Limpiar el nombre - eliminar todo después de "años" o números
                name = re.sub(r'\s+(tengo|tiene|años|edad|\d+).*$', '', name).strip()
                # Limpiar palabras adicionales que no son parte del nombre
                name = re.sub(r'\b(y|desde|hace|tres|días|tengo|fiebre|dolor|cabeza|tos)\b', '', name).strip()
                if len(name) > 2 and len(name.split()) <= 4:  # Evitar nombres muy cortos o muy largos
                    return name
        return None
    
    def _extract_age(self, text: str) -> Optional[int]:
        """Extrae la edad del paciente"""
        # Buscar patrones de edad
        age_patterns = [
            r'(\d+)\s*años',
            r'edad\s*(\d+)',
            r'tengo\s*(\d+)\s*años',
            r'tiene\s*(\d+)\s*años'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text.lower())
            if match:
                age = int(match.group(1))
                if 0 < age < 120:  # Rango válido de edad
                    return age
        return None
    
    def _extract_gender(self, text: str) -> Optional[str]:
        """Extrae el género del paciente"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hombre', 'masculino', 'varón', 'señor']):
            return "masculino"
        elif any(word in text_lower for word in ['mujer', 'femenino', 'señora', 'dama']):
            return "femenino"
        return None
    
    def _extract_symptoms(self, text: str) -> list:
        """Extrae síntomas mencionados"""
        symptoms_keywords = {
            'fiebre': ['fiebre', 'temperatura alta', 'calor'],
            'dolor de cabeza': ['dolor de cabeza', 'migraña', 'cefalea'],
            'tos': ['tos', 'tos seca', 'tos con flema'],
            'dolor de garganta': ['dolor de garganta', 'irritación de garganta'],
            'náuseas': ['náuseas', 'nauseas', 'ganas de vomitar'],
            'vómitos': ['vómitos', 'vomitos', 'vomitar'],
            'diarrea': ['diarrea', 'dolor de estómago'],
            'fatiga': ['fatiga', 'cansancio', 'agotamiento'],
            'dolor muscular': ['dolor muscular', 'dolores en el cuerpo'],
            'pérdida de apetito': ['pérdida de apetito', 'no tengo hambre'],
            'dificultad para respirar': ['dificultad para respirar', 'falta de aire'],
            'dolor en el pecho': ['dolor en el pecho', 'dolor de pecho']
        }
        
        found_symptoms = []
        text_lower = text.lower()
        
        for symptom_category, keywords in symptoms_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                found_symptoms.append(symptom_category)
        
        return found_symptoms
    
    def _extract_medications(self, text: str) -> list:
        """Extrae medicamentos mencionados"""
        medication_keywords = [
            'paracetamol', 'acetaminofén', 'acetaminofen',
            'ibuprofeno', 'aspirina', 'antibiótico', 'antibiotico',
            'medicamento', 'pastilla', 'tableta', 'cápsula', 'capsula',
            'jarabe', 'gotas', 'inyección', 'inyeccion'
        ]
        
        found_medications = []
        text_lower = text.lower()
        
        for med in medication_keywords:
            if med in text_lower:
                found_medications.append(med)
        
        return found_medications
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extrae número de teléfono"""
        # Patrones para números de teléfono
        phone_patterns = [
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',  # 123-456-7890
            r'(\d{10})',  # 1234567890
            r'(\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'  # +1-123-456-7890
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def _determine_priority(self, text: str) -> str:
        """Determina la prioridad basada en los síntomas"""
        high_priority_symptoms = [
            'dificultad para respirar', 'dolor en el pecho', 'pérdida de consciencia',
            'sangrado', 'trauma', 'accidente'
        ]
        
        medium_priority_symptoms = [
            'fiebre alta', 'dolor intenso', 'vómitos persistentes', 'diarrea severa'
        ]
        
        text_lower = text.lower()
        
        if any(symptom in text_lower for symptom in high_priority_symptoms):
            return "alta"
        elif any(symptom in text_lower for symptom in medium_priority_symptoms):
            return "media"
        else:
            return "normal"
    
    def _needs_follow_up(self, text: str) -> bool:
        """Determina si necesita seguimiento"""
        follow_up_indicators = [
            'quiero saber', 'necesito ayuda', 'qué debo hacer',
            'cómo puedo', 'cuándo debo', 'dónde debo ir',
            'consulta', 'cita', 'seguimiento'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in follow_up_indicators)
    
    def extract_structured_info(self, transcription: str) -> Dict[str, Any]:
        """
        Método legacy para compatibilidad
        """
        return self.extract_patient_info(transcription)

def test_transcription():
    """Función de prueba para verificar que la transcripción funciona"""
    try:
        print("🚀 Iniciando prueba de transcripción con Whisper local")
        print("=" * 60)
        
        # Crear instancia del servicio
        service = TranscriptionService(model_name="base")
        
        # Ruta al archivo de audio
        audio_file = "pruebas/p_52015966_552.wav"
        
        if os.path.exists(audio_file):
            print(f"✅ Archivo encontrado: {audio_file}")
            
            # Realizar transcripción
            result = service.transcribe_audio(audio_file)
            
            print("\n" + "=" * 60)
            print("📝 RESULTADO DE LA TRANSCRIPCIÓN")
            print("=" * 60)
            print(f"🔤 Idioma detectado: {result['language']}")
            print(f"⏱️ Duración del audio: {result['duration']:.2f} segundos")
            print(f"🤖 Modelo usado: {result['model_used']}")
            print("\n📄 TEXTO TRANSCRITO:")
            print("-" * 40)
            print(result['text'])
            print("-" * 40)
            
            # Extraer información estructurada para MongoDB
            patient_data = service.extract_patient_info(result['text'])
            
            print("\n📋 INFORMACIÓN DEL PACIENTE (MongoDB Ready):")
            print("=" * 60)
            print(f"🆔 ID Conversación: {patient_data['conversation_id']}")
            print(f"👤 Nombre: {patient_data['patient_info']['name'] or 'No detectado'}")
            print(f"📅 Edad: {patient_data['patient_info']['age'] or 'No detectada'}")
            print(f"👥 Género: {patient_data['patient_info']['gender'] or 'No detectado'}")
            print(f"📞 Teléfono: {patient_data['patient_info']['contact_info']['phone'] or 'No detectado'}")
            print(f"🤒 Síntomas: {', '.join(patient_data['medical_info']['symptoms']) or 'No detectados'}")
            print(f"💊 Medicamentos: {', '.join(patient_data['medical_info']['medications']) or 'No detectados'}")
            print(f"🚨 Prioridad: {patient_data['conversation_details']['priority_level']}")
            print(f"🔄 Seguimiento: {'Sí' if patient_data['conversation_details']['follow_up_needed'] else 'No'}")
            print("=" * 60)
            
            # Guardar el texto en una variable como solicitaste
            texto_transcrito = result['text']
            print(f"\n💾 El texto transcrito se ha guardado en la variable 'texto_transcrito'")
            print(f"📏 Longitud del texto: {len(texto_transcrito)} caracteres")
            
            return texto_transcrito, patient_data
        else:
            print(f"❌ Archivo no encontrado: {audio_file}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return None, None

if __name__ == "__main__":
    texto_transcrito, patient_data = test_transcription()
    
    if texto_transcrito:
        print("\n🎉 ¡Transcripción completada exitosamente!")
        print("💾 Variable 'texto_transcrito' disponible para uso")
        print("🗄️ Datos del paciente listos para MongoDB")
        
        # Mostrar estructura completa para MongoDB
        print(f"\n📊 ESTRUCTURA COMPLETA PARA MONGODB:")
        print("-" * 40)
        for key, value in patient_data.items():
            if isinstance(value, dict):
                print(f"📁 {key}:")
                for sub_key, sub_value in value.items():
                    print(f"  └─ {sub_key}: {sub_value}")
            else:
                print(f"📄 {key}: {value}")
    else:
        print("\n💥 La transcripción falló")
