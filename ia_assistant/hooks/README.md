# Guia de Uso do Hook Post-Commit Interativo

Este documento explica como instalar e usar o hook post-commit interativo que foi desenvolvido para enriquecer o conhecimento da assistente de IA do projeto.

## O que é o Hook Post-Commit Interativo?

O hook post-commit interativo é um script que é executado automaticamente após cada commit no repositório Git. Ele analisa o tamanho e a importância das alterações e, quando detecta um commit significativo (com muitos arquivos ou linhas alteradas), solicita ao desenvolvedor uma explicação detalhada sobre as mudanças.

Essas explicações são armazenadas no repositório e utilizadas pela assistente de IA para enriquecer seu conhecimento sobre o projeto, permitindo respostas mais precisas e contextualizadas sobre as decisões de desenvolvimento.

## Instalação

Para instalar o hook post-commit interativo, siga os passos abaixo:

1. Navegue até a raiz do seu repositório Git:
   ```bash
   cd /caminho/para/seu/repositorio
   ```

2. Execute o script de instalação:
   ```bash
   bash ia_assistant/hooks/install_hook.sh
   ```

O script de instalação irá:
- Verificar se você está em um repositório Git
- Criar o diretório `.github/commit_explanations` para armazenar as explicações
- Configurar o caminho do projeto no script do hook
- Copiar o hook para o diretório `.git/hooks/`
- Tornar o hook executável

## Como Funciona

Após a instalação, o hook será executado automaticamente após cada commit:

1. **Para commits regulares** (pequenas alterações):
   - O hook atualiza automaticamente a base de conhecimento da assistente de IA
   - Nenhuma ação adicional é necessária

2. **Para commits significativos** (muitos arquivos ou linhas alteradas):
   - O hook detecta que o commit é significativo
   - Solicita uma explicação detalhada sobre as mudanças
   - Você digita sua explicação, finalizando com uma linha contendo apenas "FIM"
   - O hook salva a explicação em um arquivo Markdown no diretório `.github/commit_explanations/`
   - O arquivo é adicionado ao commit atual (amend)
   - A base de conhecimento da assistente de IA é atualizada automaticamente

## Exemplo de Uso

Após fazer um commit significativo:

```
$ git commit -m "Implementa novo módulo de pagamento"

=== Assistente de IA: Analisando commit ====
Commit: 7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s
Mensagem: Implementa novo módulo de pagamento
Arquivos alterados: 12
Linhas alteradas: 350

Commit significativo detectado!
Este commit alterou muitos arquivos ou linhas de código.
Uma explicação detalhada ajudará a assistente de IA a entender melhor as mudanças.

Por favor, forneça uma explicação detalhada sobre este commit:
(Descreva o propósito das mudanças, impacto no sistema, decisões arquiteturais, etc.)
Digite sua explicação abaixo e finalize com uma linha contendo apenas 'FIM':

Este commit implementa o novo módulo de pagamento que suporta múltiplos gateways de pagamento.
A implementação segue a arquitetura hexagonal, com adaptadores para diferentes provedores.

Decisões arquiteturais importantes:
1. Utilizamos o padrão Strategy para selecionar o gateway de pagamento apropriado
2. Implementamos idempotência nas operações de pagamento usando IDs de idempotência
3. Adicionamos suporte a transações assíncronas com callbacks

O módulo está integrado com o sistema de eventos Kafka para notificar outros serviços
sobre mudanças no status dos pagamentos.
FIM

Explicação salva em: .github/commit_explanations/7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s.md

Arquivo de explicação adicionado ao commit.

Atualizando a base de conhecimento da assistente de IA...
Base de conhecimento atualizada com sucesso!

=== Processamento do commit concluído ====
```

## Configuração Personalizada

Se você quiser ajustar os limiares para determinar o que constitui um "commit significativo", você pode editar o arquivo `.git/hooks/post-commit` e modificar as seguintes variáveis:

```bash
MIN_FILES_THRESHOLD=5      # Número mínimo de arquivos para considerar um commit significativo
MIN_LINES_THRESHOLD=100    # Número mínimo de linhas para considerar um commit significativo
```

## Solução de Problemas

### O hook não está sendo executado após os commits

Verifique se o hook está instalado corretamente:
```bash
ls -la .git/hooks/post-commit
```

Se o arquivo não existir ou não for executável, reinstale o hook:
```bash
bash ia_assistant/hooks/install_hook.sh
```

### Erro ao atualizar a base de conhecimento da assistente

Se você receber um erro indicando que o script da assistente não foi encontrado, verifique se:
1. O caminho do projeto está configurado corretamente no hook
2. A assistente de IA está instalada corretamente
3. As dependências Python necessárias estão instaladas

Para atualizar manualmente a base de conhecimento:
```bash
python -m ia_assistant.main --update
```

## Benefícios

- **Documentação automática**: As explicações detalhadas servem como documentação viva do projeto
- **Conhecimento contextualizado**: A assistente de IA aprende sobre as decisões e motivações por trás das mudanças
- **Melhor suporte**: Respostas mais precisas e úteis da assistente sobre o código e a arquitetura
- **Onboarding facilitado**: Novos membros da equipe podem entender melhor o histórico e as decisões do projeto
