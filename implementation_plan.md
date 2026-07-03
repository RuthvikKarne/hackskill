# HRIP — Architectural Redesign Blueprint

> **Version**: 2.0-DESIGN  
> **Status**: AWAITING APPROVAL — No code will be written until this plan is approved.  
> **Scope**: Repository-wide redesign. Documentation update, folder structure, module boundaries, coding standards, and implementation roadmap.

---

## Problem Statement

The current repository contains high-quality design documentation but the actual code does not reflect it. Gaps identified:

| Area | Current State | Required State |
|:---|:---|:---|
| Folder Structure | Flat root with `.md` files | Layered monorepo with `frontend/`, `backend/`, `ai-engine/`, `docs/`, `database/` |
| Backend | FastAPI stub (2 routes) | FastAPI modular monolith, Clean Architecture |
| Frontend | Empty directory | Next.js 15 + TypeScript + Tailwind + shadcn/ui |
| AI Engine | 6 stub routers returning placeholder strings | Structured service modules with real model interfaces |
| Event Bus | Not implemented | In-process event bus (Phase 1), Kafka-ready interfaces |
| Database | Documentation only | SQL schema files, migration strategy |
| Documentation | Root-level `.md` files (inconsistent naming) | Organized under `/docs/` |
| Security | Documented, not implemented | Security middleware layer in backend |
| CI/CD | Not present | GitHub Actions pipelines |

---

## Open Questions

> **Q1 — Backend Language**  
> `deployment.md` mentions Spring Boot but the actual code uses FastAPI. This plan recommends **FastAPI (Python)** to share the runtime with the AI Engine. Please confirm or override.

> **Q2 — Event Bus (Phase 1)**  
> Proposes an **in-process Python event dispatcher** with Kafka-compatible interfaces, so Phase 2 can swap to Kafka with zero business logic changes. Confirm?

> **Q3 — Database Hosting**  
> Proposes **Supabase** (managed PostgreSQL + Auth + Storage) abstracted behind repository classes. Confirm?

> **Q4 — Timeline**  
> Hackathon demo or full production deployment? Affects Phase 1 depth.

---

## 1. Proposed Repository Structure

