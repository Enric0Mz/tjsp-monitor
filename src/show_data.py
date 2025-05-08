import argparse

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

    args = parser.parse_args()
    if args.processos:
        list_all_case_numbers()
    else:
        print("Nenhuma ação específica solicitada. Exibindo lista de números de processos por padrão.")
        print("Use -h ou --help para ver as opções disponíveis.")
        list_all_case_numbers()
