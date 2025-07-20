"""
Testes de coleta de dados para a assistente de IA.
Valida a coleta de documentos, código e histórico Git.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import git

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.data_collector.collectors import DocumentCollector, CodeCollector, GitCollector, DataCollector

class TestDataCollection(unittest.TestCase):
    """Testes para a coleta de dados."""
    
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
        src_dir = os.path.join(self.temp_dir, "src")
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(src_dir, exist_ok=True)
        
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
    
    def test_document_collector_metadata(self):
        """Testa a extração de metadados do coletor de documentos."""
        collector = DocumentCollector()
        test_file = os.path.join(self.temp_dir, "decisoes_arquiteturais_iniciais.md")
        
        # Simula a coleta e verifica metadados
        with patch.object(collector.vector_db, 'process_and_add_document') as mock_process:
            mock_process.return_value = ["chunk1", "chunk2"]
            
            chunk_ids = collector.collect(test_file)
            
            # Verifica se o método foi chamado
            mock_process.assert_called_once()
            
            # Verifica os argumentos passados
            call_args = mock_process.call_args
            self.assertEqual(call_args[1]['collection_name'], "decisoes_arquiteturais")
            self.assertIn("decisoes_arquiteturais_iniciais.md", call_args[1]['metadata']['file_name'])
            self.assertEqual(call_args[1]['metadata']['file_type'], "markdown")
    
    def test_code_collector_structure_extraction(self):
        """Testa a extração de estrutura do código Kotlin."""
        collector = CodeCollector()
        test_file = os.path.join(self.temp_dir, "src", "Product.kt")
        
        # Simula a coleta e verifica estrutura extraída
        with patch.object(collector.vector_db, 'process_and_add_document') as mock_process:
            mock_process.return_value = ["chunk1", "chunk2"]
            
            chunk_ids = collector.collect(test_file)
            
            # Verifica se o método foi chamado
            mock_process.assert_called_once()
            
            # Verifica os metadados extraídos
            call_args = mock_process.call_args
            metadata = call_args[1]['metadata']
            
            self.assertEqual(metadata['file_type'], "kotlin")
            self.assertEqual(metadata['document_type'], "code")
            self.assertIn("Product", metadata['classes'])
            self.assertIn("updateStock", metadata['functions'])
            self.assertIn("changePrice", metadata['functions'])
    
    def test_code_collector_directory_scanning(self):
        """Testa a varredura de diretórios para código."""
        collector = CodeCollector()
        
        # Simula a coleta de diretório
        with patch.object(collector, 'collect') as mock_collect:
            mock_collect.return_value = ["chunk1"]
            
            results = collector.collect_directory(self.temp_dir, file_extension=".kt")
            
            # Verifica se pelo menos um arquivo foi processado
            self.assertGreater(len(results), 0)
    
    def test_git_collector_initialization(self):
        """Testa a inicialização do coletor Git."""
        try:
            collector = GitCollector()
            self.assertIsNotNone(collector)
        except Exception as e:
            self.fail(f"Falha ao criar coletor Git: {e}")
    
    @patch('git.Repo')
    def test_git_collector_with_mock_repo(self, mock_repo):
        """Testa o coletor Git com repositório simulado."""
        # Configura o mock do repositório
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        
        # Configura commits simulados
        mock_commit1 = MagicMock()
        mock_commit1.message = "feat: implement domain layer"
        mock_commit1.author.name = "Test Author"
        mock_commit1.committed_datetime.isoformat.return_value = "2025-01-01T10:00:00"
        
        mock_commit2 = MagicMock()
        mock_commit2.message = "docs: add architectural decisions"
        mock_commit2.author.name = "Test Author"
        mock_commit2.committed_datetime.isoformat.return_value = "2025-01-01T11:00:00"
        
        mock_repo_instance.iter_commits.return_value = [mock_commit1, mock_commit2]
        
        collector = GitCollector()
        
        # Simula a coleta
        with patch.object(collector.vector_db, 'process_and_add_document') as mock_process:
            mock_process.return_value = ["chunk1"]
            
            chunk_ids = collector.collect(self.temp_dir, max_commits=10)
            
            # Verifica se o processamento foi chamado
            self.assertGreater(mock_process.call_count, 0)
    
    def test_data_collector_integration(self):
        """Testa a integração do coletor de dados principal."""
        collector = DataCollector()
        
        # Simula a coleta completa
        with patch.object(collector.document_collector, 'collect') as mock_doc_collect:
            with patch.object(collector.code_collector, 'collect_directory') as mock_code_collect:
                with patch.object(collector.git_collector, 'collect') as mock_git_collect:
                    
                    mock_doc_collect.return_value = ["doc_chunk1"]
                    mock_code_collect.return_value = {"file1.kt": ["code_chunk1"]}
                    mock_git_collect.return_value = ["git_chunk1"]
                    
                    results = collector.collect_all(self.temp_dir)
                    
                    # Verifica se todos os coletores foram chamados
                    self.assertGreater(mock_doc_collect.call_count, 0)
                    self.assertGreater(mock_code_collect.call_count, 0)
                    self.assertGreater(mock_git_collect.call_count, 0)
                    
                    # Verifica a estrutura dos resultados
                    self.assertIn('documents', results)
                    self.assertIn('code', results)
                    self.assertIn('git', results)

if __name__ == '__main__':
    unittest.main() 