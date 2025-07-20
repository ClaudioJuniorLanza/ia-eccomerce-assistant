"""
Sistema de sugestões proativas para a assistente de IA.
Analisa padrões de uso e gera sugestões inteligentes.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import re

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuggestionType(Enum):
    """Tipos de sugestões proativas."""
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    CACHE_OPTIMIZATION = "cache_optimization"
    KNOWLEDGE_GAP = "knowledge_gap"
    USAGE_PATTERN = "usage_pattern"

class SuggestionPriority(Enum):
    """Prioridades das sugestões."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ProactiveSuggestion:
    """Sugestão proativa gerada pelo sistema."""
    suggestion_type: SuggestionType
    priority: SuggestionPriority
    title: str
    description: str
    reasoning: str
    actionable_items: List[str]
    estimated_impact: str  # low, medium, high, critical
    timestamp: datetime
    confidence: float  # 0.0 a 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        data = asdict(self)
        data['suggestion_type'] = self.suggestion_type.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProactiveSuggestion':
        """Cria instância a partir de dicionário."""
        data['suggestion_type'] = SuggestionType(data['suggestion_type'])
        data['priority'] = SuggestionPriority(data['priority'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class UsagePattern:
    """Padrão de uso detectado."""
    
    def __init__(self, pattern_type: str, frequency: int, context: str):
        self.pattern_type = pattern_type
        self.frequency = frequency
        self.context = context
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
    
    def update_frequency(self):
        """Atualiza frequência e timestamp."""
        self.frequency += 1
        self.last_seen = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'pattern_type': self.pattern_type,
            'frequency': self.frequency,
            'context': self.context,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat()
        }

class ProactiveSuggestionEngine:
    """Motor de sugestões proativas."""
    
    def __init__(self, 
                 cache_manager=None,
                 change_detector=None,
                 impact_analyzer=None):
        """
        Inicializa o motor de sugestões proativas.
        
        Args:
            cache_manager: Gerenciador de cache para análise
            change_detector: Detector de mudanças para análise
            impact_analyzer: Analisador de impacto para análise
        """
        self.cache_manager = cache_manager
        self.change_detector = change_detector
        self.impact_analyzer = impact_analyzer
        
        # Dados de análise
        self.query_history: List[Dict[str, Any]] = []
        self.cache_stats_history: List[Dict[str, Any]] = []
        self.change_history: List[Dict[str, Any]] = []
        self.usage_patterns: Dict[str, UsagePattern] = {}
        
        # Configurações de análise
        self.analysis_thresholds = {
            'cache_hit_rate_low': 0.3,
            'cache_hit_rate_medium': 0.5,
            'frequent_query_threshold': 5,
            'performance_threshold_ms': 2000,
            'documentation_gap_threshold': 0.2
        }
        
        # Histórico de sugestões
        self.suggestions_history: List[ProactiveSuggestion] = []
        
        # Padrões de detecção
        self.pattern_detectors = {
            'performance': self._detect_performance_patterns,
            'documentation': self._detect_documentation_patterns,
            'architecture': self._detect_architecture_patterns,
            'cache': self._detect_cache_patterns,
            'knowledge': self._detect_knowledge_gaps,
            'usage': self._detect_usage_patterns
        }
    
    def record_query(self, query: str, response_time: float, cache_hit: bool, 
                    query_type: str = None, tokens_used: int = None):
        """
        Registra uma consulta para análise.
        
        Args:
            query: Consulta realizada
            response_time: Tempo de resposta em ms
            cache_hit: Se foi cache hit
            query_type: Tipo da consulta
            tokens_used: Tokens utilizados
        """
        query_data = {
            'query': query,
            'response_time': response_time,
            'cache_hit': cache_hit,
            'query_type': query_type,
            'tokens_used': tokens_used,
            'timestamp': datetime.now()
        }
        
        self.query_history.append(query_data)
        
        # Limita histórico
        if len(self.query_history) > 1000:
            self.query_history = self.query_history[-1000:]
        
        # Atualiza padrões de uso
        self._update_usage_patterns(query, query_type)
    
    def record_cache_stats(self, stats: Dict[str, Any]):
        """Registra estatísticas de cache."""
        stats['timestamp'] = datetime.now()
        self.cache_stats_history.append(stats)
        
        # Limita histórico
        if len(self.cache_stats_history) > 100:
            self.cache_stats_history = self.cache_stats_history[-100:]
    
    def record_change_event(self, change_event: Dict[str, Any]):
        """Registra evento de mudança."""
        change_event['timestamp'] = datetime.now()
        self.change_history.append(change_event)
        
        # Limita histórico
        if len(self.change_history) > 100:
            self.change_history = self.change_history[-100:]
    
    def _update_usage_patterns(self, query: str, query_type: str):
        """Atualiza padrões de uso baseado na consulta."""
        # Extrai palavras-chave da consulta
        keywords = self._extract_keywords(query)
        
        for keyword in keywords:
            pattern_key = f"{query_type}_{keyword}"
            
            if pattern_key in self.usage_patterns:
                self.usage_patterns[pattern_key].update_frequency()
            else:
                self.usage_patterns[pattern_key] = UsagePattern(
                    pattern_type=query_type,
                    frequency=1,
                    context=keyword
                )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave da consulta."""
        # Remove palavras comuns
        stop_words = {'como', 'qual', 'quando', 'onde', 'por', 'que', 'é', 'são', 'está', 'estão'}
        
        # Extrai palavras relevantes
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Limita a 5 palavras-chave
    
    def generate_suggestions(self) -> List[ProactiveSuggestion]:
        """
        Gera sugestões proativas baseadas na análise de dados.
        
        Returns:
            Lista de sugestões proativas
        """
        suggestions = []
        
        try:
            # Analisa diferentes aspectos
            for detector_name, detector_func in self.pattern_detectors.items():
                detector_suggestions = detector_func()
                suggestions.extend(detector_suggestions)
            
            # Filtra sugestões duplicadas e ordena por prioridade
            suggestions = self._filter_and_rank_suggestions(suggestions)
            
            # Adiciona ao histórico
            self.suggestions_history.extend(suggestions)
            
            logger.info(f"Geradas {len(suggestions)} sugestões proativas")
            
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões: {e}")
        
        return suggestions
    
    def _detect_performance_patterns(self) -> List[ProactiveSuggestion]:
        """Detecta padrões de performance."""
        suggestions = []
        
        if not self.query_history:
            return suggestions
        
        # Analisa tempo de resposta
        recent_queries = [q for q in self.query_history 
                         if q['timestamp'] > datetime.now() - timedelta(hours=24)]
        
        if recent_queries:
            avg_response_time = sum(q['response_time'] for q in recent_queries) / len(recent_queries)
            slow_queries = [q for q in recent_queries if q['response_time'] > self.analysis_thresholds['performance_threshold_ms']]
            
            if avg_response_time > self.analysis_thresholds['performance_threshold_ms']:
                suggestions.append(ProactiveSuggestion(
                    suggestion_type=SuggestionType.PERFORMANCE,
                    priority=SuggestionPriority.HIGH,
                    title="Performance de Consultas Lenta",
                    description=f"Tempo médio de resposta: {avg_response_time:.0f}ms",
                    reasoning=f"Detectadas {len(slow_queries)} consultas lentas nas últimas 24h",
                    actionable_items=[
                        "🔧 Otimizar prompts para consultas frequentes",
                        "💾 Implementar cache mais agressivo",
                        "📊 Monitorar consultas específicas"
                    ],
                    estimated_impact="high",
                    timestamp=datetime.now(),
                    confidence=0.8
                ))
        
        return suggestions
    
    def _detect_documentation_patterns(self) -> List[ProactiveSuggestion]:
        """Detecta padrões relacionados à documentação."""
        suggestions = []
        
        if not self.query_history:
            return suggestions
        
        # Analisa consultas sobre documentação
        doc_queries = [q for q in self.query_history 
                      if any(word in q['query'].lower() for word in ['documentação', 'docs', 'como', 'guia'])]
        
        if len(doc_queries) > len(self.query_history) * self.analysis_thresholds['documentation_gap_threshold']:
            suggestions.append(ProactiveSuggestion(
                suggestion_type=SuggestionType.DOCUMENTATION,
                priority=SuggestionPriority.MEDIUM,
                title="Gap de Documentação Detectado",
                description=f"{len(doc_queries)} consultas sobre documentação",
                reasoning="Muitas consultas sobre como fazer coisas básicas",
                actionable_items=[
                    "📚 Criar guias de uso mais detalhados",
                    "🎯 Melhorar documentação de ADRs",
                    "📖 Adicionar exemplos práticos"
                ],
                estimated_impact="medium",
                timestamp=datetime.now(),
                confidence=0.7
            ))
        
        return suggestions
    
    def _detect_architecture_patterns(self) -> List[ProactiveSuggestion]:
        """Detecta padrões arquiteturais."""
        suggestions = []
        
        if not self.query_history:
            return suggestions
        
        # Analisa consultas sobre arquitetura
        arch_queries = [q for q in self.query_history 
                       if any(word in q['query'].lower() for word in ['arquitetura', 'adr', 'ddd', 'hexagonal'])]
        
        if arch_queries:
            # Verifica se há muitas consultas sobre o mesmo tópico
            arch_topics = Counter()
            for query in arch_queries:
                keywords = self._extract_keywords(query['query'])
                arch_topics.update(keywords)
            
            most_common = arch_topics.most_common(1)[0]
            if most_common[1] > self.analysis_thresholds['frequent_query_threshold']:
                suggestions.append(ProactiveSuggestion(
                    suggestion_type=SuggestionType.ARCHITECTURE,
                    priority=SuggestionPriority.HIGH,
                    title=f"Foco em Arquitetura: {most_common[0]}",
                    description=f"{most_common[1]} consultas sobre {most_common[0]}",
                    reasoning="Muitas consultas sobre o mesmo aspecto arquitetural",
                    actionable_items=[
                        f"📋 Criar ADR específico sobre {most_common[0]}",
                        "🎯 Melhorar documentação arquitetural",
                        "📊 Analisar padrões de decisão"
                    ],
                    estimated_impact="high",
                    timestamp=datetime.now(),
                    confidence=0.9
                ))
        
        return suggestions
    
    def _detect_cache_patterns(self) -> List[ProactiveSuggestion]:
        """Detecta padrões de cache."""
        suggestions = []
        
        if not self.cache_stats_history:
            return suggestions
        
        # Analisa hit rate do cache
        recent_stats = [s for s in self.cache_stats_history 
                       if s['timestamp'] > datetime.now() - timedelta(hours=24)]
        
        if recent_stats:
            avg_hit_rate = sum(s.get('hit_rate', 0) for s in recent_stats) / len(recent_stats)
            
            if avg_hit_rate < self.analysis_thresholds['cache_hit_rate_low']:
                suggestions.append(ProactiveSuggestion(
                    suggestion_type=SuggestionType.CACHE_OPTIMIZATION,
                    priority=SuggestionPriority.CRITICAL,
                    title="Cache Hit Rate Muito Baixo",
                    description=f"Hit rate médio: {avg_hit_rate:.1%}",
                    reasoning="Cache não está sendo efetivo",
                    actionable_items=[
                        "🔧 Ajustar estratégias de cache",
                        "📊 Analisar padrões de consulta",
                        "💾 Implementar cache mais inteligente"
                    ],
                    estimated_impact="critical",
                    timestamp=datetime.now(),
                    confidence=0.9
                ))
            elif avg_hit_rate < self.analysis_thresholds['cache_hit_rate_medium']:
                suggestions.append(ProactiveSuggestion(
                    suggestion_type=SuggestionType.CACHE_OPTIMIZATION,
                    priority=SuggestionPriority.MEDIUM,
                    title="Oportunidade de Melhoria no Cache",
                    description=f"Hit rate médio: {avg_hit_rate:.1%}",
                    reasoning="Cache pode ser otimizado",
                    actionable_items=[
                        "📈 Analisar consultas frequentes",
                        "🔍 Identificar padrões de cache miss",
                        "⚡ Otimizar estratégias de cache"
                    ],
                    estimated_impact="medium",
                    timestamp=datetime.now(),
                    confidence=0.7
                ))
        
        return suggestions
    
    def _detect_knowledge_gaps(self) -> List[ProactiveSuggestion]:
        """Detecta gaps de conhecimento."""
        suggestions = []
        
        if not self.query_history:
            return suggestions
        
        # Analisa consultas sem resposta satisfatória
        recent_queries = [q for q in self.query_history 
                         if q['timestamp'] > datetime.now() - timedelta(hours=24)]
        
        # Simula detecção de gaps (em implementação real, seria baseado em feedback)
        if len(recent_queries) > 10:
            # Identifica tópicos frequentes
            topics = Counter()
            for query in recent_queries:
                keywords = self._extract_keywords(query['query'])
                topics.update(keywords)
            
            # Identifica tópicos com pouca documentação
            potential_gaps = [topic for topic, count in topics.most_common(5) 
                            if count > 2 and topic not in ['como', 'qual', 'quando']]
            
            if potential_gaps:
                suggestions.append(ProactiveSuggestion(
                    suggestion_type=SuggestionType.KNOWLEDGE_GAP,
                    priority=SuggestionPriority.MEDIUM,
                    title="Possível Gap de Conhecimento",
                    description=f"Tópicos frequentes: {', '.join(potential_gaps[:3])}",
                    reasoning="Consultas frequentes sobre tópicos específicos",
                    actionable_items=[
                        "📚 Expandir documentação sobre tópicos identificados",
                        "🎯 Criar guias específicos",
                        "📖 Adicionar exemplos práticos"
                    ],
                    estimated_impact="medium",
                    timestamp=datetime.now(),
                    confidence=0.6
                ))
        
        return suggestions
    
    def _detect_usage_patterns(self) -> List[ProactiveSuggestion]:
        """Detecta padrões de uso."""
        suggestions = []
        
        if not self.usage_patterns:
            return suggestions
        
        # Analisa padrões de uso frequentes
        frequent_patterns = [pattern for pattern in self.usage_patterns.values() 
                           if pattern.frequency > self.analysis_thresholds['frequent_query_threshold']]
        
        if frequent_patterns:
            most_frequent = max(frequent_patterns, key=lambda p: p.frequency)
            
            suggestions.append(ProactiveSuggestion(
                suggestion_type=SuggestionType.USAGE_PATTERN,
                priority=SuggestionPriority.MEDIUM,
                title=f"Padrão de Uso Detectado: {most_frequent.context}",
                description=f"{most_frequent.frequency} consultas sobre {most_frequent.context}",
                reasoning="Padrão de uso consistente identificado",
                actionable_items=[
                    f"📋 Criar atalho para consultas sobre {most_frequent.context}",
                    "🎯 Otimizar respostas para este padrão",
                    "📊 Monitorar evolução do padrão"
                ],
                estimated_impact="medium",
                timestamp=datetime.now(),
                confidence=0.8
            ))
        
        return suggestions
    
    def _filter_and_rank_suggestions(self, suggestions: List[ProactiveSuggestion]) -> List[ProactiveSuggestion]:
        """Filtra e ordena sugestões."""
        # Remove duplicatas baseadas no tipo e título
        seen = set()
        filtered = []
        
        for suggestion in suggestions:
            key = (suggestion.suggestion_type, suggestion.title)
            if key not in seen:
                seen.add(key)
                filtered.append(suggestion)
        
        # Ordena por prioridade e confiança
        priority_order = {
            SuggestionPriority.CRITICAL: 4,
            SuggestionPriority.HIGH: 3,
            SuggestionPriority.MEDIUM: 2,
            SuggestionPriority.LOW: 1
        }
        
        filtered.sort(key=lambda s: (priority_order[s.priority], s.confidence), reverse=True)
        
        return filtered[:10]  # Retorna apenas as 10 melhores
    
    def get_suggestions_history(self, limit: int = 50) -> List[ProactiveSuggestion]:
        """Obtém histórico de sugestões."""
        return self.suggestions_history[-limit:]
    
    def get_usage_analytics(self) -> Dict[str, Any]:
        """Obtém analytics de uso."""
        try:
            if not self.query_history:
                return {}
            
            recent_queries = [q for q in self.query_history 
                             if q['timestamp'] > datetime.now() - timedelta(hours=24)]
            
            return {
                'total_queries': len(self.query_history),
                'recent_queries': len(recent_queries),
                'avg_response_time': sum(q['response_time'] for q in recent_queries) / len(recent_queries) if recent_queries else 0,
                'cache_hit_rate': sum(1 for q in recent_queries if q['cache_hit']) / len(recent_queries) if recent_queries else 0,
                'top_patterns': sorted(self.usage_patterns.values(), key=lambda p: p.frequency, reverse=True)[:5],
                'suggestions_generated': len(self.suggestions_history)
            }
        except Exception as e:
            logger.error(f"Erro ao obter analytics: {e}")
            return {}

# Instância global do motor de sugestões
suggestion_engine = None 