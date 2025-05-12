package com.ia_ecommerce_assistant.catalog.domain.port.driving

import com.ia_ecommerce_assistant.catalog.domain.product.Product
import com.ia_ecommerce_assistant.catalog.domain.product.ProductId
import java.math.BigDecimal

/**
 * Porta Primária (Driving Port) para o caso de uso de criar um novo produto.
 */
interface CreateProductUseCase {
    fun createProduct(command: CreateProductCommand): ProductId
}

data class CreateProductCommand(
    val name: String,
    val description: String,
    val price: BigDecimal,
    val stockQuantity: Int
)

/**
 * Porta Primária (Driving Port) para o caso de uso de buscar um produto pelo ID.
 */
interface GetProductByIdUseCase {
    fun getProductById(id: ProductId): Product?
}

/**
 * Porta Primária (Driving Port) para o caso de uso de listar todos os produtos.
 */
interface ListProductsUseCase {
    fun listProducts(): List<Product>
}

/**
 * Porta Primária (Driving Port) para o caso de uso de atualizar detalhes de um produto.
 */
interface UpdateProductDetailsUseCase {
    fun updateProductDetails(command: UpdateProductDetailsCommand): Product
}

data class UpdateProductDetailsCommand(
    val id: ProductId,
    val name: String? = null, // Campos opcionais para atualização parcial
    val description: String? = null,
    val price: BigDecimal? = null
)

/**
 * Porta Primária (Driving Port) para o caso de uso de atualizar o estoque de um produto.
 */
interface UpdateStockUseCase {
    fun updateStock(id: ProductId, newQuantity: Int): Product
}

