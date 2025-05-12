package com.ia_ecommerce_assistant.catalog.application.service

import com.ia_ecommerce_assistant.catalog.domain.product.Product
import com.ia_ecommerce_assistant.catalog.domain.product.ProductId
import com.ia_ecommerce_assistant.catalog.domain.port.driven.ProductRepositoryPort
import com.ia_ecommerce_assistant.catalog.domain.port.driving.*
import java.math.BigDecimal

/**
 * Serviço de aplicação que implementa os casos de uso para a entidade Produto.
 * Orquestra a lógica de aplicação e interage com as portas do domínio.
 */
class ProductService(
    private val productRepository: ProductRepositoryPort
) : CreateProductUseCase, GetProductByIdUseCase, ListProductsUseCase, UpdateProductDetailsUseCase, UpdateStockUseCase {

    override fun createProduct(command: CreateProductCommand): ProductId {
        val product = Product(
            id = ProductId(), // Gera novo ID
            name = command.name,
            description = command.description,
            price = command.price,
            stockQuantity = command.stockQuantity
        )
        // Validações de negócio podem ser adicionadas aqui ou na entidade, se apropriado.
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
        command.price?.let { product.changePrice(it) } // Usando o método da entidade para validação

        return productRepository.save(product)
    }

    override fun updateStock(id: ProductId, newQuantity: Int): Product {
        val product = productRepository.findById(id)
            ?: throw NoSuchElementException("Produto com ID $id não encontrado.")

        product.updateStock(newQuantity) // Usando o método da entidade para validação
        return productRepository.save(product)
    }
}

