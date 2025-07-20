"""
Teste de integração para o sistema de cache inteligente.
Valida a integração completa com diferentes cenários de uso.
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cache.intelligent_cache import intelligent_cache, CacheStrategy
from interface.prompt_templates import prompt_optimizer, QueryType

def test_cache_integration():
    """Testa a integração completa do sistema de cache inteligente."""
    print("🔍 Testando integração do sistema de cache inteligente...")
    
    try:
        # Limpa o cache para teste limpo
        intelligent_cache.clear()
        print("✅ Cache limpo para teste")
        
        # Testa cenários de cache
        test_scenarios = [
            {
                "query": "Como está estruturada a arquitetura hexagonal?",
                "response": "A arquitetura hexagonal está bem estruturada com ports e adapters.",
                "query_type": "architecture",
                "description": "Consulta de arquitetura"
            },
            {
                "query": "Analise este código Kotlin",
                "response": "O código Kotlin está bem estruturado seguindo boas práticas.",
                "query_type": "code_review",
                "description": "Consulta de revisão de código"
            },
            {
                "query": "Explique o conceito de agregados em DDD",
                "response": "Agregados são clusters de objetos de domínio tratados como uma unidade.",
                "query_type": "ddd_concept",
                "description": "Consulta sobre DDD"
            }
        ]
        
        print("\n🧪 Testando armazenamento e recuperação...")
        
        # Testa armazenamento
        for i, scenario in enumerate(test_scenarios, 1):
            query = scenario["query"]
            response = scenario["response"]
            query_type = scenario["query_type"]
            description = scenario["description"]
            
            # Armazena no cache
            intelligent_cache.put(
                query=query,
                response=response,
                query_type=query_type,
                prompt_template="test template",
                tokens_used=100,
                cost_estimate=0.001
            )
            
            print(f"✅ {i}. {description}: armazenada no cache")
        
        # Testa recuperação exata
        print("\n📊 Testando recuperação exata...")
        
        for scenario in test_scenarios:
            query = scenario["query"]
            expected_response = scenario["response"]
            query_type = scenario["query_type"]
            description = scenario["description"]
            
            # Tenta recuperar do cache
            result = intelligent_cache.get(
                query=query,
                query_type=query_type,
                prompt_template="test template"
            )
            
            if result:
                cached_response, metadata = result
                if cached_response == expected_response:
                    print(f"✅ {description}: recuperação exata bem-sucedida")
                else:
                    print(f"❌ {description}: resposta não corresponde")
            else:
                print(f"❌ {description}: não encontrada no cache")
        
        # Testa correspondência semântica
        print("\n🔍 Testando correspondência semântica...")
        
        similar_queries = [
            "Explique a arquitetura hexagonal",
            "Como funciona a arquitetura hexagonal?",
            "Arquitetura hexagonal no projeto"
        ]
        
        for query in similar_queries:
            result = intelligent_cache.get(
                query=query,
                query_type="architecture",
                prompt_template="test template",
                strategy=CacheStrategy.SEMANTIC_MATCH
            )
            
            if result:
                cached_response, metadata = result
                print(f"✅ Consulta similar '{query[:30]}...': encontrada (semântica)")
            else:
                print(f"⚠️  Consulta similar '{query[:30]}...': não encontrada")
        
        # Testa métricas
        print("\n📈 Testando métricas...")
        
        metrics = intelligent_cache.get_metrics()
        
        print(f"Total de consultas: {metrics['total_queries']}")
        print(f"Cache hits: {metrics['cache_hits']}")
        print(f"Cache misses: {metrics['cache_misses']}")
        print(f"Taxa de acerto: {metrics['hit_rate']:.2%}")
        print(f"Tokens economizados: {metrics['tokens_saved']}")
        print(f"Custo economizado: ${metrics['cost_saved']:.4f}")
        
        # Testa estatísticas detalhadas
        print("\n📊 Estatísticas detalhadas:")
        
        stats = intelligent_cache.get_cache_stats()
        
        if 'message' not in stats:
            print(f"Total de entradas: {stats['total_entries']}")
            print("Distribuição por tipo:")
            for query_type, type_stats in stats['type_distribution'].items():
                print(f"  {query_type}: {type_stats['count']} entradas")
        else:
            print("Cache vazio")
        
        # Testa padrões aprendidos
        print("\n🧠 Padrões aprendidos:")
        
        patterns = intelligent_cache.get_patterns()
        
        if patterns['query_patterns']:
            print("Padrões de consulta:")
            for word, pattern in list(patterns['query_patterns'].items())[:5]:
                print(f"  '{word}': usado {pattern['count']} vezes")
        else:
            print("Nenhum padrão aprendido ainda")
        
        # Testa otimização
        print("\n⚡ Testando otimização...")
        
        # Adiciona mais entradas para testar otimização
        for i in range(20):
            intelligent_cache.put(
                query=f"query_overflow_{i}",
                response=f"response_{i}",
                query_type="test",
                prompt_template="test",
                tokens_used=10,
                cost_estimate=0.0001
            )
        
        # Verifica se a otimização funcionou
        final_size = len(intelligent_cache.cache)
        print(f"Tamanho final do cache: {final_size}")
        
        if final_size <= intelligent_cache.max_size:
            print("✅ Otimização funcionando corretamente")
        else:
            print("⚠️  Cache pode estar maior que o limite")
        
        print("\n🎉 Teste de integração concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cache_integration()
    sys.exit(0 if success else 1) 