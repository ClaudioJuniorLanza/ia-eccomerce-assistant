package com.ia_ecommerce_assistant.catalog.domain.port.driven

import com.ia_ecommerce_assistant.catalog.domain.product.Product
import com.ia_ecommerce_assistant.catalog.domain.product.ProductId

/**
 * Porta Secundária (Driven Port) para interações de persistência com a entidade Produto.
 * Define o contrato que os adaptadores de infraestrutura (ex: banco de dados) devem implementar.
 */
interface ProductRepositoryPort {
    fun save(product: Product): Product
    fun findById(id: ProductId): Product?
    fun findAll(): List<Product>
    fun deleteById(id: ProductId): Boolean
    // Outras operações de busca podem ser adicionadas aqui, ex: findByName, findByPriceRange, etc.
}

