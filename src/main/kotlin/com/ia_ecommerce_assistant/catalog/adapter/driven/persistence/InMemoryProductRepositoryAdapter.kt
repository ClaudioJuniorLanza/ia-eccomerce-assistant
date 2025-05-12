package com.ia_ecommerce_assistant.catalog.adapter.driven.persistence

import com.ia_ecommerce_assistant.catalog.domain.product.Product
import com.ia_ecommerce_assistant.catalog.domain.product.ProductId
import com.ia_ecommerce_assistant.catalog.domain.port.driven.ProductRepositoryPort
import java.util.concurrent.ConcurrentHashMap

/**
 * Implementação em memória do ProductRepositoryPort para o MVP.
 * Simula a persistência de produtos sem a necessidade de um banco de dados externo.
 */
class InMemoryProductRepositoryAdapter : ProductRepositoryPort {

    private val products: MutableMap<ProductId, Product> = ConcurrentHashMap()

    override fun save(product: Product): Product {
        products[product.id] = product
        return product
    }

    override fun findById(id: ProductId): Product? {
        return products[id]
    }

    override fun findAll(): List<Product> {
        return products.values.toList()
    }

    override fun deleteById(id: ProductId): Boolean {
        return products.remove(id) != null
    }
}

