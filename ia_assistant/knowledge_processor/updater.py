"""
Sistema de atualização contínua do conhecimento para a assistente de IA.
Implementa mecanismos para detectar mudanças e atualizar a base de conhecimento
de forma incremental, sem reprocessar todo o conteúdo.
"""

import os
import time
import hashlib
import json
import git
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime

# Importa os coletores de dados
from ia_assistant.data_collector.collectors import (
    DocumentCollector, CodeCollector, GitCollector, DataCollector
)

# Importa a base de dados vetorial
from ia_assistant.database.vector_db import get_vector_database, VectorDatabase

class ChangeDetector:
    """Detector de mudanças em arquivos e repositório Git."""
    
    def __init__(self, project_root: str, cache_file: Optional[str] = None):
        """
        Inicializa o detector de mudanças.
        
        Args:
            project_root: Caminho raiz do projeto.
            cache_file: Caminho opcional para o arquivo de cache. Se não fornecido,
                        será criado em project_root/.ia_assistant/change_cache.json.
        """
        self.project_root = project_root
        
        # Define o arquivo de cache
        if cache_file is None:
            cache_dir = os.path.join(project_root, ".ia_assistant")
            os.makedirs(cache_dir, exist_ok=True)
            self.cache_file = os.path.join(cache_dir, "change_cache.json")
        else:
            self.cache_file = cache_file
        
        # Carrega o cache existente ou cria um novo
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """
        Carrega o cache de mudanças.
        
        Returns:
            Dicionário com o cache de mudanças.
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")
                return self._create_empty_cache()
        else:
            return self._create_empty_cache()
    
    def _create_empty_cache(self) -> Dict[str, Any]:
        """
        Cria um cache vazio.
        
        Returns:
            Dicionário com o cache vazio.
        """
        return {
            "last_update": datetime.now().isoformat(),
            "files": {},
            "git": {
                "last_commit": None
            }
        }
    
    def _save_cache(self) -> None:
        """Salva o cache de mudanças."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calcula o hash de um arquivo.
        
        Args:
            file_path: Caminho do arquivo.
            
        Returns:
            Hash do arquivo.
        """
        if not os.path.exists(file_path):
            return ""
        
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def detect_file_changes(self, extensions: List[str] = [".md", ".kt"]) -> Dict[str, List[str]]:
        """
        Detecta mudanças em arquivos do projeto.
        
        Args:
            extensions: Lista de extensões de arquivo a serem monitoradas.
            
        Returns:
            Dicionário com arquivos adicionados, modificados e removidos.
        """
        changes = {
            "added": [],
            "modified": [],
            "removed": []
        }
        
        # Obtém todos os arquivos com as extensões especificadas
        current_files = {}
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    current_files[file_path] = self._calculate_file_hash(file_path)
        
        # Compara com o cache
        cached_files = self.cache.get("files", {})
        
        # Detecta arquivos adicionados ou modificados
        for file_path, file_hash in current_files.items():
            if file_path not in cached_files:
                changes["added"].append(file_path)
            elif cached_files[file_path] != file_hash:
                changes["modified"].append(file_path)
        
        # Detecta arquivos removidos
        for file_path in cached_files:
            if file_path not in current_files:
                changes["removed"].append(file_path)
        
        # Atualiza o cache
        self.cache["files"] = current_files
        self.cache["last_update"] = datetime.now().isoformat()
        self._save_cache()
        
        return changes
    
    def detect_git_changes(self) -> Dict[str, Any]:
        """
        Detecta mudanças no repositório Git.
        
        Returns:
            Dicionário com informações sobre novos commits.
        """
        changes = {
            "new_commits": []
        }
        
        # Verifica se o diretório é um repositório Git
        git_dir = os.path.join(self.project_root, ".git")
        if not os.path.exists(git_dir):
            return changes
        
        # Abre o repositório
        repo = git.Repo(self.project_root)
        
        # Obtém o último commit
        try:
            latest_commit = list(repo.iter_commits('main', max_count=1))[0]
            latest_commit_hash = latest_commit.hexsha
        except Exception as e:
            print(f"Erro ao obter último commit: {e}")
            return changes
        
        # Compara com o cache
        last_commit = self.cache.get("git", {}).get("last_commit")
        
        if last_commit != latest_commit_hash:
            # Obtém todos os novos commits desde o último commit conhecido
            if last_commit:
                try:
                    new_commits = list(repo.iter_commits(f"{last_commit}..main"))
                    changes["new_commits"] = [commit.hexsha for commit in new_commits]
                except Exception as e:
                    print(f"Erro ao obter novos commits: {e}")
                    changes["new_commits"] = [latest_commit_hash]
            else:
                # Se não houver commit anterior, considera o último commit como novo
                changes["new_commits"] = [latest_commit_hash]
            
            # Atualiza o cache
            self.cache["git"] = {"last_commit": latest_commit_hash}
            self.cache["last_update"] = datetime.now().isoformat()
            self._save_cache()
        
        return changes


class IncrementalUpdater:
    """Atualizador incremental da base de conhecimento."""
    
    def __init__(self, project_root: str, vector_db: Optional[VectorDatabase] = None):
        """
        Inicializa o atualizador incremental.
        
        Args:
            project_root: Caminho raiz do projeto.
            vector_db: Instância opcional da base de dados vetorial. Se não fornecida, uma nova será criada.
        """
        self.project_root = project_root
        self.vector_db = vector_db if vector_db is not None else get_vector_database()
        
        # Inicializa os coletores
        self.document_collector = DocumentCollector(self.vector_db)
        self.code_collector = CodeCollector(self.vector_db)
        self.git_collector = GitCollector(self.vector_db)
        
        # Inicializa o detector de mudanças
        self.change_detector = ChangeDetector(project_root)
    
    def update_documents(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Atualiza documentos na base de conhecimento.
        
        Args:
            file_paths: Lista de caminhos de arquivos a serem atualizados.
            
        Returns:
            Dicionário com resultados da atualização.
        """
        results = {
            "updated": [],
            "failed": []
        }
        
        for file_path in file_paths:
            try:
                # Determina a coleção apropriada
                if file_path.endswith(".md"):
                    collection_name = "decisoes_arquiteturais" if "decisoes_arquiteturais" in file_path else "documentacao_ddd"
                    # Atualiza o documento
                    self.document_collector.collect(file_path, collection_name)
                    results["updated"].append(file_path)
                elif file_path.endswith(".kt"):
                    # Atualiza o código
                    self.code_collector.collect(file_path)
                    results["updated"].append(file_path)
            except Exception as e:
                print(f"Erro ao atualizar arquivo {file_path}: {e}")
                results["failed"].append(file_path)
        
        return results
    
    def update_git_history(self, commit_hashes: List[str]) -> Dict[str, Any]:
        """
        Atualiza o histórico Git na base de conhecimento.
        
        Args:
            commit_hashes: Lista de hashes de commits a serem atualizados.
            
        Returns:
            Dicionário com resultados da atualização.
        """
        results = {
            "updated_commits": [],
            "failed_commits": []
        }
        
        # Verifica se o diretório é um repositório Git
        git_dir = os.path.join(self.project_root, ".git")
        if not os.path.exists(git_dir):
            return results
        
        # Abre o repositório
        repo = git.Repo(self.project_root)
        
        for commit_hash in commit_hashes:
            try:
                # Obtém o commit
                commit = repo.commit(commit_hash)
                
                # Formata a mensagem do commit
                commit_message = f"""
Commit: {commit.hexsha}
Autor: {commit.author.name} <{commit.author.email}>
Data: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')}
Mensagem:
{commit.message}

Arquivos alterados:
{', '.join([item.a_path for item in commit.diff(commit.parents[0] if commit.parents else None)])}
"""
                
                # Prepara metadados para o commit
                metadata = {
                    "source": self.project_root,
                    "document_type": "git_commit",
                    "document_id": commit.hexsha,
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "date": commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    "commit_hash": commit.hexsha,
                    "commit_summary": commit.summary
                }
                
                # Adiciona o commit à base de dados
                self.vector_db.process_and_add_document(
                    collection_name="commits_historico",
                    document=commit_message,
                    metadata=metadata,
                    document_id=commit.hexsha
                )
                
                results["updated_commits"].append(commit_hash)
            except Exception as e:
                print(f"Erro ao atualizar commit {commit_hash}: {e}")
                results["failed_commits"].append(commit_hash)
        
        return results
    
    def update_all(self) -> Dict[str, Any]:
        """
        Atualiza toda a base de conhecimento de forma incremental.
        
        Returns:
            Dicionário com resultados da atualização.
        """
        results = {
            "files": {
                "detected_changes": {},
                "update_results": {}
            },
            "git": {
                "detected_changes": {},
                "update_results": {}
            }
        }
        
        # Detecta mudanças em arquivos
        file_changes = self.change_detector.detect_file_changes()
        results["files"]["detected_changes"] = file_changes
        
        # Atualiza arquivos adicionados ou modificados
        files_to_update = file_changes["added"] + file_changes["modified"]
        if files_to_update:
            update_results = self.update_documents(files_to_update)
            results["files"]["update_results"] = update_results
        
        # Detecta mudanças no Git
        git_changes = self.change_detector.detect_git_changes()
        results["git"]["detected_changes"] = git_changes
        
        # Atualiza commits
        if git_changes["new_commits"]:
            update_results = self.update_git_history(git_changes["new_commits"])
            results["git"]["update_results"] = update_results
        
        return results


