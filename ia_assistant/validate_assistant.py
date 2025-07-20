"""
Script para validar a funcionalidade da assistente de IA.
Este script testa a integração de todos os componentes da assistente,
desde a ingestão de dados até a geração de respostas contextualizadas.
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Optional

# Adiciona o diretório raiz ao path para importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os componentes da assistente
from ia_assistant.database.vector_db import get_vector_database
from ia_assistant.database.robust_vector_db import get_robust_vector_database
from ia_assistant.data_collector.collectors import DataCollector
from ia_assistant.knowledge_processor.updater import UpdateManager
from ia_assistant.interface.cli import QueryProcessor

def initialize_knowledge_base(project_root: str) -> Dict[str, Any]:
    """
    Inicializa a base de conhecimento com os dados do projeto.
    
    Args:
        project_root: Caminho raiz do projeto.
        
    Returns:
        Resultados da inicialização.
    """
    print("\n=== Inicializando Base de Conhecimento ===")
    
    # Testa a base de dados robusta primeiro
    print("🛡️  Testando base de dados robusta...")
    robust_db = get_robust_vector_database()
    
    # Verifica health check
    health_status = robust_db.health_check()
    print(f"📊 Status da base de dados: {health_status['status']}")
    print(f"🔗 Conexão: {health_status['connection']}")
    
    if health_status['status'] == 'healthy':
        print("✅ Base de dados robusta funcionando corretamente")
    else:
        print(f"⚠️  Base de dados com problemas: {health_status.get('error', 'Erro desconhecido')}")
    
    # Cria a base de dados vetorial
    vector_db = get_vector_database()
    
    # Cria o gerenciador de atualização
    update_manager = UpdateManager(project_root, vector_db)
    
    # Inicializa a base de conhecimento
    results = update_manager.initialize_knowledge_base()
    
    print(f"Inicialização concluída. Resultados:")
    print(f"- Status: {results['initialization']}")
    
    # Exibe estatísticas das coleções
    for collection_name, stats in results["consistency"].items():
        print(f"- Coleção '{collection_name}': {stats['document_count']} documentos")
    
    # Exibe métricas de performance
    print("\n📈 Métricas de Performance:")
    metrics = robust_db.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    return results

def test_queries(project_root: str, queries: List[str], model_name: str = "gpt-3.5-turbo-instruct") -> Dict[str, Any]:
    """
    Testa consultas à assistente de IA.
    
    Args:
        project_root: Caminho raiz do projeto.
        queries: Lista de consultas a serem testadas.
        model_name: Nome do modelo da OpenAI a ser utilizado.
        
    Returns:
        Resultados dos testes.
    """
    print("\n=== Testando Consultas à Assistente de IA ===")
    
    # Cria a base de dados vetorial
    vector_db = get_vector_database()
    
    # Cria o processador de consultas
    query_processor = QueryProcessor(vector_db, model_name=model_name)
    
    results = {}
    
    # Processa cada consulta
    for i, query in enumerate(queries):
        print(f"\nConsulta {i+1}: {query}")
        print("-" * 80)
        
        try:
            # Processa a consulta
            response = query_processor.process_query(query)
            
            # Exibe a resposta
            print("Resposta:")
            print(response)
            print("-" * 80)
            
            results[query] = {
                "status": "success",
                "response": response
            }
        except Exception as e:
            print(f"Erro ao processar consulta: {e}")
            results[query] = {
                "status": "error",
                "error": str(e)
            }
    
    return results

def main():
    """Função principal para validação da assistente de IA."""
    parser = argparse.ArgumentParser(description="Validação da Assistente de IA")
    parser.add_argument("--project-root", type=str, default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       help="Caminho raiz do projeto")
    parser.add_argument("--initialize", action="store_true",
                       help="Inicializar a base de conhecimento")
    parser.add_argument("--model", choices=["gpt-3.5", "gpt-4"], default="gpt-3.5",
                       help="Modelo da OpenAI a ser utilizado")
    
    args = parser.parse_args()
    
    # Define o modelo a ser utilizado
    model_name = "gpt-4" if args.model == "gpt-4" else "gpt-3.5-turbo-instruct"
    
    # Inicializa a base de conhecimento se solicitado
    if args.initialize:
        initialize_knowledge_base(args.project_root)
    
    # Define consultas de teste
    test_queries_list = [
        "Quais são as principais decisões arquiteturais do projeto?",
        "Por que foi escolhida a arquitetura hexagonal para o projeto?",
        "Como está estruturado o módulo de catálogo do e-commerce?",
        "Quais são as considerações sobre custos e modelos de IA no projeto?",
        "Explique como a entidade Produto foi implementada no domínio."
    ]
    
    # Testa as consultas
    test_results = test_queries(args.project_root, test_queries_list, model_name)
    
    print("\n=== Resumo dos Testes ===")
    for query, result in test_results.items():
        status = "✅ Sucesso" if result["status"] == "success" else f"❌ Erro: {result['error']}"
        print(f"- Consulta: '{query}' => {status}")

if __name__ == "__main__":
    main()
