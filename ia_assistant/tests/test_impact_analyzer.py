"""
Testes para o sistema de análise de impacto.
Valida análise de dependências e impacto de mudanças.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.analysis.impact_analyzer import (
    ImpactAnalyzer, 
    ImpactLevel, 
    DependencyType,
    Dependency,
    ImpactAnalysis
)

class TestImpactAnalyzer(unittest.TestCase):
    """Testes para o analisador de impacto."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = os.path.join(self.temp_dir, "test_knowledge_base")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Cria arquivos de teste com dependências
        self.test_files = {
            "adr_001.md": "# ADR 001: Arquitetura Hexagonal\n\nVeja também [ADR 002](adr_002.md).",
            "adr_002.md": "# ADR 002: DDD\n\nImplementa [conceitos DDD](ddd_concepts.md).",
            "ddd_concepts.md": "# DDD Concepts\n\nBaseado em [ADR 001](adr_001.md).",
            "implementation.py": "# Implementation\nimport adr_001\nfrom ddd_concepts import DomainModel"
        }
        
        for filename, content in self.test_files.items():
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Inicializa analisador
        self.analyzer = ImpactAnalyzer([self.test_dir])
    
    def tearDown(self):
        """Limpeza após os testes."""
        shutil.rmtree(self.temp_dir)
    
    def test_analyzer_initialization(self):
        """Testa inicialização do analisador."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.base_paths), 1)
        self.assertIsNotNone(self.analyzer.dependency_graph)
    
    def test_dependency_detection(self):
        """Testa detecção de dependências."""
        # Verifica se dependências foram detectadas
        self.assertGreater(len(self.analyzer.file_dependencies), 0)
        
        # Verifica se grafo foi construído
        self.assertGreater(len(self.analyzer.dependency_graph.nodes), 0)
        self.assertGreater(len(self.analyzer.dependency_graph.edges), 0)
    
    def test_impact_analysis(self):
        """Testa análise de impacto."""
        # Analisa impacto de mudança em ADR
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        analysis = self.analyzer.analyze_impact(adr_file)
        
        self.assertIsInstance(analysis, ImpactAnalysis)
        self.assertEqual(analysis.changed_file, adr_file)
        self.assertIsInstance(analysis.impact_level, ImpactLevel)
        self.assertIsInstance(analysis.affected_files, list)
        self.assertIsInstance(analysis.recommendations, list)
    
    def test_impact_level_calculation(self):
        """Testa cálculo de nível de impacto."""
        # Testa arquivo ADR (alto impacto)
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        analysis = self.analyzer.analyze_impact(adr_file)
        
        # ADRs devem ter impacto médio ou alto
        self.assertIn(analysis.impact_level, [ImpactLevel.MEDIUM, ImpactLevel.HIGH, ImpactLevel.CRITICAL])
        
        # Testa arquivo de implementação (impacto menor)
        impl_file = os.path.join(self.test_dir, "implementation.py")
        analysis = self.analyzer.analyze_impact(impl_file)
        
        # Código pode ter impacto variável
        self.assertIsInstance(analysis.impact_level, ImpactLevel)
    
    def test_affected_files_detection(self):
        """Testa detecção de arquivos afetados."""
        # Modifica arquivo ADR que é referenciado por outros
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        analysis = self.analyzer.analyze_impact(adr_file)
        
        # Deve encontrar arquivos que dependem do ADR
        self.assertGreater(len(analysis.affected_files), 0)
        self.assertIn(adr_file, analysis.affected_files)
    
    def test_dependency_strength_calculation(self):
        """Testa cálculo de força de dependência."""
        # Testa diferentes tipos de dependência
        strength = self.analyzer._calculate_dependency_strength('imports', 'import adr_001')
        self.assertGreater(strength, 0.5)  # Imports têm força alta
        
        strength = self.analyzer._calculate_dependency_strength('reference', '[ADR 001](adr_001.md)')
        self.assertLess(strength, 0.5)  # Referências têm força menor
    
    def test_recommendations_generation(self):
        """Testa geração de recomendações."""
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        analysis = self.analyzer.analyze_impact(adr_file)
        
        # Deve gerar recomendações
        self.assertIsInstance(analysis.recommendations, list)
        self.assertGreater(len(analysis.recommendations), 0)
        
        # Verifica se recomendações contêm informações úteis
        recommendations_text = ' '.join(analysis.recommendations)
        self.assertIn('impact', recommendations_text.lower())
    
    def test_effort_estimation(self):
        """Testa estimativa de esforço."""
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        analysis = self.analyzer.analyze_impact(adr_file)
        
        # Deve estimar esforço
        self.assertIn(analysis.estimated_effort, ['low', 'medium', 'high', 'critical'])
    
    def test_file_type_detection(self):
        """Testa detecção de tipo de arquivo."""
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        file_type = self.analyzer._get_file_type(adr_file)
        self.assertEqual(file_type, 'adr')
        
        impl_file = os.path.join(self.test_dir, "implementation.py")
        file_type = self.analyzer._get_file_type(impl_file)
        self.assertEqual(file_type, 'code')
    
    def test_dependency_resolution(self):
        """Testa resolução de dependências."""
        # Testa resolução de arquivo existente
        target = self.analyzer._resolve_target_file("adr_001.md", os.path.join(self.test_dir, "test.md"))
        self.assertIsNotNone(target)
        self.assertTrue(os.path.exists(target))
        
        # Testa resolução de arquivo inexistente
        target = self.analyzer._resolve_target_file("nonexistent.md", os.path.join(self.test_dir, "test.md"))
        self.assertIsNone(target)
    
    def test_impact_history(self):
        """Testa histórico de análises de impacto."""
        # Realiza algumas análises
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        self.analyzer.analyze_impact(adr_file)
        
        impl_file = os.path.join(self.test_dir, "implementation.py")
        self.analyzer.analyze_impact(impl_file)
        
        # Verifica histórico
        history = self.analyzer.get_impact_history()
        self.assertGreater(len(history), 0)
        self.assertLessEqual(len(history), 50)  # Limite padrão
    
    def test_dependency_stats(self):
        """Testa estatísticas de dependências."""
        stats = self.analyzer.get_dependency_stats()
        
        self.assertIn('total_files', stats)
        self.assertIn('total_dependencies', stats)
        self.assertIn('strongest_dependencies', stats)
        self.assertIn('most_referenced_files', stats)
        self.assertIn('dependency_types', stats)
    
    def test_ignore_patterns(self):
        """Testa padrões de ignorar arquivos."""
        # Testa diretórios ignorados
        self.assertTrue(self.analyzer._should_ignore_directory('.git'))
        self.assertTrue(self.analyzer._should_ignore_directory('__pycache__'))
        self.assertFalse(self.analyzer._should_ignore_directory('docs'))
        
        # Testa arquivos ignorados
        self.assertTrue(self.analyzer._should_ignore_file('test.pyc'))
        self.assertTrue(self.analyzer._should_ignore_file('test.log'))
        self.assertFalse(self.analyzer._should_ignore_file('test.md'))
        self.assertFalse(self.analyzer._should_ignore_file('test.py'))
    
    def test_serialization(self):
        """Testa serialização de objetos."""
        # Testa Dependency
        dependency = Dependency(
            source_file="test1.md",
            target_file="test2.md",
            dependency_type=DependencyType.REFERENCE,
            line_number=10,
            context="[test](test2.md)",
            strength=0.5
        )
        
        data = dependency.to_dict()
        new_dependency = Dependency.from_dict(data)
        
        self.assertEqual(dependency.source_file, new_dependency.source_file)
        self.assertEqual(dependency.dependency_type, new_dependency.dependency_type)
        self.assertEqual(dependency.strength, new_dependency.strength)
        
        # Testa ImpactAnalysis
        analysis = ImpactAnalysis(
            changed_file="test.md",
            impact_level=ImpactLevel.MEDIUM,
            affected_files=["test1.md", "test2.md"],
            dependencies=[dependency],
            estimated_effort="medium",
            recommendations=["Test recommendation"],
            timestamp=datetime.now()
        )
        
        data = analysis.to_dict()
        new_analysis = ImpactAnalysis.from_dict(data)
        
        self.assertEqual(analysis.changed_file, new_analysis.changed_file)
        self.assertEqual(analysis.impact_level, new_analysis.impact_level)
        self.assertEqual(len(analysis.affected_files), len(new_analysis.affected_files))

if __name__ == '__main__':
    unittest.main() 