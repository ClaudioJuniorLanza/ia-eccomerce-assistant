# ADR 003: Adoção do Gerenciador de Dependências e Build Gradle

## Status

Proposto

## Contexto

O projeto IA E-commerce Assistant está desenvolvendo um microsserviço em Kotlin. A ausência de um sistema de build e gerenciador de dependências padronizado pode levar a inconsistências no processo de compilação, dificuldades no gerenciamento de bibliotecas e dependências, e impactar negativamente a produtividade do desenvolvedor. É fundamental adotar uma ferramenta robusta que se integre bem com Kotlin e suporte as necessidades de um projeto de microsserviços.

## Decisão

Adotar o **Gradle** como o sistema de build e gerenciador de dependências para o microsserviço do projeto. O Gradle é um sistema de automação de build de código aberto que oferece flexibilidade e eficiência na construção de aplicações, com suporte nativo a Kotlin DSL.

## Consequências

### Positivas

*   **Flexibilidade e Extensibilidade:** Permite configurações de build altamente personalizadas através de sua DSL, ideal para projetos complexos e requisitos específicos.
*   **Desempenho Superior:** Utiliza cache de build, compilação incremental e paralelização de tarefas, acelerando significativamente o processo de build.
*   **Gerenciamento de Dependências Robusto:** Facilita a resolução de dependências transitivas, gerenciamento de conflitos e integração com diversos repositórios.
*   **Suporte a Kotlin DSL:** Oferece autocompletar, verificação de tipo em tempo de compilação e melhor legibilidade para desenvolvedores Kotlin, otimizando a experiência de desenvolvimento.
*   **Automação de Tarefas:** Além do build, pode ser usado para automatizar diversas tarefas de desenvolvimento, como execução de testes, geração de documentação e deploy.

### Negativas

*   **Curva de Aprendizagem:** Desenvolvedores não familiarizados com Gradle, especialmente com sua DSL, podem enfrentar uma curva de aprendizado inicial.
*   **Complexidade para Pequenos Projetos:** Para projetos muito simples, a flexibilidade do Gradle pode parecer excessiva, adicionando uma complexidade inicial desnecessária.

## Alternativas Consideradas

*   **Apache Maven:** Um sistema de build maduro e amplamente utilizado, baseado em convenções. Embora seja uma alternativa sólida, o Maven é mais verboso (XML) e menos flexível que o Gradle para customizações complexas. Além disso, o suporte nativo a Kotlin DSL no Gradle é uma vantagem significativa para este projeto.
*   **Apache Ant:** Uma ferramenta de build mais antiga e de baixo nível, que exige que o desenvolvedor especifique explicitamente cada passo do processo de build. É menos produtivo e flexível que o Gradle para gerenciamento de dependências e automação de tarefas complexas.

## Referências

*   [Gradle - Site Oficial](https://gradle.org/)
*   [HNZ - Gradle: saiba o que é e como utilizar](https://hnz.com.br/gradle-saiba-o-que-e-e-como-utilizar/)


