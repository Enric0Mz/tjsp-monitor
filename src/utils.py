import textwrap

def format_and_print_details(case_data, involved_parties, events, petitions, incidents):
    # Função auxiliar para formatar e imprimir os detalhes de um caso
    if not case_data:
        print("Erro interno: dados do processo não fornecidos para formatação.")
        return

    print("\n" + "="*80)
    print(f"Detalhes do Processo: {case_data.get('numero_processo', 'N/A')}")
    print("="*80)

    print("\n--- Dados Principais ---")
    print(f"  Classe:         {case_data.get('classe_processo', 'N/A')}")
    print(f"  Assunto:        {case_data.get('assunto', 'N/A')}")
    print(f"  Foro:           {case_data.get('foro', 'N/A')}")
    print(f"  Vara:           {case_data.get('vara', 'N/A')}")
    print(f"  Juiz:           {case_data.get('juiz', 'N/A')}")
    print(f"  Status:         {case_data.get('status', 'N/A')}")
    print(f"  Área:           {case_data.get('area', 'N/A')}")
    print(f"  Valor da Ação:  {case_data.get('valor_causa', 'N/A')}")
    print(f"  Distribuição:   {case_data.get('data_distribuicao', 'N/A')}") 
    print(f"  Controle:       {case_data.get('controle', 'N/A')}")
    print(f"  Última Extração:{case_data.get('data_extracao', 'N/A')}")
    
    print("\n--- Partes Envolvidas ---")
    if involved_parties:
        for party in involved_parties:
            print(f"  - {party.get('papel_envolvido', 'Papel N/A')}: {party.get('nome_envolvido', 'Nome N/A')}")
    else:
        print("  (Nenhuma parte envolvida encontrada)")

    print("\n--- Movimentações (50 Últimas ocorrências adicionadas) ---")
    if events:
        for event in events: 
            desc = event.get('descricao_evento', 'N/A')
            wrapped_desc = textwrap.fill(desc, width=70, initial_indent=' ' * 6, subsequent_indent=' ' * 6)
            print(f"  - {event.get('data_evento', 'N/A')}:\n{wrapped_desc}")
            print()
    else:
        print("  (Nenhuma movimentação encontrada)")

    print("\n--- Petições ---")
    if petitions:
        for petition in petitions:
            print(f"  - {petition.get('data_peticao', 'N/A')}: {petition.get('tipo_peticao', 'N/A')}")
    else:
        print("(Nenhuma petição encontrada)")

    print("\n--- Incidentes ---")
    if incidents:
        for incident in incidents:
            print(f"  - {incident.get('data_incidente', 'N/A')}: {incident.get('classe', 'N/A')}")
    else:
        print("(Nenhum incidente encontrado)")

    print("="*80)
