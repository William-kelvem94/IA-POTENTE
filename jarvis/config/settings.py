import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Settings:
    # Diretórios
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = DATA_DIR / "models"
    TRAINING_DIR: Path = DATA_DIR / "training"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Modelo de IA
    AI_MODEL_NAME: str = "tiiuae/falcon-7b-instruct"
    TOKENIZER_NAME: str = "tiiuae/falcon-7b-instruct"
    
    # Configurações de Áudio
    SAMPLE_RATE: int = 16000
    VOICE_SILENCE_THRESHOLD: float = 0.01
    
    # Segurança
    API_KEYS = {
        'huggingface': os.getenv('HF_API_KEY', '')
    }

    @classmethod
    def create_dirs(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.MODELS_DIR.mkdir(exist_ok=True)
        cls.TRAINING_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

# Inicialização
settings = Settings()
settings.create_dirs()