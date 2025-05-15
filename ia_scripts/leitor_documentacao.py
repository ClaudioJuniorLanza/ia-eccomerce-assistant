# ia_scripts/leitor_documentacao.py

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define o caminho para o arquivo de documentação
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCUMENTATION_FILE_PATH = os.path.join(PROJECT_ROOT, "decisoes_arquiteturais_iniciais.md")

# IMPORTANTE: Para este script funcionar, a variável de ambiente OPENAI_API_KEY
# deve estar configurada com sua chave da API da OpenAI.
# Exemplo: export OPENAI_API_KEY="sk-sua-chave-aqui"

def ler_documento_arquitetura():
    """Lê o conteúdo do arquivo de decisões arquiteturais."""
    try:
        with open(DOCUMENTATION_FILE_PATH, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        print(f"Conteúdo do arquivo \'{DOCUMENTATION_FILE_PATH}\' lido com sucesso.")
        return conteudo
    except FileNotFoundError:
        print(f"Erro: Arquivo \'{DOCUMENTATION_FILE_PATH}\' não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler o arquivo \'{DOCUMENTATION_FILE_PATH}\': {e}")
        return None

def resumir_documento_com_ia(texto_documento):
    """Usa Langchain e OpenAI para resumir o texto do documento."""
    if not texto_documento:
        return "Nenhum texto fornecido para resumir."

    if not os.getenv("OPENAI_API_KEY"):
        return ("Erro: A variável de ambiente OPENAI_API_KEY não está configurada. "
                "Por favor, configure-a com sua chave da API da OpenAI para continuar.")

    try:
        print("\n--- Iniciando resumo com IA (Langchain + OpenAI) ---")
        # Modelo GPT-3.5-turbo é uma boa opção para custo-benefício em resumos
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Você é um assistente de IA especializado em resumir documentos técnicos de arquitetura de software de forma concisa e clara."),
            ("human", "Por favor, resuma o seguinte documento de decisões arquiteturais:\n\n{documento}")
        ])

        parser = StrOutputParser()
        chain = prompt_template | llm | parser

        resumo = chain.invoke({"documento": texto_documento})
        print("--- Resumo Gerado ---")
        print(resumo)
        print("---------------------")
        return resumo

    except Exception as e:
        return f"Erro ao processar o documento com a IA: {e}"

if __name__ == "__main__":
    conteudo_documento = ler_documento_arquitetura()
    if conteudo_documento:
        print("--------------------------------------------------")
        print(conteudo_documento) # Imprime o conteúdo completo para referência
        print("--------------------------------------------------")
        
        resultado_ia = resumir_documento_com_ia(conteudo_documento)
        print(f"\nResultado do processamento pela IA: {resultado_ia}")

