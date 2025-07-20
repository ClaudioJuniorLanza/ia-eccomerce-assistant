"""
Configuração e implementação da base de dados vetorial usando ChromaDB.
Este módulo define a estrutura de coleções, mecanismos de embedding e funções
para armazenamento e recuperação de conhecimento para a assistente de IA.
"""

import os
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional, Union

# Configuração de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
os.makedirs(DB_DIR, exist_ok=True)

# Configuração do ChromaDB
client = chromadb.PersistentClient(path=DB_DIR, settings=Settings(allow_reset=True))

# Definição das coleções conforme a arquitetura
COLLECTIONS = {
    "decisoes_arquiteturais": "Armazena chunks do documento de decisões arquiteturais e suas atualizações",
    "codigo_fonte": "Armazena chunks de código Kotlin, organizados por módulos e funcionalidades",
    "commits_historico": "Armazena mensagens e metadados de commits, permitindo rastrear a evolução do projeto",
    "documentacao_ddd": "Armazena conhecimento específico sobre Domain Driven Design aplicado ao projeto",
    "documentacao_arquitetura": "Armazena conhecimento sobre Arquitetura Hexagonal e sua implementação no projeto",
    "documentacao_tecnologias": "Armazena conhecimento sobre Kotlin, Quarkus e outras tecnologias utilizadas"
}

# Configuração do modelo de embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Configuração do text splitter para chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

class VectorDatabase:
    """Classe para gerenciar a base de dados vetorial."""
    
    def __init__(self):
        """Inicializa a base de dados vetorial e cria as coleções necessárias."""
        self.client = client
        self.collections = {}
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Inicializa as coleções definidas na arquitetura."""
        for collection_name, description in COLLECTIONS.items():
            try:
                # Tenta obter a coleção se já existir
                collection = self.client.get_collection(name=collection_name)
                print(f"Coleção '{collection_name}' já existe.")
            except:
                # Cria a coleção se não existir
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": description}
                )
                print(f"Coleção '{collection_name}' criada com sucesso.")
            
            self.collections[collection_name] = collection
    
    def add_documents(self, collection_name: str, texts: List[str], 
                     metadatas: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> List[str]:
        """
        Adiciona documentos a uma coleção específica.
        
        Args:
            collection_name: Nome da coleção onde os documentos serão adicionados.
            texts: Lista de textos a serem adicionados.
            metadatas: Lista de metadados associados a cada texto.
            ids: Lista opcional de IDs para os documentos. Se não fornecido, IDs serão gerados.
            
        Returns:
            Lista de IDs dos documentos adicionados.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Coleção '{collection_name}' não encontrada.")
        
        collection = self.collections[collection_name]
        
        # Gera embeddings para os textos
        embeddings_list = [embeddings.embed_query(text) for text in texts]
        
        # Se IDs não foram fornecidos, gera IDs únicos
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Adiciona os documentos à coleção
        collection.add(
            embeddings=embeddings_list,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def process_and_add_document(self, collection_name: str, document: str, 
                               metadata: Dict[str, Any], document_id: Optional[str] = None) -> List[str]:
        """
        Processa um documento (divide em chunks) e adiciona à coleção.
        
        Args:
            collection_name: Nome da coleção onde os chunks serão adicionados.
            document: Texto completo do documento.
            metadata: Metadados base associados ao documento.
            document_id: ID opcional do documento. Se não fornecido, um ID será gerado.
            
        Returns:
            Lista de IDs dos chunks adicionados.
        """
        # Divide o documento em chunks
        chunks = text_splitter.split_text(document)
        
        # Prepara metadados para cada chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["chunk_count"] = len(chunks)
            metadatas.append(chunk_metadata)
        
        # Gera IDs para os chunks baseados no document_id
        if document_id is None:
            import uuid
            document_id = str(uuid.uuid4())
        
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Adiciona os chunks à coleção
        return self.add_documents(collection_name, chunks, metadatas, chunk_ids)
    
    def query(self, collection_name: str, query_text: str, n_results: int = 5, 
             filter_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza uma consulta na coleção especificada.
        
        Args:
            collection_name: Nome da coleção a ser consultada.
            query_text: Texto da consulta.
            n_results: Número de resultados a retornar.
            filter_criteria: Critérios opcionais para filtrar os resultados.
            
        Returns:
            Dicionário com os resultados da consulta.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Coleção '{collection_name}' não encontrada.")
        
        collection = self.collections[collection_name]
        
        # Gera embedding para a consulta
        query_embedding = embeddings.embed_query(query_text)
        
        # Realiza a consulta
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_criteria
        )
        
        return results
    
    def query_all_collections(self, query_text: str, n_results_per_collection: int = 3) -> Dict[str, Any]:
        """
        Realiza uma consulta em todas as coleções.
        
        Args:
            query_text: Texto da consulta.
            n_results_per_collection: Número de resultados a retornar por coleção.
            
        Returns:
            Dicionário com os resultados da consulta por coleção.
        """
        all_results = {}
        
        for collection_name in self.collections:
            try:
                results = self.query(collection_name, query_text, n_results_per_collection)
                all_results[collection_name] = results
            except Exception as e:
                print(f"Erro ao consultar coleção '{collection_name}': {e}")
                all_results[collection_name] = {"error": str(e)}
        
        return all_results
    
    def delete_document(self, collection_name: str, document_id: str) -> None:
        """
        Remove um documento e seus chunks de uma coleção.
        
        Args:
            collection_name: Nome da coleção.
            document_id: ID do documento a ser removido.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Coleção '{collection_name}' não encontrada.")
        
        collection = self.collections[collection_name]
        
        # Remove todos os chunks associados ao document_id
        collection.delete(where={"document_id": document_id})
    
    def reset_collection(self, collection_name: str) -> None:
        """
        Limpa todos os documentos de uma coleção.
        
        Args:
            collection_name: Nome da coleção a ser limpa.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Coleção '{collection_name}' não encontrada.")
        
        # Recria a coleção
        self.client.delete_collection(collection_name)
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"description": COLLECTIONS[collection_name]}
        )
        self.collections[collection_name] = collection
        print(f"Coleção '{collection_name}' foi redefinida.")
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre uma coleção.
        
        Args:
            collection_name: Nome da coleção.
            
        Returns:
            Dicionário com estatísticas da coleção.
        """
        if collection_name not in self.collections:
            raise ValueError(f"Coleção '{collection_name}' não encontrada.")
        
        collection = self.collections[collection_name]
        
        # Obtém contagem de documentos
        count = collection.count()
        
        # Obtém alguns metadados de exemplo
        sample = collection.peek(10)
        
        return {
            "name": collection_name,
            "description": COLLECTIONS[collection_name],
            "document_count": count,
            "sample": sample
        }
    
    def get_all_collections_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtém estatísticas sobre todas as coleções.
        
        Returns:
            Dicionário com estatísticas de todas as coleções.
        """
        stats = {}
        
        for collection_name in self.collections:
            stats[collection_name] = self.get_collection_stats(collection_name)
        
        return stats


# Importa a versão robusta
from .robust_vector_db import get_robust_vector_database, RobustVectorDatabase

# Função para criar uma instância da base de dados vetorial
def get_vector_database() -> VectorDatabase:
    """
    Cria e retorna uma instância robusta da base de dados vetorial.
    
    Returns:
        Instância robusta da base de dados vetorial.
    """
    return get_robust_vector_database()

# Mantém compatibilidade com a interface anterior
VectorDatabase = RobustVectorDatabase
