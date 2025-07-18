package com.ia_ecommerce_assistant.catalog.domain.valueobjects

import java.math.BigDecimal

data class Price(val value: BigDecimal) {
    init {
        require(value >= BigDecimal.ZERO) { "Price must be non-negative" }
    }
    
    companion object {
        fun of(value: String): Price = Price(BigDecimal(value))
        fun of(value: Double): Price = Price(BigDecimal.valueOf(value))
        fun of(value: BigDecimal): Price = Price(value)
    }
} 