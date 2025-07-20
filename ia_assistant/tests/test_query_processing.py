"""
Testes de processamento de consultas para a assistente de IA.
Valida a capacidade de responder perguntas e processar diferentes tipos de consultas.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.interface.cli import QueryProcessor

class TestQueryProcessing(unittest.TestCase):
    """Testes para o processamento de consultas."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_root = self.temp_dir
        
        # Cria estrutura de teste
        self._create_test_structure()
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_structure(self):
        """Cria estrutura de teste para os testes."""
        # Cria diretórios
        docs_dir = os.path.join(self.temp_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        # Arquivo ADR para testes
        adr_file = os.path.join(docs_dir, "adr-001-arquitetura-hexagonal.md")
        with open(adr_file, 'w', encoding='utf-8') as f:
            f.write("""# ADR-001: Adoção da Arquitetura Hexagonal

## Status
Aceito

## Contexto
No desenvolvimento do projeto IA E-commerce Assistant, precisamos definir uma arquitetura que permita:
- Separação clara de responsabilidades
- Facilidade de teste
- Independência de frameworks e tecnologias externas

## Decisão
Adotaremos a **Arquitetura Hexagonal** como padrão arquitetural para o projeto.

## Consequências

### Positivas
- Testabilidade aprimorada
- Flexibilidade tecnológica
- Clareza de responsabilidades
- Suporte a DDD

### Negativas
- Complexidade inicial
- Curva de aprendizado
- Overhead de desenvolvimento
""")
    
    def test_query_processor_initialization(self):
        """Testa a inicialização do processador de consultas."""
        try:
            processor = QueryProcessor()
            self.assertIsNotNone(processor)
            self.assertEqual(processor.model_name, "gpt-3.5-turbo-instruct")
        except Exception as e:
            self.fail(f"Falha ao inicializar processador: {e}")
    
    def test_listing_query_detection(self):
        """Testa a detecção de consultas de listagem."""
        processor = QueryProcessor()
        
        # Testa diferentes padrões de consultas de listagem
        listing_queries = [
            "Quais são os ADRs do projeto?",
            "Listar as decisões arquiteturais",
            "Mostrar os ADRs",
            "Quais decisões arquiteturais temos?",
            "Listar documentos",
            "Exibir ADRs"
        ]
        
        for query in listing_queries:
            self.assertTrue(processor._is_listing_query(query), 
                          f"Falha ao detectar consulta de listagem: {query}")
        
        # Testa consultas que não são de listagem
        non_listing_queries = [
            "Como funciona a arquitetura hexagonal?",
            "Explique o DDD",
            "Qual é o objetivo do projeto?"
        ]
        
        for query in non_listing_queries:
            self.assertFalse(processor._is_listing_query(query), 
                           f"Detectou incorretamente como listagem: {query}")
    
    def test_specific_adr_query_detection(self):
        """Testa a detecção de consultas sobre ADRs específicos."""
        processor = QueryProcessor()
        
        # Testa diferentes padrões de consultas sobre ADRs específicos
        adr_queries = [
            "Sobre a ADR-001",
            "Detalhes da ADR 001",
            "Explicar a ADR-001",
            "Conteúdo da ADR-001",
            "Informações sobre a ADR-001",
            "Me dê informações sobre a ADR-001",
            "Quero saber sobre a ADR-001",
            "Fale sobre a ADR-001"
        ]
        
        for query in adr_queries:
            self.assertTrue(processor._is_specific_adr_query(query), 
                          f"Falha ao detectar consulta sobre ADR específico: {query}")
        
        # Testa consultas que não são sobre ADRs específicos
        non_adr_queries = [
            "Quais são os ADRs?",
            "Listar ADRs",
            "Como funciona a arquitetura?"
        ]
        
        for query in non_adr_queries:
            self.assertFalse(processor._is_specific_adr_query(query), 
                           f"Detectou incorretamente como ADR específico: {query}")
    
    def test_resource_type_extraction(self):
        """Testa a extração do tipo de recurso da consulta."""
        processor = QueryProcessor()
        
        # Testa diferentes tipos de recursos
        test_cases = [
            ("Quais são os ADRs?", "adr"),
            ("Listar decisões arquiteturais", "adr"),
            ("Mostrar documentos", "documento"),
            ("Quais códigos temos?", "código"),
            ("Histórico de commits", "git")
        ]
        
        for query, expected_type in test_cases:
            extracted_type = processor._get_resource_type_from_query(query)
            self.assertEqual(extracted_type, expected_type, 
                           f"Falha ao extrair tipo de recurso de: {query}")
    
    def test_specific_resource_id_extraction(self):
        """Testa a extração de IDs de recursos específicos."""
        processor = QueryProcessor()
        
        # Testa diferentes padrões de IDs
        test_cases = [
            ("Sobre a ADR-001", "001"),
            ("Detalhes da ADR 002", "002"),
            ("Informações sobre ADR-003", "003"),
            ("Explicar ADR-004", "004")
        ]
        
        for query, expected_id in test_cases:
            extracted_id = processor._get_specific_resource_id(query)
            self.assertEqual(extracted_id, expected_id, 
                           f"Falha ao extrair ID de: {query}")
    
    @patch('ia_assistant.interface.cli.OpenAI')
    def test_query_processing_with_mock_llm(self, mock_openai):
        """Testa o processamento de consultas com LLM simulado."""
        # Configura o mock do LLM
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Resposta simulada da IA"
        mock_openai.return_value = mock_llm_instance
        
        processor = QueryProcessor()
        
        # Simula contexto relevante
        with patch.object(processor, '_get_relevant_context') as mock_context:
            mock_context.return_value = "Contexto relevante do projeto"
            
            # Testa processamento de consulta
            response = processor.process_query("Como funciona a arquitetura hexagonal?")
            
            # Verifica se a resposta foi gerada
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
    
    def test_context_retrieval(self):
        """Testa a recuperação de contexto relevante."""
        processor = QueryProcessor()
        
        # Simula busca na base de dados vetorial
        with patch.object(processor.vector_db, 'search') as mock_search:
            mock_search.return_value = [
                {"document": "Contexto sobre arquitetura hexagonal", "metadata": {}},
                {"document": "Informações sobre DDD", "metadata": {}}
            ]
            
            context = processor._get_relevant_context("arquitetura hexagonal")
            
            # Verifica se o contexto foi recuperado
            self.assertIsNotNone(context)
            self.assertIsInstance(context, str)
            self.assertIn("arquitetura hexagonal", context.lower())
    
    def test_model_switching(self):
        """Testa a troca de modelos."""
        processor = QueryProcessor()
        
        # Testa troca para GPT-4
        processor.switch_model("gpt-4")
        self.assertEqual(processor.model_name, "gpt-4")
        
        # Testa troca de volta para GPT-3.5
        processor.switch_model("gpt-3.5-turbo-instruct")
        self.assertEqual(processor.model_name, "gpt-3.5-turbo-instruct")
    
    def test_error_handling(self):
        """Testa o tratamento de erros."""
        processor = QueryProcessor()
        
        # Simula erro na busca
        with patch.object(processor.vector_db, 'search') as mock_search:
            mock_search.side_effect = Exception("Erro de conexão")
            
            # Deve lidar graciosamente com o erro
            try:
                response = processor.process_query("Teste de erro")
                self.assertIn("erro", response.lower())
            except Exception as e:
                self.fail(f"Falha no tratamento de erro: {e}")
    
    def test_empty_query_handling(self):
        """Testa o tratamento de consultas vazias."""
        processor = QueryProcessor()
        
        # Testa consulta vazia
        response = processor.process_query("")
        self.assertIn("vazia", response.lower() or "pergunta", response.lower())
        
        # Testa consulta com apenas espaços
        response = processor.process_query("   ")
        self.assertIn("vazia", response.lower() or "pergunta", response.lower())

if __name__ == '__main__':
    unittest.main() 