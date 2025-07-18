package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId

data class CategoryDeactivatedEvent(
    val categoryId: CategoryId
) : BaseDomainEvent(
    aggregateId = categoryId.value.toString(),
    aggregateType = "Category"
) 