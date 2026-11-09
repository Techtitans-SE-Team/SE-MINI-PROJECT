
# Doctor Prescription Reminder - ER Diagram

## Sprint 2 Updated Database Design

```mermaid
erDiagram

    ROLES ||--o{ USERS : assigns
    USERS ||--o| PATIENTS : has
    USERS ||--o| DOCTORS : has

    PATIENTS ||--o{ PRESCRIPTIONS : receives
    DOCTORS ||--o{ PRESCRIPTIONS : creates

    PRESCRIPTIONS ||--o{ MEDICINES : contains
    PRESCRIPTIONS ||--o{ PRESCRIPTION_FILES : has

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
    }

    PATIENTS {
        int patient_id PK
        int user_id FK
        date date_of_birth
        varchar phone
        varchar preferred_language
        varchar address
        enum status
    }

    DOCTORS {
        int doctor_id PK
        int user_id FK
        varchar specialization
        varchar qualification
        varchar license_number
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
        enum processing_status
        enum status
    }

    MEDICINES {
        int medicine_id PK
        int prescription_id FK
        varchar medicine_name
        varchar dosage
        varchar frequency
        varchar duration
        text instructions
        enum extraction_status
    }

    PRESCRIPTION_FILES {
        int file_id PK
        int prescription_id FK
        varchar original_file_name
        varchar stored_file_path
        varchar file_type
        bigint file_size
        timestamp upload_date
        enum upload_status
    }
```

## Sprint 2 Changes

- Added MEDICINES to store extracted medicine details.
- Added PRESCRIPTION_FILES to store uploaded prescription file metadata.
- Added processing_status to PRESCRIPTIONS.
- Established one-to-many relationships between PRESCRIPTIONS and both new entities.
