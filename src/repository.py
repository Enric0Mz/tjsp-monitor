import sqlite3
from . models import get_db_connection


def add_or_update_process(case_data):
    # Cria um novo processo

    sql = """
        INSERT INTO Processos (
            numero_processo, nome_caso, classe_processo, juiz, vara,
            assunto, status, foro, valor_causa, area,
            data_distribuicao, controle, data_extracao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(numero_processo) DO UPDATE SET
            nome_caso=excluded.nome_caso,
            classe_processo=excluded.classe_processo,
            juiz=excluded.juiz,
            vara=excluded.vara,
            assunto=excluded.assunto,
            status=excluded.status,
            foro=excluded.foro,
            valor_causa=excluded.valor_causa,
            area=excluded.area,
            data_distribuicao=excluded.data_distribuicao,
            controle=excluded.controle,
            data_extracao=CURRENT_TIMESTAMP
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            case_data.get('number'), case_data.get('name'), case_data.get('_class'),
            case_data.get('judge'), case_data.get('division'),
            case_data.get('subject'), case_data.get('status'), case_data.get('foro'),
            case_data.get('amount'), case_data.get('area'),
            case_data.get('filling_date'),
            case_data.get('control')
        ))
        conn.commit()
        if cursor.rowcount >= 0:
            case_id = case_data.get('number')
            print(f"Processo de numero {case_id} ADICIONADO ao banco de dados")
            return case_id
        else:
            raise sqlite3.Error(f"Operação teve um erro inesperado para o processo {case_id}")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar processo: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_envolved(case_id: str, envolved_data: dict):
    # Cria um novo processo

    name = envolved_data.get('name')
    role = envolved_data.get('role')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se envolvido ja esta na tabela
        sql_check = """
            SELECT 1 from Envolvidos
            WHERE id_processo = ? AND nome_envolvido = ? AND papel_envolvido = ?
            LIMIT 1
        """
        cursor.execute(sql_check, (case_id, name, role))

        if cursor.fetchone():
            return None
        
        sql_insert = """
            INSERT INTO Envolvidos (
                id_processo, nome_envolvido, papel_envolvido
            ) VALUES (?, ?, ?)
        """
        cursor.execute(sql_insert, (
            case_id, name, role,
        ))
        conn.commit()
        result = cursor.lastrowid 
        print(f"Envolvido de nome '{name}' ADICIONADO ao processo {case_id}. ID da Movimentação: {result}")
        return result

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar processo: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_case_event(case_id: str, case_event_data: dict):
    # Adiciona movimentacao
    
    date = case_event_data.get('date')
    description = case_event_data.get('description')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se movimentacao ja esta na tabela
        sql_check = """
            SELECT 1 FROM Movimentacoes
            WHERE id_processo = ? AND data_evento = ? AND descricao_evento = ?
            LIMIT 1
        """
        cursor.execute(sql_check, (case_id, date, description))
        
        if cursor.fetchone():
            return None

        sql_insert = """
            INSERT INTO Movimentacoes (id_processo, data_evento, descricao_evento)
            VALUES (?, ?, ?)
        """
        cursor.execute(sql_insert, (case_id, date, description))
        conn.commit()
        result = cursor.lastrowid
        print(f"Movimentação de '{date}' ADICIONADA ao processo {case_id}. ID da Movimentação: {result}")
        return result

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao processar movimentação de '{date}' para o processo ID {case_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_petition(case_id: str, petition_data: dict):
    #Adiciona peticao
    date = petition_data.get('date') 
    type = petition_data.get('type')

    conn = None
    try:
        conn = get_db_connection() 
        cursor = conn.cursor()

        # Verifica se peticao ja existe no banco de dados 
        sql_check = """
            SELECT 1 FROM Peticoes
            WHERE id_processo = ? AND data_peticao = ? AND tipo_peticao = ?
            LIMIT 1
        """
        cursor.execute(sql_check, (case_id, date, type))
        
        if cursor.fetchone():
            return None

        sql_insert = """
            INSERT INTO Peticoes (id_processo, data_peticao, tipo_peticao)
            VALUES (?, ?, ?)
        """
        cursor.execute(sql_insert, (case_id, date, type))
        conn.commit()
        result = cursor.lastrowid
        print(f"Peticao de '{date}' ADICIONADA ao processo {case_id}. ID da Movimentação: {result}")
        return result 

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao processar peticao de '{date}' para o processo {case_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_incident(case_id: str, incident_data: dict):
    # Adiciona incidente

    incident_date = incident_data.get('date') 
    incident_class = incident_data.get('class_description')

    conn = None
    try:
        conn = get_db_connection() 
        cursor = conn.cursor()
        # Verifica se peticao ja existe no banco de dados 
        sql_check = """
            SELECT 1 FROM Incidentes
            WHERE id_processo = ? AND data_incidente = ? AND classe = ?
            LIMIT 1
        """
        cursor.execute(sql_check, (case_id, incident_date, incident_class))
        
        if cursor.fetchone():
            return None 

        sql_insert = """
            INSERT INTO Incidentes (id_processo, data_incidente, classe)
            VALUES (?, ?, ?)
        """
        cursor.execute(sql_insert, (case_id, incident_date, incident_class))
        conn.commit()
        
        result_id = cursor.lastrowid 
        print(f"Novo incidente de '{incident_date}', da classe '{incident_class}' adicionado ao caso {case_id}. Id da operacao {result_id}")
        return result_id

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro processando incidente de '{incident_date}',  do processo {case_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_case_numbers():
    # Lista numeros de processo salvos no banco de dados
    sql = "SELECT numero_processo FROM Processos ORDER BY numero_processo;"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall() 
        
        case_numbers = [row[0] for row in results] 
        return case_numbers
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_case(case_id: str):
    # Mostra detalhes de um processo

    conn = None
    case = {
        "main_data": None,
        "involved_parties": [],
        "case_events": [],
        "petitions": [],
        "incidents": []
    }

    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. Busca dados principais do processo
        cursor.execute("SELECT * FROM Processos WHERE numero_processo = ?", (case_id,))
        main_data = cursor.fetchone()

        if not main_data:
            print(f"Processo '{case_id}' nao foi encontrado.")
            return None

        case["main_data"] = dict(main_data) 

        # 2. Busca Partes Envolvidas
        cursor.execute("SELECT * FROM Envolvidos WHERE id_processo = ? ORDER BY nome_envolvido", (case_id,))
        involved_parties = cursor.fetchall()
        case["involved_parties"] = [dict(row) for row in involved_parties]

        # 3. Busca Movimentações (Movimentacoes) - Ordenando por ID (ordem de inserção)
        cursor.execute("SELECT * FROM Movimentacoes WHERE id_processo = ? ORDER BY id LIMIT 50", (case_id,))
        case_events = cursor.fetchall()
        case["case_events"] = [dict(row) for row in case_events]

        # 4. Busca Petições (Peticoes) - Ordenando por ID
        cursor.execute("SELECT * FROM Peticoes WHERE id_processo = ? ORDER BY id_peticao", (case_id,))
        petitions_rows = cursor.fetchall()
        case["petitions"] = [dict(row) for row in petitions_rows]

        # 5. Busca Incidentes (Incidentes) - Ordenando por ID
        cursor.execute("SELECT * FROM Incidentes WHERE id_processo = ? ORDER BY id_incidentes", (case_id,))
        incidents_rows = cursor.fetchall()
        case["incidents"] = [dict(row) for row in incidents_rows]

        print(f"Dados do processo {case_id} buscados com sucesso")
        return case

    except Exception as e:
        print(f"Um erro inesperado ocorreu para o processo'{case_id}': {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_latest_case_events(limit: int = 50):
    # Busca ultimas movimentacoes adicionadas

    sql = """
        SELECT id_processo, data_evento, descricao_evento 
        FROM Movimentacoes 
        ORDER BY id DESC 
        LIMIT ?
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        cursor.execute(sql, (limit,)) # Passa o limite como parâmetro
        
        results_rows = cursor.fetchall() 
        
        # Converte as linhas para uma lista de dicionários
        latest_events = [dict(row) for row in results_rows]
        
        print(f"Ùltimas {len(latest_events)} movimentacões buscadas com sucesso")
        return latest_events
        
    except Exception as e:
        print(f"Um erro inesperado ocorreu buscando ultimas movimentacoes: {e}")
        return None
    finally:
        if conn:
            conn.close()
