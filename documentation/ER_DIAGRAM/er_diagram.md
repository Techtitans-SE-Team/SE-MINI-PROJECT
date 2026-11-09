
# Doctor Prescription Reminder System
## Entity Relationship Diagram (ER Diagram)

```mermaid
erDiagram
    ROLES ||--o{ USERS : has
    USERS ||--o| PATIENTS : "patient profile"
    USERS ||--o| DOCTORS : "doctor profile"
    PATIENTS ||--o{ PRESCRIPTIONS : receives
    DOCTORS ||--o{ PRESCRIPTIONS : creates

    ROLES {
        int role_id PK
        varchar role_name
    }

    USERS {
        int user_id PK
        varchar name
        varchar email
        varchar password_hash
        int role_id FK
        timestamp created_at
    }

    PATIENTS {
        int patient_id PK
        int user_id FK
        date date_of_birth
        varchar phone
        varchar preferred_language
        varchar address
        enum status
        timestamp created_at
    }

    DOCTORS {
        int doctor_id PK
        int user_id FK
        varchar specialization
        varchar qualification
        varchar license_number
        timestamp created_at
    }

    PRESCRIPTIONS {
        int prescription_id PK
        int patient_id FK
        int doctor_id FK
        varchar medicine_name
        varchar dosage
        varchar frequency
        varchar duration
        text instructions
        date prescription_date
        enum verification_status
        enum status
        timestamp created_at
    }
```

## Relationship Explanation

1. ROLES and USERS:
   One role can be assigned to many users.

2. USERS and PATIENTS:
   A user can have one patient profile.

3. USERS and DOCTORS:
   A user can have one doctor profile.

4. PATIENTS and PRESCRIPTIONS:
   One patient can receive multiple prescriptions.

5. DOCTORS and PRESCRIPTIONS:
   One doctor can create multiple prescriptions.

## Primary Keys

- roles: role_id
- users: user_id
- patients: patient_id
- doctors: doctor_id
- prescriptions: prescription_id

## Foreign Keys

- users.role_id references roles.role_id
- patients.user_id references users.user_id
- doctors.user_id references users.user_id
- prescriptions.patient_id references patients.patient_id
- prescriptions.doctor_id references doctors.doctor_id
