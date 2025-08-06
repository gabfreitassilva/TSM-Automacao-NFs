import pyautogui
import keyboard
import threading
import sys
import time
import os

# =====================================================
# MECANISMO DE INTERRUPÇÃO (Não precisa modificar)
# =====================================================
class AutomationController:
    def __init__(self):
        self.should_pause = False
        self.should_stop = False
        self.listener_thread = threading.Thread(target=self._keyboard_listener, daemon=True)
        self.listener_thread.start()
        print("Controle ativado. Pressione:")
        print("  [P] Pausar/Continuar")
        print("  [Q] Sair imediatamente")
        print("  [ESC] Sair com confirmação")

    def _keyboard_listener(self):
        while True:
            # Verifica pausa/continuação
            if keyboard.is_pressed('p'):
                self.should_pause = not self.should_pause
                status = "PAUSADO" if self.should_pause else "CONTINUANDO"
                print(f"\n*** {status} ***")
                time.sleep(0.5)  # Debounce
                
            # Verifica saída imediata
            if keyboard.is_pressed('q'):
                print("\n*** SAÍDA DE EMERGÊNCIA ***")
                os._exit(1)
                
            # Verifica saída com confirmação
            if keyboard.is_pressed('esc'):
                if pyautogui.confirm("Deseja realmente sair?", buttons=['Sim', 'Não']) == 'Sim':
                    print("\n*** FINALIZADO PELO USUÁRIO ***")
                    self.should_stop = True
                    break
            
            time.sleep(0.01)  # Reduz consumo de CPU

    def wait_if_paused(self):
        while self.should_pause:
            time.sleep(0.1)

    def should_exit(self):
        return self.should_stop

# =====================================================
# SEU CÓDIGO PRINCIPAL COMEÇA AQUI
# =====================================================
if __name__ == "__main__":
    # Inicializa o controlador
    controller = AutomationController()
    
    try:
        # Exemplo de automação 1
        pyautogui.alert("Iniciando automação...")
        
        # Exemplo de automação 2
        for i in range(10):
            if controller.should_exit():
                break
                
            controller.wait_if_paused()
            
            pyautogui.click(100, 100)
            pyautogui.write(f"Texto {i}")
            pyautogui.press('enter')
            
            # Não precisa verificar teclas aqui!
            time.sleep(1)
        
        # Exemplo de automação 3 (longa)
        controller.wait_if_paused()
        pyautogui.moveTo(500, 500, duration=5)  # Movimento longo
        
        # Mais ações...
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print("Execução concluída")