-- =============================================================================
-- 010_audit.sql — Immutable audit log
-- Records ALL important events. No UPDATE or DELETE permitted on this table.
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit.audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id        UUID NOT NULL UNIQUE,           -- from BaseEvent.event_id
    event_type      TEXT NOT NULL,
    hospital_id     UUID,
    district_id     UUID,
    actor_id        UUID,
    actor_role      TEXT,
    aggregate_type  TEXT NOT NULL,
    aggregate_id    UUID,
    action          TEXT NOT NULL,
    previous_state  JSONB,
    new_state       JSONB,
    ip_address      INET,
    request_id      UUID,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
    -- NO updated_at, NO deleted_at — this table is append-only
);

-- Enforce append-only with a rule
CREATE RULE audit_no_update AS ON UPDATE TO audit.audit_logs DO INSTEAD NOTHING;
CREATE RULE audit_no_delete AS ON DELETE TO audit.audit_logs DO INSTEAD NOTHING;

CREATE INDEX IF NOT EXISTS idx_audit_hospital ON audit.audit_logs (hospital_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit.audit_logs (actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_aggregate ON audit.audit_logs (aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit.audit_logs (event_type, created_at DESC);

COMMENT ON TABLE audit.audit_logs IS
    'Immutable audit log. Append-only. No updates or deletes permitted.';
