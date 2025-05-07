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
            cursor.execute("SELECT id FROM Processos WHERE numero_processo = ?", (case_data.get('number'),))
            result = cursor.fetchone()
            if result:
                return result[0]
        else:
            raise sqlite3.Error(f"Operação teve um erro inesperado para o processo {case_data.get('number')}")

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar processo: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_envolved(case_id, envolved_data):
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
        return cursor.lastrowid 

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar processo: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_case_event(case_id: int, case_event_data: dict):
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
        print(f"Movimentação de '{date}' ADICIONADA ao processo ID {case_id}. ID da Movimentação: {result}")
        return result

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao processar movimentação de '{date}' para o processo ID {case_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_petition(case_id: int, petition_data: dict):
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

        return cursor.lastrowid 

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao processar peticao de '{date}' para o processo ID {case_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()