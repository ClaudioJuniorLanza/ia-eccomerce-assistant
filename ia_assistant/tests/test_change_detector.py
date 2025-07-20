"""
Testes para o sistema de detecção automática de mudanças.
Valida monitoramento de arquivos e invalidação de cache.
"""

import os
import sys
import unittest
import tempfile
import shutil
import time
from unittest.mock import patch, MagicMock
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ia_assistant.monitoring.change_detector import (
    KnowledgeBaseMonitor, 
    ChangeEvent, 
    ChangeType
)

class TestChangeDetector(unittest.TestCase):
    """Testes para o sistema de detecção de mudanças."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = os.path.join(self.temp_dir, "test_monitor")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Cria alguns arquivos de teste
        self.test_files = {
            "test1.md": "# Teste 1\nConteúdo inicial",
            "test2.py": "# Teste 2\nCódigo inicial",
            "adr_001.md": "# ADR 001\nArquitetura hexagonal"
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write(content)
        
        # Mock do cache manager
        self.mock_cache_manager = MagicMock()
        
        # Configurações de teste
        self.test_config = {
            'base_paths': [self.test_dir],
            'cache_manager': self.mock_cache_manager,
            'check_interval': 1  # 1 segundo para testes
        }
        
        self.monitor = KnowledgeBaseMonitor(**self.test_config)
    
    def tearDown(self):
        """Limpeza após os testes."""
        if hasattr(self, 'monitor') and self.monitor.monitoring:
            self.monitor.stop_monitoring()
        shutil.rmtree(self.temp_dir)
    
    def test_monitor_initialization(self):
        """Testa inicialização do monitor."""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(len(self.monitor.file_hashes), 3)
        self.assertEqual(len(self.monitor.content_hashes), 3)
        self.assertIsNotNone(self.monitor.structure_hash)
    
    def test_file_hash_calculation(self):
        """Testa cálculo de hash de arquivo."""
        test_file = os.path.join(self.test_dir, "test1.md")
        
        file_hash = self.monitor._calculate_file_hash(test_file)
        content_hash = self.monitor._calculate_content_hash(test_file)
        
        self.assertIsInstance(file_hash, str)
        self.assertIsInstance(content_hash, str)
        self.assertNotEqual(file_hash, "")
        self.assertNotEqual(content_hash, "")
    
    def test_should_ignore_file(self):
        """Testa detecção de arquivos ignorados."""
        # Arquivos que devem ser ignorados
        ignored_files = [
            "test.pyc",
            "test.pyo",
            "__pycache__/test.py",
            ".git/config",
            ".DS_Store",
            "test.tmp"
        ]
        
        for file_path in ignored_files:
            self.assertTrue(self.monitor._should_ignore_file(file_path))
        
        # Arquivos que não devem ser ignorados
        valid_files = [
            "test.md",
            "test.py",
            "test.txt",
            "adr_001.md"
        ]
        
        for file_path in valid_files:
            self.assertFalse(self.monitor._should_ignore_file(file_path))
    
    def test_detect_file_changes(self):
        """Testa detecção de mudanças em arquivos."""
        # Verifica estado inicial
        initial_changes = self.monitor._detect_file_changes()
        self.assertEqual(len(initial_changes), 0)
        
        # Modifica um arquivo
        test_file = os.path.join(self.test_dir, "test1.md")
        with open(test_file, 'w') as f:
            f.write("# Teste 1\nConteúdo modificado")
        
        # Detecta mudanças
        changes = self.monitor._detect_file_changes()
        
        self.assertGreater(len(changes), 0)
        self.assertEqual(changes[0].change_type, ChangeType.CONTENT_CHANGED)
        self.assertEqual(changes[0].file_path, test_file)
    
    def test_detect_new_file(self):
        """Testa detecção de novo arquivo."""
        # Cria novo arquivo
        new_file = os.path.join(self.test_dir, "new_test.md")
        with open(new_file, 'w') as f:
            f.write("# Novo arquivo")
        
        # Detecta mudanças
        changes = self.monitor._detect_file_changes()
        
        self.assertGreater(len(changes), 0)
        new_file_changes = [c for c in changes if c.change_type == ChangeType.FILE_ADDED]
        self.assertGreater(len(new_file_changes), 0)
    
    def test_detect_deleted_file(self):
        """Testa detecção de arquivo deletado."""
        # Remove arquivo
        test_file = os.path.join(self.test_dir, "test1.md")
        os.remove(test_file)
        
        # Detecta mudanças
        changes = self.monitor._detect_file_changes()
        
        self.assertGreater(len(changes), 0)
        deleted_file_changes = [c for c in changes if c.change_type == ChangeType.FILE_DELETED]
        self.assertGreater(len(deleted_file_changes), 0)
    
    def test_cache_invalidation_on_content_change(self):
        """Testa invalidação de cache quando conteúdo muda."""
        # Modifica arquivo ADR
        adr_file = os.path.join(self.test_dir, "adr_001.md")
        with open(adr_file, 'w') as f:
            f.write("# ADR 001\nArquitetura hexagonal modificada")
        
        # Detecta mudanças
        changes = self.monitor._detect_file_changes()
        
        # Processa mudanças
        self.monitor._handle_changes(changes)
        
        # Verifica se cache foi invalidado
        self.mock_cache_manager.invalidate.assert_called()
    
    def test_cache_invalidation_on_structure_change(self):
        """Testa invalidação de cache quando estrutura muda."""
        # Adiciona novo arquivo
        new_file = os.path.join(self.test_dir, "new_adr.md")
        with open(new_file, 'w') as f:
            f.write("# Novo ADR")
        
        # Detecta mudanças
        changes = self.monitor._detect_file_changes()
        
        # Processa mudanças
        self.monitor._handle_changes(changes)
        
        # Verifica se cache foi invalidado ou limpo
        self.assertTrue(
            self.mock_cache_manager.invalidate.called or 
            self.mock_cache_manager.clear.called
        )
    
    def test_change_history(self):
        """Testa histórico de mudanças."""
        # Modifica arquivo
        test_file = os.path.join(self.test_dir, "test1.md")
        with open(test_file, 'w') as f:
            f.write("# Teste 1\nConteúdo modificado")
        
        # Detecta e processa mudanças
        changes = self.monitor._detect_file_changes()
        self.monitor._handle_changes(changes)
        
        # Verifica histórico
        history = self.monitor.get_change_history()
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1].change_type, ChangeType.CONTENT_CHANGED)
    
    def test_monitoring_stats(self):
        """Testa estatísticas de monitoramento."""
        stats = self.monitor.get_monitoring_stats()
        
        self.assertIn('monitored_files', stats)
        self.assertIn('base_paths', stats)
        self.assertIn('check_interval', stats)
        self.assertIn('monitoring_active', stats)
        self.assertIn('total_changes', stats)
        self.assertIn('structure_hash', stats)
        
        self.assertEqual(stats['monitored_files'], 3)
        self.assertEqual(stats['check_interval'], 1)
    
    def test_force_check(self):
        """Testa verificação forçada de mudanças."""
        # Modifica arquivo
        test_file = os.path.join(self.test_dir, "test1.md")
        with open(test_file, 'w') as f:
            f.write("# Teste 1\nConteúdo modificado")
        
        # Força verificação
        changes = self.monitor.force_check()
        
        self.assertGreater(len(changes), 0)
        self.assertEqual(changes[0].change_type, ChangeType.CONTENT_CHANGED)
    
    def test_monitoring_thread(self):
        """Testa thread de monitoramento."""
        # Inicia monitoramento
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring)
        
        # Aguarda um pouco
        time.sleep(2)
        
        # Para monitoramento
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring)
    
    def test_change_event_serialization(self):
        """Testa serialização de eventos de mudança."""
        event = ChangeEvent(
            change_type=ChangeType.CONTENT_CHANGED,
            file_path="/test/file.md",
            old_hash="old_hash",
            new_hash="new_hash",
            timestamp=datetime.now(),
            description="Teste de mudança",
            impact_level="high"
        )
        
        # Serializa
        data = event.to_dict()
        self.assertIn('change_type', data)
        self.assertIn('file_path', data)
        self.assertIn('timestamp', data)
        
        # Deserializa
        new_event = ChangeEvent.from_dict(data)
        self.assertEqual(new_event.change_type, event.change_type)
        self.assertEqual(new_event.file_path, event.file_path)
        self.assertEqual(new_event.impact_level, event.impact_level)
    
    def test_impact_level_detection(self):
        """Testa detecção de nível de impacto."""
        # Testa mudança de conteúdo (alto impacto)
        test_file = os.path.join(self.test_dir, "adr_001.md")
        with open(test_file, 'w') as f:
            f.write("# ADR 001\nConteúdo completamente modificado")
        
        changes = self.monitor._detect_file_changes()
        self.monitor._handle_changes(changes)
        
        # Verifica que cache foi invalidado
        self.mock_cache_manager.invalidate.assert_called()
    
    def test_multiple_changes(self):
        """Testa múltiplas mudanças simultâneas."""
        # Modifica múltiplos arquivos
        files_to_modify = ["test1.md", "test2.py", "adr_001.md"]
        
        for filename in files_to_modify:
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(f"# {filename}\nConteúdo modificado")
        
        # Detecta mudanças
        changes = self.monitor._detect_file_changes()
        
        # Verifica que todas as mudanças foram detectadas
        self.assertEqual(len(changes), len(files_to_modify))
        
        # Verifica tipos de mudança
        content_changes = [c for c in changes if c.change_type == ChangeType.CONTENT_CHANGED]
        self.assertEqual(len(content_changes), len(files_to_modify))

if __name__ == '__main__':
    unittest.main() 