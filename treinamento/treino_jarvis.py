import os
import torch
from datetime import datetime
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback
)
from datasets import load_dataset, concatenate_datasets
from peft import LoraConfig, get_peft_model
import numpy as np
from sklearn.model_selection import train_test_split

# Configurações
MODEL_NAME = "tiiuae/falcon-7b"
DATA_PATH = "../jarvis/data/training"
OUTPUT_DIR = "../jarvis/data/models/jarvis_v1"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class JarvisTrainer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = self._prepare_model()
        self.data = self._load_data()

    def _prepare_model(self):
        """Carrega e prepara o modelo com LoRA"""
        base_model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            load_in_4bit=True
        )
        
        peft_config = LoraConfig(
            r=32,
            lora_alpha=64,
            target_modules=["query_key_value"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        return get_peft_model(base_model, peft_config)

    def _load_data(self):
        """Carrega e combina datasets"""
        datasets = {
            'assistente': load_dataset("OpenAssistant/oasst1"),
            'personalidade': load_dataset("allenai/soda"),
            'comandos': self._generate_commands_dataset()
        }
        
        def format_text(examples):
            return {"text": [f"USER: {q}\nJARVIS: {a}" for q, a in zip(examples['input'], examples['output'])]}
        
        combined = concatenate_datasets([
            datasets['assistente']['train'].map(format_text, batched=True),
            datasets['personalidade']['train'].map(format_text, batched=True),
            datasets['comandos'].map(format_text, batched=True)
        ])
        
        return combined.train_test_split(test_size=0.1)

    def _generate_commands_dataset(self):
        """Gera dataset sintético de comandos"""
        commands = [
            ("Abra o navegador", "Abrindo o navegador Chrome..."),
            ("Pesquise arquivos sobre relatórios", "Procurando por 'relatórios' em seus documentos..."),
            ("Ative o modo silencioso", "Modo silencioso ativado. Notificações serão silenciadas."),
            ("Conte uma piada sobre IA", "Por que a IA foi ruim no poker? Porque sempre foldava quando via um neural network!")
        ]
        return {
            'input': [c[0] for c in commands],
            'output': [c[1] for c in commands]
        }

    def _tokenize(self, examples):
        """Tokenização otimizada para diálogos"""
        return self.tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

    def train(self):
        """Executa o treinamento completo"""
        args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            num_train_epochs=5,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            gradient_accumulation_steps=2,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=1000,
            learning_rate=2e-5,
            fp16=True,
            logging_dir=f"{OUTPUT_DIR}/logs",
            report_to="tensorboard",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            group_by_length=True,
            resume_from_checkpoint=True
        )
        
        trainer = Trainer(
            model=self.model,
            args=args,
            train_dataset=self.data["train"],
            eval_dataset=self.data["test"],
            data_collator=DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        try:
            print("Iniciando treinamento...")
            trainer.train()
            self.model.save_pretrained(OUTPUT_DIR)
            self.tokenizer.save_pretrained(OUTPUT_DIR)
            print("Treinamento concluído com sucesso!")
        except Exception as e:
            print(f"Erro grave: {e}")
            self.model.save_pretrained(f"{OUTPUT_DIR}_backup_{datetime.now().strftime('%Y%m%d_%H%M')}")

if __name__ == "__main__":
    trainer = JarvisTrainer()
    trainer.train()