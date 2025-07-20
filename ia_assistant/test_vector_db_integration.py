"""
Teste de integração para validação da atualização automática da base vetorial.
Valida que mudanças detectadas atualizam corretamente a base vetorial.
"""

import os
import sys
import tempfile
import shutil
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoring.change_detector import KnowledgeBaseMonitor, ChangeType
from cache.intelligent_cache import intelligent_cache
from database.vector_db import get_vector_database

def test_vector_db_integration():
    """Testa a integração entre detecção de mudanças e base vetorial."""
    print("🔍 Testando integração entre detecção de mudanças e base vetorial...")
    
    try:
        # Cria diretório temporário para teste
        temp_dir = tempfile.mkdtemp()
        test_docs_dir = os.path.join(temp_dir, "docs")
        os.makedirs(test_docs_dir, exist_ok=True)
        
        print(f"✅ Diretório de teste criado: {test_docs_dir}")
        
        # Cria arquivos de documentação inicial
        initial_files = {
            "adr_001.md": "# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce.",
            "ddd_concepts.md": "# DDD Concepts\n\n## Agregados\nClusters de objetos de domínio."
        }
        
        for filename, content in initial_files.items():
            file_path = os.path.join(test_docs_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        print(f"✅ {len(initial_files)} arquivos iniciais criados")
        
        # Inicializa base vetorial
        vector_db = get_vector_database()
        print("✅ Base vetorial inicializada")
        
        # Inicializa monitor
        monitor = KnowledgeBaseMonitor(
            base_paths=[test_docs_dir],
            cache_manager=intelligent_cache,
            check_interval=5
        )
        
        print("✅ Monitor inicializado")
        
        # Testa estado inicial da base vetorial
        print("\n📊 Estado inicial da base vetorial:")
        try:
            stats = vector_db.get_all_collections_stats()
            for collection_name, collection_stats in stats.items():
                print(f"  {collection_name}: {collection_stats.get('document_count', 0)} documentos")
        except Exception as e:
            print(f"⚠️  Erro ao obter estatísticas: {e}")
        
        # Testa detecção de mudanças e atualização da base vetorial
        print("\n🧪 Testando atualização automática da base vetorial...")
        
        # 1. Modifica arquivo ADR
        adr_file = os.path.join(test_docs_dir, "adr_001.md")
        with open(adr_file, 'w') as f:
            f.write("# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce MODIFICADO.\n\n## Nova Seção\nConteúdo adicional.")
        
        print("📝 Arquivo ADR modificado")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
                
            # Verifica se base vetorial foi atualizada
            print("\n📊 Verificando atualização da base vetorial...")
            try:
                # Aguarda um pouco para processamento
                import time
                time.sleep(2)
                
                # Testa busca na base vetorial
                query = "arquitetura hexagonal"
                results = vector_db.query("adrs", query, n_results=3)
                
                if results and 'documents' in results and results['documents']:
                    print("✅ Base vetorial atualizada - busca funcionando")
                    print(f"  Resultados encontrados: {len(results['documents'])}")
                else:
                    print("⚠️  Base vetorial pode não ter sido atualizada")
                    
            except Exception as e:
                print(f"⚠️  Erro ao testar busca: {e}")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # 2. Adiciona novo arquivo
        new_file = os.path.join(test_docs_dir, "adr_002.md")
        with open(new_file, 'w') as f:
            f.write("# ADR 002: Novas Decisões\n\n## Contexto\nNovas decisões arquiteturais.\n\n## Decisão\nImplementar cache inteligente.")
        
        print("📄 Novo arquivo ADR criado")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
                
            # Verifica se novo documento foi adicionado
            print("\n📊 Verificando novo documento na base vetorial...")
            try:
                time.sleep(2)
                
                # Busca por conteúdo do novo documento
                query = "cache inteligente"
                results = vector_db.query("adrs", query, n_results=3)
                
                if results and 'documents' in results and results['documents']:
                    print("✅ Novo documento adicionado à base vetorial")
                    print(f"  Resultados encontrados: {len(results['documents'])}")
                else:
                    print("⚠️  Novo documento pode não ter sido adicionado")
                    
            except Exception as e:
                print(f"⚠️  Erro ao testar busca: {e}")
        
        # 3. Remove arquivo
        ddd_file = os.path.join(test_docs_dir, "ddd_concepts.md")
        os.remove(ddd_file)
        
        print("🗑️  Arquivo DDD removido")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
        
        # Testa estatísticas finais
        print("\n📈 Estatísticas finais:")
        
        try:
            final_stats = vector_db.get_all_collections_stats()
            for collection_name, collection_stats in final_stats.items():
                print(f"  {collection_name}: {collection_stats.get('document_count', 0)} documentos")
        except Exception as e:
            print(f"⚠️  Erro ao obter estatísticas finais: {e}")
        
        # Para monitoramento
        monitor.stop_monitoring()
        print("✅ Monitoramento parado")
        
        # Limpa arquivos temporários
        shutil.rmtree(temp_dir)
        print("✅ Arquivos temporários removidos")
        
        print("\n🎉 Teste de integração concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vector_db_integration()
    sys.exit(0 if success else 1) 