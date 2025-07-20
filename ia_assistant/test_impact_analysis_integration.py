"""
Teste de integração para validação da análise de impacto.
Valida integração entre detecção de mudanças e análise de impacto.
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
from analysis.impact_analyzer import ImpactAnalyzer, ImpactLevel

def test_impact_analysis_integration():
    """Testa a integração entre detecção de mudanças e análise de impacto."""
    print("🔍 Testando integração entre detecção de mudanças e análise de impacto...")
    
    try:
        # Cria diretório temporário para teste
        temp_dir = tempfile.mkdtemp()
        test_docs_dir = os.path.join(temp_dir, "docs")
        os.makedirs(test_docs_dir, exist_ok=True)
        
        print(f"✅ Diretório de teste criado: {test_docs_dir}")
        
        # Cria arquivos de documentação com dependências
        initial_files = {
            "adr_001.md": "# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce.\n\nVeja também [ADR 002](adr_002.md).",
            "adr_002.md": "# ADR 002: DDD\n\n## Contexto\nImplementa [conceitos DDD](ddd_concepts.md).\n\nBaseado em [ADR 001](adr_001.md).",
            "ddd_concepts.md": "# DDD Concepts\n\n## Agregados\nClusters de objetos de domínio.\n\nReferencia [ADR 001](adr_001.md).",
            "implementation.py": "# Implementation\nimport adr_001\nfrom ddd_concepts import DomainModel\n\n# Baseado em ADR 001"
        }
        
        for filename, content in initial_files.items():
            file_path = os.path.join(test_docs_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        print(f"✅ {len(initial_files)} arquivos com dependências criados")
        
        # Inicializa analisador de impacto
        impact_analyzer = ImpactAnalyzer([test_docs_dir])
        print("✅ Analisador de impacto inicializado")
        
        # Inicializa monitor
        monitor = KnowledgeBaseMonitor(
            base_paths=[test_docs_dir],
            cache_manager=intelligent_cache,
            check_interval=5
        )
        
        print("✅ Monitor inicializado")
        
        # Testa análise de impacto inicial
        print("\n📊 Análise de impacto inicial:")
        
        adr_file = os.path.join(test_docs_dir, "adr_001.md")
        initial_analysis = impact_analyzer.analyze_impact(adr_file)
        
        print(f"  Arquivo: {os.path.basename(adr_file)}")
        print(f"  Nível de impacto: {initial_analysis.impact_level.value}")
        print(f"  Arquivos afetados: {len(initial_analysis.affected_files)}")
        print(f"  Esforço estimado: {initial_analysis.estimated_effort}")
        
        # Testa detecção de mudanças com análise de impacto
        print("\n🧪 Testando detecção de mudanças com análise de impacto...")
        
        # 1. Modifica arquivo ADR crítico
        with open(adr_file, 'w') as f:
            f.write("# ADR 001: Arquitetura Hexagonal\n\n## Contexto\nProjeto de e-commerce MODIFICADO.\n\n## Nova Seção\nConteúdo adicional.\n\nVeja também [ADR 002](adr_002.md).")
        
        print("📝 Arquivo ADR crítico modificado")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
                
                # Analisa impacto da mudança
                if change.change_type in [ChangeType.CONTENT_CHANGED, ChangeType.FILE_ADDED, ChangeType.FILE_DELETED]:
                    analysis = impact_analyzer.analyze_impact(change.file_path)
                    print(f"    Impacto: {analysis.impact_level.value} - {len(analysis.affected_files)} arquivos afetados")
                    
                    # Mostra recomendações
                    if analysis.recommendations:
                        print("    Recomendações:")
                        for rec in analysis.recommendations[:3]:  # Mostra apenas as 3 primeiras
                            print(f"      • {rec}")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # 2. Adiciona novo arquivo que depende de outros
        new_file = os.path.join(test_docs_dir, "adr_003.md")
        with open(new_file, 'w') as f:
            f.write("# ADR 003: Novas Decisões\n\n## Contexto\nNovas decisões arquiteturais.\n\n## Dependências\nBaseado em [ADR 001](adr_001.md) e [DDD](ddd_concepts.md).")
        
        print("📄 Novo arquivo ADR com dependências criado")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
                
                # Analisa impacto da mudança
                if change.change_type in [ChangeType.CONTENT_CHANGED, ChangeType.FILE_ADDED, ChangeType.FILE_DELETED]:
                    analysis = impact_analyzer.analyze_impact(change.file_path)
                    print(f"    Impacto: {analysis.impact_level.value} - {len(analysis.affected_files)} arquivos afetados")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # 3. Remove arquivo que é referenciado por outros
        ddd_file = os.path.join(test_docs_dir, "ddd_concepts.md")
        os.remove(ddd_file)
        
        print("🗑️  Arquivo DDD referenciado removido")
        
        # Força verificação
        changes = monitor.force_check()
        
        if changes:
            print(f"✅ {len(changes)} mudanças detectadas:")
            for change in changes:
                print(f"  - {change.description} ({change.change_type.value})")
                
                # Analisa impacto da mudança
                if change.change_type in [ChangeType.CONTENT_CHANGED, ChangeType.FILE_ADDED, ChangeType.FILE_DELETED]:
                    analysis = impact_analyzer.analyze_impact(change.file_path)
                    print(f"    Impacto: {analysis.impact_level.value} - {len(analysis.affected_files)} arquivos afetados")
        else:
            print("⚠️  Nenhuma mudança detectada")
        
        # Testa estatísticas de dependências
        print("\n📈 Estatísticas de dependências:")
        
        stats = impact_analyzer.get_dependency_stats()
        print(f"Total de arquivos: {stats.get('total_files', 0)}")
        print(f"Total de dependências: {stats.get('total_dependencies', 0)}")
        
        # Mostra dependências mais fortes
        strongest_deps = stats.get('strongest_dependencies', [])
        if strongest_deps:
            print("Dependências mais fortes:")
            for source, target, strength in strongest_deps[:3]:
                print(f"  {os.path.basename(source)} → {os.path.basename(target)} (força: {strength:.2f})")
        
        # Mostra arquivos mais referenciados
        most_referenced = stats.get('most_referenced_files', [])
        if most_referenced:
            print("Arquivos mais referenciados:")
            for file_path, count in most_referenced[:3]:
                print(f"  {os.path.basename(file_path)}: {count} referências")
        
        # Testa histórico de análises
        print("\n📋 Histórico de análises de impacto:")
        
        history = impact_analyzer.get_impact_history()
        print(f"Total de análises: {len(history)}")
        
        if history:
            print("Últimas análises:")
            for i, analysis in enumerate(history[-3:], 1):
                print(f"  {i}. {os.path.basename(analysis.changed_file)}: {analysis.impact_level.value} ({len(analysis.affected_files)} afetados)")
        
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
    success = test_impact_analysis_integration()
    sys.exit(0 if success else 1) 