package com.ia_ecommerce_assistant.catalog.domain.events

import com.ia_ecommerce_assistant.catalog.domain.valueobjects.OutboxEventStatus
import java.time.LocalDateTime
import java.util.UUID

data class OutboxEvent(
    val id: UUID,
    val aggregateId: String,
    val aggregateType: String,
    val eventType: String,
    val eventData: String,
    val status: OutboxEventStatus,
    val createdAt: LocalDateTime,
    val processedAt: LocalDateTime?,
    val errorMessage: String?
) {
    companion object {
        fun from(
            domainEvent: DomainEvent,
            aggregateId: String,
            aggregateType: String
        ): OutboxEvent {
            return OutboxEvent(
                id = UUID.randomUUID(),
                aggregateId = aggregateId,
                aggregateType = aggregateType,
                eventType = domainEvent::class.simpleName ?: "UnknownEvent",
                eventData = domainEvent.toString(), // Em produção, seria JSON serializado
                status = OutboxEventStatus.PENDING,
                createdAt = LocalDateTime.now(),
                processedAt = null,
                errorMessage = null
            )
        }
    }
} 