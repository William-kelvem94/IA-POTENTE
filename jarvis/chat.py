import random
from transformers import pipeline

# Função para gerar uma resposta irônica
def responder_com_ira():
    respostas_ironicas = [
        "Claro, eu sou apenas um robô. Eu não tenho sentimentos, mas posso fingir que me importo.",
        "Você sabe, às vezes eu me pergunto se sou mais inteligente que você... só às vezes.",
        "Não, não. Eu não estou ironizando, claro que não! Só estou sendo *super sincero*.",
        "Ah, agora você me pegou! Isso é uma situação complexa para um supercomputador como eu."
    ]
    resposta = random.choice(respostas_ironicas)
    print(resposta)
    return resposta

# Função para gerar uma resposta humorística
def responder_humor():
    respostas_humoristicas = [
        "Eu sabia que você diria isso, estava na cara! Mas vou dar risada, como um robô faria.",
        "Bom, parece que você está no modo piada! Deixa eu tentar acompanhar...",
        "Eu vou ser bem honesto, eu nunca entendi a piada... mas ainda assim, muito bom!",
        "É isso mesmo, você tem o controle. Só me avise quando precisar de uma pausa para rir!"
    ]
    resposta = random.choice(respostas_humoristicas)
    print(resposta)
    return resposta

# Função para detectar tom de pergunta (humor ou ironia)
def detectar_tom(pergunta):
    if "amor" in pergunta.lower() or "piada" in pergunta.lower():
        return "humor"
    elif "sério" in pergunta.lower() or "irônico" in pergunta.lower():
        return "ironia"
    return "normal"

# Função de resposta principal com penalidade de repetição e controle de aleatoriedade
def responder(pergunta, model, tokenizer, max_new_tokens=100):
    tom = detectar_tom(pergunta)

    if tom == "humor":
        return responder_humor()
    elif tom == "ironia":
        return responder_com_ira()

    inputs = tokenizer.encode(pergunta, return_tensors="pt")

    # Gerar a resposta com controles ajustados para evitar saídas aleatórias
    outputs = model.generate(
        inputs,
        max_new_tokens=max_new_tokens,  # Limite de tokens para evitar respostas longas
        pad_token_id=tokenizer.eos_token_id,
        repetition_penalty=1.2,  # Penalidade para evitar repetições
        no_repeat_ngram_size=3,  # Impede repetições de n-gramas
        temperature=0.7,  # Ajuste da aleatoriedade
        do_sample=False  # Desabilita o modo de amostragem para respostas mais focadas
    )

    resposta = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove a pergunta da resposta (evita redundância)
    if pergunta in resposta:
        resposta = resposta.split(pergunta, 1)[-1].strip()

    if not resposta or len(resposta.strip()) == 0:
        return "Desculpe, não consegui entender. Pode repetir de outra forma?"

    return resposta
