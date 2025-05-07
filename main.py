import time
from typing import Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from src import models
from src import repository



CASE_NUMBERS = [
    "1075531-81.2021.8.26.0053",
    # "0034950-46.2018.8.26.0053",
    # "0010364-03.2022.8.26.0344",
    # "0032483-55.2022.8.26.0053",
    # "0001622-51.2023.8.26.0506",
    # "1053943-81.2022.8.26.0053",
    # "0423239-43.1999.8.26.0053",
    # "1008635-22.2022.8.26.0053"
]

def setup_driver() -> webdriver.Chrome:
    chrome_options = Options()
    # Ativar modo --headless em producao
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=chrome_options)
    

def scrap_case(driver: webdriver.Chrome, case_number: str) -> Dict[str, Any]:
    url = "https://esaj.tjsp.jus.br/cpopg/open.do"
    driver.get(url)

    #Aguada a pagina carregar ate encontrar form
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "numeroDigitoAnoUnificado"))
        )
        print("Formulário de busca carregado.")
    except TimeoutException:
        print("Erro: Formulário de busca não carregou a tempo.")
        return None

    #Usa list slicing para separar numero e foro
    numero_digito_ano = case_number[0:15]
    foro_numero = case_number[21:]
    
    #Preenche o form e confirma
    driver.find_element(By.ID, "numeroDigitoAnoUnificado").send_keys(numero_digito_ano)
    driver.find_element(By.ID, "foroNumeroUnificado").send_keys(foro_numero)
    driver.find_element(By.ID, "botaoConsultarProcessos").click()
    try:
        driver.find_element(By.ID, "containerDadosPrincipaisProcesso")
        print(f"Página do processo {case_number} carregada.")
    except NoSuchElementException:
        print(f"Processo {case_number} não encontrado ou não retornou resultados.")
        return None

    # Definicao de um processo
    case_data = {
        "number": case_number,
        "name": "",
        "_class": "",
        "judge": "",
        "division": "",
        "court": "",
        "subject": "",
        "status": "",
        "amount": "",
        "area": "",
        "filling_date": "",
        "control": "",
        "complementary": False,
        "complementary_ids": "",
        "envolved": [],
        "case_events": [],
        "petitions": []
    }


    # Items do processo
    # Abrindo dropdown
    try:
        print("Tentando expandir dados secundários...")
        see_more_btn1 = driver.find_element(By.ID, "botaoExpandirDadosSecundarios")
        see_more_btn1.click()
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "dataHoraDistribuicaoProcesso"))
        )
        print("Dropdown de dados secundários expandido.")
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Aviso: Não foi possível expandir/encontrar dados secundários: {e}")
        pass

    # Extracao de dados - cabecalho
    print("Extraindo dados do cabeçalho...")
    try:
        case_data["_class"] = driver.find_element(By.ID, "classeProcesso").text.strip()
        case_data["subject"] = driver.find_element(By.ID, "assuntoProcesso").text.strip()
        case_data["court"] = driver.find_element(By.ID, "foroProcesso").text.strip()
        case_data["division"] = driver.find_element(By.ID, "varaProcesso").text.strip()
        case_data["judge"] = driver.find_element(By.ID, "juizProcesso").text.strip()
        status_elements = driver.find_elements(By.CSS_SELECTOR, "span.unj-tag[style*='margin-left']")
        if status_elements:
            case_data["status"] = status_elements[0].text.strip()
        else:
            case_data["status"] = driver.find_element(By.CLASS_NAME, "unj-tag").text.strip()

    except NoSuchElementException as e:
        print(f"Aviso: Elemento do cabeçalho não encontrado: {e}")

    # Extracao de dados - dropdown do cabecalho
    print("Extraindo dados do dropdown do cabeçalho...")
    try:
        case_data["filling_date"] = driver.find_element(By.ID, "dataHoraDistribuicaoProcesso").text.strip()
        case_data["amount"] = driver.find_element(By.ID, "valorAcaoProcesso").text.strip()
        case_data["area"] = driver.find_element(By.XPATH, '//*[@id="areaProcesso"]/span').text.strip()
        case_data["control"] = driver.find_element(By.ID, "numeroControleProcesso").text.strip()
    except NoSuchElementException as e:
        print(f"Aviso: Elemento do dropdown do cabeçalho não encontrado: {e}")

    # Partes envolvidas
    print("Extraindo partes envolvidas...")
    try:
        link_partes = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "linkpartes"))
        )
        link_partes.click()
        print("Link 'Partes do Processo' clicado.")

        parties_table = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "tableTodasPartes"))
        )
        print("Tabela de partes visível.")

        # Extrai os dados
        parties = parties_table.find_elements(By.XPATH, ".//tbody/tr")
        print(f"Encontradas {len(parties)} linhas na tabela de partes.")
        for party in parties:
            cols = party.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                role = cols[0].text.strip().replace(':', '')
                name_raw = cols[1].text.strip()
                name = ' '.join(name_raw.split())

                if name and role:
                    case_data["envolved"].append({
                        "name": name,
                        "role": role
                    })
        print(f"{len(case_data['envolved'])} partes adicionadas.")

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Aviso: Não foi possível extrair as partes envolvidas: {e}")

    # Movimentacoes
    print("Extraindo movimentacoes...")
    try:
        # Encontra o botao e clica
        link_movimentacoes = driver.find_element(By.ID, "linkmovimentacoes")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", link_movimentacoes)
        see_more_btn3 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "linkmovimentacoes"))
            )
        see_more_btn3.click()

        #Extrair dados de movimentacoes
        case_event_table = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "tabelaTodasMovimentacoes"))
        )
        case_events = case_event_table.find_elements(By.XPATH, ".//tr[contains(@class, 'containerMovimentacao')]")
        print(f"Encontradas {len(case_events)} linhas de movimentação na tabela.")
        if not case_events:
            print("Nenhuma movimentacao encontrada")

        for case_event in case_events:
            cols = case_event.find_elements(By.TAG_NAME, "td")
            
            if len(cols) >= 3:
                date = cols[0].text.strip()
                description = cols[2].text.strip()

                if date and description:
                    case_data["case_events"].append({
                        "date": date,
                        "description": description
                    })
        print(f"{len(case_data['case_events'])} partes adicionadas.")

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Aviso: Não foi possível extrair as movimentacoes: {e}")

    # Peticoes diversas
    print("Iniciando extração de Petições...")

    try:
        # Encontra peticoes diversas na pagina
        petitions_table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/table[4]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", petitions_table)
        time.sleep(0.5)

        petitions = petitions_table.find_element(By.TAG_NAME, "tbody")
        petition_rows = petitions.find_elements(By.XPATH, "./tr")
        print(f"Encontradas {len(petition_rows)} linhas na tabela de peticoes.")

        for petition in petition_rows:
            cols = petition.find_elements(By.TAG_NAME, "td")
            
            if len(cols) >= 2:
                petition_date = cols[0].text.strip()
                petition_type = cols[1].text.strip()

                if petition_date and petition_type:
                    case_data["petitions"].append({
                        "date": petition_date,
                        "type": petition_type
                    })
        print(f"{len(case_data['petitions'])} petições adicionadas.")

    except (NoSuchElementException, TimeoutException) as e:
        print(f"Aviso: Não foi possível extrair as peticoes diversas: {e}")

    case_id = repository.add_or_update_process(case_data)
    if case_id:
        for envolved in case_data["envolved"]:
            repository.add_envolved(case_id, envolved)


if __name__ == "__main__":
    # Cricao do banco de dados
    print("Inicializando banco de dados e tabelas...")
    models.create_tables()
    print("Banco de dados e tabelas prontos.")
    
    # Instancia do driver 

    driver = setup_driver()

    # Logica principal de scrapping

    all_cases = []
    for case_number in CASE_NUMBERS:
        data = scrap_case(driver, case_number)
        if data:
            all_cases.append(data)
    print(all_cases)

    driver.quit()