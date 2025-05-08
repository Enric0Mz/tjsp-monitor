import sqlite3
import os


# Sobe dois diretorios para armazenar dados em /data
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(PROJECT_ROOT, "data")

# Arquivo que ira armazenar os dados
DB_NAME = "stored_data.db"
DB_PATH = os.path.join(DB_DIR, DB_NAME)


def get_db_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_tables():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Processos (
            numero_processo TEXT PRIMARY KEY,
            classe_processo TEXT,
            juiz TEXT,
            vara TEXT,
            assunto TEXT,
            status TEXT,
            foro TEXT,
            valor_causa TEXT,
            area TEXT,
            data_distribuicao TEXT,
            controle TEXT,
            data_extracao TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_processo INTEGER NOT NULL,
            data_evento TEXT NOT NULL,
            descricao_evento TEXT NOT NULL,
            FOREIGN KEY(id_processo) REFERENCES Processos(numero_processo) ON DELETE CASCADE
        );
            """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Envolvidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_processo TEXT NOT NULL,
            nome_envolvido TEXT NOT NULL,
            papel_envolvido TEXT,
            FOREIGN KEY(id_processo) REFERENCES Processos(numero_processo) ON DELETE CASCADE -- Opcional: ON DELETE CASCADE
        );
            """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Peticoes (
            id_peticao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_processo TEXT NOT NULL,
            data_peticao TEXT NOT NULL,
            tipo_peticao TEXT NOT NULL,
            FOREIGN KEY(id_processo) REFERENCES Processos(numero_processo) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Incidentes (
            id_incidentes INTEGER PRIMARY KEY AUTOINCREMENT,
            id_processo TEXT NOT NULL,
            data_incidente TEXT NOT NULL,
            classe TEXT NOT NULL,
            FOREIGN KEY(id_processo) REFERENCES Processos(numero_processo) ON DELETE CASCADE
        );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_envolvidos_id_processo ON Envolvidos(id_processo);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_movimentacoes_id_processo ON Movimentacoes(id_processo);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON Movimentacoes(data_evento);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_peticoes_id_processo ON Peticoes(id_processo);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_peticoes_data ON Peticoes(data_peticao);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_peticoes_data ON Incidentes(data_peticao);
        """)

        print(f"Tabelas do banco de dados verificadas/criadas com sucesso em {DB_PATH}.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print(f"Executando create_tables() a partir de {__file__}...")
    create_tables()
    print("Teste de create_tables() concluído.")
