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
  - Exibir detalhes completos de um processo específico (`--detalhes NUMERO_PROCESSO`).
  - Mostrar as últimas 50 movimentações adicionadas ao banco (`--movimentacoes_recentes`).
  - Exibir um resumo com a contagem de registros por tabela (`--contagem-dados`).

## Tecnologias e Requisitos

- **Linguagem:** Python 3.10
- **Gerenciador de Pacotes:** Poetry
- **Bibliotecas Principais:**
  - `selenium` (`^4.32.0`) - Para automação do navegador e web scraping.
  - `webdriver-manager` (`^4.0.2`) - Para gerenciar automaticamente o ChromeDriver.
  - `sqlite3` (embutido no Python) - Para interação com o banco de dados.
- **Navegador:** Google Chrome (precisa estar instalado)
- **Banco de Dados:** SQLite

## Configuração e Instalação

1.  **Clone o Repositório:**

    git clone [https://github.com/Enric0Mz/tjsp-monitor.git](https://github.com/Enric0Mz/tjsp-monitor.git)

    cd [tjsp-monitor]

2.  **Instale o Poetry (se ainda não tiver):**
    Siga as instruções oficiais em [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).

3.  **Instale as Dependências do Projeto:**
    Navegue até o diretório raiz do projeto e execute:

    ```bash
    poetry install
    ```

    O Poetry criará um ambiente virtual automaticamente (ou usará um existente) e instalará as dependências do `pyproject.toml`.

4.  **Instale o Google Chrome:**
    Certifique-se de que você tem o Google Chrome instalado. O `webdriver-manager` cuidará do download do ChromeDriver.

## Como Executar

Execute os comandos a partir do **diretório raiz** do projeto.

1.  **Executar o Scraper:**

    ```bash
    # Usando poetry run:
    poetry run python -m src.scraper
    # Ou ative o ambiente antes (poetry shell) e depois execute:
    python -m src.scraper
    ```

    - Isso iniciará o processo de scraping para os números definidos em `CASE_NUMBERS`.
    - Logs serão exibidos no console e salvos em `logs/scraper.log`.
    - Os dados serão salvos/atualizados em `data/stored_data.db`.

2.  **Visualizar os Dados:**
    Use o script `view_data.py` com as seguintes opções:
    - **Listar Números de Processos (Ação Padrão):**
      ```bash
      poetry run python -m src.view_data
      # OU
      python -m src.view_data
      ```
    - **Mostrar Detalhes de um Processo:**
      ```bash
      poetry run python -m src.view_data --detalhes "NUMERO_COMPLETO_DO_PROCESSO"
      # Exemplo: poetry run python -m src.view_data --detalhes "1075531-81.2021.8.26.0053"
      ```
    - **Mostrar Últimas 50 Movimentações:**
      ```bash
      poetry run python -m src.view_data --movimentacoes-recentes
      ```
    - **Mostrar Resumo/Contagens (se implementado no repositório):**
      ```bash
      poetry run python -m src.view_data --contagem-dados
      ```
    - **Obter Ajuda:**
      ```bash
      poetry run python -m src.view_data --help
      ```

## Dívidas técnicas / Limitações

- **Dependência do Site:** Mudanças no site TJSP ESAJ podem quebrar o scraper.
- **Fragilidade dos Seletores:** Alguns seletores podem precisar de ajustes futuros.
- **Rate Limiting/Bloqueio:** Não implementado tratamento para bloqueios por excesso de requisições.
- **Modo Headless** O modo --headless, usado para extrair dados sem abertura do navegador, não funciona como esperado

## Melhorias Futuras

- Seletores mais robustos.
- Implementação de API para visualização de dados robusta e integrações com outros sistemas
- Scrapping de documentos relacionados, como precatórios e incidentes do processo
- Containerização da aplicação com Docker

## Autor

- **Enrico Marquez**
- **enricovmarquezz@gmail.com**

## Licença

Este projeto é licenciado sob os termos da Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
