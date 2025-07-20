"""
Teste básico da base de dados robusta.
Testa apenas a funcionalidade de retry e health check sem operações que dependam de embeddings.
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.robust_vector_db import get_robust_vector_database

def test_robust_database_basic():
    """Testa a base de dados robusta com operações básicas."""
    print("🔍 Testando base de dados robusta (operações básicas)...")
    
    try:
        # Cria instância da base robusta
        robust_db = get_robust_vector_database()
        print("✅ Base de dados robusta criada com sucesso")
        
        # Testa health check
        print("\n📊 Verificando health check...")
        health_status = robust_db.health_check()
        
        print(f"Status: {health_status['status']}")
        print(f"Conexão: {health_status['connection']}")
        print(f"Número de coleções: {health_status['collections_count']}")
        
        if health_status['status'] == 'healthy':
            print("✅ Base de dados está saudável")
        else:
            print(f"⚠️  Base de dados com problemas: {health_status.get('error', 'Erro desconhecido')}")
        
        # Testa operações básicas
        print("\n🧪 Testando operações básicas...")
        
        # Lista coleções
        collections = robust_db.list_collections()
        print(f"Coleções existentes: {collections}")
        
        # Testa criação de coleção
        test_collection = "test_collection_basic"
        collection = robust_db.get_or_create_collection(test_collection, {"description": "Coleção de teste básico"})
        print(f"✅ Coleção '{test_collection}' criada/obtida com sucesso")
        
        # Testa obtenção de informações da coleção
        collection_info = robust_db.get_collection_info(test_collection)
        print(f"✅ Informações da coleção: {collection_info}")
        
        # Testa operações de métricas
        print("\n📈 Testando métricas...")
        
        # Reseta métricas
        robust_db.reset_metrics()
        print("✅ Métricas resetadas")
        
        # Exibe métricas iniciais
        metrics = robust_db.get_metrics()
        print("Métricas iniciais:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Testa operação simples
        def test_operation():
            return "success"
        
        result = robust_db.retry_operation(test_operation)
        print(f"✅ Operação de teste executada: {result}")
        
        # Exibe métricas após operação
        metrics_after = robust_db.get_metrics()
        print("Métricas após operação:")
        for key, value in metrics_after.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Limpa coleção de teste
        robust_db.delete_collection(test_collection)
        print(f"✅ Coleção '{test_collection}' removida")
        
        print("\n🎉 Teste básico da base de dados robusta concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_robust_database_basic()
    sys.exit(0 if success else 1) 