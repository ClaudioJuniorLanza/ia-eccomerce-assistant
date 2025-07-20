"""
Sistema de análise de impacto para a assistente de IA.
Analisa dependências e impacto de mudanças na base de conhecimento.
"""

import os
import sys
import re
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
from collections import defaultdict

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImpactLevel(Enum):
    """Níveis de impacto das mudanças."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DependencyType(Enum):
    """Tipos de dependências entre documentos."""
    REFERENCE = "reference"  # Referência direta
    IMPORTS = "imports"      # Importação de código
    EXTENDS = "extends"      # Extensão de conceitos
    IMPLEMENTS = "implements" # Implementação
    DEPENDS_ON = "depends_on" # Dependência funcional

@dataclass
class Dependency:
    """Representa uma dependência entre documentos."""
    source_file: str
    target_file: str
    dependency_type: DependencyType
    line_number: Optional[int]
    context: str
    strength: float  # 0.0 a 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        data = asdict(self)
        data['dependency_type'] = self.dependency_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dependency':
        """Cria instância a partir de dicionário."""
        data['dependency_type'] = DependencyType(data['dependency_type'])
        return cls(**data)

@dataclass
class ImpactAnalysis:
    """Resultado da análise de impacto."""
    changed_file: str
    impact_level: ImpactLevel
    affected_files: List[str]
    dependencies: List[Dependency]
    estimated_effort: str  # low, medium, high, critical
    recommendations: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        data = asdict(self)
        data['impact_level'] = self.impact_level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImpactAnalysis':
        """Cria instância a partir de dicionário."""
        data['impact_level'] = ImpactLevel(data['impact_level'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class ImpactAnalyzer:
    """Analisador de impacto de mudanças."""
    
    def __init__(self, base_paths: List[str]):
        """
        Inicializa o analisador de impacto.
        
        Args:
            base_paths: Caminhos da base de conhecimento
        """
        self.base_paths = base_paths
        self.dependency_graph = nx.DiGraph()
        self.file_dependencies: Dict[str, List[Dependency]] = defaultdict(list)
        self.impact_history: List[ImpactAnalysis] = []
        
        # Padrões de detecção de dependências
        self.dependency_patterns = {
            'reference': [
                r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
                r'@([a-zA-Z0-9_-]+)',        # Mentions
                r'see\s+([a-zA-Z0-9_/-]+\.md)',  # See references
            ],
            'imports': [
                r'import\s+([a-zA-Z0-9_.]+)',  # Python imports
                r'from\s+([a-zA-Z0-9_.]+)\s+import',  # Python from imports
                r'require\s+["\']([^"\']+)["\']',  # Node.js requires
            ],
            'extends': [
                r'extends\s+([a-zA-Z0-9_.]+)',  # Class extension
                r'inherits\s+from\s+([a-zA-Z0-9_.]+)',  # Inheritance
            ],
            'implements': [
                r'implements\s+([a-zA-Z0-9_.]+)',  # Interface implementation
                r'interface\s+([a-zA-Z0-9_.]+)',  # Interface definition
            ],
            'depends_on': [
                r'depends\s+on\s+([a-zA-Z0-9_.]+)',  # Explicit dependencies
                r'requires\s+([a-zA-Z0-9_.]+)',  # Requirements
            ]
        }
        
        # Inicializa análise de dependências
        self._build_dependency_graph()
    
    def _build_dependency_graph(self):
        """Constrói o grafo de dependências."""
        logger.info("Construindo grafo de dependências...")
        
        try:
            # Escaneia todos os arquivos
            for base_path in self.base_paths:
                if os.path.exists(base_path):
                    self._scan_directory_for_dependencies(base_path)
            
            # Constrói grafo
            for file_path, dependencies in self.file_dependencies.items():
                for dep in dependencies:
                    self.dependency_graph.add_edge(
                        file_path, 
                        dep.target_file, 
                        weight=dep.strength,
                        dependency_type=dep.dependency_type.value
                    )
            
            logger.info(f"Grafo de dependências construído: {len(self.dependency_graph.nodes)} nós, {len(self.dependency_graph.edges)} arestas")
            
        except Exception as e:
            logger.error(f"Erro ao construir grafo de dependências: {e}")
    
    def _scan_directory_for_dependencies(self, directory: str):
        """Escaneia diretório em busca de dependências."""
        for root, dirs, files in os.walk(directory):
            # Remove diretórios ignorados
            dirs[:] = [d for d in dirs if not self._should_ignore_directory(d)]
            
            for file in files:
                if not self._should_ignore_file(file):
                    file_path = os.path.join(root, file)
                    self._analyze_file_dependencies(file_path)
    
    def _should_ignore_directory(self, dir_name: str) -> bool:
        """Verifica se diretório deve ser ignorado."""
        ignored_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
        return dir_name in ignored_dirs
    
    def _should_ignore_file(self, file_name: str) -> bool:
        """Verifica se arquivo deve ser ignorado."""
        ignored_extensions = {'.pyc', '.pyo', '.log', '.tmp', '.cache'}
        return any(file_name.endswith(ext) for ext in ignored_extensions)
    
    def _analyze_file_dependencies(self, file_path: str):
        """Analisa dependências de um arquivo específico."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = []
            
            # Analisa cada tipo de dependência
            for dep_type, patterns in self.dependency_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        target = match.group(1)
                        target_file = self._resolve_target_file(target, file_path)
                        
                        if target_file and target_file != file_path:
                            dependency = Dependency(
                                source_file=file_path,
                                target_file=target_file,
                                dependency_type=DependencyType(dep_type),
                                line_number=self._get_line_number(content, match.start()),
                                context=match.group(0),
                                strength=self._calculate_dependency_strength(dep_type, match.group(0))
                            )
                            dependencies.append(dependency)
            
            if dependencies:
                self.file_dependencies[file_path] = dependencies
                
        except Exception as e:
            logger.warning(f"Erro ao analisar dependências de {file_path}: {e}")
    
    def _resolve_target_file(self, target: str, source_file: str) -> Optional[str]:
        """Resolve o caminho do arquivo alvo."""
        try:
            # Se é um caminho relativo
            if target.startswith('./') or target.startswith('../'):
                source_dir = os.path.dirname(source_file)
                resolved_path = os.path.normpath(os.path.join(source_dir, target))
                if os.path.exists(resolved_path):
                    return resolved_path
            
            # Se é um nome de arquivo
            elif target.endswith('.md') or target.endswith('.py'):
                # Procura em todos os diretórios base
                for base_path in self.base_paths:
                    potential_path = os.path.join(base_path, target)
                    if os.path.exists(potential_path):
                        return potential_path
                    
                    # Procura recursivamente
                    for root, dirs, files in os.walk(base_path):
                        if target in files:
                            return os.path.join(root, target)
            
            # Se é uma referência por nome
            else:
                # Procura arquivos com esse nome
                for base_path in self.base_paths:
                    for root, dirs, files in os.walk(base_path):
                        for file in files:
                            if file.lower().startswith(target.lower()) or target.lower() in file.lower():
                                return os.path.join(root, file)
            
        except Exception as e:
            logger.warning(f"Erro ao resolver target {target}: {e}")
        
        return None
    
    def _get_line_number(self, content: str, position: int) -> Optional[int]:
        """Obtém número da linha baseado na posição."""
        try:
            return content[:position].count('\n') + 1
        except:
            return None
    
    def _calculate_dependency_strength(self, dep_type: str, context: str) -> float:
        """Calcula força da dependência (0.0 a 1.0)."""
        base_strengths = {
            'reference': 0.3,
            'imports': 0.8,
            'extends': 0.9,
            'implements': 0.9,
            'depends_on': 0.7
        }
        
        base_strength = base_strengths.get(dep_type, 0.5)
        
        # Ajusta baseado no contexto
        if 'critical' in context.lower() or 'essential' in context.lower():
            base_strength *= 1.2
        elif 'optional' in context.lower() or 'maybe' in context.lower():
            base_strength *= 0.8
        
        return min(1.0, base_strength)
    
    def analyze_impact(self, changed_file: str) -> ImpactAnalysis:
        """
        Analisa o impacto de uma mudança em um arquivo.
        
        Args:
            changed_file: Caminho do arquivo que mudou
            
        Returns:
            Análise de impacto
        """
        try:
            logger.info(f"Analisando impacto de mudança em: {changed_file}")
            
            # Encontra arquivos afetados
            affected_files = self._find_affected_files(changed_file)
            
            # Calcula nível de impacto
            impact_level = self._calculate_impact_level(changed_file, affected_files)
            
            # Obtém dependências relacionadas
            dependencies = self._get_related_dependencies(changed_file)
            
            # Estima esforço
            estimated_effort = self._estimate_effort(impact_level, len(affected_files))
            
            # Gera recomendações
            recommendations = self._generate_recommendations(changed_file, impact_level, affected_files)
            
            # Cria análise
            analysis = ImpactAnalysis(
                changed_file=changed_file,
                impact_level=impact_level,
                affected_files=affected_files,
                dependencies=dependencies,
                estimated_effort=estimated_effort,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
            # Adiciona ao histórico
            self.impact_history.append(analysis)
            
            logger.info(f"Análise de impacto concluída: {impact_level.value} - {len(affected_files)} arquivos afetados")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar impacto: {e}")
            raise
    
    def _find_affected_files(self, changed_file: str) -> List[str]:
        """Encontra arquivos afetados pela mudança."""
        affected_files = set()
        
        try:
            # Usa o grafo de dependências para encontrar arquivos afetados
            if changed_file in self.dependency_graph:
                # Encontra todos os nós que dependem do arquivo mudado
                descendants = nx.descendants(self.dependency_graph, changed_file)
                affected_files.update(descendants)
                
                # Também inclui o próprio arquivo
                affected_files.add(changed_file)
            
            # Busca por referências reversas
            for file_path, deps in self.file_dependencies.items():
                for dep in deps:
                    if dep.target_file == changed_file:
                        affected_files.add(file_path)
            
        except Exception as e:
            logger.error(f"Erro ao encontrar arquivos afetados: {e}")
        
        return list(affected_files)
    
    def _calculate_impact_level(self, changed_file: str, affected_files: List[str]) -> ImpactLevel:
        """Calcula o nível de impacto da mudança."""
        try:
            # Fatores para cálculo de impacto
            num_affected = len(affected_files)
            file_type = self._get_file_type(changed_file)
            dependency_count = len(self.file_dependencies.get(changed_file, []))
            
            # Pontuação base
            score = 0
            
            # Número de arquivos afetados
            if num_affected <= 2:
                score += 1
            elif num_affected <= 5:
                score += 2
            elif num_affected <= 10:
                score += 3
            else:
                score += 4
            
            # Tipo de arquivo
            if file_type in ['adr', 'architecture']:
                score += 3  # ADRs têm alto impacto
            elif file_type in ['ddd', 'domain']:
                score += 2  # Conceitos de domínio têm impacto médio-alto
            elif file_type in ['implementation', 'code']:
                score += 1  # Código tem impacto variável
            
            # Número de dependências
            if dependency_count <= 2:
                score += 1
            elif dependency_count <= 5:
                score += 2
            else:
                score += 3
            
            # Determina nível de impacto
            if score <= 3:
                return ImpactLevel.LOW
            elif score <= 5:
                return ImpactLevel.MEDIUM
            elif score <= 7:
                return ImpactLevel.HIGH
            else:
                return ImpactLevel.CRITICAL
                
        except Exception as e:
            logger.error(f"Erro ao calcular nível de impacto: {e}")
            return ImpactLevel.MEDIUM
    
    def _get_file_type(self, file_path: str) -> str:
        """Determina o tipo do arquivo baseado no nome e conteúdo."""
        file_name = os.path.basename(file_path).lower()
        
        if 'adr' in file_name:
            return 'adr'
        elif 'ddd' in file_name or 'domain' in file_name:
            return 'ddd'
        elif file_name.endswith('.py'):
            return 'code'
        elif file_name.endswith('.md'):
            return 'documentation'
        else:
            return 'other'
    
    def _get_related_dependencies(self, changed_file: str) -> List[Dependency]:
        """Obtém dependências relacionadas ao arquivo mudado."""
        dependencies = []
        
        # Dependências do arquivo mudado
        dependencies.extend(self.file_dependencies.get(changed_file, []))
        
        # Dependências que apontam para o arquivo mudado
        for file_path, deps in self.file_dependencies.items():
            for dep in deps:
                if dep.target_file == changed_file:
                    dependencies.append(dep)
        
        return dependencies
    
    def _estimate_effort(self, impact_level: ImpactLevel, num_affected: int) -> str:
        """Estima o esforço necessário para a mudança."""
        if impact_level == ImpactLevel.CRITICAL:
            return "critical"
        elif impact_level == ImpactLevel.HIGH or num_affected > 5:
            return "high"
        elif impact_level == ImpactLevel.MEDIUM or num_affected > 2:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, changed_file: str, impact_level: ImpactLevel, affected_files: List[str]) -> List[str]:
        """Gera recomendações baseadas na análise de impacto."""
        recommendations = []
        
        if impact_level == ImpactLevel.CRITICAL:
            recommendations.extend([
                "🔴 MUDANÇA CRÍTICA: Revisar todas as dependências antes de prosseguir",
                "📋 Criar plano de migração detalhado",
                "🧪 Executar testes completos em todos os arquivos afetados",
                "👥 Coordenar com toda a equipe antes da implementação"
            ])
        elif impact_level == ImpactLevel.HIGH:
            recommendations.extend([
                "🟡 IMPACTO ALTO: Verificar dependências principais",
                "📝 Documentar mudanças em detalhes",
                "🧪 Testar arquivos mais afetados",
                "👥 Notificar equipe sobre mudanças"
            ])
        elif impact_level == ImpactLevel.MEDIUM:
            recommendations.extend([
                "🟢 IMPACTO MÉDIO: Revisar dependências locais",
                "📝 Atualizar documentação relacionada",
                "🧪 Testar funcionalidades afetadas"
            ])
        else:
            recommendations.extend([
                "🟢 IMPACTO BAIXO: Mudança localizada",
                "📝 Atualizar documentação se necessário"
            ])
        
        # Recomendações específicas baseadas no número de arquivos afetados
        if len(affected_files) > 10:
            recommendations.append("⚠️ Muitos arquivos afetados - considere refatoração incremental")
        elif len(affected_files) > 5:
            recommendations.append("📋 Criar checklist de arquivos para atualizar")
        
        return recommendations
    
    def get_impact_history(self, limit: int = 50) -> List[ImpactAnalysis]:
        """Obtém histórico de análises de impacto."""
        return self.impact_history[-limit:]
    
    def get_dependency_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do grafo de dependências."""
        try:
            return {
                'total_files': len(self.dependency_graph.nodes),
                'total_dependencies': len(self.dependency_graph.edges),
                'strongest_dependencies': self._get_strongest_dependencies(),
                'most_referenced_files': self._get_most_referenced_files(),
                'dependency_types': self._get_dependency_type_stats()
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def _get_strongest_dependencies(self) -> List[Tuple[str, str, float]]:
        """Obtém as dependências mais fortes."""
        try:
            edges = self.dependency_graph.edges(data=True)
            sorted_edges = sorted(edges, key=lambda x: x[2].get('weight', 0), reverse=True)
            return [(u, v, d.get('weight', 0)) for u, v, d in sorted_edges[:10]]
        except:
            return []
    
    def _get_most_referenced_files(self) -> List[Tuple[str, int]]:
        """Obtém os arquivos mais referenciados."""
        try:
            in_degrees = dict(self.dependency_graph.in_degree())
            sorted_files = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
            return sorted_files[:10]
        except:
            return []
    
    def _get_dependency_type_stats(self) -> Dict[str, int]:
        """Obtém estatísticas por tipo de dependência."""
        try:
            type_counts = defaultdict(int)
            for _, _, data in self.dependency_graph.edges(data=True):
                dep_type = data.get('dependency_type', 'unknown')
                type_counts[dep_type] += 1
            return dict(type_counts)
        except:
            return {}

# Instância global do analisador de impacto
impact_analyzer = None 