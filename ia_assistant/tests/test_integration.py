"""
Testes de integração para a assistente de IA.
Valida o funcionamento completo do sistema, desde a coleta até a resposta.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import json

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.main import initialize_assistant
from ia_assistant.validate_assistant import test_queries
from ia_assistant.interface.cli import QueryProcessor
from ia_assistant.data_collector.collectors import DataCollector

class TestIntegration(unittest.TestCase):
    """Testes de integração para a assistente de IA."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_project_root = self.temp_dir
        
        # Cria estrutura de teste completa
        self._create_complete_test_structure()
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    def _create_complete_test_structure(self):
        """Cria estrutura de teste completa para integração."""
        # Cria diretórios
        docs_dir = os.path.join(self.temp_dir, "docs")
        src_dir = os.path.join(self.temp_dir, "src")
        adrs_dir = os.path.join(docs_dir, "adrs")
        
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(adrs_dir, exist_ok=True)
        
        # Arquivo de decisões arquiteturais
        decisions_file = os.path.join(self.temp_dir, "decisoes_arquiteturais_iniciais.md")
        with open(decisions_file, 'w', encoding='utf-8') as f:
            f.write("""# Decisões Arquiteturais Iniciais

## 1. Adoção da Arquitetura Hexagonal

**Data da Decisão:** 12 de Maio de 2025

**Contexto:** Para o desenvolvimento da plataforma de e-commerce simplificada, decidimos adotar o padrão de Arquitetura Hexagonal.

**Motivações Principais:**
1. **Isolamento do Domínio de Negócio**
2. **Testabilidade**
3. **Flexibilidade Tecnológica**
4. **Manutenibilidade e Evolução**
5. **Alinhamento com Domain-Driven Design (DDD)**

## 2. Modelagem Inicial do Domínio

**Entidade Produto:**
```kotlin
data class Product(
    val id: ProductId,
    var name: String,
    var description: String,
    var price: BigDecimal,
    var stockQuantity: Int
)
```

## 3. Considerações sobre Custos

**Modelos de IA:**
- GPT-3.5-turbo: Mais econômico para consultas simples
- GPT-4: Mais avançado para análises complexas

**Estratégias de Otimização:**
- Caching de respostas
- Controle de tokens
- Filtragem prévia
- Prompts otimizados
""")
        
        # Arquivo de código Kotlin
        code_file = os.path.join(src_dir, "Product.kt")
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write("""package com.ia_ecommerce_assistant.catalog.domain.product

import java.math.BigDecimal
import java.util.UUID

data class Product(
    val id: ProductId,
    var name: String,
    var description: String,
    var price: BigDecimal,
    var stockQuantity: Int
) {
    fun updateStock(newQuantity: Int) {
        if (newQuantity < 0) {
            throw IllegalArgumentException("Estoque não pode ser negativo.")
        }
        this.stockQuantity = newQuantity
    }

    fun changePrice(newPrice: BigDecimal) {
        if (newPrice <= BigDecimal.ZERO) {
            throw IllegalArgumentException("Preço deve ser positivo.")
        }
        this.price = newPrice
    }
}

@JvmInline
value class ProductId(val value: UUID = UUID.randomUUID()) {
    override fun toString(): String = value.toString()
}
""")
        
        # Arquivo ADR
        adr_file = os.path.join(adrs_dir, "adr-001-arquitetura-hexagonal.md")
        with open(adr_file, 'w', encoding='utf-8') as f:
            f.write("""# ADR-001: Adoção da Arquitetura Hexagonal

## Status
Aceito

## Contexto
No desenvolvimento do projeto IA E-commerce Assistant, precisamos definir uma arquitetura que permita:
- Separação clara de responsabilidades
- Facilidade de teste
- Independência de frameworks e tecnologias externas
- Flexibilidade para evolução e manutenção
- Suporte à implementação de padrões de Domain-Driven Design (DDD)

## Decisão
Adotaremos a **Arquitetura Hexagonal** (também conhecida como Ports and Adapters) como padrão arquitetural para o projeto.

## Consequências

### Positivas
- **Testabilidade aprimorada**: O domínio pode ser testado de forma isolada
- **Flexibilidade tecnológica**: Podemos trocar implementações sem afetar o domínio
- **Clareza de responsabilidades**: Cada componente tem um papel bem definido
- **Suporte a DDD**: A arquitetura facilita a implementação de conceitos de DDD
- **Evolução independente**: Diferentes partes do sistema podem evoluir independentemente

### Negativas
- **Complexidade inicial**: Requer mais código e estrutura
- **Curva de aprendizado**: Desenvolvedores precisam de tempo para adaptação
- **Overhead de desenvolvimento**: Criação de interfaces e adaptadores adicionais
""")
        
        # Arquivo de visão do projeto
        vision_file = os.path.join(docs_dir, "visao_projeto.md")
        with open(vision_file, 'w', encoding='utf-8') as f:
            f.write("""# Visão do Projeto: IA E-commerce Assistant

## O que é o projeto

O **IA E-commerce Assistant** é um projeto inovador que combina duas áreas de grande relevância tecnológica: desenvolvimento de software para e-commerce e inteligência artificial assistiva.

## Objetivo do projeto

O objetivo principal é criar um ambiente de desenvolvimento onde a inteligência artificial seja uma fonte de conhecimento viva sobre o projeto, capaz de:

1. **Documentar e preservar o conhecimento**: Capturar não apenas o "o quê" e o "como" do código, mas principalmente o "porquê" das decisões tomadas
2. **Responder dúvidas técnicas**: Auxiliar desenvolvedores a entender partes específicas do código, decisões arquiteturais e padrões implementados
3. **Facilitar a integração de novos membros**: Reduzir o tempo necessário para que novos desenvolvedores compreendam o projeto
4. **Apoiar decisões futuras**: Fornecer contexto histórico para embasar novas decisões técnicas e de negócio
5. **Servir como prova de conceito**: Demonstrar como a IA pode ser integrada ao ciclo de desenvolvimento de software

## Tecnologias utilizadas

### Plataforma de E-commerce
- **Linguagem**: Kotlin
- **Arquitetura**: Hexagonal (Ports and Adapters)
- **Metodologia**: Domain-Driven Design (DDD)

### Assistente de IA
- **Linguagem**: Python
- **Frameworks**: LangChain para orquestração de IA
- **Modelos de IA**: OpenAI GPT-3.5/GPT-4
- **Base de dados vetorial**: ChromaDB
""")
    
    @patch('ia_assistant.database.vector_db.get_vector_database')
    @patch('ia_assistant.knowledge_processor.updater.UpdateManager')
    def test_initialization_integration(self, mock_update_manager, mock_vector_db):
        """Testa a integração da inicialização da assistente."""
        # Configura os mocks
        mock_db_instance = MagicMock()
        mock_vector_db.return_value = mock_db_instance
        
        mock_manager_instance = MagicMock()
        mock_manager_instance.initialize_knowledge_base.return_value = {
            'initialization': 'success',
            'consistency': {
                'decisoes_arquiteturais': {'document_count': 5},
                'codigo_fonte': {'document_count': 10},
                'commits_historico': {'document_count': 3}
            }
        }
        mock_update_manager.return_value = mock_manager_instance
        
        # Testa a inicialização
        results = initialize_assistant(self.test_project_root)
        
        # Verifica se os componentes foram criados
        mock_vector_db.assert_called_once()
        mock_update_manager.assert_called_once_with(self.test_project_root, mock_db_instance)
        
        # Verifica os resultados
        self.assertEqual(results['initialization'], 'success')
        self.assertIn('consistency', results)
        self.assertIn('decisoes_arquiteturais', results['consistency'])
    
    @patch('ia_assistant.interface.cli.OpenAI')
    def test_query_processing_integration(self, mock_openai):
        """Testa a integração do processamento de consultas."""
        # Configura o mock do LLM
        mock_llm_instance = MagicMock()
        mock_llm_instance.return_value = "Resposta simulada da IA sobre arquitetura hexagonal"
        mock_openai.return_value = mock_llm_instance
        
        # Cria o processador
        processor = QueryProcessor()
        
        # Simula busca na base de dados
        with patch.object(processor.vector_db, 'search') as mock_search:
            mock_search.return_value = [
                {
                    "document": "A arquitetura hexagonal foi escolhida para isolar o domínio de negócio",
                    "metadata": {"source": "decisoes_arquiteturais_iniciais.md"}
                },
                {
                    "document": "O DDD complementa bem a arquitetura hexagonal",
                    "metadata": {"source": "docs/visao_projeto.md"}
                }
            ]
            
            # Testa processamento de consulta
            response = processor.process_query("Por que foi escolhida a arquitetura hexagonal?")
            
            # Verifica a resposta
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
            self.assertIn("hexagonal", response.lower())
    
    def test_data_collection_integration(self):
        """Testa a integração da coleta de dados."""
        collector = DataCollector()
        
        # Simula a coleta completa
        with patch.object(collector.document_collector, 'collect') as mock_doc_collect:
            with patch.object(collector.code_collector, 'collect_directory') as mock_code_collect:
                with patch.object(collector.git_collector, 'collect') as mock_git_collect:
                    
                    mock_doc_collect.return_value = ["doc_chunk1", "doc_chunk2"]
                    mock_code_collect.return_value = {
                        "src/Product.kt": ["code_chunk1"],
                        "src/Category.kt": ["code_chunk2"]
                    }
                    mock_git_collect.return_value = ["git_chunk1", "git_chunk2"]
                    
                    results = collector.collect_all(self.test_project_root)
                    
                    # Verifica se todos os coletores foram chamados
                    self.assertGreater(mock_doc_collect.call_count, 0)
                    self.assertGreater(mock_code_collect.call_count, 0)
                    self.assertGreater(mock_git_collect.call_count, 0)
                    
                    # Verifica a estrutura dos resultados
                    self.assertIn('documents', results)
                    self.assertIn('code', results)
                    self.assertIn('git', results)
                    
                    # Verifica se há dados coletados
                    self.assertGreater(len(results['documents']), 0)
                    self.assertGreater(len(results['code']), 0)
                    self.assertGreater(len(results['git']), 0)
    
    def test_end_to_end_query_flow(self):
        """Testa o fluxo completo de consulta end-to-end."""
        # Lista de consultas de teste
        test_queries_list = [
            "Quais são as principais decisões arquiteturais do projeto?",
            "Por que foi escolhida a arquitetura hexagonal para o projeto?",
            "Como está estruturado o módulo de catálogo do e-commerce?",
            "Quais são as considerações sobre custos e modelos de IA no projeto?",
            "Explique como a entidade Produto foi implementada no domínio."
        ]
        
        # Simula o processamento de consultas
        with patch('ia_assistant.validate_assistant.QueryProcessor') as mock_processor_class:
            mock_processor = MagicMock()
            mock_processor_class.return_value = mock_processor
            
            # Configura respostas simuladas
            mock_processor.process_query.side_effect = [
                "As principais decisões arquiteturais incluem a adoção da arquitetura hexagonal...",
                "A arquitetura hexagonal foi escolhida para isolar o domínio de negócio...",
                "O módulo de catálogo está estruturado seguindo os princípios do DDD...",
                "As considerações sobre custos incluem o uso de diferentes modelos...",
                "A entidade Produto foi implementada como uma data class em Kotlin..."
            ]
            
            # Testa as consultas
            results = test_queries(self.test_project_root, test_queries_list)
            
            # Verifica se todas as consultas foram processadas
            self.assertEqual(len(results), len(test_queries_list))
            
            # Verifica se todas as consultas tiveram sucesso
            for query, result in results.items():
                self.assertEqual(result['status'], 'success')
                self.assertIsNotNone(result['response'])
    
    def test_error_handling_integration(self):
        """Testa o tratamento de erros na integração."""
        processor = QueryProcessor()
        
        # Simula diferentes tipos de erros
        error_scenarios = [
            (Exception("Erro de conexão com a base de dados"), "erro de conexão"),
            (ValueError("Arquivo não encontrado"), "arquivo não encontrado"),
            (KeyError("Chave não encontrada"), "chave não encontrada")
        ]
        
        for exception, expected_error in error_scenarios:
            with patch.object(processor.vector_db, 'search') as mock_search:
                mock_search.side_effect = exception
                
                # Deve lidar graciosamente com o erro
                try:
                    response = processor.process_query("Teste de erro")
                    self.assertIn("erro", response.lower() or "problema", response.lower())
                except Exception as e:
                    self.fail(f"Falha no tratamento de erro {exception}: {e}")

if __name__ == '__main__':
    unittest.main() 