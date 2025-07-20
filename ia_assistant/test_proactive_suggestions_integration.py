"""
Teste de integração para validação do sistema de sugestões proativas.
Valida análise de padrões e geração de sugestões inteligentes.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proactive.suggestion_engine import ProactiveSuggestionEngine, SuggestionType, SuggestionPriority
from cache.intelligent_cache import intelligent_cache

def test_proactive_suggestions_integration():
    """Testa a integração do sistema de sugestões proativas."""
    print("🔍 Testando integração do sistema de sugestões proativas...")
    
    try:
        # Inicializa motor de sugestões
        engine = ProactiveSuggestionEngine(
            cache_manager=intelligent_cache,
            change_detector=None,
            impact_analyzer=None
        )
        
        print("✅ Motor de sugestões inicializado")
        
        # Simula consultas para gerar padrões
        print("\n🧪 Simulando consultas para análise...")
        
        # Consultas de performance (lentas)
        performance_queries = [
            "Como implementar arquitetura hexagonal com DDD e Kotlin?",
            "Explique detalhadamente o padrão Repository no contexto de DDD",
            "Como configurar Quarkus com configurações avançadas?",
            "Implementar testes de integração complexos",
            "Como otimizar performance de consultas no banco de dados?"
        ]
        
        for i, query in enumerate(performance_queries):
            engine.record_query(
                query=query,
                response_time=3000.0 + (i * 500),  # Consultas lentas
                cache_hit=False,
                query_type="architecture",
                tokens_used=150 + (i * 20)
            )
            print(f"📝 Consulta {i+1}: {query[:50]}...")
        
        # Consultas sobre documentação
        doc_queries = [
            "Como usar a documentação do projeto?",
            "Onde encontrar guias de implementação?",
            "Como documentar código seguindo padrões?",
            "Qual a melhor forma de documentar APIs?",
            "Como criar documentação técnica?"
        ]
        
        for i, query in enumerate(doc_queries):
            engine.record_query(
                query=query,
                response_time=1000.0,
                cache_hit=False,
                query_type="documentation",
                tokens_used=80
            )
            print(f"📚 Consulta doc {i+1}: {query[:50]}...")
        
        # Consultas sobre arquitetura
        arch_queries = [
            "Como implementar arquitetura hexagonal?",
            "Explique ADR 001 em detalhes",
            "Qual a melhor arquitetura para microserviços?",
            "Como usar DDD em Kotlin?",
            "Implementar hexagonal com Quarkus"
        ]
        
        for i, query in enumerate(arch_queries):
            engine.record_query(
                query=query,
                response_time=1200.0,
                cache_hit=i % 2 == 0,  # Alterna cache hit/miss
                query_type="architecture",
                tokens_used=100
            )
            print(f"🏗️ Consulta arch {i+1}: {query[:50]}...")
        
        # Simula estatísticas de cache
        print("\n💾 Simulando estatísticas de cache...")
        
        cache_stats = {
            'hit_rate': 0.25,  # 25% hit rate (baixo)
            'total_entries': 15,
            'cache_size': 200,
            'evictions': 5
        }
        
        engine.record_cache_stats(cache_stats)
        print("✅ Estatísticas de cache registradas")
        
        # Gera sugestões proativas
        print("\n🎯 Gerando sugestões proativas...")
        
        suggestions = engine.generate_suggestions()
        
        if suggestions:
            print(f"✅ {len(suggestions)} sugestões geradas:")
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n📋 Sugestão {i}:")
                print(f"  Tipo: {suggestion.suggestion_type.value}")
                print(f"  Prioridade: {suggestion.priority.value}")
                print(f"  Título: {suggestion.title}")
                print(f"  Descrição: {suggestion.description}")
                print(f"  Impacto estimado: {suggestion.estimated_impact}")
                print(f"  Confiança: {suggestion.confidence:.1%}")
                
                if suggestion.actionable_items:
                    print("  Ações recomendadas:")
                    for item in suggestion.actionable_items[:3]:  # Mostra apenas as 3 primeiras
                        print(f"    • {item}")
        else:
            print("⚠️  Nenhuma sugestão gerada")
        
        # Testa analytics de uso
        print("\n📊 Analytics de uso:")
        
        analytics = engine.get_usage_analytics()
        
        if analytics:
            print(f"Total de consultas: {analytics.get('total_queries', 0)}")
            print(f"Consultas recentes: {analytics.get('recent_queries', 0)}")
            print(f"Tempo médio de resposta: {analytics.get('avg_response_time', 0):.0f}ms")
            print(f"Taxa de cache hit: {analytics.get('cache_hit_rate', 0):.1%}")
            print(f"Sugestões geradas: {analytics.get('suggestions_generated', 0)}")
            
            # Mostra padrões mais frequentes
            top_patterns = analytics.get('top_patterns', [])
            if top_patterns:
                print("Padrões mais frequentes:")
                for pattern in top_patterns[:3]:
                    print(f"  • {pattern.context}: {pattern.frequency} vezes")
        else:
            print("⚠️  Nenhum analytics disponível")
        
        # Testa histórico de sugestões
        print("\n📋 Histórico de sugestões:")
        
        history = engine.get_suggestions_history()
        print(f"Total de sugestões no histórico: {len(history)}")
        
        if history:
            print("Últimas sugestões:")
            for i, suggestion in enumerate(history[-3:], 1):
                print(f"  {i}. {suggestion.title} ({suggestion.suggestion_type.value})")
        
        # Testa padrões de uso
        print("\n🔍 Padrões de uso detectados:")
        
        usage_patterns = engine.usage_patterns
        if usage_patterns:
            print(f"Total de padrões: {len(usage_patterns)}")
            
            # Mostra padrões mais frequentes
            sorted_patterns = sorted(usage_patterns.values(), key=lambda p: p.frequency, reverse=True)
            print("Padrões mais frequentes:")
            for pattern in sorted_patterns[:5]:
                print(f"  • {pattern.context}: {pattern.frequency} vezes ({pattern.pattern_type})")
        else:
            print("⚠️  Nenhum padrão detectado")
        
        print("\n🎉 Teste de integração concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_proactive_suggestions_integration()
    sys.exit(0 if success else 1) 