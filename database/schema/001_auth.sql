-- =============================================================================
-- 001_auth.sql — Authentication, roles, and permissions
-- =============================================================================

-- Supported user roles in the system
CREATE TYPE user_role AS ENUM (
    'SYSTEM_ADMIN',
    'DISTRICT_ADMIN',
    'HOSPITAL_ADMIN',
    'DOCTOR',
    'NURSE',
    'LAB_TECHNICIAN',
    'PHARMACIST',
    'EMERGENCY_OPERATOR',
    'RECEPTIONIST',
    'PATIENT'
);

CREATE TYPE user_status AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED');

-- Core users table
-- NOTE: Supabase Auth manages password hashing and session.
-- This table stores HRIP-specific user profile data linked to Supabase auth.users.
CREATE TABLE IF NOT EXISTS auth.hrip_users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_uid    UUID UNIQUE NOT NULL,         -- Links to auth.users.id in Supabase
    hospital_id     UUID,                          -- NULL for system/district admins
    district_id     UUID,                          -- NULL for hospital-level users
    role            user_role NOT NULL,
    status          user_status NOT NULL DEFAULT 'ACTIVE',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

-- Refresh token blocklist (for logout invalidation)
CREATE TABLE IF NOT EXISTS auth.token_blocklist (
    jti             UUID PRIMARY KEY,             -- JWT ID from token claims
    user_id         UUID NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    blocked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Auto-cleanup expired tokens (run daily via cron or pg_cron)
CREATE INDEX IF NOT EXISTS idx_token_blocklist_expires ON auth.token_blocklist (expires_at);

COMMENT ON TABLE auth.hrip_users IS
    'HRIP user profiles linked to Supabase Auth. Stores role and tenant context.';
