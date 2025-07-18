package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.ProductId
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId

data class CatalogItemRecategorizedEvent(
    val productId: ProductId,
    val newCategoryId: CategoryId
) : BaseDomainEvent(
    aggregateId = productId.value.toString(),
    aggregateType = "CatalogItem"
) 