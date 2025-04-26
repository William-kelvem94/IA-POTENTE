import threading
import time
import schedule
from agent import rodar_agente
from rotinas import configurar_rotinas
from logger import log

# Flag de controle manual do agendador
usar_agendador = False  # ✅ Mude para True se quiser ativar o agendador

def loop_agendador():
    log("Loop de rotinas iniciado.", "info")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            log(f"Erro no loop do agendador: {e}", "error")

def iniciar_sistema():
    log("Sistema Jarvis iniciando...", "info")

    if usar_agendador:
        try:
            threading.Thread(target=loop_agendador, daemon=True).start()
            configurar_rotinas()
            log("Agendador de rotinas ativado.", "success")
        except Exception as e:
            log(f"Falha ao iniciar agendador: {e}", "error")
    else:
        log("Agendador de rotinas está desativado (padrão).", "warn")

    try:
        rodar_agente()
    except KeyboardInterrupt:
        log("Execução interrompida manualmente.", "warn")
    except Exception as e:
        log(f"Erro fatal durante execução principal: {e}", "error")

if __name__ == "__main__":
    iniciar_sistema()
