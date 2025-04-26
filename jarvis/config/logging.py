import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .settings import settings

class JarvisLogger:
    def __init__(self, name="Jarvis"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        
        # File Handler (rotativo)
        file_handler = RotatingFileHandler(
            settings.LOGS_DIR / 'jarvis.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger

# Logger global
logger = JarvisLogger().get_logger()