"""Business modules — each module is an independent, plug-and-play domain.

Module Catalogue:
  auth         — Authentication, JWT, session management
  users        — User CRUD, role assignment
  hospitals    — Hospital, department, ward management
  patients     — Patient registration, admission, discharge
  inventory    — Medicine stock, expiry, procurement
  beds         — Ward/bed management, occupancy
  doctors      — Doctor profiles, attendance, shifts
  laboratory   — Lab tests, results, reports
  emergency    — Incident management, resource allocation
  notifications — SMS, Email, in-app alerts
  analytics    — KPI aggregation, trend analysis
  reports      — Report generation (PDF, CSV, Excel)
  audit        — Immutable event audit log

Adding a new module:
  1. Create modules/<name>/ with the standard 8-file structure
  2. Never import another module's service.py or repository.py
  3. Communicate via Event Bus or defined API contracts only
  See docs/10-module-boundaries.md for rules.
"""
