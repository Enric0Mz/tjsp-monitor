from typing import Dict
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import time

logger = logging.getLogger(__name__)

def initialize_case_data(case_number: str) -> Dict:
    return {
        "number": case_number,
        "name": "",
        "_class": "",
        "judge": "",
        "division": "",
        "foro": "",
        "subject": "",
        "status": "",
        "amount": "",
        "area": "",
        "filling_date": "",
        "control": "",
        "envolved": [],
        "case_events": [],
        "petitions": [],
        "incidents": []
    }

def extract_header_data(driver: WebDriver, case_data: Dict):
    logger.info("Extraindo dados do cabeçalho...")
    try:
        case_data["_class"] = driver.find_element(By.ID, "classeProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do cabeçalho 'classeProcesso' não encontrado")
    try:
        case_data["subject"] = driver.find_element(By.ID, "assuntoProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do cabeçalho 'assuntoProcesso' não encontrado")
    try:
        case_data["foro"] = driver.find_element(By.ID, "foroProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do cabeçalho 'foroProcesso' não encontrado")
    try:
        case_data["division"] = driver.find_element(By.ID, "varaProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do cabeçalho 'varaProcesso' não encontrado")
    try:
        case_data["judge"] = driver.find_element(By.ID, "juizProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do cabeçalho 'juizProcesso' não encontrado")
    try:
        status_elements = driver.find_elements(By.CSS_SELECTOR, "span.unj-tag[style*='margin-left']")
        case_data["status"] = status_elements[0].text.strip() if status_elements else driver.find_element(By.CLASS_NAME, "unj-tag").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do cabeçalho 'status' não encontrado")

def extract_dropdown_data(driver: WebDriver, case_data: Dict):
    logger.info("Expandindo e extraindo dados do dropdown...")
    try:
        see_more_btn = driver.find_element(By.ID, "botaoExpandirDadosSecundarios")
        see_more_btn.click()
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "dataHoraDistribuicaoProcesso"))
        )
        logger.info("Dropdown expandido com sucesso")
    except (NoSuchElementException, TimeoutException):
        logger.error("Falha ao expandir ou encontrar dados secundários")
        return

    try:
        case_data["filling_date"] = driver.find_element(By.ID, "dataHoraDistribuicaoProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do dropdown 'dataHoraDistribuicaoProcesso' não encontrado")
    try:
        case_data["amount"] = driver.find_element(By.ID, "valorAcaoProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do dropdown 'valorAcaoProcesso' não encontrado")
    try:
        case_data["area"] = driver.find_element(By.XPATH, '//*[@id="areaProcesso"]/span').text.strip()
    except NoSuchElementException:
        logger.error("Elemento do dropdown 'areaProcesso' não encontrado")
    try:
        case_data["control"] = driver.find_element(By.ID, "numeroControleProcesso").text.strip()
    except NoSuchElementException:
        logger.error("Elemento do dropdown 'numeroControleProcesso' não encontrado")

def extract_parties(driver: WebDriver, case_data: Dict):
    logger.info("Extraindo partes envolvidas...")
    try:
        link_partes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "linkpartes"))
        )
        link_partes.click()
        parties_table = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "tableTodasPartes"))
        )
        parties = parties_table.find_elements(By.XPATH, ".//tbody/tr")
        logger.info(f"Encontradas {len(parties)} linhas de partes")
        for party in parties:
            cols = party.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                role = cols[0].text.strip().replace(':', '')
                name = ' '.join(cols[1].text.strip().split())
                if name and role:
                    case_data["envolved"].append({"name": name, "role": role})
                else:
                    logger.warning(f"Parte com dados incompletos: Nome='{name}', Papel='{role}'")
        logger.info(f"Adicionadas {len(case_data['envolved'])} partes")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Falha ao extrair partes")

def extract_movements(driver: WebDriver, case_data: Dict):
    logger.info("Extraindo movimentações do processo...")
    try:
        link_movimentacoes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "linkmovimentacoes"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", link_movimentacoes)
        link_movimentacoes.click()
        case_event_table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "tabelaTodasMovimentacoes"))
        )
        case_events = case_event_table.find_elements(By.XPATH, ".//tr[contains(@class, 'containerMovimentacao')]")
        logger.info(f"Encontradas {len(case_events)} linhas de movimentações")
        for case_event in case_events:
            cols = case_event.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 3:
                date = cols[0].text.strip()
                description = cols[2].text.strip()
                if date and description:
                    case_data["case_events"].append({"date": date, "description": description})
                else:
                    logger.warning(f"Movimentação com dados incompletos: Data='{date}', Descrição='{description}'")
        logger.info(f"Adicionadas {len(case_data['case_events'])} movimentações")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Falha ao extrair movimentações")

def extract_petitions(driver: WebDriver, case_data: Dict):
    logger.info("Extraindo petições...")
    try:
        petitions_table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/table[4]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", petitions_table)
        time.sleep(0.5)
        petitions = petitions_table.find_element(By.TAG_NAME, "tbody")
        petition_rows = petitions.find_elements(By.XPATH, "./tr")
        logger.info(f"Encontradas {len(petition_rows)} linhas de petições")
        for petition in petition_rows:
            cols = petition.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                petition_date = cols[0].text.strip()
                petition_type = cols[1].text.strip()
                if petition_date and petition_type:
                    case_data["petitions"].append({"date": petition_date, "type": petition_type})
                else:
                    logger.warning(f"Petição com dados incompletos: Data='{petition_date}', Tipo='{petition_type}'")
        logger.info(f"Adicionadas {len(case_data['petitions'])} petições")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Falha ao extrair petições: {e}")

def extract_incidents(driver: WebDriver, case_data: Dict):
    logger.info("Extraindo incidentes...")
    try:
        incidents_table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/table[5]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", incidents_table)
        incidents = incidents_table.find_element(By.TAG_NAME, "tbody")
        incidents_rows = incidents.find_elements(By.XPATH, "./tr")
        logger.info(f"Encontradas {len(incidents_rows)} linhas de incidentes")
        for incident in incidents_rows:
            cols = incident.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                incident_date = cols[0].text.strip()
                incident_class = cols[1].text.strip()
                if incident_date and incident_class:
                    case_data["incidents"].append({"date": incident_date, "class_description": incident_class})
                else:
                    logger.warning(f"Incidente com dados incompletos: Data='{incident_date}', Classe='{incident_class}'")
        logger.info(f"Adicionadas {len(case_data['incidents'])} incidentes")
    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Falha ao extrair incidentes")