from transformers import AutoModelForCausalLM, AutoTokenizer
import random
from typing import Optional  # Adicionando importação faltante
from ..config.logging import logger
from ..perception.speech_recognition import VoiceInterpreter
from ..action.system_integration import SystemOperator
from .memory import KnowledgeBase

class JarvisCore:
    """Núcleo principal de operações do assistente"""
    
    def __init__(self):
        self.voice_interface = VoiceInterpreter()
        self.system_operator = SystemOperator()
        self.knowledge_base = KnowledgeBase()
        self._init_responses()
        self._load_models()

    def _load_models(self):
        """Carrega os modelos de IA"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-rw-1b")
            self.model = AutoModelForCausalLM.from_pretrained("tiiuae/falcon-rw-1b")
            logger.info("Modelos carregados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            raise

    def _init_responses(self) -> None:
        """Carrega respostas personalizadas"""
        self.responses = {
            "greeting": ["Às suas ordens, senhor", "Como posso ajudar?"],
            "confused": ["Parece que estou tendo um dia complicado", "Vou precisar de mais dados para isso"]
        }

    def run(self) -> None:
        """Loop principal de execução"""
        logger.info("Inicializando núcleo Jarvis...")
        try:
            while True:
                self._process_cycle()
        except KeyboardInterrupt:
            logger.info("Desligamento solicitado")
        except Exception as e:
            logger.critical(f"Falha crítica: {e}")

    def _process_cycle(self) -> None:
        """Executa um ciclo completo de interação"""
        user_input = self._get_user_input()
        if not user_input:
            return

        if self._handle_special_commands(user_input):
            return

        response = self._generate_response(user_input)
        self._execute_actions(response)
        self._store_interaction(user_input, response)

    def _get_user_input(self) -> Optional[str]:
        """Obtém entrada do usuário com múltiplos métodos"""
        try:
            return self.voice_interface.capture_voice_command()
        except Exception as e:
            logger.error(f"Falha na captura de entrada: {e}")
            return None

    def _handle_special_commands(self, command: str) -> bool:
        """Processa comandos específicos do sistema"""
        triggers = {
            "desligar": self._shutdown,
            "reiniciar": self._restart,
            "modo silencioso": lambda: logger.info("Modo silencioso ativado")
        }
        
        for trigger, action in triggers.items():
            if trigger in command.lower():
                action()
                return True
        return False

    def _generate_response(self, input_text: str) -> str:
        """Gera resposta usando IA ou regras pré-definidas"""
        try:
            if any(keyword in input_text.lower() for keyword in ["piada", "engraçado"]):
                return random.choice(self.responses["confused"])
            
            inputs = self.tokenizer(
                f"USER: {input_text}\nJARVIS:",
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=100,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True).split("JARVIS:")[-1].strip()
        
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return random.choice(self.responses["confused"])

    def _execute_actions(self, response: str) -> None:
        """Executa ações físicas no sistema"""
        if "abrir" in response.lower():
            app_name = response.split("abrir")[-1].strip()
            self.system_operator.launch_application(app_name)

    def _store_interaction(self, input_text: str, response: str) -> None:
        """Armazena interação na base de conhecimento"""
        self.knowledge_base.add_interaction(input_text, response)

    def _shutdown(self) -> None:
        """Procedimento de desligamento seguro"""
        logger.info("Iniciando desligamento...")
        raise KeyboardInterrupt

    def _restart(self) -> None:
        """Reinicialização do sistema"""
        logger.info("Reinicializando...")
        self.__init__()
        self.run()

if __name__ == "__main__":
    jarvis = JarvisCore()
    jarvis.run()