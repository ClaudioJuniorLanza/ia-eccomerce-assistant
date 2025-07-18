package com.ia_ecommerce_assistant.catalog.domain.valueobjects

data class ProductName(val value: String) {
    init {
        require(value.isNotBlank()) { "Product name must not be blank" }
        require(value.length <= 255) { "Product name must not exceed 255 characters" }
    }
} 