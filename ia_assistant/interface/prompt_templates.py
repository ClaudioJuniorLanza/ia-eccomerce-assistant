"""
Sistema de templates de prompts otimizados para a assistente de IA.
Implementa prompts especializados por tipo de consulta e contexto.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json

class QueryType(Enum):
    """Tipos de consulta identificados."""
    ARCHITECTURE = "architecture"
    CODE_REVIEW = "code_review"
    DDD_CONCEPT = "ddd_concept"
    TECHNICAL_DECISION = "technical_decision"
    IMPLEMENTATION_GUIDE = "implementation_guide"
    TROUBLESHOOTING = "troubleshooting"
    BEST_PRACTICES = "best_practices"
    GENERAL = "general"

class PromptTemplate:
    """Template de prompt otimizado para um tipo específico de consulta."""
    
    def __init__(self, 
                 query_type: QueryType,
                 system_prompt: str,
                 user_template: str,
                 max_tokens: int = 2000,
                 temperature: float = 0.7):
        """
        Inicializa um template de prompt.
        
        Args:
            query_type: Tipo de consulta
            system_prompt: Prompt do sistema
            user_template: Template para o usuário
            max_tokens: Máximo de tokens para resposta
            temperature: Temperatura para geração
        """
        self.query_type = query_type
        self.system_prompt = system_prompt
        self.user_template = user_template
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def format(self, **kwargs) -> Dict[str, Any]:
        """
        Formata o prompt com os parâmetros fornecidos.
        
        Args:
            **kwargs: Parâmetros para formatação
            
        Returns:
            Dicionário com prompt formatado
        """
        try:
            user_prompt = self.user_template.format(**kwargs)
            
            return {
                "system_prompt": self.system_prompt,
                "user_prompt": user_prompt,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        except KeyError as e:
            raise ValueError(f"Parâmetro obrigatório não fornecido: {e}")

class PromptOptimizer:
    """Otimizador de prompts com templates especializados."""
    
    def __init__(self):
        """Inicializa o otimizador de prompts."""
        self.templates = self._initialize_templates()
        self.context_enhancers = self._initialize_context_enhancers()
        self.quality_metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'average_response_length': 0,
            'query_type_distribution': {}
        }
    
    def _initialize_templates(self) -> Dict[QueryType, PromptTemplate]:
        """Inicializa os templates de prompts especializados."""
        templates = {}
        
        # Template para consultas de arquitetura
        templates[QueryType.ARCHITECTURE] = PromptTemplate(
            query_type=QueryType.ARCHITECTURE,
            system_prompt="""Você é um especialista em arquitetura de software com foco em:
- Arquitetura Hexagonal (Ports and Adapters)
- Domain-Driven Design (DDD)
- Microserviços
- Padrões de projeto e boas práticas

Forneça respostas técnicas detalhadas, incluindo:
- Explicações claras dos conceitos
- Exemplos práticos de implementação
- Considerações de trade-offs
- Referências ao código do projeto quando relevante""",
            user_template="""Contexto do projeto: {project_context}

Consulta sobre arquitetura: {query}

Base de conhecimento disponível:
{relevant_docs}

Por favor, responda de forma estruturada e técnica.""",
            max_tokens=2500,
            temperature=0.6
        )
        
        # Template para revisão de código
        templates[QueryType.CODE_REVIEW] = PromptTemplate(
            query_type=QueryType.CODE_REVIEW,
            system_prompt="""Você é um revisor de código experiente especializado em:
- Kotlin e Java
- Arquitetura Hexagonal
- DDD e Clean Architecture
- Padrões de projeto
- Boas práticas de desenvolvimento

Analise o código fornecendo:
- Identificação de problemas e melhorias
- Sugestões de refatoração
- Explicações técnicas detalhadas
- Exemplos de código melhorado""",
            user_template="""Contexto do projeto: {project_context}

Código para análise:
{code_snippet}

Consulta específica: {query}

Base de conhecimento:
{relevant_docs}

Forneça uma análise detalhada e sugestões práticas.""",
            max_tokens=3000,
            temperature=0.5
        )
        
        # Template para conceitos DDD
        templates[QueryType.DDD_CONCEPT] = PromptTemplate(
            query_type=QueryType.DDD_CONCEPT,
            system_prompt="""Você é um especialista em Domain-Driven Design (DDD) com experiência em:
- Agregados e Entidades
- Value Objects
- Domain Events
- Bounded Contexts
- Ubiquitous Language
- Strategic Design

Explique conceitos DDD de forma clara e prática, sempre relacionando com o projeto atual.""",
            user_template="""Contexto do projeto: {project_context}

Conceito DDD a ser explicado: {query}

Implementação atual no projeto:
{current_implementation}

Base de conhecimento DDD:
{relevant_docs}

Explique o conceito e sua aplicação prática no projeto.""",
            max_tokens=2000,
            temperature=0.7
        )
        
        # Template para decisões técnicas
        templates[QueryType.TECHNICAL_DECISION] = PromptTemplate(
            query_type=QueryType.TECHNICAL_DECISION,
            system_prompt="""Você é um arquiteto de software experiente especializado em:
