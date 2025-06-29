# ADR 002: Adoção do Framework Quarkus

## Status

Proposto

## Contexto

O projeto IA E-commerce Assistant está desenvolvendo um microsserviço em Kotlin, com foco em arquitetura hexagonal e implantação em ambientes de nuvem e contêineres. A escolha de um framework de aplicação adequado é crucial para garantir a performance, escalabilidade, manutenibilidade e produtividade do desenvolvimento. Atualmente, o microsserviço não possui um framework de aplicação definido, o que pode levar a um desenvolvimento menos padronizado e otimizado para o ambiente de nuvem.

## Decisão

Adotar o framework **Quarkus** para o desenvolvimento do microsserviço em Kotlin. O Quarkus é um framework Java nativo do Kubernetes, otimizado para JVMs e compilação nativa (GraalVM), projetado para a era do cloud computing e microsserviços.

## Consequências

### Positivas

*   **Performance Aprimorada:** Tempos de inicialização rápidos e baixo consumo de memória, ideais para microsserviços e funções serverless, resultando em menor custo de infraestrutura e maior densidade de aplicações por servidor.
*   **Produtividade do Desenvolvedor:** Recursos como "live coding" e uma experiência de desenvolvimento otimizada aceleram o ciclo de desenvolvimento e depuração.
*   **Otimização para Nuvem e Kubernetes:** Facilita a criação e implantação de aplicações em contêineres, com suporte nativo para recursos do Kubernetes.
*   **Ecossistema Abrangente:** Integração com bibliotecas e APIs populares do Java, permitindo o uso de ferramentas familiares.
*   **Compilação Nativa:** Possibilidade de compilar para executáveis nativos com GraalVM para desempenho ainda maior.

### Negativas

*   **Curva de Aprendizagem:** Desenvolvedores não familiarizados com Quarkus precisarão de tempo para aprender o framework e suas particularidades.
*   **Dependência de Tecnologia:** O projeto ficará acoplado ao ecossistema Quarkus, embora seja um framework robusto e com boa comunidade.

## Alternativas Consideradas

*   **Spring Boot:** Embora seja um framework maduro e amplamente utilizado, o Spring Boot tradicionalmente possui tempos de inicialização e consumo de memória maiores em comparação com o Quarkus, o que pode ser uma desvantagem em ambientes de microsserviços e serverless.
*   **Micronaut:** Outro framework moderno para microsserviços, com foco em baixo consumo de memória e inicialização rápida. É uma alternativa viável, mas o Quarkus foi escolhido devido à sua maior maturidade no ecossistema Red Hat/Kubernetes e ao suporte mais abrangente a tecnologias Java existentes.
*   **Ktor:** Um framework Kotlin nativo para construir aplicações web assíncronas. Embora seja uma excelente opção para Kotlin, o Quarkus oferece um ecossistema mais amplo e otimizações mais profundas para ambientes de contêineres e compilação nativa, que são cruciais para os objetivos do projeto.

## Referências

*   [Quarkus - Site Oficial](https://quarkus.io/)
*   [Red Hat - O que é Quarkus?](https://www.redhat.com/pt-br/topics/cloud-native-apps/what-is-quarkus)


