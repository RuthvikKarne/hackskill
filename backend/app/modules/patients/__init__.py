"""Patients Module — Patient lifecycle management.

Responsibilities:
  - Patient registration with digital health record
  - Patient search (name, phone, Aadhaar)
  - Visit records
  - Admission workflow
  - Discharge workflow
  - Medical history

Publishes Events:
  - patients.patient.registered
  - patients.patient.admitted
  - patients.patient.discharged
  - patients.patient.updated
  - patients.visit.created
"""
