package com.ia_ecommerce_assistant.catalog.domain.exceptions

class InvalidSearchCriteriaException(message: String) : 
    RuntimeException("Invalid search criteria: $message") 