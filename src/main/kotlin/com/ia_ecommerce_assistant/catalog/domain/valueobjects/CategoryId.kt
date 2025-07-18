package com.ia_ecommerce_assistant.catalog.domain.valueobjects

import java.util.UUID

data class CategoryId(val value: UUID) {
    companion object {
        fun generate(): CategoryId = CategoryId(UUID.randomUUID())
    }
}
