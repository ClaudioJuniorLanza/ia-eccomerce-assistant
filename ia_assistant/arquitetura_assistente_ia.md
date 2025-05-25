# Arquitetura da Assistente de IA para o Projeto E-commerce

## 1. Visão Geral

A Assistente de IA para o projeto E-commerce será uma ferramenta que acompanhará o desenvolvimento desde o início, aprendendo continuamente sobre as decisões arquiteturais, código, padrões e justificativas. Ela será capaz de responder perguntas, fornecer explicações e auxiliar nas decisões futuras com base no conhecimento acumulado do projeto.

## 2. Componentes Principais

### 2.1. Sistema de Armazenamento de Conhecimento

**Base de Dados Vetorial**
- Utilizaremos o ChromaDB como nossa base de dados vetorial, por ser leve, de código aberto e fácil integração com Python e Langchain.
- Os documentos serão divididos em chunks (pedaços) de tamanho apropriado para indexação e recuperação eficiente.
- Cada chunk será transformado em um embedding (representação vetorial) usando modelos da OpenAI.
- Metadados serão associados a cada chunk para facilitar filtragem e contextualização (tipo de documento, data, autor, etc.).

**Estrutura de Coleções**
- **decisoes_arquiteturais**: Armazenará chunks do documento de decisões arquiteturais e suas atualizações.
- **codigo_fonte**: Armazenará chunks de código Kotlin, organizados por módulos e funcionalidades.
- **commits_historico**: Armazenará mensagens e metadados de commits, permitindo rastrear a evolução do projeto.
- **documentacao_ddd**: Armazenará conhecimento específico sobre Domain Driven Design aplicado ao projeto.
- **documentacao_arquitetura**: Armazenará conhecimento sobre Arquitetura Hexagonal e sua implementação no projeto.
- **documentacao_tecnologias**: Armazenará conhecimento sobre Kotlin, Quarkus e outras tecnologias utilizadas.

### 2.2. Mecanismo de Coleta de Dados

**Coletores Especializados**
- **DocumentCollector**: Para processar arquivos Markdown e outros documentos de texto.
- **CodeCollector**: Para processar arquivos de código Kotlin, com capacidade de entender a estrutura do código.
- **GitCollector**: Para processar histórico de commits, mensagens e metadados do Git.

**Processadores de Texto**
- **TextSplitter**: Responsável por dividir documentos em chunks de tamanho apropriado.
- **MetadataExtractor**: Responsável por extrair e associar metadados relevantes a cada chunk.
- **EmbeddingGenerator**: Responsável por gerar embeddings para cada chunk usando a API da OpenAI.

### 2.3. Interface de Consulta

**CLI (Command Line Interface)**
- Interface inicial baseada em linha de comando para interação com a assistente.
- Suporte a diferentes tipos de consultas (perguntas diretas, busca por tópicos, etc.).
- Opção para especificar o contexto da consulta (ex: "sobre arquitetura", "sobre código").

**Processador de Consultas**
- **QueryProcessor**: Responsável por transformar a consulta do usuário em uma busca eficiente na base vetorial.
- **ContextBuilder**: Responsável por construir o contexto adequado para a consulta à API da OpenAI.
- **ResponseGenerator**: Responsável por gerar respostas coesas e contextualizadas usando a API da OpenAI.

### 2.4. Sistema de Atualização Contínua

**Mecanismo de Atualização**
- **ChangeDetector**: Responsável por detectar mudanças nos documentos e código-fonte.
- **IncrementalUpdater**: Responsável por atualizar a base de conhecimento de forma incremental, sem reprocessar tudo.
- **ConsistencyChecker**: Responsável por verificar e manter a consistência da base de conhecimento.

**Gatilhos de Atualização**
- **Commits**: Atualização automática após novos commits.
- **Manual**: Possibilidade de atualização manual sob demanda.
- **Programada**: Atualização periódica em intervalos configuráveis.

## 3. Fluxo de Dados

### 3.1. Fluxo de Ingestão de Conhecimento
1. Os coletores especializados obtêm dados das fontes (documentos, código, Git).
2. Os processadores de texto dividem o conteúdo em chunks e extraem metadados.
3. O EmbeddingGenerator cria embeddings para cada chunk.
4. Os chunks com embeddings e metadados são armazenados na base de dados vetorial.

