# Event Bus Architecture

> Version: 2.0 | Component: Core Infrastructure

---

## Purpose

The Event Bus is the communication backbone of HRIP. It decouples business modules from each other — a module publishes events without knowing which other modules will consume them.

This enables:
- **Zero direct dependencies** between business modules
- **New modules** to subscribe to existing events without modifying publishers
- **Future migration** to Kafka or any message broker with zero business logic changes

---

## Phase 1: In-Process Event Bus

Phase 1 uses a lightweight **in-process async event dispatcher** built in Python. It runs within the same FastAPI process.

### Design

```
Publisher (Service)         Event Bus              Subscribers
─────────────────        ─────────────        ──────────────────
InventoryService     →   publish(event)  →    AuditSubscriber
                                         →    NotificationSubscriber
                                         →    AnalyticsSubscriber
                                         →    AIEngineSubscriber
```

### Key Classes

```python
# core/events/base.py
@dataclass
class BaseEvent:
    event_id: UUID
    event_type: str          # e.g. "inventory.stock.critical_low"
    aggregate_id: UUID       # ID of the primary entity
    aggregate_type: str      # e.g. "Medicine"
    hospital_id: UUID        # Multi-tenant context
    actor_id: UUID           # User who triggered this
    timestamp: datetime
    payload: dict
    version: int = 1         # Schema version

# core/events/bus.py
class EventBus:
    async def publish(self, event: BaseEvent) -> None: ...
    def subscribe(self, event_type: str, handler: Callable) -> None: ...
    def unsubscribe(self, event_type: str, handler: Callable) -> None: ...

# core/events/registry.py
class HandlerRegistry:
    """Maps event_type strings to lists of async handler functions."""
```

---

## Phase 2: Kafka Migration Path

When the platform scales to multiple instances, the in-process bus is replaced by Kafka. Because all code uses the `EventBus` interface, **zero business module changes are required**.

```python
# All publishers look like this — interface unchanged in Phase 2:
await event_bus.publish(InventoryUpdatedEvent(...))

# Only the implementation changes:
# Phase 1: AsyncEventBus (in-process)
# Phase 2: KafkaEventBus (network)
```

### Kafka Topic Naming Convention

```
hrip.<domain>.<entity>.<action>

Examples:
  hrip.inventory.medicine.stock_critical_low
  hrip.patients.patient.registered
  hrip.beds.bed.status_changed
  hrip.emergency.incident.created
  hrip.ai.recommendation.generated
```

---

## Event Catalogue

### Auth Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `auth.user.logged_in` | user_id, ip, device | audit |
| `auth.user.logged_out` | user_id | audit |
| `auth.user.password_changed` | user_id | audit, notifications |
| `auth.user.failed_login` | user_id, ip, attempt_count | audit |

### Patient Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `patients.patient.registered` | patient_id, hospital_id | audit, notifications, analytics |
| `patients.patient.admitted` | patient_id, bed_id, doctor_id | beds, audit, analytics |
| `patients.patient.discharged` | patient_id, bed_id | beds, audit, analytics |
| `patients.patient.updated` | patient_id, changed_fields | audit |

### Inventory Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `inventory.medicine.stock_updated` | medicine_id, old_qty, new_qty | analytics, audit |
| `inventory.medicine.stock_critical_low` | medicine_id, current_qty, threshold | notifications, ai-engine, audit |
| `inventory.medicine.expiry_approaching` | medicine_id, expiry_date, qty | notifications, audit |
| `inventory.medicine.stock_out` | medicine_id | notifications, ai-engine, audit, emergency |
| `inventory.stock.received` | medicine_id, qty, supplier_id | analytics, audit |
| `inventory.stock.issued` | medicine_id, qty, patient_id | analytics, audit |

### Bed Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `beds.bed.allocated` | bed_id, patient_id, ward | analytics, audit |
| `beds.bed.released` | bed_id, patient_id | analytics, audit, ai-engine |
| `beds.ward.capacity_critical` | ward_id, occupancy_pct | notifications, emergency, ai-engine |

### Doctor Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `doctors.attendance.marked` | doctor_id, status, shift | analytics, audit |
| `doctors.doctor.absent` | doctor_id, date | notifications, audit |

### Emergency Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `emergency.incident.created` | incident_id, type, severity, location | notifications, beds, inventory, ai-engine, audit |
| `emergency.incident.updated` | incident_id, status | notifications, audit |
| `emergency.ambulance.dispatched` | ambulance_id, incident_id | notifications, audit |
| `emergency.incident.closed` | incident_id, outcome | analytics, audit |

### AI Events

| Event Type | Payload | Subscribers |
|:---|:---|:---|
| `ai.recommendation.generated` | recommendation_id, type, hospital_id | notifications, audit |
| `ai.recommendation.approved` | recommendation_id, approved_by | audit, relevant_module |
| `ai.recommendation.rejected` | recommendation_id, reason | audit |

---

## Event Handler Contract

All event handlers must:
1. Be `async` functions
2. Accept a single `BaseEvent` argument
3. Never raise exceptions that kill the bus — log and swallow
4. Be idempotent — safe to call multiple times with same event
5. Complete within 5 seconds (or offload to background task)

```python
async def handle_stock_critical_low(event: BaseEvent) -> None:
    try:
        medicine_id = event.payload["medicine_id"]
        # ... handler logic ...
    except Exception as e:
        logger.error("Handler failed", event_type=event.event_type, error=str(e))
        # Do not re-raise
```

---

## Publisher Contract

Services publish events AFTER the database transaction commits:

```python
# service.py pattern
async def issue_medicine(self, ...) -> MedicineIssue:
    # 1. Business validation
    # 2. Write to DB (via repository)
    result = await self.repository.create_issue(...)
    # 3. Publish event AFTER commit
    await self.event_bus.publish(StockIssuedEvent(
        aggregate_id=result.id,
        hospital_id=...,
        actor_id=...,
        payload={"medicine_id": ..., "qty": ...}
    ))
    return result
```

---

## Error Handling

- Failed handlers are logged with full context
- The event bus never propagates handler exceptions to the publisher
- Critical handler failures trigger a `system.handler.failed` meta-event to the audit log
- Phase 2 (Kafka): failed events go to a Dead Letter Queue (DLQ) for replay
