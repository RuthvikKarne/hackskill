"""Analytics Module — KPI aggregation and trend analysis.

This module is READ-ONLY. It never writes to business tables.
All data is sourced from database views and event subscriptions.

Responsibilities:
  - Hospital KPI calculation (bed utilisation, attendance rate, stock health)
  - District-wide aggregate metrics
  - Trend analysis (patient load trends, medicine consumption trends)
  - Hospital performance comparison
  - Dashboard data endpoints

Subscribes To:
  - patients.patient.registered
  - patients.patient.admitted
  - patients.patient.discharged
  - beds.bed.allocated
  - beds.bed.released
  - doctors.attendance.marked
  - inventory.medicine.stock_updated
  - emergency.incident.created
  - emergency.incident.closed
"""
