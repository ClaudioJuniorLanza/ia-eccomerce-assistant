package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryName
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryHierarchy

data class CategoryCreatedEvent(
    val categoryId: CategoryId,
    val name: CategoryName,
    val hierarchy: CategoryHierarchy
) : BaseDomainEvent(
    aggregateId = categoryId.value.toString(),
    aggregateType = "Category"
) 