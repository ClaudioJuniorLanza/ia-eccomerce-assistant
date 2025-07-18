package com.ia_ecommerce_assistant.catalog.domain.valueobjects

data class CategoryName(val value: String) {
    init {
        require(value.isNotBlank()) { "Category name must not be blank" }
    }
}
