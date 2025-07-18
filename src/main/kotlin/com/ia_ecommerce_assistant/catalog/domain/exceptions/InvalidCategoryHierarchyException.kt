package com.ia_ecommerce_assistant.catalog.domain.exceptions

class InvalidCategoryHierarchyException(message: String) : 
    RuntimeException("Invalid category hierarchy: $message") 