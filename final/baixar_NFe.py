import pyautogui
import winsound
import ast
import shutil
import os
from sys import exit
from time import sleep

pyautogui.PAUSE = 1.5

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
    with open("localizador.txt", 'r') as arquivo:
        for linha in arquivo:
            if '=' in linha:
                chave, valor = linha.strip().split('=', 1)
                if valor.startswith('(') and valor.endswith(')'):
                # Converte strings que parecem tuplas
                    config[chave] = ast.literal_eval(valor)
                else:
                    config[chave] = valor
except FileNotFoundError:
    pass  # Arquivo não existe ainda, usaremos o padrão

chaves = []
with open("chaves.txt", 'r') as arquivo_chaves:
    for chave in arquivo_chaves:
        chaves.append(chave.replace('\n', '')) 

# Se status do localizador for 0, o programa executa todas as ações abixo para obter as posições dos campos de preencimento
# e dos botões que devem ser clicados.
if config['status'] == '0':
    pyautogui.press("win")
    pyautogui.write("chrome")
    pyautogui.press("enter")
    winsound.Beep(1500, 200) # beep de alerta dos 2 segundos 
    sleep(2)  # Espera o Chrome abrir

    config['digitar_url'] = tuple(pyautogui.position()) ; double_beep() # beep de confirmação
    pyautogui.click(config['digitar_url'])
    pyautogui.write(url)
    pyautogui.press("enter")
    winsound.Beep(1500, 200) # beep de alerta dos 2 segundos 
    sleep(5)

    config['chave_acesso'] = tuple(pyautogui.position()) ; double_beep()
    pyautogui.click(config['chave_acesso'])
    pyautogui.write(chaves[0])
    winsound.Beep(1500, 200)
    sleep(5)

    config['botao_buscar'] = tuple(pyautogui.position()) ; double_beep()
    pyautogui.click(config['botao_buscar'])
    winsound.Beep(1500, 200)
    sleep(10)

    config['baixar_xml'] = tuple(pyautogui.position()) ; double_beep()
    pyautogui.click(config['baixar_xml'])
    sleep(10)

    pyautogui.click(config['botao_buscar'])
    winsound.Beep(1500, 200)
    sleep(10)
    
    config['baixar_danfe'] = tuple(pyautogui.position()) ; double_beep()
    pyautogui.click(config['baixar_danfe'])

    # Atualiza o status para 1 no dicionário
    config['status'] = '1'
    
    # Salva TODOS os valores no arquivo (incluindo o novo status)
    with open("localizador.txt", 'w') as arquivo:
        for chave, valor in config.items():
            arquivo.write(f"{chave}={valor}\n")

    pyautogui.hotkey('alt', 'f4')
    print("Posições obtidas! Programa finalizado.")
    sleep(5)
    exit()

pyautogui.press("win")
pyautogui.write("chrome")
pyautogui.press("enter")
sleep(5)  # Espera o Chrome abrir

pyautogui.click(config['digitar_url'])
pyautogui.write(url)
pyautogui.press("enter")
sleep(5) # Espera a página carregar

for chave in chaves:
    pyautogui.click(config['chave_acesso'])
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('del')
    pyautogui.click(config['chave_acesso'])
    pyautogui.write(chave)

    pyautogui.click(config['botao_buscar'])
    sleep(10) # Espera carregar a página para baixar XML

    pyautogui.click(config['baixar_xml'])
    sleep(10) # Espera carregar o retorno para a página de busca

    pyautogui.click(config['botao_buscar'])
    sleep(10) # Espera carregar a página para baixar DANFE

    pyautogui.click(config['baixar_danfe'])

    if chave == chaves[len(chaves)-1]:
        pyautogui.hotkey("alt", "f4")

downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
destino = os.path.join(downloads, 'NFs_Renomeadas')
os.makedirs(destino, exist_ok=True)

with open("chaves.txt", 'r') as arquivo_chaves:
    for linha in arquivo_chaves:
        pdf_file = f"NFE-{linha.replace('\n', '')}.pdf"
        xml_file = f"NFE-{linha.replace('\n', '')}.xml"
        caminho_pdf = os.path.join(downloads, pdf_file)
        caminho_xml = os.path.join(downloads, xml_file)
        shutil.move(caminho_pdf, destino)
        shutil.move(caminho_xml, destino)

double_beep()
print("NFs baixadas e movidas. Programa finalizado!")
sleep(5)
