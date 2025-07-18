package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.ProductId

data class CatalogItemUpdatedEvent(
    val productId: ProductId
) : BaseDomainEvent(
    aggregateId = productId.value.toString(),
    aggregateType = "CatalogItem"
) 