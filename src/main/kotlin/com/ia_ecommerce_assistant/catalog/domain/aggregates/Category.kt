package com.ia_ecommerce_assistant.catalog.domain.aggregates

import com.ia_ecommerce_assistant.catalog.domain.entities.Subcategory
import com.ia_ecommerce_assistant.catalog.domain.events.CategoryCreatedEvent
import com.ia_ecommerce_assistant.catalog.domain.events.CategoryDeactivatedEvent
import com.ia_ecommerce_assistant.catalog.domain.events.SubcategoryAddedEvent
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryId
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryName
import com.ia_ecommerce_assistant.catalog.domain.valueobjects.CategoryHierarchy
import java.time.LocalDateTime

class Category : AggregateRoot<CategoryId>() {
    
    override lateinit var id: CategoryId
        private set
    
    lateinit var name: CategoryName
        private set
    
    lateinit var hierarchy: CategoryHierarchy
        private set
    
    var subcategories: MutableList<Subcategory> = mutableListOf()
        private set
    
    var active: Boolean = true
        private set
    
    lateinit var createdAt: LocalDateTime
        private set
    
    companion object {
        fun create(
            name: CategoryName,
            hierarchy: CategoryHierarchy,
            description: String
        ): Category {
            val category = Category()
            category.id = CategoryId.generate()
            category.name = name
            category.hierarchy = hierarchy
            category.subcategories = mutableListOf()
            category.active = true
            category.createdAt = LocalDateTime.now()
            
            category.addEvent(CategoryCreatedEvent(category.id, name, hierarchy))
            
            return category
        }
    }
    
    fun addSubcategory(subcategory: Subcategory) {
        validateSubcategoryAddition(subcategory)
        this.subcategories.add(subcategory)
        addEvent(SubcategoryAddedEvent(this.id, subcategory.id))
    }
    
    fun deactivate() {
        this.active = false
        addEvent(CategoryDeactivatedEvent(this.id))
    }
    
    fun getAllDescendantIds(): List<CategoryId> {
        return subcategories.map { it.id }
    }
    
    fun isDescendantOf(potentialAncestor: Category): Boolean {
        return this.hierarchy.isDescendantOf(potentialAncestor.hierarchy)
    }
    
    fun getHierarchyLevel(): Int = hierarchy.level
    
    private fun validateSubcategoryAddition(subcategory: Subcategory) {
        // Validações de negócio para adicionar subcategoria
        require(subcategory.active) { "Subcategory must be active" }
        require(subcategories.none { it.id == subcategory.id }) { "Subcategory already exists" }
    }
} 