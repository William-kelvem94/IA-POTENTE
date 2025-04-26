# organizar_projeto.py CORRIGIDO
import os
import shutil
from pathlib import Path

def criar_estrutura(base_dir):
    estrutura = [
        ('jarvis/core/cognition', ['agent.py', 'brain.py', 'memory.py']),
        ('jarvis/core/perception', ['vision.py', 'speech_recognition.py', 'speech_generation.py']),
        ('jarvis/core/action', ['system_integration.py', 'routines.py']),
        ('jarvis/local_apis/tts', ['voice_engine.py']),
        ('jarvis/local_apis/stt', ['listener.py']),
        ('jarvis/data/training', []),
        ('jarvis/data/models', []),
        ('jarvis/data/knowledge', []),
        ('jarvis/config', ['settings.py']),
    ]
    
    for parent_dir, files in estrutura:
        full_path = Path(base_dir) / parent_dir
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Criar __init__.py automaticamente
        init_file = full_path / '__init__.py'
        if not init_file.exists():
            init_file.touch()
        
        for file in files:
            file_path = full_path / file
            if not file_path.exists():
                file_path.touch()

def mapear_arquivos(base_dir):
    mapeamento = {
        'agent.py': 'core/cognition/agent.py',
        'brain.py': 'core/cognition/brain.py',
        'memoria.py': 'core/cognition/memory.py',
        'vision.py': 'core/perception/vision.py',
        'voice.py': 'core/perception/speech_generation.py',
        'voice_input.py': 'core/perception/speech_recognition.py',
        'utils_audio.py': 'local_apis/tts/voice_engine.py',
        'integracao_pc.py': 'core/action/system_integration.py',
        'rotinas.py': 'core/action/routines.py',
        'screen.py': 'core/action/display.py',
        'logger.py': 'config/logging.py',
        'config.py': 'config/settings.py',
        'main.py': 'jarvis/main.py'
    }
    
    for arquivo_origem, destino in mapeamento.items():
        origem = Path(base_dir) / 'jarvis' / arquivo_origem
        destino_path = Path(base_dir) / 'jarvis' / destino
        
        if origem.exists():
            destino_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(origem), str(destino_path))
            print(f"Movido: {arquivo_origem} -> {destino}")

def limpar_antigos(base_dir):
    pastas_antigas = ['__pycache__', 'audios', 'dados']
    for pasta in pastas_antigas:
        path = Path(base_dir) / 'jarvis' / pasta
        if path.exists():
            shutil.rmtree(path)
            print(f"Removido: {pasta}")

if __name__ == "__main__":
    projeto_dir = input("Digite o caminho completo do diretório do projeto: ")
    
    print("\nCriando nova estrutura...")
    criar_estrutura(projeto_dir)
    
    print("\nReorganizando arquivos...")
    mapear_arquivos(projeto_dir)
    
    print("\nLimpando arquivos antigos...")
    limpar_antigos(projeto_dir)
    
    print("\nReorganização concluída com sucesso!")
    print("Nova estrutura:\n")
    os.system(f"tree {Path(projeto_dir)/'jarvis'}")