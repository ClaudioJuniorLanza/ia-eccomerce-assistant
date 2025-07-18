package com.ia_ecommerce_assistant.catalog.domain.exceptions

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId

class CategoryNotFoundException(categoryId: CategoryId) : 
    RuntimeException("Category not found with id: ${categoryId.value}") 