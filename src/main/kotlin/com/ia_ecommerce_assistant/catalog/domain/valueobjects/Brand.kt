package com.ia_ecommerce_assistant.catalog.domain.valueobjects

data class Brand(val value: String) {
    init {
        require(value.isNotBlank()) { "Brand must not be blank" }
        require(value.length <= 100) { "Brand must not exceed 100 characters" }
    }
} 