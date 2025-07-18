package com.ia_ecommerce_assistant.catalog.domain.valueobjects

/**
 * Representa a hierarquia de uma categoria (ex: caminho no catálogo)
 */
data class CategoryHierarchy(
    val path: List<CategoryId>
) {
    val level: Int get() = path.size
    
    fun addLevel(): CategoryHierarchy {
        return copy(path = path + CategoryId.generate())
    }
    
    fun isDescendantOf(other: CategoryHierarchy): Boolean {
        if (other.path.size >= this.path.size) return false
        return this.path.take(other.path.size) == other.path
    }
    
    fun isRoot(): Boolean = path.isEmpty()
    
    companion object {
        fun root(): CategoryHierarchy = CategoryHierarchy(emptyList())
    }
}
