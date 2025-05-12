package com.ia_ecommerce_assistant.catalog.domain.product

import java.util.UUID

// Value Object para o ID do Produto, garantindo tipagem forte.
@JvmInline
value class ProductId(val value: UUID = UUID.randomUUID()) {
    override fun toString(): String = value.toString()
}