class ConsistencyChecker:
    """Verificador de consistência da base de conhecimento."""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        Inicializa o verificador de consistência.
        
        Args:
            vector_db: Instância opcional da base de dados vetorial. Se não fornecida, uma nova será criada.
        """
        self.vector_db = vector_db if vector_db is not None else get_vector_database()
    
    def check_collections(self) -> Dict[str, Any]:
        """
        Verifica a consistência das coleções na base de dados.
        
        Returns:
            Dicionário com resultados da verificação.
        """
        results = {}
        
        # Obtém estatísticas de todas as coleções
        stats = self.vector_db.get_all_collections_stats()
        
        for collection_name, collection_stats in stats.items():
            results[collection_name] = {
                "document_count": collection_stats["document_count"],
                "status": "ok" if collection_stats["document_count"] > 0 else "empty"
            }
        
        return results
    
    def check_document_coverage(self, project_root: str) -> Dict[str, Any]:
        """
        Verifica a cobertura de documentos na base de conhecimento.
        
        Args:
            project_root: Caminho raiz do projeto.
            
        Returns:
            Dicionário com resultados da verificação.
        """
        results = {
            "markdown_files": {
                "total": 0,
                "indexed": 0,
                "missing": []
            },
            "kotlin_files": {
                "total": 0,
                "indexed": 0,
                "missing": []
            }
        }
        
        # Obtém todos os arquivos Markdown e Kotlin no projeto
        markdown_files = []
        kotlin_files = []
        
        for root, _, files in os.walk(project_root):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    markdown_files.append(file_path)
                elif file.endswith(".kt"):
                    file_path = os.path.join(root, file)
                    kotlin_files.append(file_path)
        
        results["markdown_files"]["total"] = len(markdown_files)
        results["kotlin_files"]["total"] = len(kotlin_files)
        
        # Verifica quais arquivos estão indexados
        for file_path in markdown_files:
            # Simplificação: considera que o arquivo está indexado se o nome do arquivo
            # estiver presente em algum metadado na coleção apropriada
            file_name = os.path.basename(file_path)
            collection_name = "decisoes_arquiteturais" if "decisoes_arquiteturais" in file_path else "documentacao_ddd"
            
            try:
                # Consulta a coleção por metadados que contenham o nome do arquivo
                query_results = self.vector_db.query(
                    collection_name=collection_name,
                    query_text=file_name,
                    n_results=1,
                    filter_criteria={"file_name": file_name}
                )
                
                if query_results["metadatas"] and len(query_results["metadatas"][0]) > 0:
                    results["markdown_files"]["indexed"] += 1
                else:
                    results["markdown_files"]["missing"].append(file_path)
            except Exception as e:
                print(f"Erro ao verificar arquivo {file_path}: {e}")
                results["markdown_files"]["missing"].append(file_path)
        
        # Verifica quais arquivos Kotlin estão indexados
        for file_path in kotlin_files:
            file_name = os.path.basename(file_path)
            
            try:
                # Consulta a coleção por metadados que contenham o nome do arquivo
                query_results = self.vector_db.query(
                    collection_name="codigo_fonte",
                    query_text=file_name,
                    n_results=1,
                    filter_criteria={"file_name": file_name}
                )
                
                if query_results["metadatas"] and len(query_results["metadatas"][0]) > 0:
                    results["kotlin_files"]["indexed"] += 1
                else:
                    results["kotlin_files"]["missing"].append(file_path)
            except Exception as e:
                print(f"Erro ao verificar arquivo {file_path}: {e}")
                results["kotlin_files"]["missing"].append(file_path)
        
        return results
    
    def fix_inconsistencies(self, project_root: str) -> Dict[str, Any]:
        """
        Corrige inconsistências na base de conhecimento.
        
        Args:
            project_root: Caminho raiz do projeto.
            
        Returns:
            Dicionário com resultados da correção.
        """
        results = {
            "fixed_files": [],
            "failed_files": []
        }
        
        # Verifica a cobertura de documentos
        coverage = self.check_document_coverage(project_root)
        
        # Cria coletores
        document_collector = DocumentCollector(self.vector_db)
        code_collector = CodeCollector(self.vector_db)
        
        # Corrige arquivos Markdown ausentes
        for file_path in coverage["markdown_files"]["missing"]:
            try:
                collection_name = "decisoes_arquiteturais" if "decisoes_arquiteturais" in file_path else "documentacao_ddd"
                document_collector.collect(file_path, collection_name)
                results["fixed_files"].append(file_path)
            except Exception as e:
                print(f"Erro ao corrigir arquivo {file_path}: {e}")
                results["failed_files"].append(file_path)
        
        # Corrige arquivos Kotlin ausentes
        for file_path in coverage["kotlin_files"]["missing"]:
            try:
                code_collector.collect(file_path)
                results["fixed_files"].append(file_path)
            except Exception as e:
                print(f"Erro ao corrigir arquivo {file_path}: {e}")
                results["failed_files"].append(file_path)
        
        return results


class UpdateManager:
    """Gerenciador de atualização da base de conhecimento."""
    
    def __init__(self, project_root: str, vector_db: Optional[VectorDatabase] = None):
        """
        Inicializa o gerenciador de atualização.
        
        Args:
            project_root: Caminho raiz do projeto.
            vector_db: Instância opcional da base de dados vetorial. Se não fornecida, uma nova será criada.
        """
        self.project_root = project_root
        self.vector_db = vector_db if vector_db is not None else get_vector_database()
        
        # Inicializa componentes
        self.updater = IncrementalUpdater(project_root, self.vector_db)
        self.checker = ConsistencyChecker(self.vector_db)
    
    def initialize_knowledge_base(self) -> Dict[str, Any]:
        """
        Inicializa a base de conhecimento com todos os dados do projeto.
        
        Returns:
            Dicionário com resultados da inicialização.
        """
        results = {
            "initialization": "started",
            "collection_results": {}
        }
        
        # Cria o coletor de dados
        data_collector = DataCollector(self.vector_db)
        
        # Coleta todos os dados
        collection_results = data_collector.collect_all(self.project_root)
        results["collection_results"] = collection_results
        
        # Verifica a consistência
        consistency_results = self.checker.check_collections()
        results["consistency"] = consistency_results
        
        results["initialization"] = "completed"
        
        return results
    
    def update_knowledge_base(self) -> Dict[str, Any]:
        """
        Atualiza a base de conhecimento de forma incremental.
        
        Returns:
            Dicionário com resultados da atualização.
        """
        results = {
            "update": "started",
            "incremental_update": {},
            "consistency_check": {},
            "fixes": {}
        }
        
        # Realiza a atualização incremental
        incremental_results = self.updater.update_all()
        results["incremental_update"] = incremental_results
        
        # Verifica a consistência
        consistency_results = self.checker.check_collections()
        results["consistency_check"] = consistency_results
        
        # Verifica a cobertura e corrige inconsistências
        coverage_results = self.checker.check_document_coverage(self.project_root)
        results["coverage"] = coverage_results
        
        # Se houver arquivos ausentes, corrige
        missing_markdown = coverage_results["markdown_files"]["missing"]
        missing_kotlin = coverage_results["kotlin_files"]["missing"]
        
        if missing_markdown or missing_kotlin:
            fix_results = self.checker.fix_inconsistencies(self.project_root)
            results["fixes"] = fix_results
        
        results["update"] = "completed"
        
        return results
    
    def schedule_periodic_update(self, interval_seconds: int = 3600) -> None:
        """
        Agenda atualizações periódicas da base de conhecimento.
        
        Args:
            interval_seconds: Intervalo em segundos entre atualizações.
        """
        print(f"Agendando atualizações periódicas a cada {interval_seconds} segundos.")
        
        try:
            while True:
                print(f"Executando atualização em {datetime.now().isoformat()}")
                self.update_knowledge_base()
                print(f"Próxima atualização em {interval_seconds} segundos.")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("Atualização periódica interrompida pelo usuário.")


# Função para criar uma instância do gerenciador de atualização
def get_update_manager(project_root: str, vector_db: Optional[VectorDatabase] = None) -> UpdateManager:
    """
    Cria e retorna uma instância do gerenciador de atualização.
    
    Args:
        project_root: Caminho raiz do projeto.
        vector_db: Instância opcional da base de dados vetorial.
        
    Returns:
        Instância de UpdateManager.
    """
    return UpdateManager(project_root, vector_db)
