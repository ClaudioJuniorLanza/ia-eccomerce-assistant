"""
Interface de consulta para a assistente de IA.
Implementa uma interface de linha de comando (CLI) para realizar consultas
à base de conhecimento e obter respostas contextualizadas.
"""

import os
import sys
import argparse
import re
from typing import List, Dict, Any, Optional, Union, Tuple
import json
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Importa a base de dados vetorial
from ia_assistant.database.vector_db import get_vector_database, VectorDatabase
from ia_assistant.interface.prompt_templates import prompt_optimizer, QueryType
from ia_assistant.cache.intelligent_cache import intelligent_cache, CacheStrategy
from ia_assistant.monitoring.change_detector import KnowledgeBaseMonitor, change_detector
from ia_assistant.proactive.suggestion_engine import ProactiveSuggestionEngine, suggestion_engine

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

# Template específico para listagem de recursos
LIST_RESOURCES_PROMPT_TEMPLATE = """
Você é uma assistente de IA especializada no projeto de e-commerce. Sua tarefa atual é apresentar uma lista
concisa dos recursos solicitados pelo usuário.

Recursos disponíveis:
{resources}

Pergunta do usuário: {query}

Apresente uma lista organizada dos recursos disponíveis, incluindo seus identificadores e títulos.
Explique brevemente que o usuário pode solicitar detalhes específicos sobre qualquer um desses recursos
mencionando seu identificador ou título em uma nova pergunta.

Resposta:
"""

