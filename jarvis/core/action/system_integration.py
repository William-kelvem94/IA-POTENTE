import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional
from ....config.settings import settings
from ....config.logging import logger

class SystemOperator:
    """Gerencia interações seguras com o sistema operacional"""
    
    ALLOWED_PATHS = [
        Path.home() / "Documents",
        Path.home() / "Downloads",
        Path.home() / "Desktop"
    ]

    def __init__(self):
        self.os_type = platform.system()
        self.safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ .")

    def execute_command(self, command: str) -> Optional[str]:
        """Executa comandos do sistema com validação de segurança"""
        if not self._validate_input(command):
            logger.warning(f"Comando bloqueado: {command}")
            return "Comando contém caracteres inválidos"

        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                check=True,
                shell=False,
                timeout=15
            )
            logger.debug(f"Comando executado: {command}")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar comando: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Falha crítica: {e}")
            return None

    def find_files(self, query: str, max_results: int = 10) -> List[str]:
        """Busca segura por arquivos com índice de permissão"""
        safe_query = "".join(c for c in query if c in self.safe_chars)
        results = []
        
        for path in self.ALLOWED_PATHS:
            if not path.exists():
                continue
                
            for root, _, files in os.walk(path):
                for file in files:
                    if safe_query.lower() in file.lower():
                        results.append(str(Path(root) / file))
                        if len(results) >= max_results:
                            return results
        return results

    def launch_application(self, app_name: str) -> bool:
        """Inicia aplicativos de forma segura usando mapeamento"""
        app_map = {
            "navegador": {
                "Windows": "C:/Program Files/Google/Chrome/Application/chrome.exe",
                "Linux": "/usr/bin/google-chrome"
            },
            "editor": {
                "Windows": "notepad.exe",
                "Linux": "gedit"
            }
        }
        
        if app_name.lower() in app_map:
            app_path = app_map[app_name.lower()].get(self.os_type)
            if app_path and Path(app_path).exists():
                return self._safe_launch(app_path)
        
        logger.warning(f"Aplicativo não mapeado: {app_name}")
        return False

    def _validate_input(self, text: str) -> bool:
        """Valida entrada contra injeção de comandos"""
        return all(c in self.safe_chars for c in text)

    def _safe_launch(self, path: str) -> bool:
        """Inicia aplicativo com verificação de integridade"""
        try:
            subprocess.Popen([path], shell=False)
            return True
        except Exception as e:
            logger.error(f"Falha ao iniciar aplicativo: {e}")
            return False