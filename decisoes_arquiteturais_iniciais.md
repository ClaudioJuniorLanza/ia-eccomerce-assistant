# Decisões Arquiteturais Iniciais do Projeto IA E-commerce Assistant

Este documento registra as discussões e decisões arquiteturais tomadas no início do projeto "IA E-commerce Assistant", que utilizará uma plataforma de e-commerce simplificada como estudo de caso.

## 1. Adoção da Arquitetura Hexagonal (Portas e Adaptadores)

**Data da Decisão:** 12 de Maio de 2025

**Contexto:**

Para o desenvolvimento da plataforma de e-commerce simplificada, que servirá de base para o aprendizado e atuação da IA Assistente, decidimos adotar o padrão de Arquitetura Hexagonal, também conhecido como Portas e Adaptadores. Esta escolha está alinhada com as boas práticas de desenvolvimento de software moderno e com o ecossistema tecnológico mencionado pelo usuário, que já utiliza arquiteturas homogêneas e Domain-Driven Design (DDD).

**Motivações Principais:**

1.  **Isolamento do Domínio de Negócio:** A principal motivação é proteger a lógica de negócio (o "hexágono" central) de dependências de tecnologias de infraestrutura (frameworks web, bancos de dados, sistemas de mensageria, etc.). Isso permite que o domínio evolua de forma independente.
2.  **Testabilidade:** Ao isolar o domínio, torna-se muito mais fácil testar a lógica de negócio em isolamento, sem a necessidade de mocks complexos ou ambientes de infraestrutura completos. Testes unitários e de integração do domínio são mais rápidos e confiáveis.
3.  **Flexibilidade Tecnológica:** A arquitetura permite trocar ou adicionar novas tecnologias de infraestrutura (adaptadores) sem impactar o núcleo da aplicação. Por exemplo, podemos começar com um banco de dados em memória para o MVP e depois mudar para um PostgreSQL sem alterar a lógica de negócio.
4.  **Manutenibilidade e Evolução:** A clara separação de responsabilidades facilita o entendimento do código, a manutenção e a evolução do sistema a longo prazo. Novas funcionalidades ou integrações podem ser adicionadas de forma mais organizada.
5.  **Alinhamento com Domain-Driven Design (DDD):** A Arquitetura Hexagonal complementa muito bem os princípios do DDD, pois o "hexágono" central naturalmente encapsula os agregados, entidades e serviços de domínio.

**Portas e Adaptadores no Contexto do E-commerce:**

*   **Portas Primárias (Driving Adapters):** Serão as interfaces que conduzem a aplicação, como APIs REST (para interações de frontend ou outros serviços), consumidores de eventos Kafka (para processamento assíncrono de pedidos, por exemplo), ou até mesmo uma CLI para administração.
*   **Portas Secundárias (Driven Adapters):** Serão as interfaces que a aplicação usa para interagir com o mundo externo, como repositórios de banco de dados (para persistir Produtos, Pedidos, Clientes), clientes de serviços de terceiros (gateways de pagamento, serviços de entrega – mesmo que simulados no MVP), ou produtores de eventos Kafka.

**Considerações para o Projeto de Estudo:**

*   Mesmo sendo um projeto de estudo, a aplicação desses princípios desde o início fornecerá um excelente material para a IA Assistente aprender sobre decisões de design e suas justificativas.
*   A IA poderá, no futuro, analisar o código e verificar a aderência a este padrão, ou ajudar a identificar onde novas portas e adaptadores podem ser necessários.

**Próximos Passos Imediatos:**

*   Definir as principais portas para os módulos de Catálogo, Carrinho e Pedidos do e-commerce.
*   Começar a modelar os objetos de domínio (entidades, value objects) que residirão no hexágono.

## 2. Discussão sobre Mensageria: Kafka e Padrão Outbox (A ser detalhado)

**Contexto:** O usuário mencionou o interesse em usar Kafka para comunicação entre microsserviços e a possibilidade de usar Kafka Connect com o padrão Outbox Pattern, além de políticas para isolar o consumo de eventos.

**Status:** Esta é uma discussão arquitetural importante que será detalhada em uma seção subsequente. O objetivo será registrar as vantagens do Outbox Pattern (garantir consistência entre a escrita no banco de dados e a publicação de eventos), como o Kafka Connect pode facilitar sua implementação, e as considerações sobre o isolamento de eventos.

*(Esta seção será expandida conforme avançamos na discussão e implementação)*

## 3. Modelagem Inicial do Domínio: Módulo de Catálogo - Entidade Produto

