# folder-structure.md

# Healthcare Resource Intelligence Platform (HRIP)

Version: 1.0

---

# Purpose

This document defines the standard repository structure for the Healthcare Resource Intelligence Platform (HRIP).

The architecture follows:

- Domain Driven Design (DDD)
- Clean Architecture
- Modular Monolith (Phase 1)
- Microservice Ready (Future)
- Plug & Play Modules
- Feature-Based Organization

The structure is designed so that any module can later be extracted into an independent microservice without major refactoring.

---

# Repository Structure

```text
healthcare-resource-intelligence-platform/
│
├── README.md
├── AGENTS.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
├── .editorconfig
├── docker-compose.yml
├── .env.example
│
├── docs/
├── backend/
├── frontend/
├── ai-engine/
├── database/
├── api/
├── deployment/
├── scripts/
├── diagrams/
├── presentation/
├── assets/
└── .github/
```

---

# Root Files

| File | Purpose |
|-------|----------|
| README.md | Project Overview |
| AGENTS.md | AI Development Rules |
| CONTRIBUTING.md | Contribution Guidelines |
| LICENSE | Project License |
| CHANGELOG.md | Release History |
| docker-compose.yml | Local Development |
| .env.example | Environment Variables |

---

# docs/

Contains all architecture and technical documentation.

```text
docs/

00-project-vision.md

01-problem-statement.md

02-system-requirements.md

03-architecture.md

04-system-design.md

05-modules.md

06-roadmap.md

07-tech-stack.md

08-database.md

09-er-diagram.md

10-api-design.md

11-security.md

12-ai-engine.md

13-deployment.md

14-testing.md

15-future-enhancements.md
```

---

# backend/

Spring Boot application.

```text
backend/

├── src/
│
├── pom.xml
│
├── Dockerfile
│
└── README.md
```

---

# Spring Boot Structure

```text
src/

main/

java/

com/

hrip/

```

---

# Package Structure

```text
com.hrip

├── common/
├── config/
├── security/
├── exception/
├── util/
├── events/
├── shared/
├── modules/
└── HripApplication.java
```

---

# common/

Reusable code.

```text
common/

constants/

dto/

mapper/

response/

utils/

validator/
```

---

# config/

```text
config/

DatabaseConfig

RedisConfig

KafkaConfig

SwaggerConfig

CorsConfig

WebSocketConfig

SecurityConfig
```

---

# security/

```text
security/

JwtProvider

JwtFilter

SecurityConfiguration

AuthenticationService

PasswordEncoder

PermissionEvaluator
```

---

# exception/

```text
exception/

GlobalExceptionHandler

BusinessException

ValidationException

ResourceNotFoundException

UnauthorizedException
```

---

# events/

```text
events/

publisher/

subscriber/

models/

topics/
```

---

# shared/

Shared reusable services.

```text
shared/

email/

sms/

storage/

notification/

audit/
```

---

# modules/

Every business capability lives here.

```text
modules/

identity/

hospital/

patient/

doctor/

nurse/

bed/

inventory/

laboratory/

bloodbank/

ambulance/

resource/

appointment/

emergency/

analytics/

report/

notification/

integration/

audit/

ai/
```

---

# Example Module Structure

Example

Patient Module

```text
patient/

controller/

service/

repository/

entity/

dto/

mapper/

validator/

event/

config/

PatientModule.java
```

---

# controller/

```text
PatientController

AdmissionController

DischargeController
```

---

# service/

```text
PatientService

AdmissionService

DischargeService
```

---

# repository/

```text
PatientRepository

VisitRepository
```

---

# entity/

```text
Patient

Visit

Admission

MedicalRecord
```

---

# dto/

```text
CreatePatientRequest

UpdatePatientRequest

PatientResponse
```

---

# mapper/

```text
PatientMapper
```

---

# validator/

```text
PatientValidator
```

---

# event/

```text
PatientRegisteredEvent

PatientAdmittedEvent

PatientDischargedEvent
```

---

# frontend/

Next.js Application

