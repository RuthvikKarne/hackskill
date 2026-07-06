CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hospital_id UUID REFERENCES hospitals(id),

    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,

    dob DATE,

    gender TEXT,

    blood_group TEXT,

    phone TEXT,

    email TEXT,

    address TEXT,

    emergency_contact TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);