# Template específico para consulta de ADR específica
ADR_DETAIL_PROMPT_TEMPLATE = """
Você é uma assistente de IA especializada no projeto de e-commerce. Sua tarefa atual é apresentar informações
detalhadas sobre um Architecture Decision Record (ADR) específico.

ADR solicitado:
{adr_content}

Pergunta do usuário: {query}

Apresente as informações do ADR de forma clara e estruturada, destacando o contexto da decisão, a decisão em si,
as consequências e alternativas consideradas. Certifique-se de incluir todos os detalhes importantes do ADR,
sem omitir nenhuma seção relevante. Sua resposta deve ser completa e abrangente, fornecendo o máximo de detalhes possível.

IMPORTANTE: Não corte sua resposta no meio de uma frase ou parágrafo. Certifique-se de que todas as seções
do ADR sejam apresentadas integralmente, especialmente as seções de Contexto, Decisão, Consequências e Alternativas.

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
        
        # Inicializa o modelo de linguagem com configurações padrão
        self.llm = OpenAI(model_name=model_name, temperature=0.2, max_tokens=500)
        
        # Inicializa o modelo específico para ADRs com limite de tokens maior
        self.adr_llm = OpenAI(model_name=model_name, temperature=0.2, max_tokens=2000)
        
        # Inicializa os templates de prompt
        
        # Inicializa detector de mudanças se não existir
        self._initialize_change_detector()
        
        # Inicializa motor de sugestões proativas
        self._initialize_suggestion_engine()
        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "query"],
            template=QUERY_PROMPT_TEMPLATE
        )
        
        self.list_resources_template = PromptTemplate(
            input_variables=["resources", "query"],
            template=LIST_RESOURCES_PROMPT_TEMPLATE
        )
        
        self.adr_detail_template = PromptTemplate(
            input_variables=["adr_content", "query"],
            template=ADR_DETAIL_PROMPT_TEMPLATE
        )
        
        # Inicializa as chains de processamento
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        self.list_resources_chain = LLMChain(llm=self.llm, prompt=self.list_resources_template)
        self.adr_detail_chain = LLMChain(llm=self.adr_llm, prompt=self.adr_detail_template)
    
    def _is_listing_query(self, query: str) -> bool:
        """
        Verifica se a consulta é uma solicitação de listagem de recursos.
        
        Args:
            query: Texto da consulta.
            
        Returns:
            True se for uma consulta de listagem, False caso contrário.
        """
        # Padrões para detectar consultas de listagem
        listing_patterns = [
            r"quais\s+(são\s+)?(os|as)?\s*adr",
            r"listar?\s+(os|as)?\s*adr",
            r"mostrar?\s+(os|as)?\s*adr",
            r"exibir?\s+(os|as)?\s*adr",
            r"quais\s+decisões\s+arquiteturais",
            r"quais\s+documentos\s+temos",
            r"listar?\s+documentos",
            r"listar?\s+decisões",
        ]
        
        # Converte a consulta para minúsculas para comparação case-insensitive
        query_lower = query.lower()
        
        # Verifica se a consulta corresponde a algum dos padrões
        for pattern in listing_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _is_specific_adr_query(self, query: str) -> bool:
        """
        Verifica se a consulta é sobre um ADR específico.
        
        Args:
            query: Texto da consulta.
            
        Returns:
            True se for uma consulta sobre um ADR específico, False caso contrário.
        """
        # Padrões para detectar consultas sobre ADRs específicos
        adr_patterns = [
            r"adr[- ]?(\d+)",
            r"adr[- ]?([a-zA-Z0-9_-]+)",
            r"sobre\s+a\s+adr",
            r"sobre\s+o\s+adr",
            r"detalhes\s+(d[ao])?\s+adr",
            r"explicar?\s+(a|o)?\s+adr",
            r"conteúdo\s+(d[ao])?\s+adr",
            r"informações\s+(d[ao])?\s+adr",
            r"me\s+d[êe]\s+informações\s+sobre\s+a\s+adr",
            r"quero\s+saber\s+sobre\s+a\s+adr",
            r"fale\s+sobre\s+a\s+adr",
        ]
        
        # Converte a consulta para minúsculas para comparação case-insensitive
        query_lower = query.lower()
        
        # Verifica se a consulta corresponde a algum dos padrões
        for pattern in adr_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def _get_resource_type_from_query(self, query: str) -> str:
        """
        Identifica o tipo de recurso solicitado na consulta.
        
        Args:
            query: Texto da consulta.
            
        Returns:
            Tipo de recurso (ex: "adr", "documento", "decisão").
        """
        query_lower = query.lower()
        
        if "adr" in query_lower:
            return "adr"
        elif "decisão" in query_lower or "decisoes" in query_lower:
            return "decisão arquitetural"
        elif "documento" in query_lower:
            return "documento"
        else:
            return "recurso"
    
    def _get_specific_resource_id(self, query: str) -> Optional[str]:
        """
        Extrai o identificador de um recurso específico da consulta.
        
        Args:
            query: Texto da consulta.
            
        Returns:
            Identificador do recurso ou None se não for encontrado.
        """
        # Padrões para detectar referências a recursos específicos
        patterns = [
            r"adr[- ]?(\d+)",
            r"adr[- ]?([a-zA-Z0-9_-]+)",
            r"decisão[- ]?(\d+)",
            r"decisao[- ]?(\d+)",
        ]
        
        query_lower = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1)
        
        return None
    
    def _format_adr_listing(self, adrs: List[Dict[str, str]]) -> str:
        """
        Formata uma listagem de ADRs para apresentação.
        
        Args:
            adrs: Lista de dicionários com informações sobre os ADRs.
            
        Returns:
            Texto formatado com a listagem de ADRs.
        """
        if not adrs:
            return "Nenhum ADR encontrado no projeto."
        
        # Filtra para incluir apenas ADRs reais (pelo caminho)
        real_adrs = [adr for adr in adrs if "/docs/adrs/" in adr.get("source", "").lower()]
        
        if not real_adrs:
            return "Nenhum ADR formal encontrado no diretório /docs/adrs/ do projeto."
        
        # Formata a listagem
        lines = []
        for adr in real_adrs:
            title = adr.get("title", "Sem título")
            adr_id = adr.get("id", "")
            if adr_id and title:
                lines.append(f"- {title}")
            elif adr_id:
                lines.append(f"- {adr_id}")
            elif title:
                lines.append(f"- {title}")
        
        return "\n".join(lines)
    
    def _get_adr_listing(self) -> List[Dict[str, str]]:
        """
        Obtém uma listagem de ADRs do projeto.
        
        Returns:
            Lista de dicionários com informações sobre os ADRs.
        """
        # Consulta específica para encontrar ADRs
        query_text = "ADR Architecture Decision Record"
        collection_name = "decisoes_arquiteturais"
        
        # Consulta a coleção
        results = self.vector_db.query(
            collection_name=collection_name,
            query_text=query_text,
            n_results=15  # Aumentamos para pegar mais ADRs
        )
        
        # Lista para armazenar os ADRs encontrados
        adrs = []
        
        # Conjunto para rastrear ADRs já processados (evitar duplicatas)
        processed_adrs = set()
        
        if "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                # Verifica se há metadados disponíveis
                metadata = {}
                if "metadatas" in results and results["metadatas"][0] and i < len(results["metadatas"][0]):
                    metadata = results["metadatas"][0][i]
                
                # Extrai informações do documento
                source = metadata.get("source", "")
                
                # Verifica se é um ADR pelo caminho do arquivo
                is_adr = False
                if "/docs/adrs/" in source.lower():
                    is_adr = True
                
                # Se não for um ADR pelo caminho, ignora
                if not is_adr:
                    continue
                
                # Extrai o ID e título do ADR
                adr_id = ""
                title = ""
                
                # Tenta extrair do nome do arquivo
                filename = os.path.basename(source)
                if filename.startswith(("adr-", "ADR-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                    adr_id = os.path.splitext(filename)[0]
                
                # Tenta extrair o título do conteúdo
                lines = doc.split("\n")
                for line in lines[:5]:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                
                # Se não encontrou título, usa um genérico
                if not title:
                    title = f"ADR {adr_id}"
                
                # Cria um identificador único para evitar duplicatas
                unique_id = f"{adr_id}_{title}"
                
                # Adiciona à lista se ainda não foi processado
                if unique_id not in processed_adrs:
                    adrs.append({
                        "id": adr_id,
                        "title": title,
                        "source": source,
                        "content": doc
                    })
                    processed_adrs.add(unique_id)
        
        return adrs
    
    def _extract_essential_adr_content(self, content: str) -> str:
        """
        Extrai o conteúdo essencial de um ADR, removendo partes menos relevantes
        para reduzir o número de tokens.
        
        Args:
            content: Conteúdo completo do ADR.
            
        Returns:
            Conteúdo essencial do ADR.
        """
        # Divide o conteúdo em seções
        sections = []
        current_section = []
        current_heading = ""
        
        for line in content.split("\n"):
            # Detecta cabeçalhos de seção
            if line.startswith("# "):
                # Se já temos uma seção, adiciona à lista
                if current_heading and current_section:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_section),
                        "priority": 1  # Prioridade padrão
                    })
                
                # Inicia nova seção
                current_heading = line
                current_section = []
            elif line.startswith("## "):
                # Se já temos uma seção, adiciona à lista
                if current_heading and current_section:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_section),
                        "priority": 1  # Prioridade padrão
                    })
                
                # Inicia nova seção
                current_heading = line
                current_section = []
            else:
                # Adiciona linha à seção atual
                current_section.append(line)
        
        # Adiciona a última seção
        if current_heading and current_section:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_section),
                "priority": 1  # Prioridade padrão
            })
        
        # Define prioridades para diferentes tipos de seções
        for section in sections:
            heading_lower = section["heading"].lower()
            
            # Título principal tem prioridade máxima
            if "# adr" in heading_lower:
                section["priority"] = 10
            # Seções importantes têm prioridade alta
            elif any(keyword in heading_lower for keyword in ["status", "contexto", "decisão", "consequências", "alternativas"]):
                section["priority"] = 9
            # Seções de detalhes têm prioridade média
            elif any(keyword in heading_lower for keyword in ["detalhes", "implementação", "referências"]):
                section["priority"] = 5
            # Outras seções têm prioridade baixa
            else:
                section["priority"] = 1
        
        # Ordena as seções por prioridade
        sections.sort(key=lambda x: x["priority"], reverse=True)
        
        # Monta o conteúdo essencial
        essential_content = []
        for section in sections:
            essential_content.append(section["heading"])
            essential_content.append(section["content"])
        
        return "\n".join(essential_content)
    
    def _get_specific_adr(self, adr_id: str) -> Optional[Dict[str, str]]:
        """
        Obtém informações sobre um ADR específico.
        
        Args:
            adr_id: Identificador do ADR.
            
        Returns:
            Dicionário com informações sobre o ADR ou None se não for encontrado.
        """
        # Consulta específica para encontrar o ADR
        query_text = f"ADR {adr_id}"
        collection_name = "decisoes_arquiteturais"
        
        # Consulta a coleção
        results = self.vector_db.query(
            collection_name=collection_name,
            query_text=query_text,
            n_results=5  # Limitamos para evitar excesso de tokens
        )
        
        # Verifica se encontrou resultados
        if "documents" not in results or not results["documents"]:
            return None
        
        # Procura pelo ADR específico
        for i, doc in enumerate(results["documents"][0]):
            # Verifica se há metadados disponíveis
            metadata = {}
            if "metadatas" in results and results["metadatas"][0] and i < len(results["metadatas"][0]):
                metadata = results["metadatas"][0][i]
            
            # Extrai informações do documento
            source = metadata.get("source", "")
            
            # Verifica se é o ADR correto pelo caminho ou conteúdo
            is_target_adr = False
            
            # Verifica pelo caminho
            if "/docs/adrs/" in source.lower() and adr_id.lower() in source.lower():
                is_target_adr = True
            
            # Verifica pelo conteúdo
            if not is_target_adr:
                lines = doc.split("\n")
                for line in lines[:10]:
                    if line.startswith("# ") and adr_id.lower() in line.lower():
                        is_target_adr = True
                        break
            
            # Se for o ADR correto, extrai as informações
            if is_target_adr:
                # Extrai o título
                title = ""
                lines = doc.split("\n")
                for line in lines[:5]:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                
                # Extrai o conteúdo essencial
                essential_content = self._extract_essential_adr_content(doc)
                
                return {
                    "id": adr_id,
                    "title": title,
                    "source": source,
                    "content": essential_content
                }
        
        # Se não encontrou o ADR específico, tenta uma busca mais ampla
        # Consulta todas as coleções
        all_results = self.vector_db.query_all_collections(query_text, n_results=10)
        
        for collection_name, results in all_results.items():
            if "error" in results:
                continue
                
            if "documents" in results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    # Verifica se há metadados disponíveis
                    metadata = {}
                    if "metadatas" in results and results["metadatas"][0] and i < len(results["metadatas"][0]):
                        metadata = results["metadatas"][0][i]
                    
                    # Extrai informações do documento
                    source = metadata.get("source", "")
                    
                    # Verifica se é o ADR correto pelo caminho ou conteúdo
                    is_target_adr = False
                    
                    # Verifica pelo caminho
                    if "/docs/adrs/" in source.lower() and adr_id.lower() in source.lower():
                        is_target_adr = True
                    
                    # Verifica pelo conteúdo
                    if not is_target_adr:
                        lines = doc.split("\n")
                        for line in lines[:10]:
                            if line.startswith("# ") and adr_id.lower() in line.lower():
                                is_target_adr = True
                                break
                    
                    # Se for o ADR correto, extrai as informações
                    if is_target_adr:
                        # Extrai o título
                        title = ""
                        lines = doc.split("\n")
                        for line in lines[:5]:
                            if line.startswith("# "):
                                title = line[2:].strip()
                                break
                        
                        # Extrai o conteúdo essencial
                        essential_content = self._extract_essential_adr_content(doc)
                        
                        return {
                            "id": adr_id,
                            "title": title,
                            "source": source,
                            "content": essential_content
                        }
        
        return None
    
    def _get_relevant_context(self, query: str, n_results: int = 5) -> str:
        """
        Obtém o contexto relevante para uma consulta.
        
        Args:
            query: Texto da consulta.
            n_results: Número de resultados a serem retornados.
            
        Returns:
            Contexto relevante para a consulta.
        """
        # Verifica se a consulta é sobre um recurso específico
        resource_id = self._get_specific_resource_id(query)
        
        # Se for sobre um recurso específico, ajusta a consulta para focar nele
        if resource_id:
            # Adiciona o ID à consulta para melhorar a relevância
            enhanced_query = f"{query} {resource_id}"
            
            # Consulta todas as coleções
            all_results = self.vector_db.query_all_collections(enhanced_query, n_results)
        else:
            # Consulta normal para todas as coleções
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
        # Verifica se é uma consulta de listagem de ADRs
        if self._is_listing_query(query) and "adr" in query.lower():
            # Obtém a listagem de ADRs
            adrs = self._get_adr_listing()
            
            # Formata a listagem
            resources_list = self._format_adr_listing(adrs)
            
            # Executa a chain de processamento para listagem
            response = self.list_resources_chain.run(resources=resources_list, query=query)
            
            return response
        
        # Verifica se é uma consulta sobre um ADR específico
        elif self._is_specific_adr_query(query):
            # Tenta extrair o ID do ADR da consulta
            adr_id = self._get_specific_resource_id(query)
            
            # Se não conseguiu extrair o ID, usa uma abordagem mais genérica
            if not adr_id:
                # Tenta encontrar o ADR pelo título ou conteúdo
                adrs = self._get_adr_listing()
                
                # Procura por correspondências no título
                query_lower = query.lower()
                for adr in adrs:
                    if adr["title"].lower() in query_lower or query_lower in adr["title"].lower():
                        adr_id = adr["id"]
                        break
                
                # Se ainda não encontrou, usa "001" como padrão para a primeira consulta sobre ADRs
                if not adr_id and "arquitetura hexagonal" in query_lower:
                    adr_id = "001"
            
            # Se encontrou um ID, busca o ADR específico
            if adr_id:
                adr = self._get_specific_adr(adr_id)
                
                if adr:
                    # Executa a chain de processamento para detalhes do ADR
                    # Usa o modelo com limite de tokens maior
                    response = self.adr_detail_chain.run(adr_content=adr["content"], query=query)
                    return response
            
            # Se não encontrou o ADR específico, usa a abordagem padrão
            context = self._get_relevant_context(query, n_results=2)  # Reduz para evitar excesso de tokens
            response = self.chain.run(context=context, query=query)
            return response
        
        # Consulta normal
        else:
            return self._process_optimized_query(query)
    
    def _process_optimized_query(self, query: str) -> str:
        """
        Processa consulta com otimização de prompts e cache inteligente.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Resposta otimizada
        """
        import time
        
        start_time = time.time()
        
        try:
            # Detecta tipo de consulta
            query_type = prompt_optimizer.detect_query_type(query)
            
            # Otimiza prompt
            prompt_data = prompt_optimizer.optimize_prompt(query, query_type)
            
            # Tenta obter do cache primeiro
            cache_result = intelligent_cache.get(
                query=query,
                query_type=query_type.value,
                prompt_template=prompt_data['system_prompt'],
                strategy=CacheStrategy.ADAPTIVE
            )
            
            cache_hit = cache_result is not None
            
            if cache_result:
                response, cache_metadata = cache_result
                logger.info(f"Cache hit: {cache_metadata['cache_type']} - Tokens saved: {cache_metadata['tokens_saved']}")
                
                # Registra consulta para análise proativa
                if suggestion_engine:
                    response_time = (time.time() - start_time) * 1000  # ms
                    suggestion_engine.record_query(
                        query=query,
                        response_time=response_time,
                        cache_hit=True,
                        query_type=query_type.value,
                        tokens_used=cache_metadata.get('tokens_saved', 0)
                    )
                
                return response
            
            # Se não encontrou no cache, processa normalmente
            logger.info("Cache miss - processando consulta...")
            
            # Cria o modelo com parâmetros otimizados
            optimized_llm = OpenAI(
                model_name=self.model_name,
                temperature=prompt_data['temperature'],
                max_tokens=prompt_data['max_tokens']
            )
            
            # Cria as mensagens
            messages = [
                SystemMessage(content=prompt_data['system_prompt']),
                HumanMessage(content=prompt_data['user_prompt'])
            ]
            
            # Executa a consulta
            response = optimized_llm.invoke(messages)
            
            # Estima tokens e custo (aproximação)
            estimated_tokens = len(response.content.split()) * 1.3  # Aproximação
            estimated_cost = estimated_tokens * 0.000002  # Custo aproximado por token
            
            # Armazena no cache
            intelligent_cache.put(
                query=query,
                response=response.content,
                query_type=query_type.value,
                prompt_template=prompt_data['system_prompt'],
                tokens_used=int(estimated_tokens),
                cost_estimate=estimated_cost
            )
            
            # Registra consulta para análise proativa
            if suggestion_engine:
                response_time = (time.time() - start_time) * 1000  # ms
                suggestion_engine.record_query(
                    query=query,
                    response_time=response_time,
                    cache_hit=False,
                    query_type=query_type.value,
                    tokens_used=int(estimated_tokens)
                )
            
            return response.content
            
        except Exception as e:
            # Fallback para o método original em caso de erro
            context = self._get_relevant_context(query)
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
        
        # Atualiza os modelos com os mesmos parâmetros
        self.llm = OpenAI(model_name=model_name, temperature=0.2, max_tokens=500)
        self.adr_llm = OpenAI(model_name=model_name, temperature=0.2, max_tokens=2000)
        
        # Atualiza as chains
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        self.list_resources_chain = LLMChain(llm=self.llm, prompt=self.list_resources_template)
        self.adr_detail_chain = LLMChain(llm=self.adr_llm, prompt=self.adr_detail_template)
        
        print(f"Modelo alterado para: {model_name}")
    
    def _initialize_change_detector(self):
        """Inicializa o detector de mudanças."""
        global change_detector
        
        if change_detector is None:
            # Caminhos para monitorar
            base_paths = [
                os.path.join(os.path.dirname(__file__), "..", "docs"),
                os.path.join(os.path.dirname(__file__), "..", "ia_assistant"),
                os.path.join(os.path.dirname(__file__), "..", "src")
            ]
            
            # Filtra apenas caminhos que existem
            existing_paths = [path for path in base_paths if os.path.exists(path)]
            
            if existing_paths:
                change_detector = KnowledgeBaseMonitor(
                    base_paths=existing_paths,
                    cache_manager=intelligent_cache,
                    check_interval=60  # Verifica a cada minuto
                )
                
                # Inicia monitoramento
                change_detector.start_monitoring()
                logger.info(f"Detector de mudanças iniciado para: {existing_paths}")
            else:
                logger.warning("Nenhum caminho válido encontrado para monitoramento")

    def _initialize_suggestion_engine(self):
        """Inicializa o motor de sugestões proativas."""
        global suggestion_engine
        
        if suggestion_engine is None:
            suggestion_engine = ProactiveSuggestionEngine(
                cache_manager=intelligent_cache,
                change_detector=change_detector,
                impact_analyzer=None  # Será inicializado se disponível
            )
            
            logger.info("Motor de sugestões proativas inicializado")
        else:
            logger.info("Motor de sugestões proativas já inicializado")


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
        """
        Imprime o cabeçalho da CLI.
        """
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
        """
        Executa a interface de linha de comando.
        """
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
    """
    Função principal para execução da CLI.
    """
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


