"""
Módulo de coleta de dados para a assistente de IA.
Implementa coletores especializados para documentos, código-fonte e histórico Git.
"""

import os
import re
import git
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Importa a base de dados vetorial
from ia_assistant.database.vector_db import get_vector_database, VectorDatabase

class BaseCollector:
    """Classe base para todos os coletores de dados."""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        Inicializa o coletor base.
        
        Args:
            vector_db: Instância opcional da base de dados vetorial. Se não fornecida, uma nova será criada.
        """
        self.vector_db = vector_db if vector_db is not None else get_vector_database()
    
    def collect(self, *args, **kwargs):
        """
        Método abstrato para coleta de dados. Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar este método")


class DocumentCollector(BaseCollector):
    """Coletor especializado para documentos de texto (Markdown, etc.)."""
    
    def collect(self, file_path: str, collection_name: str = "decisoes_arquiteturais", 
               document_id: Optional[str] = None) -> List[str]:
        """
        Coleta e processa um documento de texto.
        
        Args:
            file_path: Caminho para o arquivo de documento.
            collection_name: Nome da coleção onde o documento será armazenado.
            document_id: ID opcional para o documento. Se não fornecido, será gerado.
            
        Returns:
            Lista de IDs dos chunks adicionados à base de dados.
        """
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Lê o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extrai metadados do arquivo
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1]
        file_type = "markdown" if file_ext.lower() in ['.md', '.markdown'] else "text"
        
        # Prepara metadados para o documento
        metadata = {
            "source": file_path,
            "file_name": file_name,
            "file_type": file_type,
            "document_type": "architectural_decision" if "decisoes_arquiteturais" in file_path else "documentation",
            "document_id": document_id if document_id else file_name
        }
        
        # Processa e adiciona o documento à base de dados
        return self.vector_db.process_and_add_document(
            collection_name=collection_name,
            document=content,
            metadata=metadata,
            document_id=document_id
        )


