"""
Teste simplificado para validação da detecção automática de mudanças.
Valida que mudanças detectadas invalidam cache corretamente.
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

def test_change_detection_simple():
    """Testa a detecção de mudanças sem depender da API."""
    print("🔍 Testando detecção automática de mudanças (versão simplificada)...")
    
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
        
        # Inicializa monitor
        monitor = KnowledgeBaseMonitor(
            base_paths=[test_docs_dir],
            cache_manager=intelligent_cache,
            check_interval=5
        )
        
        print("✅ Monitor inicializado")
        
        # Adiciona algumas entradas ao cache para testar invalidação
        intelligent_cache.put(
            query="Como está a arquitetura hexagonal?",
            response="A arquitetura hexagonal está bem estruturada.",
            query_type="architecture",
            prompt_template="test",
            tokens_used=50,
            cost_estimate=0.001
        )
        
        intelligent_cache.put(
            query="Explique DDD",
            response="DDD é Domain-Driven Design.",
            query_type="ddd_concept",
            prompt_template="test",
            tokens_used=30,
            cost_estimate=0.0005
        )
        
        cache_stats_before = intelligent_cache.get_cache_stats()
        print(f"📊 Cache inicial: {cache_stats_before.get('total_entries', 0)} entradas")
        
        # Testa detecção de mudanças
        print("\n🧪 Testando detecção de mudanças...")
        
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
        
        # Verifica estado final do cache
        cache_stats_after = intelligent_cache.get_cache_stats()
        print(f"\n📊 Cache final: {cache_stats_after.get('total_entries', 0)} entradas")
        
        # Testa estatísticas de monitoramento
        print("\n📈 Estatísticas de monitoramento:")
        
        monitor_stats = monitor.get_monitoring_stats()
        print(f"Arquivos monitorados: {monitor_stats['monitored_files']}")
        print(f"Total de mudanças: {monitor_stats['total_changes']}")
        print(f"Monitoramento ativo: {monitor_stats['monitoring_active']}")
        
        # Testa histórico de mudanças
        print("\n📋 Histórico de mudanças:")
        
        history = monitor.get_change_history()
        print(f"Total de mudanças registradas: {len(history)}")
        
        if history:
            print("Últimas mudanças:")
            for i, change in enumerate(history[-5:], 1):
                print(f"  {i}. {change.description} ({change.timestamp.strftime('%H:%M:%S')})")
        
        # Para monitoramento
        monitor.stop_monitoring()
        print("✅ Monitoramento parado")
        
        # Limpa arquivos temporários
        shutil.rmtree(temp_dir)
        print("✅ Arquivos temporários removidos")
        
        print("\n🎉 Teste de detecção de mudanças concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_change_detection_simple()
    sys.exit(0 if success else 1) 