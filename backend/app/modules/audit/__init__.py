"""Audit Module — Immutable audit log.

This module is an APPEND-ONLY subscriber. It never modifies existing records.
Every important event in the system generates an audit log entry.

Audit Log Entry Contains:
  - timestamp (UTC)
  - event_type
  - actor_id (user who performed the action)
  - actor_role
  - hospital_id
  - aggregate_type (entity type)
  - aggregate_id (entity ID)
  - action (CREATE, UPDATE, DELETE, LOGIN, APPROVE, etc.)
  - previous_state (JSON snapshot before change)
  - new_state (JSON snapshot after change)
  - ip_address
  - request_id

Audit logs are immutable — no UPDATE or DELETE operations are permitted.

Subscribes To: ALL domain events
"""
