import speech_recognition as sr
import edge_tts
import pygame
import asyncio
import uuid
import os
from logger import log

r = sr.Recognizer()
PASTA_AUDIOS = "audios"

def entrada_usuario():
    log("Aguardando fala ou digite algo. (pressione Enter sem falar para usar texto)", "info")
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            texto = r.recognize_google(audio, language="pt-BR")
            return texto
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            try:
                entrada = input("Texto: ").strip()
                return entrada if entrada else None
            except EOFError:
                return None

async def _falar_async(texto):
    os.makedirs(PASTA_AUDIOS, exist_ok=True)
    nome_arquivo = os.path.join(PASTA_AUDIOS, f"audio_{uuid.uuid4().hex}.mp3")
    communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural")
    await communicate.save(nome_arquivo)

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(nome_arquivo)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.quit()

def falar(texto):
    asyncio.run(_falar_async(texto))
