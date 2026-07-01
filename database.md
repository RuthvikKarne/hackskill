database.md

1. Introduction
2. Database Architecture
3. Design Principles
4. Naming Conventions
5. Multi-Tenancy
6. Audit Columns
7. Soft Delete Strategy
8. UUID Strategy
9. Database Domains

10. Identity Schema
11. Hospital Schema
12. Patient Schema
13. Doctor Schema
14. Nurse Schema
15. Resource Schema
16. Bed Schema
17. Inventory Schema
18. Medicine Schema
19. Pharmacy Schema
20. Laboratory Schema
21. Blood Bank Schema
22. Ambulance Schema
23. Emergency Schema
24. AI Schema
25. Analytics Schema
26. Notification Schema
27. Integration Schema
28. Audit Schema

29. Relationships
30. Indexing Strategy
31. Constraints
32. Views
33. Materialized Views
34. Stored Procedures
35. Triggers
36. RLS Policies (Supabase)
37. Storage Buckets
38. Migration Strategy
39. Backup Strategy
40. Disaster Recovery


auth
├── users
├── roles
├── permissions

hospital
├── hospitals
├── departments
├── wards
├── rooms

clinical
├── patients
├── visits
├── diagnoses
├── treatments

resource
├── doctors
├── nurses
├── beds
├── ambulances
├── equipment

inventory
├── medicines
├── stock
├── suppliers
├── purchase_orders

laboratory
├── lab_tests
├── reports

blood_bank
├── blood_inventory
├── donors

emergency
├── incidents
├── casualties
├── allocations

analytics
├── forecasts
├── recommendations

audit
├── audit_logs
├── activity_logs


## patients

### Purpose

Stores master information about patients.

### Columns

| Column | Type | Nullable | Description |
|---------|------|----------|-------------|
| id | UUID | No | Primary Key |
| hospital_id | UUID | No | Current Hospital |
| first_name | TEXT | No | First Name |
| last_name | TEXT | No | Last Name |
| dob | DATE | No | Date of Birth |
| gender | TEXT | No | Gender |
| blood_group | TEXT | Yes | Blood Group |
| phone | TEXT | Yes | Contact Number |
| aadhaar | TEXT | Yes | Government ID |
| created_at | TIMESTAMP | No | Audit |
| updated_at | TIMESTAMP | No | Audit |
| deleted_at | TIMESTAMP | Yes | Soft Delete |

Indexes

- idx_patients_phone
- idx_patients_hospital
- idx_patients_aadhaar

Relationships

patient
↓
visits

patient
↓
admissions

patient
↓
medical_records

Events

PatientRegistered

PatientUpdated

PatientDeleted