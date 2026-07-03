# Module Boundaries

> Version: 2.0 | This document is the single source of truth for inter-module communication rules.

---

## The Core Rule

**Modules must never import from each other's internal layers.**

Modules communicate exclusively through:
1. **The Event Bus** (async, decoupled, fire-and-forget)
2. **Defined API contracts** (for synchronous cross-module data needs — rare)

---

## What Counts as a Module

Each subdirectory under `backend/app/modules/` is a module:

```
auth, users, hospitals, patients, inventory, beds,
doctors, laboratory, emergency, notifications,
analytics, reports, audit
```

The `core/` and `shared/` directories are **not modules** — they are infrastructure used by all modules.

---

## Permitted Imports

```python
# Any module CAN import from:
from app.core.database.base import BaseRepository          # Infrastructure
from app.core.events.bus import EventBus                   # Infrastructure
from app.core.security.rbac import require_permission      # Infrastructure
from app.shared.pagination import PaginationParams         # Shared utility
from app.shared.response import ApiResponse                # Shared utility
from app.core.exceptions.base import HRIPError             # Shared exception
```

## Forbidden Imports

```python
# NEVER do this:
from app.modules.patients.service import PatientService    # Cross-module service import
from app.modules.inventory.repository import InventoryRepo # Cross-module repo import
from app.modules.beds.models import Bed                    # Cross-module model import
```

---

## Data Sharing Patterns

### Pattern 1: Event-Driven (Preferred)

When a module needs to react to something that happened in another module:

```
[Patients module] → publishes PatientAdmittedEvent
    ↓ Event Bus
[Beds module] → subscribes, marks bed as occupied
[Analytics] → subscribes, updates occupancy KPI
[Audit] → subscribes, writes audit log
```

The Patients module never calls the Beds module directly.

### Pattern 2: Internal API Call (Synchronous Dependency)

Rare cases where a module MUST have data from another module synchronously. Use HTTP to the other module's router. Do NOT import the service class.

```python
# ACCEPTABLE (in exceptional cases only):
import httpx
response = await httpx.get(f"/api/v1/hospitals/{hospital_id}")
```

### Pattern 3: Shared Read Model (Read-Only)

For cross-cutting read queries (e.g., analytics, reports), modules may share a read-only database view. These are defined in `database/views/` and accessed through a dedicated read repository.

---

## Module Dependency Map

```
core/ (no module dependencies)
    ↑ all modules depend on core

auth ──────────────────────────────── (depends only on core)
    ↓
users ─────────────────────────────── (depends on core; references auth.users table by FK)
    ↓
hospitals ─────────────────────────── (depends on core)
    ↓
patients ──────────────────────────── (references hospitals by FK; publishes events)
    ↓
inventory ─────────────────────────── (references hospitals by FK; publishes events)
    ↓
beds ──────────────────────────────── (references hospitals; subscribes to patient events)
    ↓
doctors ───────────────────────────── (references hospitals)
    ↓
laboratory ────────────────────────── (references hospitals, patients)
    ↓
emergency ─────────────────────────── (references all resources; publishes emergency events)

── cross-cutting (subscribe to events from above) ──
notifications ─── subscribes to events from all modules
audit ─────────── subscribes to events from all modules  
analytics ──────── reads from DB views; subscribes to events
reports ──────────reads from DB views
```

**No circular dependencies are permitted.**

---

## Adding a New Module (Plug-and-Play Checklist)

To add a new module (e.g., `vaccination`, `blood_bank`, `pharmacy`):

1. Create `backend/app/modules/<name>/` with the standard 8-file structure
2. Define the module's `events.py` — what events it publishes
3. Register event subscriptions in `backend/app/main.py` startup
4. Create database migration in `database/schema/`
5. Add routes to the main router in `backend/app/main.py`
6. Add RBAC permissions in `backend/app/modules/<name>/permissions.py`
7. **Do NOT modify any existing module** — this is the plug-and-play guarantee

---

## The Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Correct Approach |
|:---|:---|:---|
| `from app.modules.beds.service import BedService` inside PatientService | Creates tight coupling | Publish `PatientAdmittedEvent`; let Beds subscribe |
| `SELECT * FROM inventory_medicines` in patients/repository.py | Cross-domain DB access | Patient module only reads its own tables |
| Calling `InventoryService.get_stock()` inside an emergency endpoint | Direct cross-module call | Emergency publishes event; Inventory reacts |
| Sharing a God Service class across modules | Kills modularity | One service per module |