**Data da Decisão:** 12 de Maio de 2025

**Contexto:**
Iniciando a implementação do Módulo de Catálogo da plataforma de e-commerce simplificada, a primeira entidade a ser modelada é `Produto`. Esta entidade residirá no núcleo do nosso domínio, seguindo os princípios da Arquitetura Hexagonal e do Domain-Driven Design (DDD).

**Definição da Entidade `Produto` (Versão Inicial - Kotlin):**

```kotlin
package com.ia_ecommerce_assistant.catalog.domain.product

import java.math.BigDecimal
import java.util.UUID

// Representa um Produto no nosso catálogo.
// Esta é uma Entidade no contexto do DDD, identificada por um 'id'.
data class Product(
    val id: ProductId,          // Identificador único do produto
    var name: String,           // Nome do produto
    var description: String,    // Descrição detalhada do produto
    var price: BigDecimal,      // Preço do produto
    var stockQuantity: Int      // Quantidade em estoque (simulada inicialmente)
) {
    // Comportamentos da entidade podem ser adicionados aqui.
    // Por exemplo, para atualizar o estoque, verificar disponibilidade, etc.

    fun updateStock(newQuantity: Int) {
        if (newQuantity < 0) {
            throw IllegalArgumentException("Estoque não pode ser negativo.")
        }
        this.stockQuantity = newQuantity
    }

    fun changePrice(newPrice: BigDecimal) {
        if (newPrice <= BigDecimal.ZERO) {
            throw IllegalArgumentException("Preço deve ser positivo.")
        }
        this.price = newPrice
    }
}

// Value Object para o ID do Produto, garantindo tipagem forte.
@JvmInline
value class ProductId(val value: UUID = UUID.randomUUID()) {
    override fun toString(): String = value.toString()
}
```

**Justificativas e Decisões de Design:**

1.  **Linguagem Kotlin:** Conforme preferência do usuário e adequação para desenvolvimento moderno e conciso.
2.  **`data class` para `Product`:** Simplifica a criação de classes que armazenam dados, fornecendo automaticamente `equals()`, `hashCode()`, `toString()`, `copy()`, etc.
3.  **`ProductId` como `value class` (inline class):** Para criar um tipo específico para o ID do produto, evitando o uso de `UUID` diretamente no domínio e melhorando a semântica e a segurança de tipo. O `@JvmInline` é a anotação moderna para inline classes.
4.  **Atributos Iniciais:**
    *   `id`: Identificador único, essencial para uma Entidade DDD.
    *   `name`, `description`, `price`: Atributos básicos de um produto.
    *   `stockQuantity`: Quantidade em estoque, inicialmente simulada. A lógica de atualização (`updateStock`) já inclui uma validação básica.
    *   `price`: Utilização de `BigDecimal` para representar valores monetários, evitando problemas de precisão com tipos de ponto flutuante.
5.  **Mutabilidade Seletiva:** `name`, `description`, `price`, e `stockQuantity` são `var` para permitir modificações (ex: atualização de preço, descrição ou estoque). O `id` é `val` pois é o identificador imutável da entidade.
6.  **Comportamentos na Entidade:** Incluídos métodos como `updateStock` e `changePrice` diretamente na entidade `Product`, alinhando-se com o princípio do DDD de manter a lógica de negócio próxima aos dados que ela opera (Rich Domain Model).

**Portas Previstas para a Entidade `Produto` (a serem detalhadas):**

*   **Portas Primárias (Driving Adapters - Casos de Uso):**
    *   `CreateProductUseCase`: Para adicionar um novo produto ao catálogo.
    *   `GetProductByIdUseCase`: Para buscar um produto específico pelo seu ID.
    *   `ListProductsUseCase`: Para listar produtos (com possíveis filtros e paginação no futuro).
    *   `UpdateProductDetailsUseCase`: Para modificar informações de um produto existente.
    *   `UpdateStockUseCase`: Para ajustar o estoque de um produto.
*   **Portas Secundárias (Driven Adapters - Infraestrutura):**
    *   `ProductRepositoryPort`: Interface que define as operações de persistência para produtos (ex: `save(product: Product)`, `findById(id: ProductId): Product?`, `findAll(): List<Product>`). A implementação concreta desta porta (ex: usando um banco de dados SQL, NoSQL ou em memória) será um adaptador.

**Próximos Passos para o Módulo de Catálogo:**

