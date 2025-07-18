package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId

data class SubcategoryAddedEvent(
    val categoryId: CategoryId,
    val subcategoryId: CategoryId
) : BaseDomainEvent(
    aggregateId = categoryId.value.toString(),
    aggregateType = "Category"
) 