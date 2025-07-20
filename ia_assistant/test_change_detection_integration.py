"""
Teste de integração para o sistema de detecção automática de mudanças.
Valida a integração completa com cache e monitoramento.
"""

import os
import sys
import time
import tempfile
import shutil
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoring.change_detector import KnowledgeBaseMonitor, ChangeType
from cache.intelligent_cache import intelligent_cache

def test_change_detection_integration():
    """Testa a integração completa do sistema de detecção de mudanças."""
    print("🔍 Testando integração do sistema de detecção automática de mudanças...")
    
    try:
        # Cria diretório temporário para teste
        temp_dir = tempfile.mkdtemp()
        test_dir = os.path.join(temp_dir, "test_knowledge_base")
        os.makedirs(test_dir, exist_ok=True)
        
        print(f"✅ Diretório de teste criado: {test_dir}")
        
        # Cria arquivos de teste
        test_files = {
            "adr_001.md": "# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce.",
            "ddd_concepts.md": "# DDD Concepts\n\n## Agregados\nClusters de objetos de domínio.",
            "implementation_guide.md": "# Guia de Implementação\n\n## Passo 1\nConfigure o projeto."
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        print(f"✅ {len(test_files)} arquivos de teste criados")
        
        # Inicializa monitor
        monitor = KnowledgeBaseMonitor(
            base_paths=[test_dir],
            cache_manager=intelligent_cache,
            check_interval=5  # 5 segundos para teste
        )
        
        print("✅ Monitor inicializado")
        
        # Verifica estado inicial
        initial_stats = monitor.get_monitoring_stats()
        print(f"📊 Estado inicial: {initial_stats['monitored_files']} arquivos monitorados")
        
        # Testa detecção de mudanças
        print("\n🧪 Testando detecção de mudanças...")
        
        # 1. Modifica arquivo existente
        adr_file = os.path.join(test_dir, "adr_001.md")
        with open(adr_file, 'w') as f:
            f.write("# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce MODIFICADO.")
        
        print("📝 Arquivo ADR modificado")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # 2. Adiciona novo arquivo
        new_file = os.path.join(test_dir, "new_adr.md")
        with open(new_file, 'w') as f:
            f.write("# ADR 002: Novas Decisões\n\n## Contexto\nNovas decisões arquiteturais.")
        
        print("📄 Novo arquivo ADR criado")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # 3. Remove arquivo
        ddd_file = os.path.join(test_dir, "ddd_concepts.md")
        os.remove(ddd_file)
        
        print("🗑️  Arquivo DDD removido")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # Testa histórico de mudanças
        print("\n📈 Testando histórico de mudanças...")
        
        history = monitor.get_change_history()
        print(f"Total de mudanças registradas: {len(history)}")
        
        if history:
            print("Últimas mudanças:")
            for i, change in enumerate(history[-3:], 1):
                print(f"  {i}. {change.description} ({change.timestamp.strftime('%H:%M:%S')})")
        
        # Testa estatísticas finais
        print("\n📊 Estatísticas finais:")
        
        final_stats = monitor.get_monitoring_stats()
        print(f"Arquivos monitorados: {final_stats['monitored_files']}")
        print(f"Total de mudanças: {final_stats['total_changes']}")
        print(f"Monitoramento ativo: {final_stats['monitoring_active']}")
        
        # Testa integração com cache
        print("\n💾 Testando integração com cache...")
        
        # Adiciona algumas entradas ao cache
        intelligent_cache.put(
            query="Como está a arquitetura hexagonal?",
            response="A arquitetura hexagonal está bem estruturada.",
            query_type="architecture",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.001
        )
        
        cache_stats_before = intelligent_cache.get_cache_stats()
        print(f"Cache antes: {cache_stats_before.get('total_entries', 0)} entradas")
        
        # Modifica arquivo ADR para invalidar cache
        with open(adr_file, 'w') as f:
            f.write("# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce FINAL.")
        
        monitor.force_check()
        
        cache_stats_after = intelligent_cache.get_cache_stats()
        print(f"Cache depois: {cache_stats_after.get('total_entries', 0)} entradas")
        
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
    success = test_change_detection_integration()
    sys.exit(0 if success else 1) 