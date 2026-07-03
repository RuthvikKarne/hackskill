-- =============================================================================
-- 002_hospitals.sql — Healthcare facility data
-- =============================================================================

CREATE TYPE hospital_type AS ENUM (
    'PHC',              -- Primary Health Centre
    'CHC',              -- Community Health Centre
    'SUB_DISTRICT',     -- Sub-District Hospital
    'DISTRICT',         -- District Hospital
    'MEDICAL_COLLEGE'   -- Government Medical College (future)
);

CREATE TYPE facility_status AS ENUM ('ACTIVE', 'INACTIVE', 'UNDER_RENOVATION');

CREATE TABLE IF NOT EXISTS hospital.hospitals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    district_id     UUID NOT NULL,
    name            TEXT NOT NULL,
    facility_code   TEXT UNIQUE NOT NULL,           -- Government facility code
    hospital_type   hospital_type NOT NULL,
    status          facility_status NOT NULL DEFAULT 'ACTIVE',
    address         TEXT NOT NULL,
    latitude        DECIMAL(9, 6),
    longitude       DECIMAL(9, 6),
    phone           TEXT,
    email           TEXT,
    bed_capacity    INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS hospital.departments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL REFERENCES hospital.hospitals(id),
    name            TEXT NOT NULL,
    head_doctor_id  UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS hospital.wards (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL REFERENCES hospital.hospitals(id),
    department_id   UUID REFERENCES hospital.departments(id),
    name            TEXT NOT NULL,
    ward_type       TEXT NOT NULL,                  -- GENERAL, ICU, MATERNITY, EMERGENCY
    total_beds      INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_hospitals_district ON hospital.hospitals (district_id);
CREATE INDEX IF NOT EXISTS idx_departments_hospital ON hospital.departments (hospital_id);
CREATE INDEX IF NOT EXISTS idx_wards_hospital ON hospital.wards (hospital_id);
