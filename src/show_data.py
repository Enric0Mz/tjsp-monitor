import argparse

from .utils import format_and_print_details
from . import repository

def list_all_case_numbers():
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

    args = parser.parse_args()
    if args.processos:
        list_all_case_numbers()
    elif args.details:
        show_case_details(args.details)
    else:
        print("Nenhuma ação específica solicitada. Exibindo lista de números de processos por padrão.")
        print("Use -h ou --help para ver as opções disponíveis.")
        list_all_case_numbers()
