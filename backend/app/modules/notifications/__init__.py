"""Notifications Module — Multi-channel notification delivery.

This module is ONLY a subscriber. It never publishes events.
Business modules publish events; Notifications decides how to deliver them.

Channels:
  - In-app notifications (stored in DB, polled by frontend)
  - Email (SMTP)
  - SMS (Gateway API)
  - WhatsApp (future)
  - Push notifications (future)

Subscribes To (all events that require user notification):
  - inventory.medicine.stock_critical_low
  - inventory.medicine.expiry_approaching
  - inventory.medicine.stock_out
  - beds.ward.capacity_critical
  - doctors.doctor.absent
  - emergency.incident.created
  - laboratory.report.ready
  - ai.recommendation.generated
  - patients.patient.registered (conditional)
"""
