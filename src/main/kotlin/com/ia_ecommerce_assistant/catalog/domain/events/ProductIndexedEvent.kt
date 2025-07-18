package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.ProductId
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId

data class ProductIndexedEvent(
    val productId: ProductId,
    val categoryId: CategoryId
) : BaseDomainEvent(
    aggregateId = productId.value.toString(),
    aggregateType = "CatalogItem"
) 