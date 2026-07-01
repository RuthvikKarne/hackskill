# modules.md

# Healthcare Resource Intelligence Platform (HRIP)

Version: 1.0

---

# Purpose

This document defines every module (business engine) in the Healthcare Resource Intelligence Platform.

Each module is designed to be:

- Independent
- Plug & Play
- API First
- Event Driven
- Scalable
- Replaceable
- Testable

Every module owns its business logic, APIs, events, and database tables.

---

# System Overview

```

HRIP

├── Identity Module
├── User Management Module
├── Hospital Management Module
├── Patient Management Module
├── Resource Management Module
├── Doctor Management Module
├── Nurse Management Module
├── Bed Management Module
├── Inventory Module
├── Laboratory Module
├── Pharmacy Module
├── Blood Bank Module
├── Ambulance Module
├── Appointment Module
├── Emergency Response Module
├── AI Decision Engine
├── Notification Module
├── Analytics Module
├── Reporting Module
├── Integration Module
└── Audit Module

```

---

# 1. Identity Module

## Purpose

Authentication and Authorization.

### Responsibilities

- Login
- Logout
- JWT
- Refresh Tokens
- RBAC
- Session Management

### Tables

```

users
roles
permissions
sessions

```

### APIs

```

POST /auth/login

POST /auth/logout

POST /auth/refresh

GET /me

```

### Events

```

UserLoggedIn

UserLoggedOut

PasswordChanged

```

---

# 2. User Management Module

## Purpose

Manage platform users.

### Responsibilities

- Create User
- Update User
- Assign Roles
- Activate User
- Deactivate User

### Tables

```

users

user_roles

```

---

# 3. Hospital Management Module

## Purpose

Manage healthcare facilities.

### Responsibilities

- Register Hospital
- PHC Management
- CHC Management
- Departments
- Wards
- Rooms

### Tables

```

hospitals
departments
wards
rooms

```

### APIs

```

GET /hospitals

POST /hospitals

PUT /hospitals/{id}

DELETE /hospitals/{id}

```

---

# 4. Patient Management Module

## Purpose

Manage patient lifecycle.

### Responsibilities

- Registration
- Admission
- Discharge
- Visit History
- Medical Records

### Tables

```

patients

visits

admissions

discharges

```

---

# 5. Doctor Management Module

## Responsibilities

- Doctor Profiles
- Specializations
- Shift Planning
- Attendance
- Availability
- Emergency Deployment

### Tables

```

doctors

doctor_schedule

doctor_attendance

```

---

# 6. Nurse Management Module

Responsibilities

- Nurse Management
- Shift Allocation
- Attendance
- Emergency Deployment

---

# 7. Resource Management Module

## Core Module

Tracks all healthcare resources.

Resources

- Beds
- Doctors
- Nurses
- Ambulances
- Ventilators
- Oxygen
- Equipment
- Blood
- Medicines

Responsibilities

- Availability
- Allocation
- Utilization
- Redistribution

Tables

```

resources

resource_status

resource_allocations

```

---

# 8. Bed Management Module

Responsibilities

- Bed Tracking
- Occupancy
- ICU Beds
- Emergency Beds
- Bed Reservation

Tables

```

beds

bed_status

```

---

# 9. Inventory Module

Responsibilities

- Medicine Stock
- Purchase
- Distribution
- Expiry
- Reorder

Tables

```

medicines

inventory

suppliers

purchase_orders

```

---

# 10. Pharmacy Module

Responsibilities

- Prescription
- Medicine Dispensing
- Stock Consumption

---

# 11. Laboratory Module

Responsibilities

- Available Tests
- Test Reports
- Equipment Status
- Daily Capacity

Tables

```

lab_tests

test_reports

lab_equipment

```

---

# 12. Blood Bank Module

Responsibilities

- Blood Units
- Donors
- Requests
- Inventory
- Expiry

Tables

```

blood_inventory

blood_requests

blood_donors

```

---

# 13. Ambulance Module

Responsibilities

- GPS Tracking
- Driver Assignment
- Live Status
- Emergency Dispatch
- ETA Calculation

Tables

```

ambulances

drivers

dispatch_history

```

---

# 14. Appointment Module

Responsibilities

- OPD Booking
- Queue Management
- Doctor Scheduling
- Token Generation

---

# 15. Emergency Response Module

## Most Important Module

Responsibilities

- Incident Registration
- Disaster Management
- Casualty Estimation
- Triage
- Resource Allocation
- Hospital Allocation
- Emergency Action Plan

Supported Incidents

- Road Accident
- Flood
- Fire
- Earthquake
- Building Collapse
- Epidemic

Tables

```

incidents

casualties

incident_resources

emergency_plans

```

Workflow

```

Incident

↓

Victim Estimation

↓

Severity Classification

↓

Nearby Hospital Discovery

↓

Capacity Analysis

↓

Resource Optimization

↓

Patient Distribution

↓

Emergency Action Plan

```

---

# 16. AI Decision Engine

Purpose

Decision Support.

Never performs automatic actions.

Responsibilities

- Patient Forecast
- Medicine Forecast
- Disease Forecast
- Doctor Demand Prediction
- Bed Prediction
- Hospital Performance
- Recommendation Engine

Outputs

- Predictions
- Risk Scores
- Recommendations
- Alerts

---

# 17. Notification Module

Responsibilities

- SMS
- Email
- Push Notification
- Dashboard Alerts
- Emergency Broadcast

Events

```

LowStock

BedFull

DoctorAbsent

Emergency

MedicineExpiry

```

---

# 18. Analytics Module

Responsibilities

- KPIs
- Dashboards
- Hospital Performance
- District Reports
- Resource Utilization
- Disease Trends

---

# 19. Reporting Module

Generate

- Daily Reports
- Weekly Reports
- Monthly Reports
- Government Reports
- Emergency Reports

Export

- PDF
- Excel
- CSV

---

# 20. Integration Module

Purpose

Connect external systems.

Supported Integrations

- ABDM
- HMIS
- Weather API
- GIS
- SMS Gateway
- Email Gateway
- IoT Devices

---

# 21. Audit Module

Responsibilities

- Audit Logs
- User Activity
- Data Changes
- Security Events
- Login History

---

# Module Dependencies

```

Identity
│
├── User
│
├── Hospital
│ ├── Doctor
│ ├── Nurse
│ ├── Bed
│ ├── Laboratory
│ ├── Pharmacy
│ ├── Blood Bank
│ └── Ambulance
│
├── Patient
│
├── Inventory
│
├── Resource
│
├── Emergency
│
├── AI
│
├── Notification
│
├── Analytics
│
├── Reporting
│
└── Integration

```

---

# Plug & Play Rules

Every module must:

✅ Have its own REST APIs

✅ Have its own Services

✅ Have its own Database Tables

✅ Publish Events

✅ Subscribe to Events

✅ Be independently testable

✅ Be independently deployable

---

# Development Priority

Phase 1

- Identity
- Hospital
- Patient

Phase 2

- Doctor
- Bed
- Inventory
- Resource

Phase 3

- Laboratory
- Pharmacy
- Ambulance
- Blood Bank

Phase 4

- Emergency
- Notifications

Phase 5

- AI Engine

Phase 6

- Analytics
- Reports

Phase 7

- Integrations

---

# Future Modules

- Telemedicine
- Citizen Mobile App
- Health Worker App
- Vaccination Module
- Disease Surveillance
- Drug Supply Chain
- IoT Monitoring
- Drone Support
- Voice Assistant
- Digital Twin