- Tomada de decisões técnicas
- Análise de trade-offs
- Avaliação de tecnologias
- Considerações de custo-benefício
- Impacto em arquitetura

Forneça análises estruturadas com:
- Prós e contras de cada opção
- Recomendações baseadas em evidências
- Considerações de longo prazo
- Exemplos práticos""",
            user_template="""Contexto do projeto: {project_context}

Decisão técnica a ser analisada: {query}

Contexto atual:
{current_context}

Base de conhecimento:
{relevant_docs}

Forneça uma análise estruturada com recomendações.""",
            max_tokens=2500,
            temperature=0.6
        )
        
        # Template para guias de implementação
        templates[QueryType.IMPLEMENTATION_GUIDE] = PromptTemplate(
            query_type=QueryType.IMPLEMENTATION_GUIDE,
            system_prompt="""Você é um desenvolvedor sênior especializado em:
- Kotlin e Quarkus
- Arquitetura Hexagonal
- DDD e Clean Architecture
- Padrões de projeto
- Boas práticas de desenvolvimento

Forneça guias práticos de implementação com:
- Passos detalhados
- Exemplos de código
- Considerações importantes
- Boas práticas""",
            user_template="""Contexto do projeto: {project_context}

Funcionalidade a ser implementada: {query}

Requisitos:
{requirements}

Base de conhecimento:
{relevant_docs}

Forneça um guia passo-a-passo de implementação.""",
            max_tokens=3000,
            temperature=0.5
        )
        
        # Template para troubleshooting
        templates[QueryType.TROUBLESHOOTING] = PromptTemplate(
            query_type=QueryType.TROUBLESHOOTING,
            system_prompt="""Você é um especialista em debugging e troubleshooting com experiência em:
- Análise de problemas técnicos
- Identificação de causas raiz
- Soluções práticas
- Prevenção de problemas similares

Forneça análises estruturadas com:
- Identificação do problema
- Possíveis causas
- Soluções recomendadas
- Passos de verificação""",
            user_template="""Contexto do projeto: {project_context}

Problema relatado: {query}

Detalhes do erro:
{error_details}

Contexto atual:
{current_context}

Base de conhecimento:
{relevant_docs}

Forneça uma análise estruturada do problema e soluções.""",
            max_tokens=2500,
            temperature=0.4
        )
        
        # Template para boas práticas
        templates[QueryType.BEST_PRACTICES] = PromptTemplate(
            query_type=QueryType.BEST_PRACTICES,
            system_prompt="""Você é um especialista em boas práticas de desenvolvimento com foco em:
- Clean Code
- SOLID Principles
- Design Patterns
- Testing
- Performance
- Security

Forneça orientações práticas com:
- Explicações claras
- Exemplos de código
- Benefícios e trade-offs
- Aplicação no contexto atual""",
            user_template="""Contexto do projeto: {project_context}

Boas práticas a serem discutidas: {query}

Contexto específico:
{specific_context}

Base de conhecimento:
{relevant_docs}

Explique as boas práticas e sua aplicação no projeto.""",
            max_tokens=2000,
            temperature=0.7
        )
        
        # Template geral (fallback)
        templates[QueryType.GENERAL] = PromptTemplate(
            query_type=QueryType.GENERAL,
            system_prompt="""Você é um assistente de IA especializado em desenvolvimento de software, 
com conhecimento em arquitetura hexagonal, DDD, Kotlin, Quarkus e boas práticas de desenvolvimento.

Forneça respostas úteis, precisas e práticas baseadas no contexto do projeto.""",
            user_template="""Contexto do projeto: {project_context}

Consulta: {query}

Base de conhecimento disponível:
{relevant_docs}

Responda de forma clara e útil.""",
            max_tokens=2000,
            temperature=0.7
        )
        
        return templates
    
    def _initialize_context_enhancers(self) -> Dict[str, str]:
        """Inicializa os aprimoradores de contexto."""
        return {
            "architecture_focus": """
Foque especialmente em:
- Arquitetura Hexagonal (Ports and Adapters)
- Separação de responsabilidades
- Inversão de dependências
- Testabilidade
""",
            "ddd_focus": """
Foque especialmente em:
- Domain-Driven Design
- Agregados e Entidades
- Value Objects
- Domain Events
- Bounded Contexts
""",
            "code_quality_focus": """
Foque especialmente em:
- Clean Code
- SOLID Principles
- Design Patterns
- Testabilidade
- Manutenibilidade
""",
            "performance_focus": """
