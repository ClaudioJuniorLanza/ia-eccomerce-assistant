package com.ia_ecommerce_assistant.catalog.domain.entities

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryName

data class Subcategory(
    val id: CategoryId,
    val name: CategoryName,
    val description: String?,
    val active: Boolean = true
) 