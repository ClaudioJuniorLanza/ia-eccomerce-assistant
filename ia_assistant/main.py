"""
Script principal para iniciar a assistente de IA.
Este script fornece uma interface simples para inicializar e executar a assistente.
"""

import os
import sys
import argparse
from typing import Dict, Any

# Adiciona o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa os componentes da assistente
from ia_assistant.database.vector_db import get_vector_database
from ia_assistant.knowledge_processor.updater import get_update_manager
from ia_assistant.interface.cli import CLI, QueryProcessor

def initialize_assistant(project_root: str) -> Dict[str, Any]:
    """
    Inicializa a assistente de IA.
    
    Args:
        project_root: Caminho raiz do projeto.
        
    Returns:
        Resultados da inicialização.
    """
    print("\n=== Inicializando Assistente de IA ===")
    
    # Cria a base de dados vetorial
    vector_db = get_vector_database()
    
    # Cria o gerenciador de atualização
    update_manager = get_update_manager(project_root, vector_db)
    
    # Inicializa a base de conhecimento
    results = update_manager.initialize_knowledge_base()
    
    print(f"Inicialização concluída. Resultados:")
    print(f"- Status: {results['initialization']}")
    
    # Exibe estatísticas das coleções
    for collection_name, stats in results["consistency"].items():
        print(f"- Coleção '{collection_name}': {stats['document_count']} documentos")
    
    return results

def main():
    """Função principal para iniciar a assistente de IA."""
    parser = argparse.ArgumentParser(description="Assistente de IA para o Projeto E-commerce")
    parser.add_argument("--project-root", type=str, default=os.path.dirname(os.path.abspath(__file__)),
                       help="Caminho raiz do projeto")
    parser.add_argument("--initialize", action="store_true",
                       help="Inicializar a base de conhecimento")
    parser.add_argument("--modelo", choices=["gpt-3.5", "gpt-4"], default="gpt-3.5",
                       help="Modelo da OpenAI a ser utilizado")
    parser.add_argument("--update", action="store_true",
                       help="Atualizar a base de conhecimento")
    parser.add_argument("--update-interval", type=int, default=0,
                       help="Intervalo em segundos para atualizações periódicas (0 = desativado)")
    
    args = parser.parse_args()
    
    # Define o modelo a ser utilizado
    model_name = "gpt-4" if args.modelo == "gpt-4" else "gpt-3.5-turbo-instruct"
    
    # Inicializa a base de conhecimento se solicitado
    if args.initialize:
        initialize_assistant(args.project_root)
    
    # Atualiza a base de conhecimento se solicitado
    if args.update:
        update_manager = get_update_manager(args.project_root)
        update_manager.update_knowledge_base()
    
    # Configura atualizações periódicas se solicitado
    if args.update_interval > 0:
        update_manager = get_update_manager(args.project_root)
        update_manager.schedule_periodic_update(interval_seconds=args.update_interval)
    else:
        # Cria o processador de consultas
        query_processor = QueryProcessor(model_name=model_name)
        
        # Cria e executa a CLI
        cli = CLI(query_processor)
        cli.run()

if __name__ == "__main__":
    main()
