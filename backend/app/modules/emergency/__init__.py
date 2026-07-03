"""Emergency Module — Incident management and emergency response.

This is the most critical module. It coordinates across all resources
during disasters, mass casualty events, and healthcare emergencies.

Responsibilities:
  - Emergency incident registration
  - Severity classification
  - Automatic resource calculation
  - Patient distribution across hospitals
  - Ambulance dispatch and tracking
  - Emergency bed reservation
  - Emergency action plan generation
  - Disaster coordination dashboard

Supported Incident Types:
  Road Accident, Flood, Fire, Earthquake, Epidemic,
  Building Collapse, Mass Casualty Event

Publishes Events:
  - emergency.incident.created
  - emergency.incident.updated
  - emergency.ambulance.dispatched
  - emergency.incident.closed

Subscribes To:
  - beds.ward.capacity_critical
  - inventory.medicine.stock_out
"""
