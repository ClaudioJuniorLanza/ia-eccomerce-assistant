package com.ia_ecommerce_assistant.catalog.domain.exceptions

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId

class ParentCategoryNotFoundException(parentId: CategoryId) : 
    RuntimeException("Parent category not found with id: ${parentId.value}") 