```text
frontend/

app/

components/

hooks/

lib/

services/

store/

styles/

types/

public/

package.json
```

---

# app/

```text
app/

login/

dashboard/

patients/

hospitals/

inventory/

beds/

emergency/

analytics/

settings/
```

---

# components/

```text
components/

ui/

charts/

forms/

tables/

layout/

maps/

cards/

modals/

widgets/
```

---

# services/

```text
services/

auth/

patient/

hospital/

inventory/

doctor/

emergency/

notification/
```

---

# store/

```text
store/

auth/

patient/

hospital/

inventory/

dashboard/
```

---

# hooks/

```text
hooks/

useAuth

usePatients

useHospitals

useInventory

useDashboard
```

---

# ai-engine/

Python AI Services

```text
ai-engine/

models/

training/

prediction/

api/

datasets/

notebooks/

tests/

Dockerfile

requirements.txt
```

---

# models/

```text
forecasting/

recommendation/

classification/

anomaly/

optimization/
```

---

# prediction/

```text
medicine_prediction.py

doctor_prediction.py

bed_prediction.py

disease_prediction.py

resource_optimizer.py
```

---

# database/

```text
database/

schema/

seed/

migration/

views/

functions/

triggers/

indexes/
```

---

# schema/

```text
users.sql

hospitals.sql

patients.sql

doctors.sql

inventory.sql

emergency.sql
```

---

# api/

```text
api/

openapi.yaml

postman_collection.json

swagger/
```

---

# deployment/

```text
deployment/

docker/

kubernetes/

terraform/

nginx/

monitoring/

backup/
```

---

# docker/

```text
backend.Dockerfile

frontend.Dockerfile

ai.Dockerfile
```

---

# kubernetes/

```text
deployment.yaml

service.yaml

configmap.yaml

secret.yaml

ingress.yaml
```

---

# monitoring/

```text
prometheus.yml

grafana/

alerts/

dashboards/
```

---

# scripts/

```text
scripts/

backup.sh

restore.sh

seed.sh

migrate.sh

build.sh

deploy.sh
```

---

# diagrams/

```text
diagrams/

architecture.mmd

erd.mmd

deployment.mmd

context.mmd

component.mmd

sequence/

activity/
```

---

# assets/

```text
assets/

logos/

icons/

images/

branding/
```

---

# presentation/

```text
presentation/

ppt/

demo/

screenshots/

videos/
```

---

# .github/

```text
.github/

workflows/

ISSUE_TEMPLATE/

PULL_REQUEST_TEMPLATE.md
```

---

# GitHub Workflows

```text
workflows/

backend.yml

frontend.yml

ai.yml

docker.yml

release.yml
```

---

# Naming Conventions

## Backend

| Item | Convention |
|--------|------------|
| Package | lowercase |
| Class | PascalCase |
| Method | camelCase |
| Variable | camelCase |
| Enum | PascalCase |
| Constant | UPPER_CASE |

---

## Database

| Item | Convention |
|--------|------------|
| Table | snake_case |
| Column | snake_case |
| Index | idx_table_column |
| Foreign Key | fk_table_reference |

---

## Frontend

| Item | Convention |
|--------|------------|
| Component | PascalCase |
| Hook | useSomething |
| Route | kebab-case |
| File | PascalCase.tsx |

---

# Future Microservices

When scaling, each module can become its own service.

```text
identity-service

hospital-service

patient-service

resource-service

inventory-service

emergency-service

analytics-service

notification-service

ai-service

integration-service
```

Each service retains the same internal folder structure, making migration straightforward.

---

# Folder Design Principles

- Feature-first organization
- One responsibility per module
- No circular dependencies
- Shared utilities isolated
- API-first implementation
- Event-driven communication
- Independent testing
- Future microservice compatibility

---

# Summary

The HRIP repository is organized around business domains rather than technical layers. Each module owns its APIs, services, entities, events, and business rules. This enables rapid development as a modular monolith while providing a clear migration path toward independently deployable microservices as the platform grows.