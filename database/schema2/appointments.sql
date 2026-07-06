CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    patient_id UUID REFERENCES patients(id),

    hospital_id UUID REFERENCES hospitals(id),

    doctor_name TEXT,

    department TEXT,

    appointment_date DATE,

    appointment_time TIME,

    status TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);