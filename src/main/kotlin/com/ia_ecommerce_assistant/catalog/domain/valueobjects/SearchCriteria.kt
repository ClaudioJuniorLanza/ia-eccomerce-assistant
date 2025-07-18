package com.ia_ecommerce_assistant.catalog.domain.valueobjects

data class SearchCriteria(
    val searchTerm: String?,
    val categoryFilter: List<CategoryId>?,
    val priceRange: PriceRange?,
    val brandFilter: List<Brand>?,
    val sortBy: SortOption,
    val page: Int,
    val size: Int
) {
    init {
        require(page >= 0) { "Page must be non-negative" }
        require(size > 0 && size <= 100) { "Size must be between 1 and 100" }
    }
    
    companion object {
        fun builder(): SearchCriteriaBuilder = SearchCriteriaBuilder()
    }
    
    data class PriceRange(
        val minPrice: Price?,
        val maxPrice: Price?
    ) {
        init {
            if (minPrice != null && maxPrice != null) {
                require(minPrice.value <= maxPrice.value) { "Min price must be less than or equal to max price" }
            }
        }
    }
    
    enum class SortOption {
        NAME_ASC, NAME_DESC, PRICE_ASC, PRICE_DESC, RELEVANCE
    }
    
    class SearchCriteriaBuilder {
        private var searchTerm: String? = null
        private var categoryFilter: List<CategoryId>? = null
        private var priceRange: SearchCriteria.PriceRange? = null
        private var brandFilter: List<Brand>? = null
        private var sortBy: SearchCriteria.SortOption = SearchCriteria.SortOption.RELEVANCE
        private var page: Int = 0
        private var size: Int = 20
        
        fun searchTerm(term: String?): SearchCriteriaBuilder {
            this.searchTerm = term
            return this
        }
        
        fun categoryFilter(categories: List<CategoryId>?): SearchCriteriaBuilder {
            this.categoryFilter = categories
            return this
        }
        
        fun priceRange(min: Price?, max: Price?): SearchCriteriaBuilder {
            this.priceRange = SearchCriteria.PriceRange(min, max)
            return this
        }
        
        fun brandFilter(brands: List<Brand>?): SearchCriteriaBuilder {
            this.brandFilter = brands
            return this
        }
        
        fun sortBy(sort: SearchCriteria.SortOption): SearchCriteriaBuilder {
            this.sortBy = sort
            return this
        }
        
        fun page(page: Int): SearchCriteriaBuilder {
            this.page = page
            return this
        }
        
        fun size(size: Int): SearchCriteriaBuilder {
            this.size = size
            return this
        }
        
        fun build(): SearchCriteria = SearchCriteria(
            searchTerm, categoryFilter, priceRange, brandFilter, sortBy, page, size
        )
    }
} 