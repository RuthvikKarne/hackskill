CREATE TABLE medical_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    patient_id UUID REFERENCES patients(id),

    visit_date DATE,

    diagnosis TEXT,

    treatment TEXT,

    prescription TEXT,

    doctor_name TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);