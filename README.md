# Healthcare Resource Intelligence Platform (HRIP)

> **Version**: 2.0 | **Status**: Active Development

An AI-powered, modular, production-grade healthcare resource management platform for government health facilities — PHCs, CHCs, District Hospitals.

---

## What It Does

- **Medicine Stock Monitoring** — Real-time stock tracking with expiry alerts
- **Patient Management** — Registration, admission, discharge, medical history
- **Bed Management** — Live occupancy tracking across all wards
- **Doctor Attendance** — Daily attendance, shift management
- **Laboratory** — Test orders, results, report management
- **Emergency Response** — Incident coordination, patient distribution, ambulance tracking
- **District Dashboard** — Real-time visibility across all hospitals in a district
- **AI Recommendations** — Demand forecasting, risk alerts, resource optimization (human approval required)

---

## Architecture

```
Frontend (Next.js 15)  →  API Gateway (FastAPI)  →  Business Modules
                                                           ↓
                                                     Event Bus
                                                      ↙  ↘  ↘  ↘
                                               Audit  AI  Notifications  Analytics
                                                           ↓
                                                     Supabase PostgreSQL
                                                     Redis (cache/sessions)
```

**Backend**: FastAPI (Python 3.11)  
**Frontend**: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui  
**Database**: Supabase PostgreSQL + Auth + Storage  
**AI Engine**: FastAPI + Prophet + XGBoost + OR-Tools + SHAP  
**Event Bus**: In-process async dispatcher (Kafka-ready interface)  

---

## Getting Started (Local Development)

### Prerequisites

- Docker + Docker Compose
- Node.js 20+
- Python 3.11+

### 1. Clone and configure

```bash
git clone https://github.com/your-org/hackskill.git
cd hackskill
cp .env.example .env
# Edit .env with your values
```

### 2. Start services

```bash
docker compose up -d
```

### 3. Access

| Service | URL |
|:---|:---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |
| AI Engine | http://localhost:8001 |

---

## Repository Structure

```
hackskill/
├── docs/              Documentation (architecture, modules, API design, etc.)
├── backend/           FastAPI modular monolith
│   └── app/
│       ├── core/      Security, Event Bus, Database, Exceptions
│       ├── modules/   13 independent business modules
│       └── shared/    Shared utilities
├── ai-engine/         AI recommendation engine (FastAPI + ML models)
├── frontend/          Next.js 15 web application
├── database/          SQL schemas and migrations
└── .github/           CI/CD workflows
```

---

## Documentation

| Document | Description |
|:---|:---|
| [Project Vision](docs/00-project-vision.md) | Goals, users, success metrics |
| [Architecture](docs/01-architecture.md) | System architecture overview |
| [Modules](docs/02-modules.md) | Module catalogue and responsibilities |
| [API Design](docs/03-api-design.md) | REST API standards and endpoints |
| [Database](docs/04-database.md) | Schema design and conventions |
| [Security](docs/05-security.md) | Authentication, RBAC, encryption |
| [AI Engine](docs/06-ai-engine.md) | AI models and recommendation workflow |
| [Deployment](docs/07-deployment.md) | Infrastructure and CI/CD |
| [Event Bus](docs/08-event-bus.md) | Event-driven architecture |
| [Coding Standards](docs/09-coding-standards.md) | Code quality rules |
| [Module Boundaries](docs/10-module-boundaries.md) | Inter-module communication rules |
| [Roadmap](docs/11-roadmap.md) | Implementation phases |
| [Implementation Plan](implementation_plan.md) | Approved architecture blueprint |
| [Task Tracker](task.md) | Current implementation progress |

---

## Key Architectural Rules

1. **Modules never import each other's service classes** — use the Event Bus
2. **AI only recommends, never executes** — human approval required
3. **JWT stored in HttpOnly cookies only** — never localStorage
4. **All APIs return standard response envelope**
5. **Every table has**: `id` (UUID), `hospital_id`, `created_at`, `updated_at`, `deleted_at`
6. **Audit log is append-only** — no updates or deletes

---

## License

Proprietary — All Rights Reserved