### 3.2. Fluxo de Consulta
1. O usuário faz uma pergunta via CLI.
2. O QueryProcessor transforma a pergunta em uma busca vetorial.
3. A base de dados vetorial retorna os chunks mais relevantes.
4. O ContextBuilder monta um contexto com os chunks relevantes.
5. O ResponseGenerator usa a API da OpenAI para gerar uma resposta contextualizada.
6. A resposta é apresentada ao usuário via CLI.

### 3.3. Fluxo de Atualização
1. O ChangeDetector identifica mudanças nas fontes de dados.
2. O IncrementalUpdater processa apenas as mudanças identificadas.
3. Novos chunks são gerados, com embeddings e metadados.
4. A base de dados vetorial é atualizada com os novos chunks.
5. O ConsistencyChecker verifica a consistência da base após a atualização.

## 4. Estratégia de Uso de Modelos GPT

### 4.1. Abordagem Mista
- **GPT-3.5-turbo**: Utilizado para consultas mais simples e frequentes, como explicações básicas, recuperação de informações diretas e resumos.
- **GPT-4**: Reservado para análises mais complexas, recomendações críticas de arquitetura, e quando a qualidade da resposta é prioritária sobre o custo.

### 4.2. Otimização de Custos
- **Caching de Respostas**: Armazenamento de respostas para consultas frequentes.
- **Controle de Tokens**: Limitação do tamanho do contexto enviado à API da OpenAI.
- **Filtragem Prévia**: Uso da base vetorial para filtrar e reduzir a quantidade de dados enviados à API.
- **Prompts Otimizados**: Desenvolvimento de prompts eficientes que minimizem o uso de tokens.

## 5. Requisitos Técnicos

### 5.1. Dependências
- Python 3.9+
- Langchain
- ChromaDB
- OpenAI API
- GitPython (para acesso ao histórico Git)
- Bibliotecas de processamento de texto e código

### 5.2. Configuração
- Arquivo de configuração para definir parâmetros como:
  - Caminhos para fontes de dados
  - Configurações da API da OpenAI
  - Parâmetros de chunking e embedding
  - Estratégias de atualização
  - Limites de uso (tokens, consultas, etc.)

## 6. Roadmap de Implementação

### Fase 1: Base de Dados Vetorial e Indexação
- Implementar ChromaDB como base de dados vetorial
- Desenvolver mecanismos de chunking e embedding
- Criar estrutura inicial de coleções

### Fase 2: Coleta de Dados Inicial
- Implementar DocumentCollector para processar decisões arquiteturais
- Implementar CodeCollector para processar código Kotlin
- Implementar GitCollector para processar histórico de commits

### Fase 3: Interface de Consulta Básica
- Desenvolver CLI para interação com a assistente
- Implementar QueryProcessor para busca vetorial
- Implementar ContextBuilder e ResponseGenerator

### Fase 4: Sistema de Atualização
- Implementar ChangeDetector para identificar mudanças
- Desenvolver IncrementalUpdater para atualizações eficientes
- Criar ConsistencyChecker para manter a integridade da base

### Fase 5: Validação e Refinamento
- Testar a assistente com diferentes tipos de consultas
- Refinar prompts e estratégias de uso de modelos
- Otimizar para equilíbrio entre custo e qualidade

### Fase 6: Documentação e Expansão
- Documentar o processo e orientações de uso
- Planejar expansões futuras (interface web, integração com IDEs, etc.)

## 7. Considerações Futuras

### 7.1. Expansão da Interface
- Interface web para acesso mais amigável
- Integração com IDEs (plugin para IntelliJ IDEA)
- Integração com ferramentas de comunicação (Slack, Discord, etc.)

### 7.2. Aprimoramento da IA
- Fine-tuning de modelos específicos para o projeto
- Exploração de alternativas open-source para redução de custos
- Implementação de feedback loop para melhoria contínua

### 7.3. Integração com Fluxo de Desenvolvimento
- Análise automática de Pull Requests
- Sugestões proativas durante o desenvolvimento
- Geração de documentação automática
