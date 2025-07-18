package com.ia_ecommerce_assistant.catalog.domain.aggregates

import com.ia_ecommerce_assistant.catalog.domain.entities.ProductAttribute
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.*
import java.time.LocalDateTime

class ProductIndex : AggregateRoot<ProductId>() {
    
    override lateinit var id: ProductId
        private set
    
    lateinit var name: ProductName
        private set
    
    lateinit var description: ProductDescription
        private set
    
    lateinit var price: Price
        private set
    
    lateinit var brand: Brand
        private set
    
    lateinit var sku: SKU
        private set
    
    lateinit var categoryId: CategoryId
        private set
    
    var attributes: MutableList<ProductAttribute> = mutableListOf()
        private set
    
    var searchableText: String = ""
        private set
    
    var indexedAt: LocalDateTime = LocalDateTime.now()
        private set
    
    companion object {
        fun from(catalogItem: CatalogItem): ProductIndex {
            val index = ProductIndex()
            index.id = catalogItem.productId
            index.name = catalogItem.name
            index.description = catalogItem.description
            index.price = catalogItem.price
            index.brand = catalogItem.brand
            index.sku = catalogItem.sku
            index.categoryId = catalogItem.categoryId
            index.attributes = catalogItem.attributes.toMutableList()
            index.searchableText = buildSearchableText(catalogItem)
            index.indexedAt = LocalDateTime.now()
            
            return index
        }
        
        private fun buildSearchableText(catalogItem: CatalogItem): String {
            return buildString {
                append(catalogItem.name.value.lowercase())
                append(" ")
                append(catalogItem.description.value.lowercase())
                append(" ")
                append(catalogItem.brand.value.lowercase())
                append(" ")
                append(catalogItem.sku.value.lowercase())
                catalogItem.attributes.forEach { attribute ->
                    append(" ")
                    append(attribute.name.lowercase())
                    append(" ")
                    append(attribute.value.lowercase())
                }
            }.trim()
        }
    }
    
    fun updateFrom(catalogItem: CatalogItem) {
        this.name = catalogItem.name
        this.description = catalogItem.description
        this.price = catalogItem.price
        this.brand = catalogItem.brand
        this.sku = catalogItem.sku
        this.categoryId = catalogItem.categoryId
        this.attributes = catalogItem.attributes.toMutableList()
        this.searchableText = buildSearchableText(catalogItem)
        this.indexedAt = LocalDateTime.now()
    }
    
    private fun buildSearchableText(catalogItem: CatalogItem): String {
        return buildString {
            append(catalogItem.name.value.lowercase())
            append(" ")
            append(catalogItem.description.value.lowercase())
            append(" ")
            append(catalogItem.brand.value.lowercase())
            append(" ")
            append(catalogItem.sku.value.lowercase())
            catalogItem.attributes.forEach { attribute ->
                append(" ")
                append(attribute.name.lowercase())
                append(" ")
                append(attribute.value.lowercase())
            }
        }.trim()
    }
} 