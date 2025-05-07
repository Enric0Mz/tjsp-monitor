import sqlite3
from . models import get_db_connection


def add_process(case_data):
    # Cria um novo processo

    sql = """
        INSERT INTO Processos (
            numero_processo, nome_caso, classe_processo, juiz, vara,
            tribunal, assunto, status, foro, valor_causa, area,
            data_distribuicao, controle
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        return cursor.lastrowid 

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar processo: {e}")
        return None
    finally:
        if conn:
            conn.close()
