CREATE TABLE hospitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    district TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    latitude DECIMAL,
    longitude DECIMAL,
    created_at TIMESTAMPTZ DEFAULT now()
);