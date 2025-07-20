"""
Teste simples para validar a base de dados robusta.
Testa apenas a funcionalidade de retry e health check sem depender da API da OpenAI.
"""

import os
import sys
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.robust_vector_db import get_robust_vector_database

def test_robust_database():
    """Testa a base de dados robusta."""
    print("🔍 Testando base de dados robusta...")
    
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
        test_collection = "test_collection"
        collection = robust_db.get_or_create_collection(test_collection, {"description": "Coleção de teste"})
        print(f"✅ Coleção '{test_collection}' criada/obtida com sucesso")
        
        # Testa adição de documentos
        documents = ["Documento de teste 1", "Documento de teste 2"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        ids = ["id1", "id2"]
        
        result_ids = robust_db.add_documents(test_collection, documents, metadatas, ids)
        print(f"✅ Documentos adicionados: {result_ids}")
        
        # Testa busca
        search_results = robust_db.search(test_collection, ["teste"], n_results=2)
        print(f"✅ Busca realizada: {len(search_results.get('documents', [[]])[0])} resultados")
        
        # Testa obtenção de informações da coleção
        collection_info = robust_db.get_collection_info(test_collection)
        print(f"✅ Informações da coleção: {collection_info}")
        
        # Exibe métricas
        print("\n📈 Métricas de Performance:")
        metrics = robust_db.get_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        # Limpa coleção de teste
        robust_db.delete_collection(test_collection)
        print(f"✅ Coleção '{test_collection}' removida")
        
        print("\n🎉 Teste da base de dados robusta concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_robust_database()
    sys.exit(0 if success else 1) 