from selenium import webdriver
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def logar_unilu():
    cpf = '13237223948'

    driver = webdriver.Chrome()
    driver.get('https://portal.unifil.br/')
    driver.maximize_window()

    input_cpf = WebDriverWait(driver,5).until(
        EC.element_to_be_clickable((By.XPATH,"//input[@id='IDLoginL']"))
    )
    input_cpf.click()
    input_cpf.send_keys(cpf)

    button_acess = WebDriverWait(driver,5).until(
        EC.element_to_be_clickable((By.XPATH,"//button[@class='btn btn-dark btn-block pull-left waves-effect waves-light']"))
    )
    button_acess.click()


    sleep(10)
    driver.quit()

logar_unilu()

    