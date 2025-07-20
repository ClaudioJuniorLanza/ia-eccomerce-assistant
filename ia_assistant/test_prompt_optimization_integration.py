"""
Teste de integração para o sistema de otimização de prompts.
Valida a integração completa com diferentes tipos de consultas.
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interface.prompt_templates import prompt_optimizer, QueryType

def test_prompt_optimization_integration():
    """Testa a integração completa do sistema de otimização de prompts."""
    print("🔍 Testando integração do sistema de otimização de prompts...")
    
    try:
        # Testa diferentes tipos de consultas
        test_cases = [
            {
                "query": "Como está estruturada a arquitetura hexagonal no projeto?",
                "expected_type": QueryType.ARCHITECTURE,
                "description": "Consulta de arquitetura"
            },
            {
                "query": "Analise este código Kotlin e sugira melhorias",
                "expected_type": QueryType.CODE_REVIEW,
                "description": "Consulta de revisão de código"
            },
            {
                "query": "Explique o conceito de agregados em DDD",
                "expected_type": QueryType.DDD_CONCEPT,
                "description": "Consulta sobre DDD"
            },
            {
                "query": "Qual tecnologia escolher para o banco de dados?",
                "expected_type": QueryType.TECHNICAL_DECISION,
                "description": "Consulta sobre decisão técnica"
            },
            {
                "query": "Como implementar um novo endpoint REST?",
                "expected_type": QueryType.IMPLEMENTATION_GUIDE,
                "description": "Consulta sobre implementação"
            },
            {
                "query": "Erro de compilação no código Kotlin",
                "expected_type": QueryType.TROUBLESHOOTING,
                "description": "Consulta de troubleshooting"
            },
            {
                "query": "Quais são as boas práticas para testes?",
                "expected_type": QueryType.BEST_PRACTICES,
                "description": "Consulta sobre boas práticas"
            },
            {
                "query": "Informações gerais sobre o projeto",
                "expected_type": QueryType.GENERAL,
                "description": "Consulta geral"
            }
        ]
        
        print("\n🧪 Testando detecção de tipos de consulta...")
        
        for i, test_case in enumerate(test_cases, 1):
            query = test_case["query"]
            expected_type = test_case["expected_type"]
            description = test_case["description"]
            
            # Detecta o tipo
            detected_type = prompt_optimizer.detect_query_type(query)
            
            # Verifica se está correto
            if detected_type == expected_type:
                print(f"✅ {i}. {description}: {detected_type.value}")
            else:
                print(f"❌ {i}. {description}: esperado {expected_type.value}, obtido {detected_type.value}")
        
        print("\n📊 Testando otimização de prompts...")
        
        # Testa otimização de prompts
        for test_case in test_cases[:3]:  # Testa apenas os primeiros 3
            query = test_case["query"]
            description = test_case["description"]
            
            try:
                # Otimiza o prompt
                prompt_data = prompt_optimizer.optimize_prompt(
                    query=query,
                    relevant_docs="Documentação relevante do projeto",
                    project_context="Projeto de e-commerce com arquitetura hexagonal"
                )
                
                # Verifica se o prompt foi gerado corretamente
                if all(key in prompt_data for key in ["system_prompt", "user_prompt", "max_tokens", "temperature"]):
                    print(f"✅ {description}: prompt otimizado com sucesso")
                else:
                    print(f"❌ {description}: prompt incompleto")
                    
            except Exception as e:
                print(f"❌ {description}: erro ao otimizar prompt - {e}")
        
        print("\n📈 Testando métricas...")
        
        # Reseta métricas
        prompt_optimizer.reset_metrics()
        
        # Simula algumas consultas
        for test_case in test_cases:
            prompt_optimizer.optimize_prompt(
                query=test_case["query"],
                relevant_docs="test",
                project_context="test"
            )
        
        # Obtém métricas
        metrics = prompt_optimizer.get_metrics()
        
        print(f"Total de consultas: {metrics['total_queries']}")
        print("Distribuição por tipo:")
        for query_type, count in metrics['query_type_distribution'].items():
            print(f"  {query_type}: {count}")
        
        print("\n🎉 Teste de integração concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prompt_optimization_integration()
    sys.exit(0 if success else 1) 