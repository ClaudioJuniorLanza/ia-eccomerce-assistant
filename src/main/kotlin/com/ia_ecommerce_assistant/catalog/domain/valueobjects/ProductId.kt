package com.ia_ecommerce_assistant.catalog.domain.valueobjects

import java.util.UUID

data class ProductId(val value: UUID) {
    companion object {
        fun generate(): ProductId = ProductId(UUID.randomUUID())
    }
} 