#!/bin/bash

# Script de instalação do hook post-commit interativo para a Assistente de IA
# Este script instala o hook post-commit no repositório Git local

# Cores para melhor visualização
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Instalador do Hook Post-Commit para Assistente de IA ===${NC}\n"

# Verifica se está em um repositório Git
if [ ! -d ".git" ]; then
    echo -e "${RED}Erro: Este diretório não parece ser um repositório Git.${NC}"
    echo -e "${YELLOW}Execute este script na raiz do seu repositório Git.${NC}"
    exit 1
fi

# Obtém o caminho absoluto do diretório atual
PROJECT_ROOT=$(pwd)
echo -e "${BLUE}Diretório do projeto:${NC} $PROJECT_ROOT"

# Cria o diretório para armazenar explicações de commits, se não existir
EXPLANATIONS_DIR=".github/commit_explanations"
mkdir -p "$EXPLANATIONS_DIR"
echo -e "${GREEN}Diretório para explicações de commits criado:${NC} $EXPLANATIONS_DIR"

# Caminho do hook post-commit
HOOK_SOURCE="$PROJECT_ROOT/ia_assistant/hooks/post-commit"
HOOK_DEST="$PROJECT_ROOT/.git/hooks/post-commit"

# Verifica se o arquivo do hook existe
if [ ! -f "$HOOK_SOURCE" ]; then
    echo -e "${RED}Erro: Arquivo do hook não encontrado:${NC} $HOOK_SOURCE"
    exit 1
fi

# Atualiza o caminho do projeto no script do hook
echo -e "${BLUE}Configurando o caminho do projeto no hook...${NC}"
sed -i "s|PROJECT_ROOT=\"/caminho/completo/para/ia-eccomerce-assistant\"|PROJECT_ROOT=\"$PROJECT_ROOT\"|g" "$HOOK_SOURCE"

# Copia o hook para o diretório .git/hooks
echo -e "${BLUE}Instalando o hook post-commit...${NC}"
cp "$HOOK_SOURCE" "$HOOK_DEST"

# Torna o hook executável
chmod +x "$HOOK_DEST"

echo -e "\n${GREEN}Hook post-commit instalado com sucesso!${NC}"
echo -e "${GREEN}O hook será executado automaticamente após cada commit.${NC}"
echo -e "${GREEN}Commits significativos solicitarão explicações detalhadas.${NC}"

# Verifica se o script da assistente existe
if [ ! -f "$PROJECT_ROOT/ia_assistant/main.py" ]; then
    echo -e "\n${YELLOW}Aviso: Script da assistente de IA não encontrado.${NC}"
    echo -e "${YELLOW}Certifique-se de que a assistente está instalada corretamente.${NC}"
fi

echo -e "\n${BLUE}=== Instalação concluída ===${NC}"
