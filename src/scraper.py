import logging
import os
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from . import extractor
from . import models
from . import repository

log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)

# Caminho do arquivo de log
log_file = os.path.join(log_dir, "scraper.logs")

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


CASE_NUMBERS = [
    "1075531-81.2021.8.26.0053",
    "0034950-46.2018.8.26.0053",
    "0010364-03.2022.8.26.0344",
    "0032483-55.2022.8.26.0053",
    "0001622-51.2023.8.26.0506",
    "1053943-81.2022.8.26.0053",
    "0423239-43.1999.8.26.0053",
    "1008635-22.2022.8.26.0053"
]

def setup_driver() -> webdriver.Chrome:
    chrome_options = Options()
    # Ativar modo --headless em producao
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=chrome_options)
    

def scrap_case(driver: webdriver.Chrome, case_number: str) -> Dict:
    url = "https://esaj.tjsp.jus.br/cpopg/open.do"
    driver.get(url)

    # Wait for form to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "numeroDigitoAnoUnificado"))
        )
        logger.info("Formulário carregado com sucesso")
    except TimeoutException:
        logger.error("Formulário não carregou a tempo")
        return None

    # Split case number
    numero_digito_ano = case_number[0:15]
    foro_numero = case_number[21:]

    # Fill and submit form
    driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(numero_digito_ano)
    driver.find_element(By.ID, "foroNumeroUnificado").send_keys(foro_numero)
    driver.find_element(By.ID, "botaoConsultarProcessos").click()

    # Check if case page loaded
    try:
        driver.find_element(By.ID, "containerDadosPrincipaisProcesso")
        logger.info(f"Página do processo {case_number} carregada")
    except NoSuchElementException:
        logger.error(f"Processo {case_number} não encontrado ou sem resultados")
        return None

    # Initialize case data
    case_data = extractor.initialize_case_data(case_number)

    # Extract data
    extractor.extract_header_data(driver, case_data)
    extractor.extract_dropdown_data(driver, case_data)
    extractor.extract_parties(driver, case_data)
    extractor.extract_movements(driver, case_data)
    extractor.extract_petitions(driver, case_data)
    extractor.extract_incidents(driver, case_data)

    # Save to database
    case_id = repository.add_or_update_process(case_data)
    if case_id:
        for envolved in case_data["envolved"]:
            repository.add_envolved(case_id, envolved)
        for case_event in case_data["case_events"]:
            repository.add_case_event(case_id, case_event)
        for petition in case_data["petitions"]:
            repository.add_petition(case_id, petition)
        for incident in case_data["incidents"]:
            repository.add_incident(case_id, incident)

    return case_data


if __name__ == "__main__":
    # Cricao do banco de dados
    logger.info("Scrapper logs - Inicializando banco de dados e tabelas...")
    models.create_tables()
    logger.info("Scrapper logs - Banco de dados e tabelas prontos.")
    
    # Instancia do driver 

    driver = setup_driver()

    # Logica principal de scrapping

    for case_number in CASE_NUMBERS:
        data = scrap_case(driver, case_number)

    driver.quit()
