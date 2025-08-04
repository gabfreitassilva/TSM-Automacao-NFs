import pyautogui
from time import sleep

pyautogui.PAUSE = 1 # tempo de processamento entre cada comando

# 1 - abrir o navegador
pyautogui.press("win")
pyautogui.write("chrome")
pyautogui.press("enter")

# 2 - abrir o site https://www.meudanfe.com.br/
pyautogui.click(x=315, y=55) # campo de pesquisa do navegador
pyautogui.write("https://www.meudanfe.com.br/")
pyautogui.press("enter")

# 3 - digitar a chave de acesso
pyautogui.click(x=353, y=403) # campo da chave de acesso
pyautogui.write(chave) # chave da NFe
pyautogui.click(x=590, y=396) # botão de buscar
sleep(10)
pyautogui.click(x=368, y=370) # botão para abixar xml
pyautogui.click(x=590, y=396) # botão de buscar
sleep(10)
pyautogui.click(x=513, y=318) # botão de danfe
sleep(2)
pyautogui.hotkey("alt", "f4") # fecha o navegador
