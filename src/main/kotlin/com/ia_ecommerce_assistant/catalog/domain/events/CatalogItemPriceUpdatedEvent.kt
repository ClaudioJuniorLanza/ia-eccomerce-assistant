package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.ProductId
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.Price

data class CatalogItemPriceUpdatedEvent(
    val productId: ProductId,
    val newPrice: Price
) : BaseDomainEvent(
    aggregateId = productId.value.toString(),
    aggregateType = "CatalogItem"
) 