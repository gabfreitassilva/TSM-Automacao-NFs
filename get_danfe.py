from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from time import sleep

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

link = "https://consultadanfe.com"

with open("bloco de notas.txt", "r") as file:
    nf1 = file.readline().strip()
    nf2 = file.readline().strip()

driver.get(link)

input_element = driver.find_element(By.ID, "chave")
input_element.send_keys(nf1)

sleep(5)

driver.find_element(By.CLASS_NAME, "g-recaptcha").click()
sleep(5)

driver.find_element(By.CLASS_NAME, "btn btn-primary")
sleep(2)

driver.find_element(By.ID, "downloadButton")