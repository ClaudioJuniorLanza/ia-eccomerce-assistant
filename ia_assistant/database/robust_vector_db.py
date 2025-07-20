"""
Base de dados vetorial robusta com retry mechanism e tratamento de falhas.
Implementa padrões de resiliência para garantir operações confiáveis.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
import chromadb
from chromadb.config import Settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustVectorDatabase:
    """
    Implementação robusta da base de dados vetorial com retry mechanism,
    tratamento de falhas e monitoramento de performance.
    """
    
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 max_retry_delay: float = 10.0,
                 backoff_factor: float = 2.0):
        """
        Inicializa a base de dados vetorial robusta.
        
        Args:
            persist_directory: Diretório para persistir os dados
            max_retries: Número máximo de tentativas
            retry_delay: Delay inicial entre tentativas (segundos)
            max_retry_delay: Delay máximo entre tentativas (segundos)
            backoff_factor: Fator de crescimento do delay
        """
        self.persist_directory = persist_directory
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_retry_delay = max_retry_delay
        self.backoff_factor = backoff_factor
        
        # Garante que o diretório existe
        os.makedirs(persist_directory, exist_ok=True)
        
        # Inicializa a conexão com retry
        self.client = self._initialize_client_with_retry()
        
        # Métricas de performance
        self.operation_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'retry_operations': 0,
            'average_response_time': 0.0
        }
    
    def _initialize_client_with_retry(self) -> chromadb.Client:
        """
        Inicializa o cliente ChromaDB com retry mechanism.
        
        Returns:
            Cliente ChromaDB inicializado
            
        Raises:
            Exception: Se não conseguir inicializar após todas as tentativas
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Tentativa {attempt + 1} de inicializar ChromaDB")
                
                client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                
                # Testa a conexão
                client.heartbeat()
                logger.info("ChromaDB inicializado com sucesso")
                return client
                
            except Exception as e:
                logger.warning(f"Falha na tentativa {attempt + 1}: {e}")
                
                if attempt == self.max_retries - 1:
                    logger.error("Falha ao inicializar ChromaDB após todas as tentativas")
                    raise Exception(f"Não foi possível inicializar ChromaDB: {e}")
                
                # Calcula delay com backoff exponencial
                delay = min(self.retry_delay * (self.backoff_factor ** attempt), self.max_retry_delay)
                logger.info(f"Aguardando {delay} segundos antes da próxima tentativa")
                time.sleep(delay)
    
    def retry_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Executa uma operação com retry mechanism.
        
        Args:
            operation: Função a ser executada
            *args: Argumentos posicionais para a operação
            **kwargs: Argumentos nomeados para a operação
            
        Returns:
            Resultado da operação
            
        Raises:
            Exception: Se a operação falhar após todas as tentativas
        """
        start_time = time.time()
        last_exception = None
        operation_successful = False
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Executando operação (tentativa {attempt + 1})")
                result = operation(*args, **kwargs)
                
                # Registra sucesso apenas uma vez por operação
                if not operation_successful:
                    self._record_success(time.time() - start_time)
                    operation_successful = True
                
                return result
                
            except Exception as e:
                last_exception = e
                
                logger.warning(f"Falha na operação (tentativa {attempt + 1}): {e}")
                
                if attempt == self.max_retries - 1:
                    # Registra falha apenas uma vez por operação
                    self._record_failure()
                    logger.error("Operação falhou após todas as tentativas")
                    raise last_exception
                
                # Calcula delay com backoff exponencial
                delay = min(self.retry_delay * (self.backoff_factor ** attempt), self.max_retry_delay)
                logger.info(f"Aguardando {delay} segundos antes da próxima tentativa")
                time.sleep(delay)
    
    def _record_success(self, response_time: float):
        """Registra uma operação bem-sucedida."""
        self.operation_metrics['total_operations'] += 1
        self.operation_metrics['successful_operations'] += 1
        
        # Atualiza tempo médio de resposta
        total_successful = self.operation_metrics['successful_operations']
        current_avg = self.operation_metrics['average_response_time']
        self.operation_metrics['average_response_time'] = (
            (current_avg * (total_successful - 1) + response_time) / total_successful
        )
    
    def _record_failure(self):
        """Registra uma operação falhada."""
        self.operation_metrics['total_operations'] += 1
        self.operation_metrics['failed_operations'] += 1
    
    def _record_retry(self):
        """Registra uma operação que precisou de retry."""
        self.operation_metrics['retry_operations'] += 1
    
    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None) -> chromadb.Collection:
        """
        Obtém ou cria uma coleção com retry mechanism.
        
        Args:
            name: Nome da coleção
            metadata: Metadados da coleção
            
        Returns:
            Coleção ChromaDB
        """
        def operation():
            try:
                return self.client.get_collection(name=name)
            except Exception:
                return self.client.create_collection(name=name, metadata=metadata or {})
        
        return self.retry_operation(operation)
    
    def add_documents(self, 
                     collection_name: str,
                     documents: List[str],
                     metadatas: List[Dict],
                     ids: List[str]) -> List[str]:
        """
        Adiciona documentos a uma coleção com retry mechanism.
        
        Args:
            collection_name: Nome da coleção
            documents: Lista de documentos
            metadatas: Lista de metadados
            ids: Lista de IDs
            
        Returns:
            Lista de IDs dos documentos adicionados
        """
        def operation():
            collection = self.get_or_create_collection(collection_name)
            return collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        return self.retry_operation(operation)
    
    def search(self, 
              collection_name: str,
              query_texts: List[str],
              n_results: int = 5,
              where: Optional[Dict] = None,
              where_document: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Realiza busca em uma coleção com retry mechanism.
        
        Args:
            collection_name: Nome da coleção
            query_texts: Textos para busca
            n_results: Número de resultados
            where: Filtros de metadados
            where_document: Filtros de documento
            
        Returns:
            Resultados da busca
        """
        def operation():
            collection = self.get_or_create_collection(collection_name)
            return collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
        
        return self.retry_operation(operation)
    
    def delete_documents(self, 
                        collection_name: str,
                        ids: List[str]) -> None:
        """
        Remove documentos de uma coleção com retry mechanism.
        
        Args:
            collection_name: Nome da coleção
            ids: IDs dos documentos a remover
        """
        def operation():
            collection = self.get_or_create_collection(collection_name)
            collection.delete(ids=ids)
        
        self.retry_operation(operation)
    
    def update_documents(self,
                        collection_name: str,
                        ids: List[str],
                        documents: List[str],
                        metadatas: List[Dict]) -> None:
        """
        Atualiza documentos em uma coleção com retry mechanism.
        
        Args:
            collection_name: Nome da coleção
            ids: IDs dos documentos
            documents: Novos documentos
            metadatas: Novos metadados
        """
        def operation():
            collection = self.get_or_create_collection(collection_name)
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
        self.retry_operation(operation)
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Obtém informações sobre uma coleção.
        
        Args:
            collection_name: Nome da coleção
            
        Returns:
            Informações da coleção
        """
        def operation():
            collection = self.get_or_create_collection(collection_name)
            return {
                'name': collection.name,
                'count': collection.count(),
                'metadata': collection.metadata
            }
        
        return self.retry_operation(operation)
    
    def list_collections(self) -> List[str]:
        """
        Lista todas as coleções.
        
        Returns:
            Lista de nomes das coleções
        """
        def operation():
            return [col.name for col in self.client.list_collections()]
        
        return self.retry_operation(operation)
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Remove uma coleção.
        
        Args:
            collection_name: Nome da coleção a remover
        """
        def operation():
            self.client.delete_collection(name=collection_name)
        
        self.retry_operation(operation)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtém métricas de performance da base de dados.
        
        Returns:
            Dicionário com métricas
        """
        total_ops = self.operation_metrics['total_operations']
        success_rate = 0.0
        if total_ops > 0:
            success_rate = (self.operation_metrics['successful_operations'] / total_ops) * 100
        
        return {
            **self.operation_metrics,
            'success_rate_percentage': success_rate,
            'retry_rate_percentage': (self.operation_metrics['retry_operations'] / max(total_ops, 1)) * 100
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da base de dados.
        
        Returns:
            Status de saúde da base de dados
        """
        try:
            # Testa conexão
            self.client.heartbeat()
            
            # Obtém métricas
            metrics = self.get_metrics()
            
            return {
                'status': 'healthy',
                'connection': 'ok',
                'metrics': metrics,
                'collections_count': len(self.list_collections())
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connection': 'failed',
                'error': str(e),
                'metrics': self.get_metrics()
            }
    
    def reset_metrics(self) -> None:
        """Reseta as métricas de performance."""
        self.operation_metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'retry_operations': 0,
            'average_response_time': 0.0
        }
        logger.info("Métricas resetadas")

def get_robust_vector_database(persist_directory: str = "./chroma_db") -> RobustVectorDatabase:
    """
    Factory function para criar uma instância robusta da base de dados vetorial.
    
    Args:
        persist_directory: Diretório para persistir os dados
        
    Returns:
        Instância robusta da base de dados vetorial
    """
    return RobustVectorDatabase(persist_directory=persist_directory) 