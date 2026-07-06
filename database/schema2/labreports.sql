CREATE TABLE lab_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    patient_id UUID REFERENCES patients(id),

    test_name TEXT,

    status TEXT,

    result TEXT,

    report_url TEXT,

    created_at TIMESTAMPTZ DEFAULT now()
);