```text
hackskill/
│
├── docs/
│   ├── 00-project-vision.md
│   ├── 01-architecture.md
│   ├── 02-modules.md
│   ├── 03-api-design.md
│   ├── 04-database.md
│   ├── 05-security.md
│   ├── 06-ai-engine.md
│   ├── 07-deployment.md
│   ├── 08-event-bus.md            ← NEW
│   ├── 09-coding-standards.md     ← NEW
│   ├── 10-module-boundaries.md    ← NEW
│   └── 11-roadmap.md
│
├── database/
│   ├── schema/
│   │   ├── 000_extensions.sql
│   │   ├── 001_auth.sql
│   │   ├── 002_hospitals.sql
│   │   ├── 003_patients.sql
│   │   ├── 004_doctors.sql
│   │   ├── 005_beds.sql
│   │   ├── 006_inventory.sql
│   │   ├── 007_laboratory.sql
│   │   ├── 008_emergency.sql
│   │   ├── 009_analytics.sql
│   │   └── 010_audit.sql
│   ├── seed/
│   │   └── seed_data.sql
│   └── views/
│       └── hospital_summary.sql
│
├── backend/
│   ├── app/
│   │   ├── main.py                # App entry point
│   │   ├── config.py              # Pydantic Settings
│   │   ├── dependencies.py        # Shared FastAPI deps
│   │   ├── core/
│   │   │   ├── security/
│   │   │   │   ├── jwt.py
│   │   │   │   ├── rbac.py
│   │   │   │   ├── password.py
│   │   │   │   └── middleware.py
│   │   │   ├── events/
│   │   │   │   ├── bus.py         # In-process event bus
│   │   │   │   ├── base.py        # BaseEvent class
│   │   │   │   └── registry.py    # Event → Handler registry
│   │   │   ├── database/
│   │   │   │   ├── session.py
│   │   │   │   └── base.py        # Base repository
│   │   │   ├── exceptions/
│   │   │   │   ├── base.py
│   │   │   │   └── handlers.py
│   │   │   └── logging/
│   │   │       └── logger.py
│   │   ├── modules/
│   │   │   ├── auth/
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   ├── repository.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── models.py
│   │   │   │   └── events.py
│   │   │   ├── users/
│   │   │   ├── hospitals/
│   │   │   ├── patients/
│   │   │   ├── inventory/
│   │   │   ├── beds/
│   │   │   ├── doctors/
│   │   │   ├── laboratory/
│   │   │   ├── emergency/
│   │   │   ├── notifications/
│   │   │   ├── analytics/
│   │   │   ├── reports/
│   │   │   └── audit/
│   │   └── shared/
│   │       ├── pagination.py
│   │       ├── response.py
│   │       └── validators.py
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
│
├── ai-engine/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── core/
│   │   │   ├── feature_store/
│   │   │   ├── model_registry/
│   │   │   └── pipeline/
│   │   └── services/
│   │       ├── forecasting/
│   │       ├── optimization/
│   │       ├── recommendation/
│   │       ├── risk_intelligence/
│   │       ├── disease_surveillance/
│   │       └── explainability/
│   ├── models/
│   ├── notebooks/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── forgot-password/
│   │   │   └── (dashboard)/
│   │   │       ├── layout.tsx
│   │   │       ├── dashboard/
│   │   │       ├── hospitals/
│   │   │       ├── patients/
│   │   │       ├── inventory/
│   │   │       ├── beds/
│   │   │       ├── doctors/
│   │   │       ├── laboratory/
│   │   │       ├── emergency/
│   │   │       ├── analytics/
│   │   │       ├── reports/
│   │   │       └── settings/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── charts/
│   │   │   ├── maps/
│   │   │   ├── forms/
│   │   │   ├── tables/
│   │   │   └── layout/
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   ├── auth/
│   │   │   └── utils/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── types/
│   ├── public/
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── .github/
│   └── workflows/
│       ├── backend.yml
│       ├── frontend.yml
│       └── ai-engine.yml
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 2. Module Boundaries & Responsibilities

Each module is a **self-contained unit**. Modules communicate ONLY through the Event Bus or defined API contracts. No module imports another module's service class.

### Module Catalogue

| Module | Responsibility | Communicates Via |
|:---|:---|:---|
| **auth** | Login, logout, JWT, refresh tokens, password reset | Event Bus → audit |
| **users** | User CRUD, role assignment, profiles | Event Bus |
| **hospitals** | Hospital / department / ward CRUD | Event Bus |
| **patients** | Registration, admission, discharge, visit history | Event Bus → audit, notifications |
| **inventory** | Medicine stock, expiry tracking, purchase orders | Event Bus → ai-engine, notifications, audit |
| **beds** | Ward/bed management, occupancy, ICU tracking | Event Bus → ai-engine, emergency |
| **doctors** | Profiles, attendance, shifts, availability | Event Bus → notifications |
| **laboratory** | Lab tests, sample tracking, results, reports | Event Bus → notifications, audit |
| **emergency** | Incident creation, ambulance coordination, resource allocation | Event Bus → all modules |
| **notifications** | SMS, Email, WhatsApp, in-app alerts | Subscribes to all domain events |
| **analytics** | KPI aggregation, trend data, hospital comparisons | DB (read-only) |
| **reports** | Report generation (PDF, Excel, CSV) | DB (read-only) |
| **audit** | Immutable audit log writer | Subscribes to all domain events |

### Module Internal Structure (Standard Template)

```text
modules/<module_name>/
├── router.py          # FastAPI router — HTTP entry points ONLY
├── service.py         # Business logic — no DB access
├── repository.py      # All DB access — no business logic
├── schemas.py         # Pydantic request/response models
├── models.py          # SQLAlchemy ORM models
├── events.py          # Events this module publishes
├── permissions.py     # RBAC permission constants
├── validators.py      # Custom business-rule validators
└── tests/
    ├── test_router.py
    ├── test_service.py
    └── test_repository.py
