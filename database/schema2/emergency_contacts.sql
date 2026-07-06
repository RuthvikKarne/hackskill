CREATE TABLE emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    hospital_id UUID REFERENCES hospitals(id),

    name TEXT,

    phone TEXT,

    type TEXT
);