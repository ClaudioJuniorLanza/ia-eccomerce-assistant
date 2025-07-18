package com.ia_ecommerce_assistant.catalog.domain.aggregates

import com.ia_ecommerce_assistant.catalog.domain.events.DomainEvent
import java.util.*

abstract class AggregateRoot<ID> {
    private val uncommittedEvents: MutableList<DomainEvent> = mutableListOf()
    
    abstract val id: ID
    
    protected fun addEvent(event: DomainEvent) {
        uncommittedEvents.add(event)
    }
    
    fun getUncommittedEvents(): List<DomainEvent> = uncommittedEvents.toList()
    
    fun clearEvents() {
        uncommittedEvents.clear()
    }
    
    fun hasUncommittedEvents(): Boolean = uncommittedEvents.isNotEmpty()
} 