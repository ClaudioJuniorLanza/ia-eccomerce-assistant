# ADR 004: Adoção de Dockerfile para Contêinerização

## Status

Proposto

## Contexto

O projeto IA E-commerce Assistant está desenvolvendo um microsserviço em um ambiente de nuvem. Para garantir a consistência, portabilidade e escalabilidade do microsserviço, é essencial adotar uma tecnologia de contêinerização. A ausência de uma abordagem padronizada para empacotar e implantar a aplicação pode levar a problemas de compatibilidade entre ambientes (desenvolvimento, teste, produção) e dificultar a automação do deploy.

## Decisão

Adotar o uso de **Dockerfile** para construir imagens Docker do microsserviço. O Dockerfile será o artefato padrão para definir o ambiente de execução da aplicação, incluindo suas dependências, configurações e o comando de inicialização.

## Consequências

### Positivas

*   **Padronização e Reprodutibilidade:** Garante que o ambiente de execução da aplicação seja consistente em todos os ambientes, eliminando problemas de compatibilidade.
*   **Isolamento:** As aplicações são executadas em contêineres isolados, aumentando a segurança e a estabilidade do sistema.
*   **Portabilidade:** As imagens Docker podem ser facilmente transportadas e executadas em qualquer ambiente com Docker instalado, facilitando o deploy em nuvem.
*   **Eficiência de Recursos:** Contêineres são mais leves que máquinas virtuais, resultando em menor consumo de recursos e maior densidade de aplicações por servidor.
*   **Versionamento e Controle de Versão:** O Dockerfile pode ser versionado junto com o código-fonte, permitindo rastrear as mudanças no ambiente de execução.
*   **Integração com CI/CD:** Facilita a automação do processo de build, teste e deploy em pipelines de Integração Contínua e Entrega Contínua.

### Negativas

*   **Complexidade Adicional:** Para desenvolvedores não familiarizados com Docker, haverá uma curva de aprendizado para entender os conceitos de contêineres e a sintaxe do Dockerfile.
*   **Overhead de Gerenciamento:** A manutenção dos Dockerfiles e das imagens Docker adiciona uma camada de gerenciamento ao projeto.

## Alternativas Consideradas

*   **Máquinas Virtuais (VMs):** Embora ofereçam um isolamento completo, as VMs são mais pesadas e consomem mais recursos que os contêineres, tornando-as menos eficientes para microsserviços.
*   **Buildpacks:** Uma alternativa mais recente para construir imagens de contêiner sem a necessidade de um Dockerfile. Embora sejam promissores, os Buildpacks são menos maduros e oferecem menos flexibilidade e controle sobre a imagem final em comparação com o Dockerfile.
*   **Implantação Direta no Host:** Implantar a aplicação diretamente no sistema operacional do host, sem contêineres. Esta abordagem não oferece isolamento, portabilidade e reprodutibilidade, tornando-a inadequada para um ambiente de microsserviços moderno.

## Referências

*   [Docker - Documentação Oficial](https://docs.docker.com/)
*   [Darede - O que é DockerFile?](https://www.darede.com.br/o-que-e-dockerfile/)


