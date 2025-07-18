package com.ia_ecommerce_assistant.catalog.domain.valueobjects

data class SKU(val value: String) {
    init {
        require(value.isNotBlank()) { "SKU must not be blank" }
        require(value.length <= 50) { "SKU must not exceed 50 characters" }
        require(value.matches(Regex("^[A-Z0-9-_]+$"))) { "SKU must contain only uppercase letters, numbers, hyphens and underscores" }
    }
} 