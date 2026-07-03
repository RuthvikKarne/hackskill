-- =============================================================================
-- 000_extensions.sql — PostgreSQL extensions required by HRIP
-- Run this first, before any other schema files.
-- =============================================================================

-- UUID generation (used as primary key for all tables)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pgcrypto for encryption functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- pg_trgm for full-text patient name search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- btree_gist for range indexing (bed reservation periods)
CREATE EXTENSION IF NOT EXISTS btree_gist;
