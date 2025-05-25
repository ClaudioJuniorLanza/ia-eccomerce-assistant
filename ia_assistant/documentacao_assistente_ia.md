"""
Documentação da Assistente de IA para o Projeto E-commerce

Este documento fornece instruções detalhadas sobre como configurar, usar e manter
a assistente de IA desenvolvida para o projeto E-commerce.
"""

# Assistente de IA para o Projeto E-commerce
## Guia de Uso e Documentação

### 1. Visão Geral

A Assistente de IA para o projeto E-commerce é uma ferramenta projetada para acompanhar o desenvolvimento do projeto desde o início, aprendendo continuamente sobre as decisões arquiteturais, código, padrões e justificativas. Ela é capaz de responder perguntas, fornecer explicações e auxiliar nas decisões futuras com base no conhecimento acumulado do projeto.

### 2. Arquitetura

A assistente é composta por quatro componentes principais:

1. **Sistema de Armazenamento de Conhecimento**: Base de dados vetorial (ChromaDB) que armazena e indexa o conhecimento do projeto.
2. **Mecanismo de Coleta de Dados**: Coletores especializados para documentos, código-fonte e histórico Git.
3. **Interface de Consulta**: CLI para interação com a assistente.
4. **Sistema de Atualização Contínua**: Mecanismos para detectar mudanças e atualizar a base de conhecimento de forma incremental.

### 3. Requisitos

Para utilizar a assistente, você precisará de:

- Python 3.9 ou superior
- Dependências Python: `chromadb`, `langchain`, `langchain_openai`, `openai`, `gitpython`
- Uma chave de API válida da OpenAI
- Acesso ao repositório Git do projeto

### 4. Instalação

1. Clone o repositório do projeto:
   ```bash
   git clone https://github.com/ClaudioJuniorLanza/ia-eccomerce-assistant.git
   cd ia-eccomerce-assistant
   ```

2. Instale as dependências:
   ```bash
   pip install chromadb langchain langchain_openai openai gitpython
   ```

3. Configure a chave da API da OpenAI como uma variável de ambiente:
   - Linux/macOS: `export OPENAI_API_KEY="sua-chave-aqui"`
   - Windows (PowerShell): `$env:OPENAI_API_KEY="sua-chave-aqui"`
   - Windows (CMD): `set OPENAI_API_KEY=sua-chave-aqui`

### 5. Inicialização da Base de Conhecimento

Antes de usar a assistente pela primeira vez, você precisa inicializar a base de conhecimento:

```bash
python -m ia_assistant.validate_assistant --initialize --project-root /caminho/para/projeto
```

Este comando irá:
- Criar as coleções necessárias na base de dados vetorial
- Processar todos os documentos Markdown no diretório do projeto
- Processar todos os arquivos de código Kotlin
- Processar o histórico de commits do Git

### 6. Uso da Interface CLI

Para interagir com a assistente via linha de comando:

```bash
python -m ia_assistant.interface.cli
```

Comandos disponíveis na CLI:
- `!ajuda` - Exibe a mensagem de ajuda
- `!modelo` - Alterna entre os modelos GPT-3.5 e GPT-4
- `!sair` - Sai da aplicação

Para fazer uma consulta, basta digitar sua pergunta e pressionar Enter.

Exemplos de perguntas que você pode fazer:
- "Quais são as principais decisões arquiteturais do projeto?"
- "Por que foi escolhida a arquitetura hexagonal para o projeto?"
- "Como está estruturado o módulo de catálogo do e-commerce?"
- "Quais são as considerações sobre custos e modelos de IA no projeto?"
- "Explique como a entidade Produto foi implementada no domínio."

### 7. Atualização da Base de Conhecimento

A base de conhecimento pode ser atualizada de forma incremental quando houver mudanças no projeto:

```bash
python -m ia_assistant.knowledge_processor.updater
```

Para configurar atualizações periódicas automáticas, você pode usar o seguinte código:

```python
from ia_assistant.knowledge_processor.updater import get_update_manager

# Cria o gerenciador de atualização
update_manager = get_update_manager("/caminho/para/projeto")

# Agenda atualizações a cada hora (3600 segundos)
update_manager.schedule_periodic_update(interval_seconds=3600)
```

### 8. Validação da Assistente

Para validar o funcionamento da assistente com um conjunto de consultas predefinidas:

```bash
python -m ia_assistant.validate_assistant --model gpt-3.5
```

Você pode escolher entre os modelos `gpt-3.5` (mais econômico) e `gpt-4` (mais avançado).

### 9. Estrutura de Diretórios

```
ia_assistant/
├── database/
│   └── vector_db.py         # Base de dados vetorial (ChromaDB)
├── data_collector/
│   └── collectors.py        # Coletores de dados (documentos, código, Git)
├── knowledge_processor/
│   └── updater.py           # Sistema de atualização contínua
├── interface/
│   └── cli.py               # Interface de linha de comando
└── validate_assistant.py    # Script de validação
```

### 10. Considerações sobre Custos

A assistente utiliza a API da OpenAI para gerar respostas, o que implica em custos baseados no número de tokens processados. Para otimizar os custos:

- Use o modelo GPT-3.5 para consultas simples e frequentes
- Reserve o modelo GPT-4 para análises mais complexas
- Mantenha suas perguntas concisas e específicas
- Considere implementar um sistema de cache para respostas frequentes

### 11. Limitações Atuais

- A assistente só tem conhecimento sobre o que foi indexado na base de dados
- A qualidade das respostas depende da qualidade da documentação e dos comentários no código
- A interface atual é limitada à linha de comando
- A assistente não tem capacidade de gerar código novo, apenas explicar o existente

### 12. Próximos Passos

Possíveis melhorias futuras:
- Interface web para acesso mais amigável
- Integração com IDEs (plugin para IntelliJ IDEA)
- Análise automática de Pull Requests
- Sugestões proativas durante o desenvolvimento
- Fine-tuning de modelos específicos para o projeto

### 13. Solução de Problemas

#### Erro de autenticação da OpenAI
Verifique se a variável de ambiente `OPENAI_API_KEY` está configurada corretamente e se a chave é válida.

#### Base de dados vazia ou incompleta
Execute o script de inicialização novamente:
```bash
python -m ia_assistant.validate_assistant --initialize
```

#### Respostas imprecisas ou incorretas
- Verifique se a documentação do projeto está atualizada e completa
- Tente usar o modelo GPT-4 para consultas mais complexas
- Atualize a base de conhecimento para incluir as informações mais recentes

### 14. Contato e Suporte

Para dúvidas, sugestões ou problemas, entre em contato com a equipe de desenvolvimento ou abra uma issue no repositório do projeto.

---

Documentação criada em: Maio de 2025
