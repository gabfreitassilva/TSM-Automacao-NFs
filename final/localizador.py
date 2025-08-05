import pyautogui
import winsound
from time import sleep

pyautogui.PAUSE = 1

# Dicionário padrão de valores
config = {
    'status':       '0',
    'digitar_url':  '0',
    'chave_acesso': '0',
    'botao_buscar': '0',
    'baixar_xml':   '0',
    'baixar_danfe': '0'
}

url = "https://www.meudanfe.com.br/"

def double_beep():
    # Primeiro beep (frequência 1000Hz, duração 200ms)
    winsound.Beep(1000, 200)
    # Pequena pausa entre os beeps (100ms)
    sleep(0.1)
    # Segundo beep (frequência 1000Hz, duração 200ms)
    winsound.Beep(1000, 200)

# Tenta carregar o arquivo existente
try:
    with open("final/localizador.txt", 'r') as arquivo:
        for linha in arquivo:
            if '=' in linha:
                chave, valor = linha.strip().split('=', 1)
                if chave in config:
                    config[chave] = valor
except FileNotFoundError:
    pass  # Arquivo não existe ainda, usaremos o padrão

# Se status for '0', executa as ações
if config['status'] == '0':
    pyautogui.press("win")
    pyautogui.write("chrome")
    pyautogui.press("enter")
    winsound.Beep(1500, 200) # beep de alerta dos 2 segundos 
    sleep(2)  # Espera o Chrome abrir

    config['digitar_url'] = pyautogui.position()
    double_beep() # beep de confirmação
    pyautogui.click(config['digitar_url'])
    pyautogui.write(url)
    pyautogui.press("enter")
    winsound.Beep(1500, 200) # beep de alerta dos 2 segundos 
    sleep(5)

    config['chave_acesso'] = pyautogui.position()
    double_beep()
    pyautogui.click(config['chave_acesso'])
    pyautogui.write()
    

    # Atualiza o status para 1 no dicionário
    config['status'] = '1'
    
    # Salva TODOS os valores no arquivo (incluindo o novo status)
    with open("final/localizador.txt", 'w') as arquivo:
        for chave, valor in config.items():
            arquivo.write(f"{chave}={valor}\n")
