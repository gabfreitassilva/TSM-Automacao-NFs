# import pyautogui
# import ast
# from sys import exit
# import os
# import shutil
# import keyboard
# from time import sleep

# # chave = []


# # with open("chaves.txt", 'r') as arquivo_chaves:
# #     for linha in arquivo_chaves:
# #         chave.append(linha.replace('\n', ''))

# # print(len(chave))

# # config = {
# #     'status':       '0',
# #     'digitar_url':  '0',
# #     'chave_acesso': '0',
# #     'botao_buscar': '0',
# #     'baixar_xml':   '0',
# #     'baixar_danfe': '0'
# # }

# # try:
# #     with open("final/localizador.txt", 'r') as arquivo:
# #         for linha in arquivo:
# #             if '=' in linha:
# #                 chave, valor = linha.strip().split('=', 1)
# #                 if valor.startswith('(') and valor.endswith(')'):
# #                 # Converte strings que parecem tuplas
# #                  config[chave] = ast.literal_eval(valor)
# #                 else:
# #                     config[chave] = valor
# # except FileNotFoundError:
# #     pass  # Arquivo não existe ainda, usaremos o padrão



# # exit("Programa finalizado!")


# # print(config['digitar_url'])

# # config['digitar_url'] = tuple(pyautogui.position())

# # print(config['digitar_url'])

# # pyautogui.click(config['digitar_url'].strip('()\n').split(','))
# # pyautogui.click(config['digitar_url'])




# # downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
# # destino = os.path.join(downloads, 'NFs_Renomeadas')

# # os.makedirs(destino, exist_ok=True)

# # with open("chaves.txt", 'r') as arquivo_chaves:
# #     for linha in arquivo_chaves:
# #         chave.append(linha.replace('\n', ''))
# #         pdf_file = f"NFE-{str(chave)}.pdf"
# #         caminho_pdf = os.path.join(downloads, pdf_file)

# #         # novo_caminho = os.path.join(destino)
# #         shutil.move(caminho_pdf, destino)


# # with open("chaves.txt", 'r') as arquivo_chaves:
# #     for linha in arquivo_chaves:
# #         pdf_file = f"NFE-{linha.replace('\n', '')}.pdf"
# #         caminho_pdf = os.path.join(downloads, pdf_file)
# #         shutil.move(caminho_pdf, destino)

# print("A qualquer momento durante a execução do programa:")
# print("Pressione [ P ] para pausar o programa.")
# print("Pressione [ R ] para retomar o programa.")
# print("Pressione [ Q ] para finalizar o programa.")

# while True:
#     if keyboard.is_pressed('p'):
#         print("\nPAUSADO! Pressione [R] para continuar")
#         while not keyboard.is_pressed('r'):
#             sleep(0.1)
#         print("Retomando execução...")
    
#     if keyboard.is_pressed('q'):
#         print("\nFinalizado pelo usuário")
#         exit()

import pyautogui
import keyboard
import threading

# Controle global
interromper = False

def monitorar_tecla():
    global interromper
    keyboard.wait('p')  # Bloqueia até pressionar P
    interromper = True

# Inicia monitoramento
threading.Thread(target=monitorar_tecla, daemon=True).start()

# -------------------------------------------
# SEU SCRIPT PRINCIPAL COMEÇA AQUI
# -------------------------------------------
pyautogui.alert("Iniciando automação...")

# Etapa 1
pyautogui.moveTo(100, 100)
if interromper: exit()

while True:
    print("OK.\n")
    if interromper: exit()


# Etapa 2p
pyautogui.click(clicks=2)
if interromper: exit()

# ... resto do seu fluxo ...pp