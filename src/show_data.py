import argparse

from .utils import format_and_print_details, format_and_print_event
from . import repository

def show_all_case_numbers():
    print("Buscando números de processo salvos no banco de dados...")
    
    case_numbers = repository.get_case_numbers() 

    if case_numbers is None:
        print("\nErro ao buscar a lista de processos do banco de dados.")
        return 
        
    if not case_numbers:
        print("\nNenhum processo encontrado no banco de dados.")
        return

    print("\n--- Números dos Processos Armazenados ---\n")
    for number in case_numbers:
        print(f"  - {number}")
            
    print("-" * 32)
    print(f"Total de processos encontrados: {len(case_numbers)}")


def show_case_details(case_number_to_find: str):
    print(f"Buscando detalhes para o processo: {case_number_to_find}...")
    
    case_details = repository.get_case(case_number_to_find) 

    if case_details is None:
        print(f"\nNão foi possível obter detalhes para o processo '{case_number_to_find}'. Verifique o número ou os logs do repositório.")
        return
    
    format_and_print_details(
        case_data=case_details.get("main_data"),
        involved_parties=case_details.get("involved_parties", []),
        events=case_details.get("case_events", []),
        petitions=case_details.get("petitions", []),
        incidents=case_details.get("incidents", [])
    )


def show_latest_events(limit: int = 50): # Função de controle agora usa a de formatação
    """Busca as últimas N movimentações do repositório e as imprime usando a função de formatação."""
    print(f"\nBuscando as últimas {limit} movimentações adicionadas...")

    latest_events = repository.get_latest_case_events(limit=limit)

    if latest_events is None:
        print("\nErro ao buscar as últimas movimentações do banco de dados.")
        return

    if not latest_events:
        print("\nNenhuma movimentação encontrada no banco de dados.")
        return

    print(f"\n--- Exibindo as {len(latest_events)} Últimas Movimentações Encontradas ---")

    for event in latest_events:
        format_and_print_event(event) 

    print("\n" + "-" * 50) 
    print(f"--- Fim da lista de {len(latest_events)} movimentações ---")

def show_summary():
    print("\nGerando resumo do banco de dados...")

    counts = repository.get_tables_size()

    if counts is None:
        print("\nErro ao buscar o resumo do banco de dados. Verifique os logs do repositório.")
        return

    if not counts:
        print("\nNenhuma tabela encontrada ou contagem retornou vazia.")
        return

    print("\n--- Resumo do Banco de Dados (Contagem de Registros) ---")
    max_len = max(len(table) for table in counts.keys()) if counts else 15
    
    for table, count in counts.items():
        print(f"  - Tabela '{table}':".ljust(max_len + 13) + f"{count} registros") 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualizador de dados de processos raspados do TJSP.",
        formatter_class=argparse.RawTextHelpFormatter 
    )

    action_group = parser.add_mutually_exclusive_group()
    
    action_group.add_argument(
        "--processos",
        action="store_true", 
        help="Listar apenas os números de todos os processos no banco."
    )

    action_group.add_argument(
        "--details", 
        metavar='NUMERO_PROCESSO', 
        type=str, 
        help="Mostrar detalhes completos para o número do processo especificado."
    )

    action_group.add_argument(
        "--recent-events",
        action="store_true",
        help="Mostrar as últimas 50 movimentações adicionadas ao banco (todos os processos)."
    )

    action_group.add_argument(
        "--summary", 
        action="store_true", 
        help="Mostrar contagem de registros em cada tabela." # Descrição do argumento
    )

    args = parser.parse_args()
    if args.processos:
        show_all_case_numbers()
    elif args.details:
        show_case_details(args.details)
    elif args.recent_events:
        show_latest_events()
    elif args.summary:
        show_summary()
    else:
        print("Nenhuma ação específica solicitada. Exibindo lista de números de processos por padrão.")
        print("Use -h ou --help para ver as opções disponíveis.")
        show_all_case_numbers()
