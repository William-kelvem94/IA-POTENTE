import sqlite3
from datetime import datetime
from typing import List, Tuple
from pathlib import Path
from ..config.settings import settings
from ..config.logging import logger

class KnowledgeBase:
    """Sistema de memória de longo prazo para armazenamento e recuperação de interações"""
    
    def __init__(self):
        self.db_path = Path(settings.DATA_DIR) / "knowledge" / "jarvis_memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Cria a estrutura inicial do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    context_tags TEXT,
                    interaction_type TEXT DEFAULT 'conversation'
                )
            ''')
            conn.commit()
            logger.info("Banco de dados de conhecimento inicializado")

    def add_interaction(self, user_input: str, response: str, tags: str = "") -> None:
        """Armazena uma nova interação na base de conhecimento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO interactions 
                    (input_text, response_text, timestamp, context_tags, interaction_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_input,
                    response,
                    datetime.now().isoformat(),
                    tags,
                    'conversation'
                ))
                conn.commit()
            logger.debug(f"Interação armazenada: {user_input[:30]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar interação: {e}")

    def search_interactions(self, query: str, limit: int = 5) -> List[Tuple]:
        """Busca interações relevantes baseado em termos-chave"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT input_text, response_text, timestamp 
                    FROM interactions
                    WHERE input_text LIKE ? OR response_text LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (f"%{query}%", f"%{query}%", limit))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Erro na busca de interações: {e}")
            return []

# Exemplo de uso
if __name__ == "__main__":
    kb = KnowledgeBase()
    kb.add_interaction("Como está o tempo?", "No momento, está ensolarado", "clima")
    results = kb.search_interactions("tempo")
    print("Resultados:", results)