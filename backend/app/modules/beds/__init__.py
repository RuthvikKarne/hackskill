"""Beds Module — Ward and bed management.

Responsibilities:
  - Ward configuration per hospital
  - Bed registration and categorisation (General, ICU, Emergency, Maternity)
  - Bed allocation to admitted patients
  - Bed release on discharge
  - Real-time occupancy tracking
  - Bed reservation for emergency cases

Publishes Events:
  - beds.bed.allocated
  - beds.bed.released
  - beds.bed.reserved
  - beds.ward.capacity_critical

Subscribes To:
  - patients.patient.admitted
  - patients.patient.discharged
  - emergency.incident.created
"""
