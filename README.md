# Scraper de Dados Processuais TJSP (ESAJ)

## Visão Geral

Este projeto consiste em um web scraper desenvolvido em Python, projetado para extrair automaticamente dados públicos de processos do portal ESAJ CPOPG (Consulta de Processos do 1º Grau) do Tribunal de Justiça de São Paulo (TJSP). Ele busca detalhes para uma lista de números de processos especificada e armazena as informações em um banco de dados SQLite local.

O objetivo principal é automatizar o processo de coleta de dados para análise jurídica ou manutenção de registros. Este projeto foi desenvolvido como um exercício prático de web scraping (utilizando Selenium), gerenciamento de banco de dados (SQLite) e estruturação de aplicações Python.

## Funcionalidades

- Realiza scraping de dados processuais com base em uma lista pré-definida de números de processos.
- Extrai informações chave, incluindo:
  - Dados do cabeçalho (Classe, Assunto, Juiz, Vara, Foro, Status, etc.)
  - Dados secundários (Data da Distribuição, Valor da Ação, Área, Número de Controle)
  - Partes Envolvidas (Nomes e Papéis)
  - Movimentações do Processo (Datas e Descrições)
  - Petições (Datas e Tipos)
  - Incidentes (Datas e Classes/Descrições)
- Armazena os dados coletados de forma persistente em um banco de dados SQLite local (`data/stored_data.db`).
- Implementa lógica "UPSERT" para os dados principais do processo: insere novos processos ou atualiza existentes com base no `numero_processo` único.
- Implementa lógica "adicionar se não existir" para dados relacionados (envolvidos, movimentações, petições, incidentes) para evitar duplicatas com base em critérios específicos.
- Utiliza Selenium com `webdriver-manager` para gerenciar automaticamente o ChromeDriver.
- Inclui logging detalhado para o console (nível INFO e acima) e para arquivos separados (`logs/scraper.log`).
- Possui tratamento de erros para lidar com situações onde elementos específicos ou seções de dados podem estar ausentes na página.
- **Inclui um script de visualização (`src/view_data.py`) com opções de linha de comando para:**
  - Listar todos os números de processos armazenados (`--processos`).
  - Exibir detalhes completos de um processo específico (`--details NUMERO_PROCESSO`).
  - Mostrar as últimas 50 movimentações adicionadas ao banco (`--recent-events`).
  - Exibir um resumo com a contagem de registros por tabela (`--summary`).

## Tecnologias e Requisitos

- **Linguagem:** Python 3.10
- **Gerenciador de Pacotes:** Poetry
- **Bibliotecas Principais:**
  - `selenium` (`^4.32.0`) - Para automação do navegador e web scraping.
  - `webdriver-manager` (`^4.0.2`) - Para gerenciar automaticamente o ChromeDriver.
  - `sqlite3` (embutido no Python) - Para interação com o banco de dados.
- **Navegador:** Google Chrome (precisa estar instalado)
- **Banco de Dados:** SQLite
