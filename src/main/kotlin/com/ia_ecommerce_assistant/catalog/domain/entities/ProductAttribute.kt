package com.ia_ecommerce_assistant.catalog.domain.entities

data class ProductAttribute(
    val name: String,
    val value: String,
    val type: AttributeType
) {
    init {
        require(name.isNotBlank()) { "Attribute name must not be blank" }
        require(value.isNotBlank()) { "Attribute value must not be blank" }
    }
    
    enum class AttributeType {
        TEXT, NUMBER, BOOLEAN, COLOR, SIZE, WEIGHT, DIMENSION
    }
} 