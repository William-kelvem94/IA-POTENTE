import schedule
import time
import threading
import webbrowser
import subprocess
from datetime import datetime
from voice import falar
from logger import log
from memoria import Memoria

memoria = Memoria()
rotinas_configuradas = []

def abrir_programa(caminho):
    try:
        subprocess.Popen(caminho, shell=True)
        log(f"Programa '{caminho}' aberto com sucesso.", "info")
    except Exception as e:
        log(f"Erro ao abrir programa: {e}", "error")

def abrir_link(url):
    try:
        webbrowser.open(url)
        log(f"Link '{url}' aberto com sucesso.", "info")
    except Exception as e:
        log(f"Erro ao abrir link: {e}", "error")

def executar_rotina(nome, acao):
    log(f"Executando rotina: {nome}", "info")
    falar(f"Executando rotina {nome}")
    acao()

def configurar_rotinas():
    log("Agendador de rotinas iniciado.", "info")
    schedule.every().day.at("08:00").do(executar_rotina, "Abrir Chrome", lambda: abrir_programa("C:/Program Files/Google/Chrome/Application/chrome.exe"))
    schedule.every().day.at("22:00").do(executar_rotina, "Fogueira no YouTube", lambda: abrir_link("https://www.youtube.com/watch?v=eyU3bRy2x44"))

    while True:
        schedule.run_pending()
        time.sleep(1)

def interpretar_rotina_personalizada(comando):
    if "abrir" in comando and "às" in comando:
        try:
            partes = comando.split("às")
            acao = partes[0].strip()
            horario = partes[1].strip()
            nome_rotina = acao

            if "chrome" in acao.lower():
                acao_exec = lambda: abrir_programa("C:/Program Files/Google/Chrome/Application/chrome.exe")
            elif "fogueira" in acao.lower():
                acao_exec = lambda: abrir_link("https://www.youtube.com/watch?v=eyU3bRy2x44")
            else:
                falar("Ainda não sei como realizar essa ação. Me ensine ou reformule.")
                return

            schedule.every().day.at(horario).do(executar_rotina, nome_rotina, acao_exec)
            falar(f"Rotina '{nome_rotina}' agendada para às {horario}.")
            log(f"Rotina personalizada criada: {nome_rotina} às {horario}", "info")

            memoria.adicionar_ao_historico(comando, f"Rotina criada: {nome_rotina} às {horario}", tipo="rotina")
        except Exception as e:
            log(f"Erro ao interpretar rotina personalizada: {e}", "error")
            falar("Houve um erro ao configurar a rotina. Pode repetir de outra forma?")
