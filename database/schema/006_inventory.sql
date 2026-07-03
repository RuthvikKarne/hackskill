-- =============================================================================
-- 006_inventory.sql — Medicine inventory management
-- =============================================================================

CREATE TYPE stock_transaction_type AS ENUM (
    'RECEIVED',
    'ISSUED',
    'RETURNED',
    'EXPIRED',
    'TRANSFERRED_OUT',
    'TRANSFERRED_IN',
    'ADJUSTMENT'
);

CREATE TABLE IF NOT EXISTS inventory.medicines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generic_name    TEXT NOT NULL,
    brand_name      TEXT,
    form            TEXT NOT NULL,                  -- TABLET, SYRUP, INJECTION, etc.
    strength        TEXT,                           -- 500mg, 5ml, etc.
    unit            TEXT NOT NULL,                  -- TAB, ML, VIAL, etc.
    reorder_level   INT NOT NULL DEFAULT 0,
    critical_level  INT NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS inventory.stock (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id     UUID NOT NULL,
    medicine_id     UUID NOT NULL REFERENCES inventory.medicines(id),
    batch_number    TEXT NOT NULL,
    quantity        INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    expiry_date     DATE NOT NULL,
    supplier_id     UUID,
    unit_cost       DECIMAL(10, 2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      UUID,
    version         INT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS inventory.stock_transactions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id         UUID NOT NULL,
    medicine_id         UUID NOT NULL,
    transaction_type    stock_transaction_type NOT NULL,
    quantity            INT NOT NULL,
    reference_id        UUID,                       -- patient_id, order_id, etc.
    notes               TEXT,
    transacted_by       UUID NOT NULL,
    transacted_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_stock_hospital_medicine ON inventory.stock (hospital_id, medicine_id);
CREATE INDEX IF NOT EXISTS idx_stock_expiry ON inventory.stock (expiry_date);
CREATE INDEX IF NOT EXISTS idx_stock_tx_hospital ON inventory.stock_transactions (hospital_id);
CREATE INDEX IF NOT EXISTS idx_stock_tx_medicine ON inventory.stock_transactions (medicine_id);
