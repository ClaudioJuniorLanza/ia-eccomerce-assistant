"""
Testes para o sistema de otimização de prompts.
Valida a detecção de tipos de consulta, templates e métricas.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.interface.prompt_templates import (
    PromptOptimizer, 
    QueryType, 
    PromptTemplate,
    prompt_optimizer
)

class TestPromptOptimization(unittest.TestCase):
    """Testes para o sistema de otimização de prompts."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.optimizer = PromptOptimizer()
    
    def test_query_type_detection_architecture(self):
        """Testa detecção de consultas de arquitetura."""
        queries = [
            "Como está estruturada a arquitetura hexagonal?",
            "Explique os ports e adapters",
            "Qual a organização das camadas?",
            "Como funciona a estrutura do projeto?"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.ARCHITECTURE)
    
    def test_query_type_detection_code_review(self):
        """Testa detecção de consultas de revisão de código."""
        queries = [
            "Analise este código",
            "Revisar implementação",
            "Melhorar esta classe",
            "Refatorar método"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.CODE_REVIEW)
    
    def test_query_type_detection_ddd(self):
        """Testa detecção de consultas sobre DDD."""
        queries = [
            "Explique o conceito de agregado",
            "Como funciona Domain Events?",
            "O que são Value Objects?",
            "Explique Bounded Context"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.DDD_CONCEPT)
    
    def test_query_type_detection_technical_decision(self):
        """Testa detecção de consultas sobre decisões técnicas."""
        queries = [
            "Qual tecnologia escolher?",
            "Compare frameworks",
            "Avalie trade-offs",
            "Qual decisão tomar?"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.TECHNICAL_DECISION)
    
    def test_query_type_detection_implementation(self):
        """Testa detecção de consultas sobre implementação."""
        queries = [
            "Como implementar?",
            "Passo a passo para criar",
            "Tutorial de desenvolvimento",
            "Guia de implementação"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.IMPLEMENTATION_GUIDE)
    
    def test_query_type_detection_troubleshooting(self):
        """Testa detecção de consultas de troubleshooting."""
        queries = [
            "Erro ao executar",
            "Problema com compilação",
            "Bug no código",
            "Não funciona"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.TROUBLESHOOTING)
    
    def test_query_type_detection_best_practices(self):
        """Testa detecção de consultas sobre boas práticas."""
        queries = [
            "Boa prática para",
            "Melhor prática",
            "Design pattern",
            "Princípio SOLID"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.BEST_PRACTICES)
    
    def test_query_type_detection_general(self):
        """Testa detecção de consultas gerais."""
        queries = [
            "Olá",
            "Como vai?",
            "Informações sobre o projeto",
            "Dúvida geral"
        ]
        
        for query in queries:
            detected_type = self.optimizer.detect_query_type(query)
            self.assertEqual(detected_type, QueryType.GENERAL)
    
    def test_prompt_template_formatting(self):
        """Testa formatação de templates de prompt."""
        template = PromptTemplate(
            query_type=QueryType.ARCHITECTURE,
            system_prompt="Você é um especialista em {domain}",
            user_template="Consulta: {query}\nContexto: {context}",
            max_tokens=2000,
            temperature=0.7
        )
        
        formatted = template.format(
            domain="arquitetura",
            query="Como funciona?",
            context="Projeto de teste"
        )
        
        self.assertIn("system_prompt", formatted)
        self.assertIn("user_prompt", formatted)
        self.assertEqual(formatted["max_tokens"], 2000)
        self.assertEqual(formatted["temperature"], 0.7)
    
    def test_prompt_template_missing_parameter(self):
        """Testa erro quando parâmetro obrigatório está faltando."""
        template = PromptTemplate(
            query_type=QueryType.ARCHITECTURE,
            system_prompt="Você é um especialista",
            user_template="Consulta: {query}\nContexto: {context}",
            max_tokens=2000,
            temperature=0.7
        )
        
        with self.assertRaises(ValueError):
            template.format(query="teste")  # context está faltando
    
    def test_optimize_prompt_architecture(self):
        """Testa otimização de prompt para arquitetura."""
        query = "Como está estruturada a arquitetura hexagonal?"
        relevant_docs = "Documentação sobre arquitetura hexagonal"
        
        prompt_data = self.optimizer.optimize_prompt(
            query=query,
            relevant_docs=relevant_docs,
            project_context="Projeto de teste"
        )
        
        self.assertIn("system_prompt", prompt_data)
        self.assertIn("user_prompt", prompt_data)
        self.assertIn("max_tokens", prompt_data)
        self.assertIn("temperature", prompt_data)
        
        # Verifica se o prompt contém informações relevantes
        system_prompt = prompt_data["system_prompt"]
        self.assertIn("arquitetura", system_prompt.lower())
        self.assertIn("hexagonal", system_prompt.lower())
    
    def test_optimize_prompt_code_review(self):
        """Testa otimização de prompt para revisão de código."""
        query = "Analise este código"
        relevant_docs = "Código Kotlin para análise"
        
        prompt_data = self.optimizer.optimize_prompt(
            query=query,
            relevant_docs=relevant_docs,
            project_context="Projeto de teste"
        )
        
        system_prompt = prompt_data["system_prompt"]
        self.assertIn("revisor", system_prompt.lower())
        self.assertIn("kotlin", system_prompt.lower())
    
    def test_optimize_prompt_ddd(self):
        """Testa otimização de prompt para DDD."""
        query = "Explique agregados"
        relevant_docs = "Documentação sobre DDD"
        
        prompt_data = self.optimizer.optimize_prompt(
            query=query,
            relevant_docs=relevant_docs,
            project_context="Projeto de teste"
        )
        
        system_prompt = prompt_data["system_prompt"]
        self.assertIn("ddd", system_prompt.lower())
        self.assertIn("domain", system_prompt.lower())
    
    def test_enhance_context_architecture(self):
        """Testa aprimoramento de contexto para arquitetura."""
        base_context = "Contexto base do projeto"
        
        enhanced = self.optimizer.enhance_context(
            QueryType.ARCHITECTURE,
            base_context
        )
        
        self.assertIn("hexagonal", enhanced.lower())
        self.assertIn("ports", enhanced.lower())
        self.assertIn("adapters", enhanced.lower())
    
    def test_enhance_context_ddd(self):
        """Testa aprimoramento de contexto para DDD."""
        base_context = "Contexto base do projeto"
        
        enhanced = self.optimizer.enhance_context(
            QueryType.DDD_CONCEPT,
            base_context
        )
        
        self.assertIn("domain", enhanced.lower())
        self.assertIn("agregado", enhanced.lower())
        self.assertIn("entidade", enhanced.lower())
    
    def test_enhance_context_with_focus_areas(self):
        """Testa aprimoramento de contexto com áreas de foco."""
        base_context = "Contexto base do projeto"
        focus_areas = ["architecture_focus", "code_quality_focus"]
        
        enhanced = self.optimizer.enhance_context(
            QueryType.ARCHITECTURE,
            base_context,
            focus_areas
        )
        
        self.assertIn("hexagonal", enhanced.lower())
        self.assertIn("clean code", enhanced.lower())
    
    def test_metrics_tracking(self):
        """Testa rastreamento de métricas."""
        # Reseta métricas
        self.optimizer.reset_metrics()
        
        # Simula algumas consultas
        queries = [
            "Como está a arquitetura?",
            "Analise este código",
            "Explique DDD",
            "Qual decisão tomar?"
        ]
        
        for query in queries:
            self.optimizer.optimize_prompt(
                query=query,
                relevant_docs="test",
                project_context="test"
            )
        
        metrics = self.optimizer.get_metrics()
        
        self.assertEqual(metrics['total_queries'], 4)
        self.assertIn('architecture', metrics['query_type_distribution'])
        self.assertIn('code_review', metrics['query_type_distribution'])
        self.assertIn('ddd_concept', metrics['query_type_distribution'])
        self.assertIn('technical_decision', metrics['query_type_distribution'])
    
    def test_reset_metrics(self):
        """Testa reset das métricas."""
        # Simula algumas consultas
        self.optimizer.optimize_prompt(
            query="teste",
            relevant_docs="test",
            project_context="test"
        )
        
        # Verifica que há métricas
        metrics_before = self.optimizer.get_metrics()
        self.assertGreater(metrics_before['total_queries'], 0)
        
        # Reseta métricas
        self.optimizer.reset_metrics()
        
        # Verifica que foram resetadas
        metrics_after = self.optimizer.get_metrics()
        self.assertEqual(metrics_after['total_queries'], 0)
        self.assertEqual(metrics_after['successful_responses'], 0)
    
    def test_global_optimizer_instance(self):
        """Testa a instância global do otimizador."""
        self.assertIsInstance(prompt_optimizer, PromptOptimizer)
        
        # Testa funcionalidade básica
        prompt_data = prompt_optimizer.optimize_prompt(
            query="teste",
            relevant_docs="test",
            project_context="test"
        )
        
        self.assertIn("system_prompt", prompt_data)
        self.assertIn("user_prompt", prompt_data)

if __name__ == '__main__':
    unittest.main() 