-- =============================================================================
-- 005_beds.sql — Bed and ward occupancy tracking
-- =============================================================================

CREATE TYPE bed_type AS ENUM ('GENERAL', 'ICU', 'EMERGENCY', 'MATERNITY', 'PAEDIATRIC', 'ISOLATION');
CREATE TYPE bed_status AS ENUM ('AVAILABLE', 'OCCUPIED', 'RESERVED', 'MAINTENANCE');

CREATE TABLE IF NOT EXISTS resource.beds (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL,
    ward_id         UUID NOT NULL,
    bed_number      TEXT NOT NULL,
    bed_type        bed_type NOT NULL DEFAULT 'GENERAL',
    status          bed_status NOT NULL DEFAULT 'AVAILABLE',
    current_patient_id  UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1,
    UNIQUE (hospital_id, ward_id, bed_number)
);

CREATE INDEX IF NOT EXISTS idx_beds_hospital ON resource.beds (hospital_id);
CREATE INDEX IF NOT EXISTS idx_beds_available ON resource.beds (hospital_id, status)
    WHERE status = 'AVAILABLE';
CREATE INDEX IF NOT EXISTS idx_beds_ward ON resource.beds (ward_id);