class CodeCollector(BaseCollector):
    """Coletor especializado para código-fonte (Kotlin, etc.)."""
    
    def _extract_code_structure(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Extrai informações estruturais do código Kotlin.
        
        Args:
            content: Conteúdo do arquivo de código.
            file_path: Caminho do arquivo.
            
        Returns:
            Dicionário com informações estruturais do código.
        """
        # Extrai o pacote
        package_match = re.search(r'package\s+([\w.]+)', content)
        package = package_match.group(1) if package_match else "unknown"
        
        # Extrai classes/interfaces
        class_matches = re.finditer(r'(class|interface|data class|enum class)\s+(\w+)', content)
        classes = [match.group(2) for match in class_matches]
        
        # Extrai funções/métodos
        function_matches = re.finditer(r'fun\s+(\w+)\s*\(', content)
        functions = [match.group(1) for match in function_matches]
        
        # Identifica se é um arquivo de domínio, adaptador, etc.
        file_type = "unknown"
        if "domain" in file_path:
            file_type = "domain"
        elif "adapter" in file_path:
            file_type = "adapter"
        elif "application" in file_path:
            file_type = "application"
        elif "port" in file_path:
            file_type = "port"
        
        return {
            "package": package,
            "classes": classes,
            "functions": functions,
            "file_type": file_type
        }
    
    def collect(self, file_path: str, collection_name: str = "codigo_fonte",
               document_id: Optional[str] = None) -> List[str]:
        """
        Coleta e processa um arquivo de código-fonte.
        
        Args:
            file_path: Caminho para o arquivo de código.
            collection_name: Nome da coleção onde o código será armazenado.
            document_id: ID opcional para o documento. Se não fornecido, será gerado.
            
        Returns:
            Lista de IDs dos chunks adicionados à base de dados.
        """
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Verifica se é um arquivo Kotlin
        if not file_path.endswith(".kt"):
            raise ValueError(f"Arquivo não é um arquivo Kotlin: {file_path}")
        
        # Lê o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extrai informações estruturais do código
        code_structure = self._extract_code_structure(content, file_path)
        
        # Extrai metadados do arquivo
        file_name = os.path.basename(file_path)
        
        # Prepara metadados para o documento
        metadata = {
            "source": file_path,
            "file_name": file_name,
            "file_type": "kotlin",
            "document_type": "code",
            "document_id": document_id if document_id else file_name,
            "package": code_structure["package"],
            "classes": ",".join(code_structure["classes"]),
            "functions": ",".join(code_structure["functions"]),
            "code_type": code_structure["file_type"]
        }
        
        # Processa e adiciona o documento à base de dados
        return self.vector_db.process_and_add_document(
            collection_name=collection_name,
            document=content,
            metadata=metadata,
            document_id=document_id
        )
    
    def collect_directory(self, directory_path: str, collection_name: str = "codigo_fonte",
                        file_extension: str = ".kt") -> Dict[str, List[str]]:
        """
        Coleta e processa todos os arquivos de código em um diretório.
        
        Args:
            directory_path: Caminho para o diretório.
            collection_name: Nome da coleção onde os códigos serão armazenados.
            file_extension: Extensão dos arquivos a serem coletados.
            
        Returns:
            Dicionário com caminhos de arquivos e IDs dos chunks adicionados.
        """
        results = {}
        
        # Percorre o diretório recursivamente
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(file_extension):
                    file_path = os.path.join(root, file)
                    try:
                        chunk_ids = self.collect(file_path, collection_name)
                        results[file_path] = chunk_ids
                    except Exception as e:
                        print(f"Erro ao processar arquivo {file_path}: {e}")
                        results[file_path] = [f"ERROR: {str(e)}"]
        
        return results


class GitCollector(BaseCollector):
    """Coletor especializado para histórico Git."""
    
    def _format_commit_message(self, commit) -> str:
        """
        Formata a mensagem de commit para armazenamento.
        
        Args:
            commit: Objeto de commit do GitPython.
            
        Returns:
            Mensagem formatada.
        """
        return f"""
Commit: {commit.hexsha}
Autor: {commit.author.name} <{commit.author.email}>
Data: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')}
Mensagem:
{commit.message}

Arquivos alterados:
{', '.join([item.a_path for item in commit.diff(commit.parents[0] if commit.parents else None)])}
"""
    
    def collect(self, repo_path: str, collection_name: str = "commits_historico",
               max_commits: int = 100) -> List[str]:
        """
        Coleta e processa o histórico de commits de um repositório Git.
        
        Args:
            repo_path: Caminho para o repositório Git.
            collection_name: Nome da coleção onde os commits serão armazenados.
            max_commits: Número máximo de commits a serem coletados.
            
        Returns:
            Lista de IDs dos chunks adicionados à base de dados.
        """
        # Verifica se o diretório é um repositório Git
        if not os.path.exists(os.path.join(repo_path, ".git")):
            raise ValueError(f"Diretório não é um repositório Git: {repo_path}")
        
        # Abre o repositório
        repo = git.Repo(repo_path)
        
        # Obtém os commits
        commits = list(repo.iter_commits('main', max_count=max_commits))
        
        all_chunk_ids = []
        
        # Processa cada commit
        for commit in commits:
            try:
                # Formata a mensagem do commit
                commit_message = self._format_commit_message(commit)
                
                # Prepara metadados para o commit
                metadata = {
                    "source": repo_path,
                    "document_type": "git_commit",
                    "document_id": commit.hexsha,
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "date": commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    "commit_hash": commit.hexsha,
                    "commit_summary": commit.summary
                }
                
                # Processa e adiciona o commit à base de dados
                chunk_ids = self.vector_db.process_and_add_document(
                    collection_name=collection_name,
                    document=commit_message,
                    metadata=metadata,
                    document_id=commit.hexsha
                )
                
                all_chunk_ids.extend(chunk_ids)
            except Exception as e:
                print(f"Erro ao processar commit {commit.hexsha}: {e}")
        
        return all_chunk_ids
    
    def collect_pull_requests(self, repo_path: str, collection_name: str = "commits_historico") -> List[str]:
        """
        Coleta e processa informações sobre Pull Requests.
        Nota: Esta é uma implementação básica que depende de arquivos locais.
        Para uma implementação completa, seria necessário usar a API do GitHub.
        
        Args:
            repo_path: Caminho para o repositório Git.
            collection_name: Nome da coleção onde os PRs serão armazenados.
            
        Returns:
            Lista de IDs dos chunks adicionados à base de dados.
        """
        # Verifica se o diretório é um repositório Git
        if not os.path.exists(os.path.join(repo_path, ".git")):
            raise ValueError(f"Diretório não é um repositório Git: {repo_path}")
        
        # Procura por arquivos de PR no diretório .github/pull_requests
        pr_dir = os.path.join(repo_path, ".github", "pull_requests")
        
        if not os.path.exists(pr_dir):
            print(f"Diretório de PRs não encontrado: {pr_dir}")
            return []
        
        all_chunk_ids = []
        
        # Processa cada arquivo de PR
        for file_name in os.listdir(pr_dir):
            if file_name.endswith(".md"):
                file_path = os.path.join(pr_dir, file_name)
                
                # Lê o conteúdo do arquivo
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Extrai o número do PR do nome do arquivo
                pr_number_match = re.search(r'pr_(\d+)', file_name)
                pr_number = pr_number_match.group(1) if pr_number_match else "unknown"
                
                # Prepara metadados para o PR
                metadata = {
                    "source": file_path,
                    "document_type": "pull_request",
                    "document_id": f"pr_{pr_number}",
                    "pr_number": pr_number
                }
                
                # Processa e adiciona o PR à base de dados
                chunk_ids = self.vector_db.process_and_add_document(
                    collection_name=collection_name,
                    document=content,
                    metadata=metadata,
                    document_id=f"pr_{pr_number}"
                )
                
                all_chunk_ids.extend(chunk_ids)
        
        return all_chunk_ids


class DataCollector:
    """Classe principal para coordenar a coleta de dados de diferentes fontes."""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        Inicializa o coletor de dados.
        
        Args:
            vector_db: Instância opcional da base de dados vetorial. Se não fornecida, uma nova será criada.
        """
        self.vector_db = vector_db if vector_db is not None else get_vector_database()
        self.document_collector = DocumentCollector(self.vector_db)
        self.code_collector = CodeCollector(self.vector_db)
        self.git_collector = GitCollector(self.vector_db)
    
    def collect_all(self, project_root: str) -> Dict[str, Any]:
        """
        Coleta dados de todas as fontes disponíveis no projeto.
        
        Args:
            project_root: Caminho raiz do projeto.
            
        Returns:
            Dicionário com resultados da coleta.
        """
        results = {
            "documents": {},
            "code": {},
            "git": {
                "commits": [],
                "pull_requests": []
            }
        }
        
        # Coleta documentos
        docs_dir = os.path.join(project_root)
        for file in os.listdir(docs_dir):
            if file.endswith(".md"):
                file_path = os.path.join(docs_dir, file)
                try:
                    collection_name = "decisoes_arquiteturais" if "decisoes_arquiteturais" in file else "documentacao_ddd"
                    chunk_ids = self.document_collector.collect(file_path, collection_name)
                    results["documents"][file_path] = chunk_ids
                except Exception as e:
                    print(f"Erro ao processar documento {file_path}: {e}")
                    results["documents"][file_path] = [f"ERROR: {str(e)}"]
        
        # Coleta código-fonte
        src_dir = os.path.join(project_root, "src")
        if os.path.exists(src_dir):
            results["code"] = self.code_collector.collect_directory(src_dir)
        
        # Coleta histórico Git
        try:
            results["git"]["commits"] = self.git_collector.collect(project_root)
            results["git"]["pull_requests"] = self.git_collector.collect_pull_requests(project_root)
        except Exception as e:
            print(f"Erro ao processar histórico Git: {e}")
            results["git"]["error"] = str(e)
        
        return results


# Função para criar uma instância do coletor de dados
def get_data_collector(vector_db: Optional[VectorDatabase] = None) -> DataCollector:
    """
    Cria e retorna uma instância do coletor de dados.
    
    Args:
        vector_db: Instância opcional da base de dados vetorial.
        
    Returns:
        Instância de DataCollector.
    """
    return DataCollector(vector_db)
