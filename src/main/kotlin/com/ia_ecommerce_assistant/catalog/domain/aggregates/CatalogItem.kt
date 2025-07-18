package com.ia_ecommerce_assistant.catalog.domain.aggregates

import com.ia_ecommerce_assistant.catalog.domain.entities.ProductAttribute
import com.ia_ecommerce_assistant.catalog.domain.events.CatalogItemPriceUpdatedEvent
import com.ia_ecommerce_assistant.catalog.domain.events.CatalogItemRecategorizedEvent
import com.ia_ecommerce_assistant.catalog.domain.events.CatalogItemUpdatedEvent
import com.ia_ecommerce_assistant.catalog.domain.events.ProductIndexedEvent
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.*
import java.time.LocalDateTime

class CatalogItem : AggregateRoot<ProductId>() {
    
    override lateinit var id: ProductId
        private set
    
    lateinit var productId: ProductId
        private set
    
    lateinit var categoryId: CategoryId
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
    
    var attributes: MutableList<ProductAttribute> = mutableListOf()
        private set
    
    var visible: Boolean = true
        private set
    
    lateinit var lastUpdated: LocalDateTime
        private set
    
    companion object {
        fun from(
            productId: ProductId,
            categoryId: CategoryId,
            name: ProductName,
            description: ProductDescription,
            price: Price,
            brand: Brand,
            sku: SKU,
            attributes: List<ProductAttribute> = emptyList()
        ): CatalogItem {
            val item = CatalogItem()
            item.id = productId
            item.productId = productId
            item.categoryId = categoryId
            item.name = name
            item.description = description
            item.price = price
            item.brand = brand
            item.sku = sku
            item.attributes = attributes.toMutableList()
            item.visible = true
            item.lastUpdated = LocalDateTime.now()
            
            item.addEvent(ProductIndexedEvent(productId, categoryId))
            
            return item
        }
    }
    
    fun updatePrice(newPrice: Price) {
        validatePrice(newPrice)
        this.price = newPrice
        this.lastUpdated = LocalDateTime.now()
        addEvent(CatalogItemPriceUpdatedEvent(this.productId, newPrice))
    }
    
    fun changeCategory(newCategoryId: CategoryId) {
        this.categoryId = newCategoryId
        this.lastUpdated = LocalDateTime.now()
        addEvent(CatalogItemRecategorizedEvent(this.productId, newCategoryId))
    }
    
    fun hide() {
        this.visible = false
        this.lastUpdated = LocalDateTime.now()
        addEvent(CatalogItemUpdatedEvent(this.productId))
    }
    
    fun show() {
        this.visible = true
        this.lastUpdated = LocalDateTime.now()
        addEvent(CatalogItemUpdatedEvent(this.productId))
    }
    
    fun addAttribute(attribute: ProductAttribute) {
        this.attributes.add(attribute)
        this.lastUpdated = LocalDateTime.now()
        addEvent(CatalogItemUpdatedEvent(this.productId))
    }
    
    fun removeAttribute(attributeName: String) {
        this.attributes.removeAll { it.name == attributeName }
        this.lastUpdated = LocalDateTime.now()
        addEvent(CatalogItemUpdatedEvent(this.productId))
    }
    
    private fun validatePrice(price: Price) {
        require(price.value >= Price.of("0").value) { "Price must be non-negative" }
    }
} 