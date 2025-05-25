"""
Interface de consulta para a assistente de IA.
Implementa uma interface de linha de comando (CLI) para realizar consultas
à base de conhecimento e obter respostas contextualizadas.
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Optional, Union
import json
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Importa a base de dados vetorial
from ia_assistant.database.vector_db import get_vector_database, VectorDatabase

# Configuração de modelos da OpenAI
GPT_3_5_MODEL = "gpt-3.5-turbo-instruct"  # Modelo mais econômico
GPT_4_MODEL = "gpt-4"  # Modelo mais avançado

# Templates de prompts
QUERY_PROMPT_TEMPLATE = """
Você é uma assistente de IA especializada no projeto de e-commerce que utiliza arquitetura hexagonal, 
Domain Driven Design (DDD), Kotlin e outras tecnologias modernas. Sua função é responder perguntas 
sobre o projeto com base no conhecimento que você tem.

Contexto relevante do projeto:
{context}

Pergunta do usuário: {query}

Responda de forma clara, direta e técnica. Se o contexto fornecido não for suficiente para responder 
à pergunta completamente, indique quais informações estão faltando e sugira como o usuário poderia 
refinar sua pergunta.

Resposta:
"""

class QueryProcessor:
    """Processador de consultas para a assistente de IA."""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None, 
                model_name: str = GPT_3_5_MODEL):
        """
        Inicializa o processador de consultas.
        
        Args:
            vector_db: Instância opcional da base de dados vetorial. Se não fornecida, uma nova será criada.
            model_name: Nome do modelo da OpenAI a ser utilizado.
        """
        self.vector_db = vector_db if vector_db is not None else get_vector_database()
        self.model_name = model_name
        
        # Inicializa o modelo de linguagem
        self.llm = OpenAI(model_name=model_name, temperature=0.2)
        
        # Inicializa o template de prompt
        self.prompt_template = PromptTemplate(
            input_variables=["context", "query"],
            template=QUERY_PROMPT_TEMPLATE
        )
        
        # Inicializa a chain de processamento
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def _get_relevant_context(self, query: str, n_results: int = 5) -> str:
        """
        Obtém o contexto relevante para a consulta a partir da base de dados vetorial.
        
        Args:
            query: Texto da consulta.
            n_results: Número de resultados a serem recuperados por coleção.
            
        Returns:
            String com o contexto relevante.
        """
        # Consulta todas as coleções
        all_results = self.vector_db.query_all_collections(query, n_results)
        
        # Formata os resultados em um contexto
        context_parts = []
        
        for collection_name, results in all_results.items():
            if "error" in results:
                continue
                
            if "documents" in results and results["documents"]:
                context_parts.append(f"\n--- Informações de {collection_name} ---\n")
                
                for i, doc in enumerate(results["documents"][0]):
                    # Adiciona metadados relevantes
                    if "metadatas" in results and results["metadatas"][0]:
                        metadata = results["metadatas"][0][i]
                        if "source" in metadata:
                            context_parts.append(f"Fonte: {metadata['source']}")
                        if "document_type" in metadata:
                            context_parts.append(f"Tipo: {metadata['document_type']}")
                    
                    # Adiciona o conteúdo do documento
                    context_parts.append(f"Conteúdo: {doc}\n")
        
        # Se não houver resultados, retorna uma mensagem
        if not context_parts:
            return "Não foram encontradas informações relevantes para esta consulta na base de conhecimento."
        
        return "\n".join(context_parts)
    
    def process_query(self, query: str) -> str:
        """
        Processa uma consulta e retorna uma resposta contextualizada.
        
        Args:
            query: Texto da consulta.
            
        Returns:
            Resposta contextualizada.
        """
        # Obtém o contexto relevante
        context = self._get_relevant_context(query)
        
        # Executa a chain de processamento
        response = self.chain.run(context=context, query=query)
        
        return response
    
    def switch_model(self, model_name: str) -> None:
        """
        Alterna entre modelos da OpenAI.
        
        Args:
            model_name: Nome do modelo a ser utilizado.
        """
        if model_name not in [GPT_3_5_MODEL, GPT_4_MODEL]:
            raise ValueError(f"Modelo não suportado: {model_name}")
        
        self.model_name = model_name
        self.llm = OpenAI(model_name=model_name, temperature=0.2)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        
        print(f"Modelo alterado para: {model_name}")


class CLI:
    """Interface de linha de comando para a assistente de IA."""
    
    def __init__(self, query_processor: Optional[QueryProcessor] = None):
        """
        Inicializa a interface de linha de comando.
        
        Args:
            query_processor: Processador de consultas opcional. Se não fornecido, um novo será criado.
        """
        self.query_processor = query_processor if query_processor is not None else QueryProcessor()
    
    def _print_header(self):
        """Imprime o cabeçalho da CLI."""
        print("\n" + "="*80)
        print("  Assistente de IA para o Projeto E-commerce  ".center(80, "="))
        print("="*80)
        print("\nModelo atual:", self.query_processor.model_name)
        print("\nComandos disponíveis:")
        print("  !ajuda     - Exibe esta mensagem de ajuda")
        print("  !modelo    - Alterna entre os modelos GPT-3.5 e GPT-4")
        print("  !sair      - Sai da aplicação")
        print("\nDigite sua pergunta ou um comando:")
        print("-"*80)
    
    def _process_command(self, command: str) -> bool:
        """
        Processa um comando da CLI.
        
        Args:
            command: Comando a ser processado.
            
        Returns:
            True se a aplicação deve continuar, False se deve sair.
        """
        if command == "!ajuda":
            self._print_header()
            return True
        
        elif command == "!modelo":
            # Alterna entre os modelos
            new_model = GPT_4_MODEL if self.query_processor.model_name == GPT_3_5_MODEL else GPT_3_5_MODEL
            self.query_processor.switch_model(new_model)
            return True
        
        elif command == "!sair":
            print("\nObrigado por utilizar a Assistente de IA. Até logo!")
            return False
        
        else:
            print(f"Comando desconhecido: {command}")
            print("Digite !ajuda para ver os comandos disponíveis.")
            return True
    
    def run(self):
        """Executa a interface de linha de comando."""
        self._print_header()
        
        while True:
            try:
                # Obtém a entrada do usuário
                user_input = input("\n> ")
                
                # Verifica se é um comando
                if user_input.startswith("!"):
                    if not self._process_command(user_input):
                        break
                    continue
                
                # Processa a consulta
                print("\nProcessando sua consulta. Isso pode levar alguns segundos...\n")
                response = self.query_processor.process_query(user_input)
                
                # Exibe a resposta
                print("\nResposta:")
                print("-"*80)
                print(response)
                print("-"*80)
                
            except KeyboardInterrupt:
                print("\n\nOperação interrompida pelo usuário.")
                break
                
            except Exception as e:
                print(f"\nErro ao processar consulta: {e}")
    
    @staticmethod
    def parse_args():
        """
        Analisa os argumentos de linha de comando.
        
        Returns:
            Argumentos analisados.
        """
        parser = argparse.ArgumentParser(description="Assistente de IA para o Projeto E-commerce")
        parser.add_argument("--modelo", choices=["gpt-3.5", "gpt-4"], default="gpt-3.5",
                           help="Modelo da OpenAI a ser utilizado")
        parser.add_argument("--consulta", type=str, help="Consulta a ser processada (modo não interativo)")
        
        return parser.parse_args()


def main():
    """Função principal para execução da CLI."""
    args = CLI.parse_args()
    
    # Define o modelo a ser utilizado
    model_name = GPT_4_MODEL if args.modelo == "gpt-4" else GPT_3_5_MODEL
    
    # Cria o processador de consultas
    query_processor = QueryProcessor(model_name=model_name)
    
    # Cria a CLI
    cli = CLI(query_processor)
    
    # Verifica se é modo não interativo
    if args.consulta:
        print(f"Processando consulta: {args.consulta}")
        response = query_processor.process_query(args.consulta)
        print("\nResposta:")
        print("-"*80)
        print(response)
        print("-"*80)
    else:
        # Modo interativo
        cli.run()


if __name__ == "__main__":
    main()
