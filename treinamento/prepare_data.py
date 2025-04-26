from datasets import load_dataset, DatasetDict, Dataset  # Adicionado import Dataset
from sklearn.model_selection import train_test_split  # Adicionado import
import pandas as pd

def criar_dataset_personalizado():
    # Carregar dados públicos
    oa = load_dataset("OpenAssistant/oasst1")['train'].select(range(5000))
    soda = load_dataset("allenai/soda")['train'].select(range(2000))
    
    # Converter para formato pandas para manipulação
    df_oa = pd.DataFrame(oa)
    df_soda = pd.DataFrame(soda)
    
    # Limpar e formatar
    df_oa = df_oa[['text']].rename(columns={'text': 'dialog'})
    df_soda = df_soda[['dialogue']].rename(columns={'dialogue': 'dialog'})
    
    # Combinar datasets
    combined = pd.concat([df_oa, df_soda])
    combined = combined.sample(frac=1).reset_index(drop=True)  # Embaralhar
    
    # Dividir treino/teste
    train, test = train_test_split(combined, test_size=0.1)
    
    # Converter para Dataset HuggingFace
    return DatasetDict({
        'train': Dataset.from_pandas(train),
        'test': Dataset.from_pandas(test)
    })