-- =============================================================================
-- 003_patients.sql — Patient records and clinical data
-- =============================================================================

CREATE TYPE gender AS ENUM ('MALE', 'FEMALE', 'OTHER');
CREATE TYPE blood_group AS ENUM ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'UNKNOWN');
CREATE TYPE admission_status AS ENUM ('ADMITTED', 'DISCHARGED', 'TRANSFERRED');

CREATE TABLE IF NOT EXISTS clinical.patients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL,
    mrn             TEXT UNIQUE NOT NULL,           -- Medical Record Number
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    dob             DATE NOT NULL,
    gender          gender NOT NULL,
    blood_group     blood_group,
    -- Sensitive fields (encrypted at application layer)
    phone           TEXT,                           -- Stored encrypted
    aadhaar_hash    TEXT,                           -- SHA-256 hash only — never store plaintext
    address         TEXT,
    emergency_contact_name  TEXT,
    emergency_contact_phone TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clinical.visits (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL,
    patient_id      UUID NOT NULL REFERENCES clinical.patients(id),
    visit_date      DATE NOT NULL,
    visit_type      TEXT NOT NULL,                  -- OPD, IPD, EMERGENCY
    chief_complaint TEXT,
    diagnosis       TEXT,
    doctor_id       UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clinical.admissions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL,
    patient_id      UUID NOT NULL REFERENCES clinical.patients(id),
    bed_id          UUID NOT NULL,
    doctor_id       UUID NOT NULL,
    admitted_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    discharged_at   TIMESTAMPTZ,
    status          admission_status NOT NULL DEFAULT 'ADMITTED',
    discharge_notes TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_patients_hospital ON clinical.patients (hospital_id);
CREATE INDEX IF NOT EXISTS idx_patients_mrn ON clinical.patients (mrn);
CREATE INDEX IF NOT EXISTS idx_patients_name_search ON clinical.patients USING gin (
    (first_name || ' ' || last_name) gin_trgm_ops
);
CREATE INDEX IF NOT EXISTS idx_visits_patient ON clinical.visits (patient_id);
CREATE INDEX IF NOT EXISTS idx_admissions_patient ON clinical.admissions (patient_id);
CREATE INDEX IF NOT EXISTS idx_admissions_active ON clinical.admissions (hospital_id, status)
    WHERE status = 'ADMITTED';
