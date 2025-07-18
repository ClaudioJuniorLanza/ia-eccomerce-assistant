package com.ia_ecommerce_assistant.catalog.domain.events

import java.time.LocalDateTime
import java.util.UUID

interface DomainEvent {
    val eventId: UUID
    val occurredAt: LocalDateTime
    val aggregateId: String
    val aggregateType: String
}

abstract class BaseDomainEvent(
    override val aggregateId: String,
    override val aggregateType: String
) : DomainEvent {
    override val eventId: UUID = UUID.randomUUID()
    override val occurredAt: LocalDateTime = LocalDateTime.now()
} 