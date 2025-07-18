package com.ia_ecommerce_assistant.catalog.domain.valueobjects

enum class OutboxEventStatus {
    PENDING,
    PROCESSING,
    PROCESSED,
    FAILED
} 