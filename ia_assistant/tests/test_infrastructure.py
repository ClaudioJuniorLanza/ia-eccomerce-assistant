"""
Testes de infraestrutura para a assistente de IA.
Valida componentes básicos como base de dados, coletores e configurações.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.database.vector_db import get_vector_database, VectorDatabase
from ia_assistant.data_collector.collectors import DocumentCollector, CodeCollector, GitCollector
from ia_assistant.interface.cli import QueryProcessor

class TestInfrastructure(unittest.TestCase):
    """Testes para a infraestrutura básica da assistente."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_root = self.temp_dir
        
        # Cria arquivos de teste
        self._create_test_files()
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_files(self):
        """Cria arquivos de teste para os testes."""
        # Arquivo de decisões arquiteturais
        decisions_file = os.path.join(self.temp_dir, "decisoes_arquiteturais_iniciais.md")
        with open(decisions_file, 'w', encoding='utf-8') as f:
            f.write("# Decisões Arquiteturais\n\nEste é um arquivo de teste.")
        
        # Arquivo de código Kotlin
        code_file = os.path.join(self.temp_dir, "test.kt")
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write("package com.test\n\nclass TestClass {\n    fun test() {}\n}")
    
    def test_vector_database_creation(self):
        """Testa a criação da base de dados vetorial."""
        try:
            vector_db = get_vector_database()
            self.assertIsNotNone(vector_db)
            self.assertIsInstance(vector_db, VectorDatabase)
        except Exception as e:
            self.fail(f"Falha ao criar base de dados vetorial: {e}")
    
    def test_document_collector(self):
        """Testa o coletor de documentos."""
        try:
            collector = DocumentCollector()
            self.assertIsNotNone(collector)
            
            # Testa coleta de documento
            test_file = os.path.join(self.temp_dir, "decisoes_arquiteturais_iniciais.md")
            chunk_ids = collector.collect(test_file)
            self.assertIsInstance(chunk_ids, list)
            self.assertGreater(len(chunk_ids), 0)
        except Exception as e:
            self.fail(f"Falha no coletor de documentos: {e}")
    
    def test_code_collector(self):
        """Testa o coletor de código."""
        try:
            collector = CodeCollector()
            self.assertIsNotNone(collector)
            
            # Testa coleta de código
            test_file = os.path.join(self.temp_dir, "test.kt")
            chunk_ids = collector.collect(test_file)
            self.assertIsInstance(chunk_ids, list)
            self.assertGreater(len(chunk_ids), 0)
        except Exception as e:
            self.fail(f"Falha no coletor de código: {e}")
    
    def test_query_processor_creation(self):
        """Testa a criação do processador de consultas."""
        try:
            processor = QueryProcessor()
            self.assertIsNotNone(processor)
            self.assertEqual(processor.model_name, "gpt-3.5-turbo-instruct")
        except Exception as e:
            self.fail(f"Falha ao criar processador de consultas: {e}")
    
    def test_query_processor_model_switching(self):
        """Testa a troca de modelos no processador."""
        try:
            processor = QueryProcessor()
            
            # Testa troca para GPT-4
            processor.switch_model("gpt-4")
            self.assertEqual(processor.model_name, "gpt-4")
            
            # Testa troca de volta para GPT-3.5
            processor.switch_model("gpt-3.5-turbo-instruct")
            self.assertEqual(processor.model_name, "gpt-3.5-turbo-instruct")
        except Exception as e:
            self.fail(f"Falha na troca de modelos: {e}")
    
    @patch('os.environ.get')
    def test_openai_api_key_validation(self, mock_env_get):
        """Testa a validação da chave da API da OpenAI."""
        # Simula chave ausente
        mock_env_get.return_value = None
        
        with self.assertRaises(Exception):
            QueryProcessor()
        
        # Simula chave presente
        mock_env_get.return_value = "test-key"
        
        try:
            processor = QueryProcessor()
            self.assertIsNotNone(processor)
        except Exception as e:
            self.fail(f"Falha com chave válida: {e}")

if __name__ == '__main__':
    unittest.main() 