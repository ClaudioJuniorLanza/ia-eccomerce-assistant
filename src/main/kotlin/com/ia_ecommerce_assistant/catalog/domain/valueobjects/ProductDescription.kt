package com.ia_ecommerce_assistant.catalog.domain.valueobjects

data class ProductDescription(val value: String) {
    init {
        require(value.isNotBlank()) { "Product description must not be blank" }
        require(value.length <= 1000) { "Product description must not exceed 1000 characters" }
    }
} 