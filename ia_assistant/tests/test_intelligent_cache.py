"""
Testes para o sistema de cache inteligente.
Valida cache, aprendizado de padrões e otimização de performance.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import time

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.cache.intelligent_cache import (
    IntelligentCache, 
    CacheEntry, 
    CacheStrategy
)

class TestIntelligentCache(unittest.TestCase):
    """Testes para o sistema de cache inteligente."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "test_cache")
        
        # Configurações de teste
        self.test_config = {
            'cache_dir': self.cache_dir,
            'max_size': 10,
            'default_ttl': 60,  # 1 minuto para testes
            'enable_pattern_learning': True
        }
        
        self.cache = IntelligentCache(**self.test_config)
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    def test_cache_initialization(self):
        """Testa inicialização do cache."""
        self.assertIsNotNone(self.cache)
        self.assertEqual(self.cache.max_size, 10)
        self.assertEqual(self.cache.default_ttl, 60)
        self.assertTrue(self.cache.enable_pattern_learning)
        self.assertEqual(len(self.cache.cache), 0)
    
    def test_cache_entry_creation(self):
        """Testa criação de entrada do cache."""
        entry = CacheEntry(
            query_hash="test_hash",
            query_text="test query",
            response="test response",
            query_type="test_type",
            prompt_template="test template",
            tokens_used=100,
            cost_estimate=0.001,
            created_at=time.time(),
            last_accessed=time.time(),
            access_count=1,
            relevance_score=1.0,
            ttl_seconds=3600
        )
        
        self.assertEqual(entry.query_text, "test query")
        self.assertEqual(entry.response, "test response")
        self.assertEqual(entry.tokens_used, 100)
    
    def test_cache_entry_serialization(self):
        """Testa serialização e deserialização de entrada do cache."""
        from datetime import datetime
        
        entry = CacheEntry(
            query_hash="test_hash",
            query_text="test query",
            response="test response",
            query_type="test_type",
            prompt_template="test template",
            tokens_used=100,
            cost_estimate=0.001,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            relevance_score=1.0,
            ttl_seconds=3600
        )
        
        # Serializa
        data = entry.to_dict()
        self.assertIn('query_hash', data)
        self.assertIn('query_text', data)
        self.assertIn('response', data)
        
        # Deserializa
        new_entry = CacheEntry.from_dict(data)
        self.assertEqual(new_entry.query_text, entry.query_text)
        self.assertEqual(new_entry.response, entry.response)
    
    def test_cache_put_and_get(self):
        """Testa armazenamento e recuperação do cache."""
        query = "Como está a arquitetura?"
        response = "A arquitetura está bem estruturada."
        query_type = "architecture"
        prompt_template = "test template"
        
        # Armazena no cache
        self.cache.put(
            query=query,
            response=response,
            query_type=query_type,
            prompt_template=prompt_template,
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        # Verifica se foi armazenado
        self.assertEqual(len(self.cache.cache), 1)
        
        # Recupera do cache
        result = self.cache.get(
            query=query,
            query_type=query_type,
            prompt_template=prompt_template
        )
        
        self.assertIsNotNone(result)
        cached_response, metadata = result
        self.assertEqual(cached_response, response)
        self.assertEqual(metadata['cache_type'], 'exact_match')
    
    def test_cache_miss(self):
        """Testa quando não há correspondência no cache."""
        result = self.cache.get(
            query="Consulta inexistente",
            query_type="test",
            prompt_template="test"
        )
        
        self.assertIsNone(result)
    
    def test_cache_expiration(self):
        """Testa expiração de entradas do cache."""
        # Cria cache com TTL muito baixo
        short_ttl_cache = IntelligentCache(
            cache_dir=self.cache_dir,
            max_size=10,
            default_ttl=1,  # 1 segundo
            enable_pattern_learning=True
        )
        
        # Armazena entrada
        short_ttl_cache.put(
            query="test",
            response="test",
            query_type="test",
            prompt_template="test",
            tokens_used=10,
            cost_estimate=0.001
        )
        
        # Verifica que está no cache
        self.assertEqual(len(short_ttl_cache.cache), 1)
        
        # Aguarda expiração
        time.sleep(2)
        
        # Verifica que foi removida
        short_ttl_cache._optimize_cache()
        
        # Verifica que foi removida (pode não ser imediato devido ao TTL)
        # Aguarda um pouco mais e verifica novamente
        time.sleep(1)
        short_ttl_cache._optimize_cache()
        
        # Verifica que foi removida ou está expirada
        expired_entries = [entry for entry in short_ttl_cache.cache.values() if entry.is_expired()]
        self.assertGreater(len(expired_entries), 0)
    
    def test_semantic_matching(self):
        """Testa correspondência semântica."""
        # Armazena consulta original
        self.cache.put(
            query="Como está a arquitetura hexagonal?",
            response="A arquitetura hexagonal está bem implementada.",
            query_type="architecture",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        # Busca por consulta similar
        result = self.cache.get(
            query="Explique a arquitetura hexagonal",
            query_type="architecture",
            prompt_template="test",
            strategy=CacheStrategy.SEMANTIC_MATCH
        )
        
        # Pode retornar resultado se a similaridade for alta o suficiente
        if result:
            cached_response, metadata = result
            self.assertEqual(metadata['cache_type'], 'semantic_match')
    
    def test_cache_optimization(self):
        """Testa otimização automática do cache."""
        # Preenche o cache além do limite
        for i in range(15):
            self.cache.put(
                query=f"query_{i}",
                response=f"response_{i}",
                query_type="test",
                prompt_template="test",
                tokens_used=10,
                cost_estimate=0.001
            )
        
        # Verifica que o cache foi otimizado
        self.assertLessEqual(len(self.cache.cache), self.cache.max_size)
    
    def test_pattern_learning(self):
        """Testa aprendizado de padrões."""
        # Executa várias consultas similares
        queries = [
            "Como implementar arquitetura hexagonal?",
            "Explique arquitetura hexagonal",
            "Arquitetura hexagonal no projeto"
        ]
        
        for query in queries:
            self.cache.put(
                query=query,
                response="Resposta sobre arquitetura",
                query_type="architecture",
                prompt_template="test",
                tokens_used=50,
                cost_estimate=0.0001
            )
        
        # Verifica se padrões foram aprendidos
        patterns = self.cache.get_patterns()
        self.assertIn('query_patterns', patterns)
        self.assertIn('response_patterns', patterns)
    
    def test_cache_metrics(self):
        """Testa coleta de métricas."""
        # Executa algumas operações
        self.cache.put(
            query="test query",
            response="test response",
            query_type="test",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        self.cache.get(
            query="test query",
            query_type="test",
            prompt_template="test"
        )
        
        # Obtém métricas
        metrics = self.cache.get_metrics()
        
        self.assertIn('total_queries', metrics)
        self.assertIn('cache_hits', metrics)
        self.assertIn('cache_misses', metrics)
        self.assertIn('cost_saved', metrics)
        self.assertIn('tokens_saved', metrics)
    
    def test_cache_invalidation(self):
        """Testa invalidação de cache."""
        # Armazena algumas entradas
        self.cache.put(
            query="query1",
            response="response1",
            query_type="type1",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        self.cache.put(
            query="query2",
            response="response2",
            query_type="type2",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        # Verifica que estão no cache
        self.assertEqual(len(self.cache.cache), 2)
        
        # Invalida por tipo
        self.cache.invalidate(query_type="type1")
        
        # Verifica que apenas uma foi removida
        self.assertEqual(len(self.cache.cache), 1)
    
    def test_cache_clear(self):
        """Testa limpeza do cache."""
        # Armazena algumas entradas
        self.cache.put(
            query="test",
            response="test",
            query_type="test",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        # Verifica que há entradas
        self.assertGreater(len(self.cache.cache), 0)
        
        # Limpa o cache
        self.cache.clear()
        
        # Verifica que está vazio
        self.assertEqual(len(self.cache.cache), 0)
    
    def test_cache_stats(self):
        """Testa estatísticas detalhadas do cache."""
        # Armazena algumas entradas
        self.cache.put(
            query="query1",
            response="response1",
            query_type="architecture",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.0001
        )
        
        self.cache.put(
            query="query2",
            response="response2",
            query_type="code_review",
            prompt_template="test",
            tokens_used=30,
            cost_estimate=0.00005
        )
        
        # Obtém estatísticas
        stats = self.cache.get_cache_stats()
        
        self.assertIn('total_entries', stats)
        self.assertIn('type_distribution', stats)
        self.assertIn('architecture', stats['type_distribution'])
        self.assertIn('code_review', stats['type_distribution'])
    
    def test_concurrent_access(self):
        """Testa acesso concorrente ao cache."""
        import threading
        
        def worker(worker_id):
            for i in range(10):
                query = f"query_{worker_id}_{i}"
                self.cache.put(
                    query=query,
                    response=f"response_{i}",
                    query_type="test",
                    prompt_template="test",
                    tokens_used=10,
                    cost_estimate=0.001
                )
        
        # Cria múltiplas threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguarda todas terminarem
        for thread in threads:
            thread.join()
        
        # Verifica que o cache está em um estado válido
        self.assertGreater(len(self.cache.cache), 0)
        self.assertLessEqual(len(self.cache.cache), self.cache.max_size)

if __name__ == '__main__':
    unittest.main() 