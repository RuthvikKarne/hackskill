-- =============================================================================
-- 009_analytics.sql — AI recommendations and analytics storage
-- =============================================================================

CREATE TYPE recommendation_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'DEFERRED', 'EXPIRED');
CREATE TYPE recommendation_type AS ENUM (
    'MEDICINE_REORDER',
    'PATIENT_LOAD_FORECAST',
    'BED_CAPACITY_WARNING',
    'DOCTOR_SHORTAGE',
    'RESOURCE_REDISTRIBUTION',
    'DISEASE_OUTBREAK_ALERT',
    'HOSPITAL_PERFORMANCE'
);

-- AI-generated recommendations (written by AI engine, approved by humans)
CREATE TABLE IF NOT EXISTS analytics.ai_recommendations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id         UUID NOT NULL,
    recommendation_type recommendation_type NOT NULL,
    status              recommendation_status NOT NULL DEFAULT 'PENDING',
    title               TEXT NOT NULL,
    description         TEXT NOT NULL,
    confidence_score    DECIMAL(3, 2) CHECK (confidence_score BETWEEN 0 AND 1),
    explanation         TEXT,                       -- Human-readable SHAP explanation
    model_version       TEXT NOT NULL,
    payload             JSONB NOT NULL,             -- Full recommendation data
    reviewed_by         UUID,                       -- User who approved/rejected
    reviewed_at         TIMESTAMPTZ,
    rejection_reason    TEXT,
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by          UUID                        -- System: AI engine service account
);

CREATE INDEX IF NOT EXISTS idx_ai_recs_hospital ON analytics.ai_recommendations (hospital_id, status);
CREATE INDEX IF NOT EXISTS idx_ai_recs_pending ON analytics.ai_recommendations (status, created_at)
    WHERE status = 'PENDING';
