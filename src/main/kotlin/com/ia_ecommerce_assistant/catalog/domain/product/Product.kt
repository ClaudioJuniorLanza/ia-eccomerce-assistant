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

