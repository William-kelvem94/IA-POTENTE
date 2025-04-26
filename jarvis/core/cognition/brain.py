from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional
import torch
import random
from ..config.settings import settings
from ..config.logging import logger

class CognitiveProcessor:
    """Núcleo de processamento de decisões e geração de respostas"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_models()
        self.humor_responses = [
            "Ah, agora você me pegou! Isso é uma situação complexa para um supercomputador como eu.",
            "Não estou caindo na sua ironia, mas adorei a tentativa. Ah, como é bom ser humano!"
        ]

    def _load_models(self) -> None:
        """Carrega os modelos de linguagem"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.TOKENIZER_NAME,
                padding_side="left"
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.AI_MODEL_NAME,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            logger.info("Modelos de linguagem carregados com sucesso")
        except Exception as e:
            logger.error(f"Falha ao carregar modelos: {e}")
            raise

    def process_input(self, user_input: str) -> str:
        """Processa a entrada do usuário e gera uma resposta contextual"""
        if not user_input.strip():
            return "Desculpe, não entendi. Poderia repetir?"
        
        if self._detect_humor(user_input):
            return self._generate_humorous_response()
        
        return self._generate_serious_response(user_input)

    def _detect_humor(self, text: str) -> bool:
        """Detecta intenção humorística no texto"""
        keywords = ["piada", "engraçado", "irônico", "brincadeira"]
        return any(keyword in text.lower() for keyword in keywords)

    def _generate_humorous_response(self) -> str:
        """Gera resposta humorística"""
        return random.choice(self.humor_responses)

    def _generate_serious_response(self, prompt: str) -> str:
        """Gera resposta séria usando o modelo de linguagem"""
        try:
            inputs = self.tokenizer(
                f"Responda de forma objetiva: {prompt}",
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            return self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            ).split(":")[-1].strip()
        
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return "Estou tendo dificuldades para processar isso no momento."