```

### Golden Dependency Rules

```
router.py      → may import → service.py, schemas.py
service.py     → may import → repository.py, events.py, shared/
repository.py  → may import → models.py, core/database/session.py

service.py     → NEVER imports another module's service.py
repository.py  → NEVER imports another module's repository.py
router.py      → NEVER imports repository.py directly
```

---

## 3. Event Bus Design

### Event Flow — Medicine Stock Updated

```
[Inventory Service]
    → publishes: InventoryUpdatedEvent
    → Event Bus
        ├── [AI Engine Subscriber]     → triggers demand re-forecast
        ├── [Notification Subscriber]  → sends low-stock alert
        ├── [Audit Subscriber]         → writes audit log entry
        └── [Analytics Subscriber]     → updates KPI aggregates
```

### Event Catalogue

| Event | Publisher | Subscribers |
|:---|:---|:---|
| `UserLoggedIn` | auth | audit |
| `PatientRegistered` | patients | audit, notifications, analytics |
| `PatientAdmitted` | patients | beds, audit, analytics |
| `PatientDischarged` | patients | beds, audit, analytics |
| `InventoryUpdated` | inventory | ai-engine, notifications, audit |
| `StockCriticalLow` | inventory | notifications, audit, ai-engine |
| `BedStatusChanged` | beds | emergency, ai-engine, analytics |
| `DoctorAttendanceMarked` | doctors | audit, analytics |
| `LabReportUploaded` | laboratory | notifications, audit |
| `EmergencyIncidentCreated` | emergency | notifications, beds, inventory, ai-engine, audit |
| `AIRecommendationGenerated` | ai-engine | notifications, audit |
| `AIRecommendationApproved` | users | audit, relevant module |

### Base Event Structure

```python
class BaseEvent:
    event_id: UUID       # Unique event ID
    event_type: str      # e.g., "inventory.stock.critical_low"
    aggregate_id: UUID   # ID of the primary entity
    aggregate_type: str  # e.g., "Medicine"
    hospital_id: UUID    # Multi-tenant context
    actor_id: UUID       # User who triggered the action
    timestamp: datetime
    payload: dict        # Event-specific data
    version: int         # Schema version for forward compatibility
```

---

## 4. API Design

### Gateway Rules (Strictly Enforced)

The API gateway (FastAPI middleware) performs ONLY:
- JWT validation
- Role + permission extraction
- Request ID injection
- Rate limiting
- CORS
- Request/response logging
- API version routing (`/api/v1/...`)

**Zero business logic in the gateway.**

### Standard Response Envelope

```json
{
  "success": true,
  "message": "Patient registered successfully",
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-07-03T08:00:00Z",
    "version": "1.0"
  }
}
```

### Key API Endpoints

```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me

GET    /api/v1/patients
POST   /api/v1/patients
GET    /api/v1/patients/{id}
PUT    /api/v1/patients/{id}
POST   /api/v1/patients/{id}/admit
POST   /api/v1/patients/{id}/discharge

GET    /api/v1/inventory/medicines
GET    /api/v1/inventory/low-stock
POST   /api/v1/inventory/receive
POST   /api/v1/inventory/issue

GET    /api/v1/beds
GET    /api/v1/beds/available
POST   /api/v1/beds/{id}/allocate

GET    /api/v1/ai/recommendations
POST   /api/v1/ai/recommendations/{id}/approve
POST   /api/v1/ai/recommendations/{id}/reject
```

---

## 5. Data Access Layer (Repository Pattern)

No service class executes SQL directly. All DB interaction is in repository classes.

### Base Repository

```python
class BaseRepository:
    async def get_by_id(id: UUID) -> Model | None
    async def get_all(filters, pagination) -> list[Model]
    async def create(data: dict) -> Model
    async def update(id: UUID, data: dict) -> Model
    async def soft_delete(id: UUID) -> bool
    async def exists(id: UUID) -> bool
