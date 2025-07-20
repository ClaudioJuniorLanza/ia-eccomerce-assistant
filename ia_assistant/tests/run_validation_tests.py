"""
Script para executar todos os testes de validação da assistente de IA.
Executa testes de infraestrutura, coleta de dados, processamento de consultas e integração.
"""

import os
import sys
import unittest
import argparse
import json
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests(verbose=False, output_file=None):
    """
    Executa todos os testes de validação da assistente de IA.
    
    Args:
        verbose: Se True, exibe informações detalhadas dos testes
        output_file: Arquivo para salvar os resultados dos testes
        
    Returns:
        Dicionário com resultados dos testes
    """
    print("🧪 Iniciando Validação Completa da Assistente de IA")
    print("=" * 60)
    
    # Lista de módulos de teste
    test_modules = [
        'ia_assistant.tests.test_infrastructure',
        'ia_assistant.tests.test_data_collection',
        'ia_assistant.tests.test_query_processing',
        'ia_assistant.tests.test_integration'
    ]
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'errors': 0,
        'test_suites': {}
    }
    
    # Executa cada módulo de teste
    for module_name in test_modules:
        print(f"\n📋 Executando: {module_name}")
        print("-" * 40)
        
        try:
            # Carrega o módulo de teste
            module = __import__(module_name, fromlist=[''])
            
            # Cria um test suite para o módulo
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # Executa os testes
            runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
            test_result = runner.run(suite)
            
            # Coleta resultados
            module_results = {
                'total': test_result.testsRun,
                'passed': test_result.testsRun - len(test_result.failures) - len(test_result.errors),
                'failed': len(test_result.failures),
                'errors': len(test_result.errors),
                'failures': [str(failure[1]) for failure in test_result.failures],
                'errors': [str(error[1]) for error in test_result.errors]
            }
            
            results['test_suites'][module_name] = module_results
            results['total_tests'] += module_results['total']
            results['passed_tests'] += module_results['passed']
            results['failed_tests'] += module_results['failed']
            results['errors'] += module_results['errors']
            
            # Exibe resumo do módulo
            status = "✅ PASSOU" if module_results['failed'] == 0 and module_results['errors'] == 0 else "❌ FALHOU"
            print(f"Status: {status}")
            print(f"Total: {module_results['total']}, Passou: {module_results['passed']}, Falhou: {module_results['failed']}, Erros: {module_results['errors']}")
            
        except Exception as e:
            print(f"❌ Erro ao executar {module_name}: {e}")
            results['test_suites'][module_name] = {
                'error': str(e),
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 1
            }
    
    # Exibe resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL DOS TESTES")
    print("=" * 60)
    
    total_suites = len(results['test_suites'])
    passed_suites = sum(1 for suite in results['test_suites'].values() 
                       if suite.get('failed', 0) == 0 and suite.get('errors', 0) == 0)
    
    print(f"📦 Suites de Teste: {total_suites}")
    print(f"✅ Suites Passaram: {passed_suites}")
    print(f"❌ Suites Falharam: {total_suites - passed_suites}")
    print(f"🧪 Total de Testes: {results['total_tests']}")
    print(f"✅ Testes Passaram: {results['passed_tests']}")
    print(f"❌ Testes Falharam: {results['failed_tests']}")
    print(f"⚠️  Erros: {results['errors']}")
    
    # Calcula taxa de sucesso
    if results['total_tests'] > 0:
        success_rate = (results['passed_tests'] / results['total_tests']) * 100
        print(f"📈 Taxa de Sucesso: {success_rate:.1f}%")
    
    # Salva resultados em arquivo se solicitado
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultados salvos em: {output_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
    
    # Retorna código de saída apropriado
    if results['failed_tests'] > 0 or results['errors'] > 0:
        print("\n❌ VALIDAÇÃO FALHOU - Alguns testes falharam")
        return 1
    else:
        print("\n✅ VALIDAÇÃO PASSOU - Todos os testes passaram")
        return 0

def run_specific_test(test_name, verbose=False):
    """
    Executa um teste específico.
    
    Args:
        test_name: Nome do teste específico
        verbose: Se True, exibe informações detalhadas
        
    Returns:
        Código de saída (0 para sucesso, 1 para falha)
    """
    print(f"🧪 Executando teste específico: {test_name}")
    
    try:
        # Executa o teste específico
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_name)
        
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✅ Teste passou")
            return 0
        else:
            print("❌ Teste falhou")
            return 1
            
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return 1

def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(description="Validação Completa da Assistente de IA")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Exibe informações detalhadas dos testes")
    parser.add_argument("--output", "-o", type=str,
                       help="Arquivo para salvar os resultados dos testes")
    parser.add_argument("--test", "-t", type=str,
                       help="Executa um teste específico")
    
    args = parser.parse_args()
    
    if args.test:
        return run_specific_test(args.test, args.verbose)
    else:
        return run_all_tests(args.verbose, args.output)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 