Foque especialmente em:
- Performance
- Escalabilidade
- Otimização
- Monitoramento
- Métricas
"""
        }
    
    def detect_query_type(self, query: str) -> QueryType:
        """
        Detecta o tipo de consulta baseado no conteúdo.
        
        Args:
            query: Texto da consulta
            
        Returns:
            Tipo de consulta detectado
        """
        query_lower = query.lower()
        
        # Palavras-chave para cada tipo
        architecture_keywords = [
            "arquitetura", "hexagonal", "ports", "adapters", "camadas",
            "estrutura", "organização", "componentes"
        ]
        
        code_keywords = [
            "código", "implementação", "classe", "método", "função",
            "revisar", "analisar", "refatorar", "melhorar"
        ]
        
        ddd_keywords = [
            "ddd", "domain", "agregado", "entidade", "value object",
            "bounded context", "domain event", "ubiquitous language"
        ]
        
        decision_keywords = [
            "decisão", "escolher", "tecnologia", "framework", "biblioteca",
            "trade-off", "comparar", "avaliar"
        ]
        
        implementation_keywords = [
            "implementar", "criar", "desenvolver", "como fazer",
            "passo a passo", "tutorial", "guia", "desenvolvimento"
        ]
        
        troubleshooting_keywords = [
            "erro", "problema", "bug", "falha", "não funciona",
            "troubleshooting", "debug", "corrigir", "compilação"
        ]
        
        best_practices_keywords = [
            "boa prática", "melhor prática", "padrão", "princípio",
            "clean code", "solid", "design pattern", "boas práticas"
        ]
        
        # Verifica cada tipo (ordem de prioridade)
        if any(keyword in query_lower for keyword in troubleshooting_keywords):
            return QueryType.TROUBLESHOOTING
        elif any(keyword in query_lower for keyword in implementation_keywords):
            return QueryType.IMPLEMENTATION_GUIDE
        elif any(keyword in query_lower for keyword in architecture_keywords):
            return QueryType.ARCHITECTURE
        elif any(keyword in query_lower for keyword in code_keywords):
            return QueryType.CODE_REVIEW
        elif any(keyword in query_lower for keyword in ddd_keywords):
            return QueryType.DDD_CONCEPT
        elif any(keyword in query_lower for keyword in decision_keywords):
            return QueryType.TECHNICAL_DECISION
        elif any(keyword in query_lower for keyword in best_practices_keywords):
            return QueryType.BEST_PRACTICES
        else:
            return QueryType.GENERAL
    
    def enhance_context(self, 
                       query_type: QueryType, 
                       base_context: str,
                       focus_areas: Optional[List[str]] = None) -> str:
        """
        Aprimora o contexto baseado no tipo de consulta.
        
        Args:
            query_type: Tipo de consulta
            base_context: Contexto base
            focus_areas: Áreas de foco específicas
            
        Returns:
            Contexto aprimorado
        """
        enhanced_context = base_context
        
        # Adiciona foco específico baseado no tipo
        if query_type == QueryType.ARCHITECTURE:
            enhanced_context += self.context_enhancers["architecture_focus"]
        elif query_type == QueryType.DDD_CONCEPT:
            enhanced_context += self.context_enhancers["ddd_focus"]
        elif query_type in [QueryType.CODE_REVIEW, QueryType.IMPLEMENTATION_GUIDE]:
            enhanced_context += self.context_enhancers["code_quality_focus"]
        
        # Adiciona focos específicos solicitados
        if focus_areas:
            for focus in focus_areas:
                if focus in self.context_enhancers:
                    enhanced_context += self.context_enhancers[focus]
        
        return enhanced_context
    
    def optimize_prompt(self, 
                       query: str,
                       relevant_docs: str,
                       project_context: str = "",
                       focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Otimiza o prompt para a consulta específica.
        
        Args:
            query: Consulta do usuário
            relevant_docs: Documentos relevantes
            project_context: Contexto do projeto
            focus_areas: Áreas de foco específicas
            
        Returns:
            Prompt otimizado
        """
        # Detecta o tipo de consulta
        query_type = self.detect_query_type(query)
        
        # Obtém o template apropriado
        template = self.templates.get(query_type, self.templates[QueryType.GENERAL])
        
        # Aprimora o contexto
        enhanced_context = self.enhance_context(query_type, project_context, focus_areas)
        
        # Formata o prompt
        prompt_data = template.format(
            query=query,
            relevant_docs=relevant_docs,
            project_context=enhanced_context,
            current_context="",  # Pode ser preenchido dinamicamente
            requirements="",     # Pode ser preenchido dinamicamente
            error_details="",   # Pode ser preenchido dinamicamente
            specific_context="", # Pode ser preenchido dinamicamente
            code_snippet="",    # Pode ser preenchido dinamicamente
            current_implementation=""  # Pode ser preenchido dinamicamente
        )
        
        # Registra métricas
        self._record_metrics(query_type)
        
        return prompt_data
    
    def _record_metrics(self, query_type: QueryType):
        """Registra métricas de uso."""
        self.quality_metrics['total_queries'] += 1
        
        # Atualiza distribuição de tipos de consulta
        type_name = query_type.value
        if type_name not in self.quality_metrics['query_type_distribution']:
            self.quality_metrics['query_type_distribution'][type_name] = 0
        self.quality_metrics['query_type_distribution'][type_name] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de qualidade dos prompts."""
        return self.quality_metrics.copy()
    
    def reset_metrics(self):
        """Reseta as métricas."""
        self.quality_metrics = {
            'total_queries': 0,
            'successful_responses': 0,
            'average_response_length': 0,
            'query_type_distribution': {}
        }

# Instância global do otimizador
prompt_optimizer = PromptOptimizer() 