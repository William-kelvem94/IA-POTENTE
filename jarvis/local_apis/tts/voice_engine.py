import wave
import numpy as np
import pyaudio
import audioop
from typing import Optional
from pathlib import Path
from datetime import datetime
from pydub import AudioSegment, effects
from ....config.settings import settings
from ....config.logging import logger

class VoiceEngine:
    """Motor de processamento de áudio completo e otimizado"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.sample_rate = settings.SAMPLE_RATE
        self.chunk_size = 1024
        self.silence_threshold = settings.VOICE_SILENCE_THRESHOLD

    def record_audio(self, duration: float = 5.0) -> Optional[Path]:
        """Grava áudio do microfone com tratamento de ruído"""
        try:
            file_path = Path(settings.DATA_DIR) / "audio" / f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            logger.info(f"Iniciando gravação de {duration} segundos...")
            frames = []
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size)
                frames.append(self._process_chunk(data))

            stream.stop_stream()
            stream.close()

            self._save_recording(frames, file_path)
            return self._postprocess_audio(file_path)
        
        except Exception as e:
            logger.error(f"Falha na gravação: {e}")
            return None

    def _process_chunk(self, data: bytes) -> bytes:
        """Processa cada chunk de áudio em tempo real"""
        try:
            # Remove silêncio e normaliza
            rms = audioop.rms(data, 2)
            if rms < self.silence_threshold:
                return b""
            return audioop.mul(data, 2, 2)
        except:
            return data

    def _save_recording(self, frames: list, path: Path) -> None:
        """Salva os dados brutos de áudio"""
        with wave.open(str(path), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

    def _postprocess_audio(self, path: Path) -> Path:
        """Aplica pós-processamento no áudio gravado"""
        try:
            audio = AudioSegment.from_file(str(path))
            audio = effects.normalize(audio)
            audio = audio.low_pass_filter(3000)
            audio.export(str(path), format="wav")
            logger.info(f"Áudio processado e salvo em: {path}")
            return path
        except Exception as e:
            logger.error(f"Erro no pós-processamento: {e}")
            return path

    def __del__(self):
        self.audio.terminate()