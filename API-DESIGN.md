# API Design

Version: 1.0

---

# Purpose

This document defines the REST API standards, endpoint conventions, request/response formats, authentication strategy, versioning, pagination, filtering, and module APIs for the Healthcare Resource Intelligence Platform (HRIP).

The platform follows an API-First approach where every business capability is exposed through RESTful APIs.

---

# API Principles

- RESTful
- Resource Oriented
- Stateless
- JSON Only
- Versioned
- Secure by Default
- Predictable Responses
- Idempotent where applicable

---

# Base URL

Development

```
http://localhost:8080/api/v1
```

Production

```
https://api.hrip.gov.in/api/v1
```

---

# Authentication

Every protected endpoint requires

```
Authorization: Bearer <JWT_TOKEN>
```

Public APIs

- Login
- Refresh Token
- Health Check

Everything else requires authentication.

---

# Standard Response Format

Success

```json
{
  "success": true,
  "message": "Patient created successfully",
  "timestamp": "2026-07-01T12:30:00Z",
  "data": {}
}
```

Error

```json
{
  "success": false,
  "message": "Validation Failed",
  "timestamp": "2026-07-01T12:30:00Z",
  "errors": [
    {
      "field": "phone",
      "message": "Phone number already exists"
    }
  ]
}
```

---

# HTTP Status Codes

| Code | Meaning |
|------|----------|
|200|Success|
|201|Created|
|204|No Content|
|400|Validation Error|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Business Rule Error|
|500|Internal Server Error|

---

# API Versioning

```
/api/v1/...
```

Future

```
/api/v2/...
```

---

# Pagination

```
GET /patients?page=1&size=20
```

Response

```json
{
  "page": 1,
  "size": 20,
  "total": 256,
  "data": []
}
```

---

# Filtering

Examples

```
GET /patients?gender=MALE

GET /doctors?specialization=CARDIOLOGY

GET /medicines?status=LOW_STOCK
```

---

# Sorting

```
GET /patients?sort=createdAt,desc

GET /doctors?sort=name,asc
```

---

# Search

```
GET /patients/search?q=ramesh
```

---

# Module APIs

---

# Identity Module

```
POST /auth/login

POST /auth/logout

POST /auth/refresh

GET /me
```

---

# Hospital Module

```
GET /hospitals

GET /hospitals/{id}

POST /hospitals

PUT /hospitals/{id}

DELETE /hospitals/{id}
```

---

# Patient Module

```
GET /patients

GET /patients/{id}

POST /patients

PUT /patients/{id}

DELETE /patients/{id}
```

Additional

```
GET /patients/{id}/visits

GET /patients/{id}/history

POST /patients/{id}/admit

POST /patients/{id}/discharge
```

---

# Doctor Module

```
GET /doctors

POST /doctors

PUT /doctors/{id}

DELETE /doctors/{id}

GET /doctors/{id}/availability

POST /doctors/{id}/attendance
```

---

# Bed Module

```
GET /beds

POST /beds

PUT /beds/{id}

GET /beds/available

GET /beds/icu
```

---

# Inventory Module

```
GET /medicines

POST /medicines

GET /inventory

POST /inventory/receive

POST /inventory/issue

GET /inventory/low-stock
```

---

# Laboratory Module

```
GET /lab/tests

POST /lab/tests

POST /lab/reports

GET /lab/reports/{id}
```

---

# Blood Bank Module

```
GET /blood

POST /blood

POST /blood/request

GET /blood/inventory
```

---

# Ambulance Module

```
GET /ambulances

POST /ambulances

GET /ambulances/available

POST /ambulances/dispatch
```

---

# Emergency Module

```
POST /incidents

GET /incidents

GET /incidents/{id}

POST /incidents/{id}/triage

POST /incidents/{id}/allocate

POST /incidents/{id}/close
```

---

# AI Module

```
GET /ai/predictions

GET /ai/recommendations

POST /ai/forecast

POST /ai/resource-plan

GET /ai/risk-score
```

---

# Analytics Module

```
GET /analytics/dashboard

GET /analytics/hospital

GET /analytics/resource

GET /analytics/patient

GET /analytics/emergency
```

---

# Notification Module

```
GET /notifications

POST /notifications

PUT /notifications/{id}/read
```

---

# Audit Module

```
GET /audit/logs

GET /audit/users/{id}
```

---

# Rate Limiting

| Role | Limit |
|-------|------|
|Public|50/min|
|Authenticated|500/min|
|Admin|1000/min|

---

# API Naming Rules

Use plural resources

Good

```
/patients

/doctors

/hospitals
```

Avoid verbs

Bad

```
/getPatients

/createDoctor
```

---

# OpenAPI

Every endpoint must be documented using OpenAPI 3.1.

Swagger UI must be generated automatically during deployment.