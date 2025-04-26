import speech_recognition as sr
from typing import Optional
from pathlib import Path
from ....config.settings import settings
from ....config.logging import logger
from ....local_apis.stt.listener import AudioListener

class VoiceInterpreter:
    """Sistema avançado de reconhecimento de voz com fallback offline"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.listener = AudioListener()
        self._configure_recognizer()

    def _configure_recognizer(self) -> None:
        """Configura parâmetros de qualidade de áudio"""
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = False

    def capture_voice_command(self, timeout: int = 5) -> Optional[str]:
        """Captura e processa comandos de voz com tratamento de ruído"""
        try:
            with self.listener as source:
                logger.debug("Ajustando ruído ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("Aguardando comando de voz...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=8
                )
                
                return self._process_audio(audio)
        
        except sr.WaitTimeoutError:
            logger.warning("Tempo limite de gravação excedido")
        except Exception as e:
            logger.error(f"Falha na captura de voz: {e}")
        return None

    def _process_audio(self, audio: sr.AudioData) -> Optional[str]:
        """Processa o áudio usando múltiplos motores de reconhecimento"""
        try:
            # Tentativa com serviço online
            return self.recognizer.recognize_google(
                audio, 
                language=settings.VOICE_LANG
            ).lower()
            
        except sr.UnknownValueError:
            logger.warning("Fala não reconhecida")
        except sr.RequestError:
            logger.warning("Usando fallback offline...")
            return self._try_offline_recognition(audio)
            
        return None

    def _try_offline_recognition(self, audio: sr.AudioData) -> Optional[str]:
        """Fallback para reconhecimento offline usando Vosk"""
        try:
            from vosk import Model, KaldiRecognizer
            import json
            
            model_path = Path(settings.MODELS_DIR) / "vosk"
            if not model_path.exists():
                model_path.mkdir(parents=True)
                logger.warning("Faça o download do modelo Vosk em https://alphacephei.com/vosk/models")
                return None

            model = Model(str(model_path))
            recognizer = KaldiRecognizer(model, 16000)
            
            recognizer.AcceptWaveform(audio.get_wav_data())
            result = json.loads(recognizer.FinalResult())
            
            return result.get("text", "").lower()
            
        except ImportError:
            logger.error("Biblioteca Vosk não instalada")
        except Exception as e:
            logger.error(f"Falha no reconhecimento offline: {e}")
        return None