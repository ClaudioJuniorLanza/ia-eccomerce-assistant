"""
Sistema de detecção automática de mudanças para a assistente de IA.
Monitora alterações na base de conhecimento e atualiza cache automaticamente.
"""

import os
import sys
import hashlib
import json
import time
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
import glob

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importa base vetorial
try:
    from ia_assistant.database.vector_db import get_vector_database
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False

class ChangeType(Enum):
    """Tipos de mudanças detectadas."""
    FILE_ADDED = "file_added"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    CONTENT_CHANGED = "content_changed"
    STRUCTURE_CHANGED = "structure_changed"

@dataclass
class ChangeEvent:
    """Evento de mudança detectada."""
    change_type: ChangeType
    file_path: str
    old_hash: Optional[str]
    new_hash: Optional[str]
    timestamp: datetime
    description: str
    impact_level: str  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        data = asdict(self)
        data['change_type'] = self.change_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeEvent':
        """Cria instância a partir de dicionário."""
        data['change_type'] = ChangeType(data['change_type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class KnowledgeBaseMonitor:
    """Monitor da base de conhecimento."""
    
    def __init__(self, 
                 base_paths: List[str],
                 cache_manager=None,
                 check_interval: int = 30):
        """
        Inicializa o monitor da base de conhecimento.
        
        Args:
            base_paths: Caminhos para monitorar
            cache_manager: Gerenciador de cache para invalidar
            check_interval: Intervalo de verificação em segundos
        """
        self.base_paths = base_paths
        self.cache_manager = cache_manager
        self.check_interval = check_interval
        
        # Estruturas de dados para monitoramento
        self.file_hashes: Dict[str, str] = {}
        self.content_hashes: Dict[str, str] = {}
        self.structure_hash: str = ""
        self.change_history: List[ChangeEvent] = []
        
        # Configurações de monitoramento
        self.ignored_patterns = [
            "*.pyc", "*.pyo", "__pycache__", "*.log",
            ".git", ".svn", ".DS_Store", "*.tmp"
        ]
        
        # Thread de monitoramento
        self.monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # Inicializa hashes
        self._initialize_hashes()
    
    def _initialize_hashes(self):
        """Inicializa hashes da base de conhecimento."""
        logger.info("Inicializando monitoramento da base de conhecimento...")
        
        for base_path in self.base_paths:
            if os.path.exists(base_path):
                self._scan_directory(base_path)
        
        # Calcula hash da estrutura
        self._update_structure_hash()
        
        logger.info(f"Monitoramento inicializado: {len(self.file_hashes)} arquivos")
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """Verifica se o arquivo deve ser ignorado."""
        for pattern in self.ignored_patterns:
            if pattern.startswith("*."):
                if file_path.endswith(pattern[1:]):
                    return True
            elif pattern in file_path:
                return True
        return False
    
    def _scan_directory(self, directory: str):
        """Escaneia diretório recursivamente."""
        for root, dirs, files in os.walk(directory):
            # Remove diretórios ignorados
            dirs[:] = [d for d in dirs if not self._should_ignore_file(d)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not self._should_ignore_file(file_path):
                    self._add_file_to_monitoring(file_path)
    
    def _add_file_to_monitoring(self, file_path: str):
        """Adiciona arquivo ao monitoramento."""
        try:
            if os.path.isfile(file_path):
                file_hash = self._calculate_file_hash(file_path)
                content_hash = self._calculate_content_hash(file_path)
                
                self.file_hashes[file_path] = file_hash
                self.content_hashes[file_path] = content_hash
                
        except Exception as e:
            logger.warning(f"Erro ao adicionar arquivo {file_path}: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash do arquivo (metadados)."""
        try:
            stat = os.stat(file_path)
            metadata = f"{stat.st_size}_{stat.st_mtime}_{stat.st_ctime}"
            return hashlib.md5(metadata.encode()).hexdigest()
        except Exception:
            return ""
    
    def _calculate_content_hash(self, file_path: str) -> str:
        """Calcula hash do conteúdo do arquivo."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _update_structure_hash(self):
        """Atualiza hash da estrutura de arquivos."""
        try:
            # Cria representação da estrutura
            structure_data = []
            for file_path in sorted(self.file_hashes.keys()):
                relative_path = os.path.relpath(file_path, self.base_paths[0])
                structure_data.append(relative_path)
            
            structure_str = "|".join(structure_data)
            self.structure_hash = hashlib.md5(structure_str.encode()).hexdigest()
            
        except Exception as e:
            logger.warning(f"Erro ao calcular hash da estrutura: {e}")
    
    def _detect_file_changes(self) -> List[ChangeEvent]:
        """Detecta mudanças nos arquivos monitorados."""
        changes = []
        
        try:
            # Verifica arquivos existentes
            for file_path in list(self.file_hashes.keys()):
                if not os.path.exists(file_path):
                    # Arquivo foi deletado
                    change = ChangeEvent(
                        change_type=ChangeType.FILE_DELETED,
                        file_path=file_path,
                        old_hash=self.file_hashes[file_path],
                        new_hash=None,
                        timestamp=datetime.now(),
                        description=f"Arquivo deletado: {file_path}",
                        impact_level="medium"
                    )
                    changes.append(change)
                    
                    # Remove do monitoramento
                    del self.file_hashes[file_path]
                    if file_path in self.content_hashes:
                        del self.content_hashes[file_path]
                
                else:
                    # Verifica se arquivo foi modificado
                    new_file_hash = self._calculate_file_hash(file_path)
                    new_content_hash = self._calculate_content_hash(file_path)
                    
                    if new_file_hash != self.file_hashes[file_path]:
                        change_type = ChangeType.FILE_MODIFIED
                        if new_content_hash != self.content_hashes.get(file_path, ""):
                            change_type = ChangeType.CONTENT_CHANGED
                        
                        change = ChangeEvent(
                            change_type=change_type,
                            file_path=file_path,
                            old_hash=self.file_hashes[file_path],
                            new_hash=new_file_hash,
                            timestamp=datetime.now(),
                            description=f"Arquivo modificado: {file_path}",
                            impact_level="high" if change_type == ChangeType.CONTENT_CHANGED else "medium"
                        )
                        changes.append(change)
                        
                        # Atualiza hashes
                        self.file_hashes[file_path] = new_file_hash
                        self.content_hashes[file_path] = new_content_hash
            
            # Verifica novos arquivos
            for base_path in self.base_paths:
                if os.path.exists(base_path):
                    for root, dirs, files in os.walk(base_path):
                        dirs[:] = [d for d in dirs if not self._should_ignore_file(d)]
                        
                        for file in files:
                            file_path = os.path.join(root, file)
                            if not self._should_ignore_file(file_path) and file_path not in self.file_hashes:
                                # Novo arquivo
                                self._add_file_to_monitoring(file_path)
                                
                                change = ChangeEvent(
                                    change_type=ChangeType.FILE_ADDED,
                                    file_path=file_path,
                                    old_hash=None,
                                    new_hash=self.file_hashes[file_path],
                                    timestamp=datetime.now(),
                                    description=f"Novo arquivo: {file_path}",
                                    impact_level="medium"
                                )
                                changes.append(change)
            
            # Verifica mudanças na estrutura
            old_structure_hash = self.structure_hash
            self._update_structure_hash()
            
            if self.structure_hash != old_structure_hash:
                change = ChangeEvent(
                    change_type=ChangeType.STRUCTURE_CHANGED,
                    file_path="",
                    old_hash=old_structure_hash,
                    new_hash=self.structure_hash,
                    timestamp=datetime.now(),
                    description="Estrutura de arquivos alterada",
                    impact_level="high"
                )
                changes.append(change)
            
        except Exception as e:
            logger.error(f"Erro ao detectar mudanças: {e}")
        
        return changes
    
    def _handle_changes(self, changes: List[ChangeEvent]):
        """Processa mudanças detectadas."""
        if not changes:
            return
        
        logger.info(f"Detectadas {len(changes)} mudanças na base de conhecimento")
        
        for change in changes:
            logger.info(f"Mudança: {change.description} ({change.change_type.value})")
            
            # Adiciona ao histórico
            self.change_history.append(change)
            
            # Determina impacto no cache
            self._invalidate_cache_if_needed(change)
        
        # Limita histórico
        if len(self.change_history) > 100:
            self.change_history = self.change_history[-100:]
    
    def _invalidate_cache_if_needed(self, change: ChangeEvent):
        """Invalida cache e recarrega base vetorial baseado no tipo de mudança."""
        if not self.cache_manager:
            return
        
        try:
            # Flag para indicar se precisa recarregar base vetorial
            reload_vector_db = False
            
            if change.change_type == ChangeType.CONTENT_CHANGED:
                # Mudança de conteúdo - invalida cache relacionado
                file_name = os.path.basename(change.file_path)
                if file_name.endswith(('.md', '.txt', '.py')):
                    reload_vector_db = True  # Sempre recarrega para mudanças de conteúdo
                    
                    # Invalida cache baseado no tipo de arquivo
                    if 'adr' in file_name.lower():
                        self.cache_manager.invalidate(query_type="architecture")
                        logger.info("Cache de arquitetura invalidado")
                    elif 'ddd' in file_name.lower():
                        self.cache_manager.invalidate(query_type="ddd_concept")
                        logger.info("Cache de DDD invalidado")
                    else:
                        # Invalida cache geral
                        self.cache_manager.invalidate()
                        logger.info("Cache geral invalidado")
            
            elif change.change_type == ChangeType.STRUCTURE_CHANGED:
                # Mudança estrutural - invalida todo cache e recarrega base vetorial
                self.cache_manager.clear()
                reload_vector_db = True
                logger.info("Cache limpo devido a mudança estrutural")
            
            elif change.change_type == ChangeType.FILE_DELETED:
                # Arquivo deletado - invalida cache relacionado e recarrega base vetorial
                file_name = os.path.basename(change.file_path)
                reload_vector_db = True
                
                if 'adr' in file_name.lower():
                    self.cache_manager.invalidate(query_type="architecture")
                    logger.info("Cache de arquitetura invalidado")
            
            elif change.change_type == ChangeType.FILE_ADDED:
                # Novo arquivo - recarrega base vetorial
                file_name = os.path.basename(change.file_path)
                if file_name.endswith(('.md', '.txt', '.py')):
                    reload_vector_db = True
                    logger.info("Novo arquivo detectado - base vetorial será recarregada")
            
            # Recarrega base vetorial se necessário
            if reload_vector_db and VECTOR_DB_AVAILABLE:
                self._reload_vector_database()
        
        except Exception as e:
            logger.error(f"Erro ao invalidar cache: {e}")
    
    def _reload_vector_database(self):
        """Recarrega a base vetorial com as mudanças detectadas."""
        try:
            logger.info("Recarregando base vetorial...")
            
            # Obtém nova instância da base vetorial
            vector_db = get_vector_database()
            
            # Força recarregamento dos documentos
            if hasattr(vector_db, 'reload_documents'):
                vector_db.reload_documents()
                logger.info("Base vetorial recarregada com sucesso")
            else:
                logger.warning("Método reload_documents não disponível na base vetorial")
            
        except Exception as e:
            logger.error(f"Erro ao recarregar base vetorial: {e}")
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo."""
        if self.monitoring:
            logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoramento parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring:
            try:
                with self.lock:
                    changes = self._detect_file_changes()
                    if changes:
                        self._handle_changes(changes)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(self.check_interval)
    
    def get_change_history(self, limit: int = 50) -> List[ChangeEvent]:
        """Obtém histórico de mudanças."""
        with self.lock:
            return self.change_history[-limit:]
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de monitoramento."""
        with self.lock:
            return {
                'monitored_files': len(self.file_hashes),
                'base_paths': self.base_paths,
                'check_interval': self.check_interval,
                'monitoring_active': self.monitoring,
                'total_changes': len(self.change_history),
                'recent_changes': len([c for c in self.change_history 
                                     if c.timestamp > datetime.now() - timedelta(hours=1)]),
                'structure_hash': self.structure_hash
            }
    
    def force_check(self) -> List[ChangeEvent]:
        """Força verificação de mudanças."""
        with self.lock:
            changes = self._detect_file_changes()
            if changes:
                self._handle_changes(changes)
            return changes

class FileChangeHandler(FileSystemEventHandler):
    """Handler para eventos de mudança de arquivo."""
    
    def __init__(self, change_detector: KnowledgeBaseMonitor):
        self.change_detector = change_detector
    
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"Arquivo criado: {event.src_path}")
            self.change_detector.force_check()
    
    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"Arquivo modificado: {event.src_path}")
            self.change_detector.force_check()
    
    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"Arquivo deletado: {event.src_path}")
            self.change_detector.force_check()

# Instância global do detector de mudanças
change_detector = None 