```

### Mandatory Table Columns

| Column | Type | Purpose |
|:---|:---|:---|
| `id` | `UUID` | Primary key |
| `hospital_id` | `UUID` FK | Multi-tenancy |
| `created_at` | `TIMESTAMPTZ` | Audit |
| `updated_at` | `TIMESTAMPTZ` | Audit |
| `deleted_at` | `TIMESTAMPTZ` nullable | Soft delete |
| `created_by` | `UUID` FK | Actor tracking |
| `version` | `INT` | Optimistic locking |

---

## 6. Security Architecture

### Request Lifecycle

```
Browser Request
    ↓ TLS (HTTPS only — HTTP rejected)
    ↓ Rate Limiter (Redis-backed, per IP + per user)
    ↓ JWT Middleware → validate signature, expiry, extract claims
    ↓ RBAC Middleware → check route permission against role
    ↓ Business Module Router
    ↓ Service (business logic)
    ↓ Repository (DB access, hospital-scoped)
    ↓ Response (sensitive fields stripped)
```

### JWT Strategy

| Token | Lifetime | Storage |
|:---|:---|:---|
| Access Token | 15 minutes | HttpOnly Secure SameSite=Strict Cookie |
| Refresh Token | 7 days | HttpOnly Secure SameSite=Strict Cookie |

**JWT NEVER stored in localStorage or sessionStorage.**

### RBAC Permission Matrix

| Module | Sys Admin | District Admin | Hospital Admin | Doctor | Nurse | Lab Tech | Pharmacist | Emergency Op |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Users | CRUD | R | R (own) | Own | Own | Own | Own | Own |
| Hospitals | CRUD | R | CRUD (own) | R | R | R | R | R |
| Patients | CRUD | R | CRUD | CRUD | RU | R | R | R |
| Inventory | CRUD | R | CRUD | R | R | R | CRUD | R |
| Beds | CRUD | R | CRUD | R | RU | - | - | CRUD |
| Doctors | CRUD | CRUD | CRUD (own) | Own | R | - | - | R |
| Laboratory | CRUD | R | CRUD | R | R | CRUD | R | R |
| Emergency | CRUD | CRUD | CRUD | R | R | R | R | CRUD |
| AI Recs | CRUD | Approve | Approve | - | - | - | - | - |
| Audit | Read | Read (district) | Read (hospital) | - | - | - | - | - |

---

## 7. Authentication Flow

```
1.  User submits email + password
2.  Auth Service validates credentials
3.  Issues: Access Token (JWT, 15 min) + Refresh Token (opaque, 7 days) → HttpOnly Cookies
4.  JWT payload:
    { "sub": "user_uuid", "role": "HOSPITAL_ADMIN",
      "hospital_id": "uuid", "district_id": "uuid",
      "permissions": ["patients:read", "beds:write"], "exp": ... }
5.  Every request: JWT middleware validates + injects user context
6.  Token refresh: POST /api/v1/auth/refresh before expiry
7.  Logout: Refresh token added to Redis blocklist; cookies cleared
```

---

## 8. AI Engine Architecture

### Principles

- Separate FastAPI service (separate container)
- Read-only DB access — no INSERT/UPDATE/DELETE on business tables
- Writes only to `ai.recommendations` table
- Every recommendation requires human approval before execution
- Every recommendation includes: confidence score, reasoning, model version, SHAP explanations

### AI Services

| Service | ML Approach | Output |
|:---|:---|:---|
| `forecasting` | Prophet + XGBoost | Patient load forecast (7/30 days) |
| `inventory_forecast` | Prophet | Medicine demand + reorder point |
| `risk_intelligence` | XGBoost | Risk scores per hospital |
| `optimization` | OR-Tools | Optimal resource redistribution plan |
| `disease_surveillance` | Random Forest | Outbreak risk alerts |
| `explainability` | SHAP | Feature importance + explanation text |

### Human Approval Workflow

```
AI generates recommendation → writes to ai.recommendations (PENDING)
    → Notification sent to admin
    → Admin reviews in dashboard
        → APPROVE → backend executes action → audit log
        → REJECT  → reason recorded → audit log
