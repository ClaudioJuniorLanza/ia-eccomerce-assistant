package com.ia_ecommerce_assistant.catalog.domain.exceptions

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.ProductId

class ProductNotInCatalogException(productId: ProductId) : 
    RuntimeException("Product not found in catalog with id: ${productId.value}") 