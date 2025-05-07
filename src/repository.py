import sqlite3
from . models import get_db_connection


def add_or_update_process(case_data):
    # Cria um novo processo

    sql = """
        INSERT INTO Processos (
            numero_processo, nome_caso, classe_processo, juiz, vara,
            tribunal, assunto, status, foro, valor_causa, area,
            data_distribuicao, controle, data_extracao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(numero_processo) DO UPDATE SET
            nome_caso=excluded.nome_caso,
            classe_processo=excluded.classe_processo,
            juiz=excluded.juiz,
            vara=excluded.vara,
            tribunal=excluded.tribunal,
            assunto=excluded.assunto,
            status=excluded.status,
            foro=excluded.foro,
            valor_causa=excluded.valor_causa,
            area=excluded.area,
            data_distribuicao=excluded.data_distribuicao, -- Cuidado com a conversão de data
            controle=excluded.controle,
            data_extracao=CURRENT_TIMESTAMP
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            case_data.get('number'), case_data.get('name'), case_data.get('_class'),
            case_data.get('judge'), case_data.get('division'), case_data.get('court'),
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

def get_envolved(case_id: int, name: str, role: str):
    # Verifica se envolvido ja esta na tabela

    sql = """
        SELECT 1 from Envolvidos
        WHERE id_processo = ? AND nome_envolvido = ? AND papel_envolvido = ?
        LIMIT 1
    """

    conn = None
    exists = False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (case_id, name, role))
        
        if cursor.fetchone():
            exists = True
    
    except sqlite3.Error as e:
        print(f"Erro ao verificar existência do envolvido '{name}' para o processo ID {case_id}: {e}")
    finally:
        if conn:
            conn.close()
    return exists

def add_envolved(case_id, envolved_data):
    # Cria um novo processo

    name = envolved_data.get('name')
    role = envolved_data.get('role')

    if get_envolved(case_id, name, role):
        return None

    sql = """
        INSERT INTO Envolvidos (
            id_processo, nome_envolvido, papel_envolvido
        ) VALUES (?, ?, ?)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            case_id, name, role,
        ))
        conn.commit()
        print(f"Envolvido '{name}' ({role}) ADICIONADO ao processo ID {case_id}.")
        return cursor.lastrowid 

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar processo: {e}")
        return None
    finally:
        if conn:
            conn.close()
