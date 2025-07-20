"""
Testes para a base de dados vetorial robusta.
Valida o retry mechanism, tratamento de falhas e métricas de performance.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
import tempfile
import shutil
import time

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.database.robust_vector_db import RobustVectorDatabase, get_robust_vector_database

class TestRobustVectorDatabase(unittest.TestCase):
    """Testes para a base de dados vetorial robusta."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_chroma_db")
        
        # Configurações de teste
        self.test_config = {
            'persist_directory': self.test_db_path,
            'max_retries': 3,
            'retry_delay': 0.1,  # Delay menor para testes
            'max_retry_delay': 1.0,
            'backoff_factor': 2.0
        }
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_initialization_with_retry_success(self, mock_client):
        """Testa inicialização bem-sucedida com retry."""
        # Configura o mock para sucesso na primeira tentativa
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        # Cria a instância
        db = RobustVectorDatabase(**self.test_config)
        
        # Verifica se foi chamado apenas uma vez
        mock_client.assert_called_once()
        mock_client_instance.heartbeat.assert_called_once()
        
        # Verifica se as métricas foram inicializadas
        self.assertEqual(db.operation_metrics['total_operations'], 0)
        self.assertEqual(db.operation_metrics['successful_operations'], 0)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_initialization_with_retry_failure_then_success(self, mock_client):
        """Testa inicialização com falha inicial seguida de sucesso."""
        # Configura o mock para falhar na primeira tentativa e sucesso na segunda
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.side_effect = [Exception("Connection failed"), None]
        mock_client.return_value = mock_client_instance
        
        # Cria a instância
        db = RobustVectorDatabase(**self.test_config)
        
        # Verifica se foi chamado duas vezes
        self.assertEqual(mock_client.call_count, 2)
        self.assertEqual(mock_client_instance.heartbeat.call_count, 2)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_initialization_with_all_retries_failing(self, mock_client):
        """Testa inicialização com todas as tentativas falhando."""
        # Configura o mock para falhar sempre
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_client_instance
        
        # Deve falhar após todas as tentativas
        with self.assertRaises(Exception):
            RobustVectorDatabase(**self.test_config)
        
        # Verifica se foi chamado o número correto de vezes
        self.assertEqual(mock_client.call_count, self.test_config['max_retries'])
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_retry_operation_success(self, mock_client):
        """Testa operação com retry bem-sucedida."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Testa operação simples
        def test_operation():
            return "success"
        
        result = db.retry_operation(test_operation)
        
        # Verifica resultado
        self.assertEqual(result, "success")
        
        # Verifica métricas
        self.assertEqual(db.operation_metrics['total_operations'], 1)
        self.assertEqual(db.operation_metrics['successful_operations'], 1)
        self.assertEqual(db.operation_metrics['failed_operations'], 0)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_retry_operation_with_failure_then_success(self, mock_client):
        """Testa operação com falha inicial seguida de sucesso."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Reseta métricas para garantir estado limpo
        db.reset_metrics()
        
        # Contador para simular falha inicial
        call_count = 0
        
        def test_operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary failure")
            return "success"
        
        result = db.retry_operation(test_operation)
        
        # Verifica resultado
        self.assertEqual(result, "success")
        
        # Verifica métricas
        self.assertEqual(db.operation_metrics['total_operations'], 1)
        self.assertEqual(db.operation_metrics['successful_operations'], 1)
        self.assertEqual(db.operation_metrics['failed_operations'], 0)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_retry_operation_with_all_failures(self, mock_client):
        """Testa operação com todas as tentativas falhando."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Reseta métricas para garantir estado limpo
        db.reset_metrics()
        
        def test_operation():
            raise Exception("Persistent failure")
        
        # Deve falhar após todas as tentativas
        with self.assertRaises(Exception):
            db.retry_operation(test_operation)
        
        # Verifica métricas
        self.assertEqual(db.operation_metrics['total_operations'], 1)
        self.assertEqual(db.operation_metrics['successful_operations'], 0)
        self.assertEqual(db.operation_metrics['failed_operations'], 1)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_add_documents_with_retry(self, mock_client):
        """Testa adição de documentos com retry mechanism."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        # Mock da coleção
        mock_collection = MagicMock()
        mock_collection.add.return_value = ["doc1", "doc2"]
        mock_client_instance.get_collection.return_value = mock_collection
        mock_client_instance.create_collection.return_value = mock_collection
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Testa adição de documentos
        documents = ["Document 1", "Document 2"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        ids = ["id1", "id2"]
        
        result = db.add_documents("test_collection", documents, metadatas, ids)
        
        # Verifica resultado
        self.assertEqual(result, ["doc1", "doc2"])
        
        # Verifica se a operação foi chamada
        mock_collection.add.assert_called_once()
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_search_with_retry(self, mock_client):
        """Testa busca com retry mechanism."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        # Mock da coleção
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["result1", "result2"]],
            "metadatas": [[{"source": "test1"}, {"source": "test2"}]],
            "distances": [[0.1, 0.2]]
        }
        mock_client_instance.get_collection.return_value = mock_collection
        mock_client_instance.create_collection.return_value = mock_collection
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Testa busca
        result = db.search("test_collection", ["query"], n_results=5)
        
        # Verifica resultado
        self.assertIn("documents", result)
        self.assertIn("metadatas", result)
        self.assertIn("distances", result)
        
        # Verifica se a operação foi chamada
        mock_collection.query.assert_called_once()
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_health_check_healthy(self, mock_client):
        """Testa health check quando a base está saudável."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        # Mock das coleções
        mock_client_instance.list_collections.return_value = [MagicMock(name="test_collection")]
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Testa health check
        health = db.health_check()
        
        # Verifica resultado
        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(health['connection'], 'ok')
        self.assertIn('metrics', health)
        self.assertIn('collections_count', health)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_health_check_unhealthy(self, mock_client):
        """Testa health check quando a base está com problemas."""
        # Configura o mock para falhar
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.side_effect = Exception("Connection failed")
        mock_client.return_value = mock_client_instance
        
        # Deve falhar na inicialização
        with self.assertRaises(Exception):
            RobustVectorDatabase(**self.test_config)
        
        # Cria uma instância que já falhou para testar health check
        db = RobustVectorDatabase.__new__(RobustVectorDatabase)
        db.operation_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'retry_operations': 0,
            'average_response_time': 0.0
        }
        db.client = mock_client_instance
        
        # Testa health check
        health = db.health_check()
        
        # Verifica resultado
        self.assertEqual(health['status'], 'unhealthy')
        self.assertEqual(health['connection'], 'failed')
        self.assertIn('error', health)
        self.assertIn('metrics', health)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_metrics_tracking(self, mock_client):
        """Testa o rastreamento de métricas."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Reseta métricas para garantir estado limpo
        db.reset_metrics()
        
        # Executa algumas operações
        def success_operation():
            return "success"
        
        def failure_operation():
            raise Exception("failure")
        
        # Operação bem-sucedida
        db.retry_operation(success_operation)
        
        # Operação que falha
        with self.assertRaises(Exception):
            db.retry_operation(failure_operation)
        
        # Obtém métricas
        metrics = db.get_metrics()
        
        # Verifica métricas
        self.assertEqual(metrics['total_operations'], 2)
        self.assertEqual(metrics['successful_operations'], 1)
        self.assertEqual(metrics['failed_operations'], 1)
        self.assertGreater(metrics['average_response_time'], 0)
    
    @patch('ia_assistant.database.robust_vector_db.chromadb.PersistentClient')
    def test_reset_metrics(self, mock_client):
        """Testa o reset das métricas."""
        # Configura o mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = None
        mock_client.return_value = mock_client_instance
        
        db = RobustVectorDatabase(**self.test_config)
        
        # Executa uma operação
        db.retry_operation(lambda: "success")
        
        # Verifica que há métricas
        metrics_before = db.get_metrics()
        self.assertGreater(metrics_before['total_operations'], 0)
        
        # Reseta métricas
        db.reset_metrics()
        
        # Verifica que as métricas foram resetadas
        metrics_after = db.get_metrics()
        self.assertEqual(metrics_after['total_operations'], 0)
        self.assertEqual(metrics_after['successful_operations'], 0)
        self.assertEqual(metrics_after['failed_operations'], 0)
    
    def test_factory_function(self):
        """Testa a função factory."""
        with patch('ia_assistant.database.robust_vector_db.RobustVectorDatabase') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance
            
            # Chama a função factory
            result = get_robust_vector_database("/test/path")
            
            # Verifica se a classe foi chamada com os parâmetros corretos
            mock_class.assert_called_once_with(persist_directory="/test/path")
            self.assertEqual(result, mock_instance)

if __name__ == '__main__':
    unittest.main() 