```

---

## 9. Coding Standards

### Python (Backend + AI Engine)

| Rule | Standard |
|:---|:---|
| Formatter | `black` (line length 88) |
| Linter | `ruff` |
| Type hints | Required on ALL functions |
| Docstrings | Google-style on all public functions |
| Tests | `pytest` + `pytest-asyncio` |
| Coverage | ≥80% services, 100% core/security |
| Async | All DB ops must be async |
| Errors | Always log with context before re-raising |

### TypeScript (Frontend)

| Rule | Standard |
|:---|:---|
| Formatter | `prettier` |
| Linter | `eslint` + `@typescript-eslint` |
| Strict | `"strict": true` — no `any` |
| State | Zustand (global) + TanStack Query (server) |
| API calls | All through `lib/api/` — never raw fetch in components |

### General

- Secrets via env vars only — never hardcoded
- All IDs are UUIDs in API responses
- All timestamps UTC ISO 8601
- Soft deletes only for clinical + audit data
- Git commits: `type(scope): description`

---

## 10. Implementation Roadmap

### Phase 0 — Repository Reorganization *(No business code)*
- Move all root `.md` files into `docs/`
- Create empty module directories in `backend/app/modules/`
- Restructure `ai-engine/` under `ai-engine/app/`
- Create `database/schema/` SQL stubs
- Write new docs: event-bus, coding-standards, module-boundaries
- Create `docker-compose.yml`, `.env.example`, update `README.md`

### Phase 1 — Backend Foundation
FastAPI skeleton, async DB (SQLAlchemy + asyncpg), Alembic migrations, Redis, in-process Event Bus, JWT + RBAC middleware, global exception handler, rate limiter, structured logging, Base Repository, health checks.

### Phase 2 — Authentication Module
Login, JWT (RS256), refresh tokens, HttpOnly cookies, logout with token blocklist, RBAC permissions, integration tests.

### Phase 3 — Core Business Modules
Build in order: hospitals → users → patients → inventory → beds → doctors → laboratory.  
Each: migration → model → repository → service → schemas → router → RBAC → tests.

### Phase 4 — Cross-Cutting Services
Notifications (event subscriber), Audit (immutable log writer), Analytics (read-only KPIs), Reports (PDF/CSV).

### Phase 5 — Emergency Response Module
Incident CRUD, resource calculator, patient distribution, ambulance tracking.

### Phase 6 — AI Engine (Real Models)
Feature store, Prophet forecasting, XGBoost risk scoring, OR-Tools optimization, SHAP explainability, approval workflow.

### Phase 7 — Frontend
Next.js 15, shadcn/ui, Zustand + TanStack Query, all dashboard pages, role-based navigation, AI recommendations panel, responsive layout.

### Phase 8 — Infrastructure & CI/CD
Dockerfiles, docker-compose.prod.yml, GitHub Actions pipelines, Nginx config, Prometheus metrics.

---

## Architecture Compliance Checklist

Before any module is marked "done":

- [ ] No module imports another module's `service.py`
- [ ] No `router.py` directly accesses the DB
- [ ] No business logic in `repository.py`
- [ ] All cross-module communication through Event Bus
- [ ] JWT not stored in `localStorage`
- [ ] All APIs return standard response envelope
- [ ] All tables have: `id`, `hospital_id`, `created_at`, `updated_at`, `deleted_at`
- [ ] All endpoints have RBAC permission checks
- [ ] Audit events published for all state-changing operations
- [ ] AI recommendations require human approval before execution

---

*Approve this plan to begin Phase 0.*
