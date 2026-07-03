# Coding Standards

> Version: 2.0 | Applies To: All code in this repository

These standards are enforced by automated tooling (linters, formatters, CI checks). Every pull request must pass all checks before merge.

---

## Python (Backend + AI Engine)

### Tooling

| Tool | Purpose | Config |
|:---|:---|:---|
| `black` | Code formatter | `pyproject.toml` — line length 88 |
| `ruff` | Linter (replaces flake8, isort, pylint) | `pyproject.toml` |
| `mypy` | Static type checker | `pyproject.toml` — strict mode |
| `pytest` | Test runner | `pyproject.toml` |
| `pytest-asyncio` | Async test support | `pytest.ini` or `pyproject.toml` |
| `pytest-cov` | Coverage reporting | minimum 80% |

### Type Hints

- **Required** on all function signatures and class attributes
- Use `from __future__ import annotations` at the top of every file
- Use `Optional[X]` or `X | None` (Python 3.10+), not bare `Optional`
- Never use `Any` without an explicit `# type: ignore` comment with justification

```python
# CORRECT
async def get_patient(patient_id: UUID, hospital_id: UUID) -> Patient | None:
    ...

# INCORRECT
async def get_patient(patient_id, hospital_id):
    ...
```

### Naming Conventions

| Element | Convention | Example |
|:---|:---|:---|
| Variables | `snake_case` | `patient_id`, `stock_level` |
| Functions | `snake_case` | `get_by_id()`, `mark_attendance()` |
| Classes | `PascalCase` | `PatientService`, `BaseRepository` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `TOKEN_EXPIRY` |
| Modules | `snake_case` | `patient_service.py` |
| Type aliases | `PascalCase` | `PatientList = list[Patient]` |
| Private methods | `_snake_case` | `_validate_phone()` |

### Docstrings

Google-style docstrings on all public classes and functions:

```python
async def admit_patient(
    self,
    patient_id: UUID,
    bed_id: UUID,
    doctor_id: UUID,
) -> Admission:
    """Admit a patient to a specific bed.

    Validates that the bed is available, assigns the patient,
    and publishes a PatientAdmittedEvent.

    Args:
        patient_id: UUID of the patient to admit.
        bed_id: UUID of the bed to allocate.
        doctor_id: UUID of the responsible doctor.

    Returns:
        The created Admission record.

    Raises:
        BedNotAvailableError: If the bed is already occupied.
        PatientNotFoundError: If patient_id does not exist.
    """
```

### Error Handling

```python
# CORRECT — log with context, use domain exceptions
try:
    result = await self.repository.create(data)
except IntegrityError as e:
    logger.error("DB constraint violated", entity="Patient", error=str(e))
    raise DuplicatePatientError(f"Patient with phone {data['phone']} already exists")

# INCORRECT — never swallow exceptions silently
try:
    result = await self.repository.create(data)
except Exception:
    pass
```

### Async Rules

- All database operations MUST be `async def` using `await`
- Never use synchronous `time.sleep()` — use `asyncio.sleep()`
- Never block the event loop with CPU-intensive work — use `asyncio.run_in_executor()`
- All FastAPI endpoint functions must be `async def`

### Import Order (enforced by ruff)

```python
# 1. Standard library
from __future__ import annotations
import asyncio
from uuid import UUID

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Internal (absolute imports only)
from app.core.database.base import BaseRepository
from app.modules.patients.models import Patient
```

---

## TypeScript (Frontend)

### Tooling

| Tool | Purpose | Config |
|:---|:---|:---|
| `prettier` | Formatter | `.prettierrc` |
| `eslint` | Linter | `.eslintrc.json` |
| `@typescript-eslint` | TypeScript-specific lint rules | |
| `tsc` | Type checker | `tsconfig.json` — strict mode |

### TypeScript Config Requirements

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### Naming Conventions

| Element | Convention | Example |
|:---|:---|:---|
| Components | `PascalCase` | `PatientCard`, `BedStatusTable` |
| Hooks | `camelCase` with `use` prefix | `usePatients`, `useBedStatus` |
| Functions | `camelCase` | `formatDate`, `getAvailableBeds` |
| Types / Interfaces | `PascalCase` | `Patient`, `ApiResponse<T>` |
| Constants | `UPPER_SNAKE_CASE` | `API_BASE_URL` |
| Files (components) | `PascalCase.tsx` | `PatientCard.tsx` |
| Files (utils/hooks) | `camelCase.ts` | `usePatients.ts` |

### Component Rules

- Functional components only — no class components
- Props interfaces defined above the component
- No inline styles — use Tailwind classes
- No `any` type — ever

```typescript
// CORRECT
interface PatientCardProps {
  patient: Patient;
  onAdmit: (patientId: string) => void;
}

export function PatientCard({ patient, onAdmit }: PatientCardProps) {
  return <div className="rounded-lg border p-4">...</div>;
}

// INCORRECT
export function PatientCard(props: any) { ... }
```

### API Call Rules

- ALL API calls go through `lib/api/` — never raw `fetch` in components
- Use TanStack Query for server state
- Use Zustand for client-only state
- Never store JWT tokens in `localStorage`

---

## Git Standards

### Commit Messages

Format: `type(scope): description`

| Type | When to use |
|:---|:---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change, no feature/fix |
| `test` | Adding or fixing tests |
| `chore` | Build process, tooling |
| `perf` | Performance improvement |

Examples:
```
feat(patients): add admission endpoint with bed allocation
fix(inventory): correct expiry date comparison logic
docs(api-design): update response envelope format
test(auth): add refresh token expiry integration test
```

### Branch Naming

```
feature/<short-description>    e.g. feature/patient-admission
fix/<short-description>        e.g. fix/jwt-expiry-check
docs/<short-description>       e.g. docs/event-bus-spec
refactor/<short-description>
```

### PR Rules

- All CI checks must pass (lint, type-check, tests)
- Minimum 80% coverage on changed service files
- No `TODO` comments without a linked issue
- Self-review checklist completed before requesting review

---

## Security Standards

- Never hardcode secrets, API keys, or passwords
- Never log sensitive data (passwords, tokens, Aadhaar, phone numbers)
- Never store JWT in localStorage or sessionStorage
- Always validate input at the API boundary (Pydantic / Zod)
- Always use parameterized queries (SQLAlchemy ORM — no raw SQL string interpolation)
- Always use `UUID` as primary key — never expose sequential integers

---

## Testing Standards

### Python Test Structure

```
tests/
├── unit/
│   ├── test_patient_service.py     # Test service with mocked repository
│   ├── test_inventory_service.py
│   └── ...
├── integration/
│   ├── test_patient_router.py      # Test full HTTP stack with test DB
│   └── ...
└── conftest.py                     # Shared fixtures (test DB, test client)
```

### Coverage Requirements

| Layer | Minimum Coverage |
|:---|:---|
| `core/security/` | 100% |
| `core/events/` | 100% |
| `modules/*/service.py` | ≥ 80% |
| `modules/*/repository.py` | ≥ 70% |
| `modules/*/router.py` | ≥ 80% (integration tests) |

### Test Naming

```python
# Pattern: test_<method>_<scenario>_<expected_result>
def test_admit_patient_when_bed_occupied_raises_bed_not_available_error(): ...
def test_login_with_valid_credentials_returns_access_token(): ...
def test_get_low_stock_medicines_returns_only_below_threshold(): ...
```
