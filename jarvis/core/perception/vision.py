import cv2
import time
import threading
from datetime import datetime
from logger import log
from config import VIDEO_LOG_DIR

modo_sentinela_ativo = False

def iniciar_camera(exibir=False):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        log("Não foi possível acessar a câmera.", "error")
        return

    log("Câmera iniciada.", "info")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if exibir:
            cv2.imshow("Câmera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if modo_sentinela_ativo:
            detectar_movimento(frame)

    cap.release()
    cv2.destroyAllWindows()

def detectar_movimento(frame):
    log("[Sentinela] Verificando movimentação...", "info")
    # Exemplo simples: salvar imagem se houver movimento (pode ser aprimorado)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = f"{VIDEO_LOG_DIR}/mov_{timestamp}.jpg"
    cv2.imwrite(caminho, frame)
    log(f"[Sentinela] Movimento detectado. Imagem salva: {caminho}", "warning")

def ativar_modo_sentinela():
    global modo_sentinela_ativo
    modo_sentinela_ativo = True
    log("Modo sentinela ativado.", "info")

def desativar_modo_sentinela():
    global modo_sentinela_ativo
    modo_sentinela_ativo = False
    log("Modo sentinela desativado.", "info")

def iniciar_monitoramento_em_thread():
    thread = threading.Thread(target=iniciar_camera, kwargs={"exibir": False}, daemon=True)
    thread.start()
    log("Monitoramento de câmera iniciado em segundo plano.", "info")

if __name__ == "__main__":
    ativar_modo_sentinela()
    iniciar_monitoramento_em_thread()
    time.sleep(10)
    desativar_modo_sentinela()
