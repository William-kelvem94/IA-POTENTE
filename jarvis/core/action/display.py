import pygetwindow as gw
import pyautogui
import pytesseract
import os
from datetime import datetime
from logger import log
from config import SCREENSHOT_DIR

# Configura o caminho do Tesseract se necessário
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def listar_janelas_abertas():
    try:
        janelas = gw.getAllTitles()
        janelas = [j for j in janelas if j.strip() != '']
        log(f"Janelas abertas detectadas: {janelas}", "info")
        return janelas
    except Exception as e:
        log(f"Erro ao listar janelas: {e}", "error")
        return []

def buscar_janela_por_nome(nome):
    janelas = listar_janelas_abertas()
    for janela in janelas:
        if nome.lower() in janela.lower():
            log(f"Janela encontrada: {janela}", "info")
            return janela
    log(f"Janela com nome '{nome}' não encontrada.", "warning")
    return None

def tirar_screenshot():
    try:
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR)

        nome_arquivo = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        caminho_completo = os.path.join(SCREENSHOT_DIR, nome_arquivo)

        screenshot = pyautogui.screenshot()
        screenshot.save(caminho_completo)
        log(f"Screenshot salva em: {caminho_completo}", "info")
        return caminho_completo
    except Exception as e:
        log(f"Erro ao tirar screenshot: {e}", "error")
        return None

def ler_texto_da_tela():
    try:
        caminho_imagem = tirar_screenshot()
        if caminho_imagem:
            texto = pytesseract.image_to_string(caminho_imagem, lang='por')
            log(f"Texto detectado na tela: {texto.strip()[:100]}...", "info")
            return texto.strip()
        else:
            return ""
    except Exception as e:
        log(f"Erro ao ler texto da tela: {e}", "error")
        return ""

if __name__ == "__main__":
    print(listar_janelas_abertas())
    print(buscar_janela_por_nome("chrome"))
    print(tirar_screenshot())
    print(ler_texto_da_tela())