*   Implementar a estrutura de pastas para o domínio do catálogo (`com.ia_ecommerce_assistant.catalog.domain.product`).
*   Criar os arquivos Kotlin para `Product.kt` e `ProductId.kt`.
*   Definir as interfaces para as Portas (Casos de Uso e Repositório).
*   Criar um adaptador de repositório em memória para o MVP.
*   Começar a implementar os casos de uso básicos.

*(Esta seção será atualizada conforme o desenvolvimento do módulo de catálogo avança e novas decisões são tomadas.)*



## 4. Implementação do Serviço de Aplicação para Catálogo (`ProductService`)

**Data da Decisão/Implementação:** 12 de Maio de 2025

**Contexto:**
Com as entidades de domínio (`Product`, `ProductId`), as portas de driving (`ProductUseCasesPort.kt` contendo `CreateProductUseCase`, `GetProductByIdUseCase`, etc.) e a porta driven (`ProductRepositoryPort`) definidas, além de um adaptador de persistência em memória (`InMemoryProductRepositoryAdapter`), o próximo passo é implementar o serviço de aplicação que orquestra a lógica para os casos de uso do catálogo.

**Implementação:**
Foi criado o `ProductService.kt` em `com.ia_ecommerce_assistant.catalog.application.service`.

```kotlin
package com.ia_ecommerce_assistant.catalog.application.service

import com.ia_ecommerce_assistant.catalog.domain.product.Product
import com.ia_ecommerce_assistant.catalog.domain.product.ProductId
import com.ia_ecommerce_assistant.catalog.domain.port.driven.ProductRepositoryPort
import com.ia_ecommerce_assistant.catalog.domain.port.driving.*
import java.math.BigDecimal

class ProductService(
    private val productRepository: ProductRepositoryPort
) : CreateProductUseCase, GetProductByIdUseCase, ListProductsUseCase, UpdateProductDetailsUseCase, UpdateStockUseCase {

    override fun createProduct(command: CreateProductCommand): ProductId {
        val product = Product(
            id = ProductId(),
            name = command.name,
            description = command.description,
            price = command.price,
            stockQuantity = command.stockQuantity
        )
        productRepository.save(product)
        return product.id
    }

    override fun getProductById(id: ProductId): Product? {
        return productRepository.findById(id)
    }

    override fun listProducts(): List<Product> {
        return productRepository.findAll()
    }

    override fun updateProductDetails(command: UpdateProductDetailsCommand): Product {
        val product = productRepository.findById(command.id)
            ?: throw NoSuchElementException("Produto com ID ${command.id} não encontrado.")

        command.name?.let { product.name = it }
        command.description?.let { product.description = it }
        command.price?.let { product.changePrice(it) }

        return productRepository.save(product)
    }

    override fun updateStock(id: ProductId, newQuantity: Int): Product {
        val product = productRepository.findById(id)
            ?: throw NoSuchElementException("Produto com ID $id não encontrado.")

        product.updateStock(newQuantity)
        return productRepository.save(product)
    }
}
```

**Justificativas e Decisões de Design:**

1.  **Injeção de Dependência:** O `ProductService` recebe uma instância de `ProductRepositoryPort` via construtor, seguindo o princípio de Inversão de Dependência. Isso permite que a implementação concreta do repositório seja facilmente trocada (ex: de `InMemoryProductRepositoryAdapter` para um adaptador de banco de dados real) sem alterar o serviço de aplicação.
2.  **Implementação das Interfaces de Caso de Uso:** O `ProductService` implementa as interfaces definidas em `ProductUseCasesPort.kt`, tornando explícitos os casos de uso que ele suporta.
3.  **Orquestração e Delegação:** O serviço não contém lógica de negócio complexa. Ele orquestra o fluxo: recebe um comando (DTO), interage com o repositório para buscar ou salvar entidades, e pode chamar métodos de domínio nas próprias entidades para executar lógica de negócio (como `product.updateStock()` ou `product.changePrice()`).
4.  **Tratamento de Exceções (Básico):** No caso de um produto não ser encontrado para atualização, uma `NoSuchElementException` é lançada. Em um sistema real, um tratamento de erro mais robusto e específico do domínio seria implementado.
5.  **Retorno de Tipos de Domínio ou Primitivos:** Os casos de uso retornam `ProductId`, `Product` ou `List<Product>`, mantendo a consistência com os tipos de domínio.

**Próximos Passos:**

*   Realizar o commit desta implementação no repositório Git.
*   Começar a planejar a integração da IA para analisar estes artefatos de código e a documentação de decisão associada.
*   Considerar a implementação de testes unitários para o `ProductService` e para as entidades de domínio.
