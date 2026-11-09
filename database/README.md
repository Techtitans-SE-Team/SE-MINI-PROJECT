# Database Module
## Doctor Prescription Reminder System

### 1. Overview

This folder contains the MySQL database module for the Doctor Prescription Reminder System.

The database manages user roles, user accounts, patient profiles, doctor profiles, prescriptions, uploaded prescription file metadata, and extracted medicine details.

It supports prescription management, processing status tracking, medicine extraction status tracking, and verification workflows.

### 2. Technologies Used

- Database: MySQL
- Storage Engine: InnoDB
- Query Language: SQL
- Database Name: `doctor_reminder_db`

### 3. Folder Structure

```text
database/
├── schema/
│   ├── 01_create_database.sql
│   ├── 02_create_users.sql
│   ├── 03_create_patients.sql
│   ├── 04_create_doctors.sql
│   ├── 05_create_prescriptions.sql
│   ├── 06_update_prescriptions.sql
│   ├── 07_create_medicines.sql
│   └── 08_create_prescription_files.sql
│
├── sample_data/
│   ├── insert_sample_data.sql
│   └── sprint2_sample_data.sql
│
├── queries/
│   ├── prescription_queries.sql
│   ├── sprint2_prescription_queries.sql
│   └── sprint2_database_validation.sql
│
└── README.md

documentation/
├── ER_DIAGRAM/
│   └── er_diagram.md
├── sprint1/
│   └── database_design.md
└── sprint2/
    └── database_testing_report.md
```

### 4. Database Tables

| Table | Description |
|---|---|
| roles | Stores user roles |
| users | Stores user account details |
| patients | Stores patient profiles |
| doctors | Stores doctor profiles |
| prescriptions | Stores prescription details and processing/verification statuses |
| medicines | Stores medicine details extracted from prescriptions |
| prescription_files | Stores uploaded prescription file metadata |

### 5. Database Relationships

- Roles → Users
- Users → Patients
- Users → Doctors
- Patients → Prescriptions
- Doctors → Prescriptions
- Prescriptions → Medicines
- Prescriptions → Prescription Files

Primary keys and foreign keys maintain referential integrity between related records.

### 6. Database Setup Instructions

1. Install MySQL Server and MySQL Shell.
2. Connect to MySQL Shell in SQL mode.
3. Execute the schema files in the following order.

Sprint 1 schema:

```sql
\source "database/schema/01_create_database.sql"
\source "database/schema/02_create_users.sql"
\source "database/schema/03_create_patients.sql"
\source "database/schema/04_create_doctors.sql"
\source "database/schema/05_create_prescriptions.sql"
```

Sprint 2 schema:

```sql
\source "database/schema/06_update_prescriptions.sql"
\source "database/schema/07_create_medicines.sql"
\source "database/schema/08_create_prescription_files.sql"
```

Replace relative paths with the appropriate full file paths if required.

Note: Sprint 2 scripts extend the existing Sprint 1 database. Execute the Sprint 1 schema first when setting up a fresh database.

### 7. Insert Sample Data

Sprint 1 sample data:

```sql
\source "database/sample_data/insert_sample_data.sql"
```

Sprint 2 sample data:

```sql
\source "database/sample_data/sprint2_sample_data.sql"
```

Sprint 2 sample data includes:

- Sample extracted medicine information.
- Sample prescription file metadata.
- Related prescription records.

The sample file entry represents metadata only. The actual PDF or image file must be uploaded and stored by the backend.

### 8. Run SQL Queries

Sprint 1 queries:

```sql
\source "database/queries/prescription_queries.sql"
```

Sprint 2 queries:

```sql
\source "database/queries/sprint2_prescription_queries.sql"
```

The queries support:

- Retrieving prescriptions.
- Retrieving patient and doctor details.
- Searching prescriptions by patient or doctor.
- Retrieving extracted medicines.
- Retrieving uploaded prescription file metadata.
- Updating prescription processing status.
- Updating medicine extraction status.
- Updating file upload status.
- Retrieving prescriptions pending verification.

### 9. Database Validation

Execute:

```sql
\source "database/queries/sprint2_database_validation.sql"
```

The validation script checks:

- Existing database tables.
- Record counts.
- Prescription-to-medicine relationships.
- Prescription-to-file relationships.
- Foreign key constraints.
- Current processing, extraction, and upload statuses.

### 10. Important Notes

- Execute schema files in the specified order.
- Sample data is intended for development and testing.
- Sample password values are placeholders, not valid authentication hashes.
- Actual passwords must be securely hashed by the backend.
- Prescription information must be verified before generating patient instructions or reminders.
- Uploaded file metadata is stored in the database; actual file storage is handled by the backend.
- Sample medicine information is not medical advice.

### 11. Implementation Status

#### Sprint 1 – Database Foundation

- Database creation.
- Roles and users management.
- Patient profile table.
- Doctor profile table.
- Prescription management table.
- Primary and foreign key relationships.
- Sample data insertion.
- Prescription retrieval queries.
- Verification status tracking.
- Database design documentation.
- Initial ER diagram.

#### Sprint 2 – Prescription Management

- Updated prescriptions table with processing status tracking.
- Created medicines table for extracted medicine details.
- Created prescription_files table for uploaded file metadata.
- Added Sprint 2 sample data.
- Created prescription retrieval and update queries.
- Added database validation scripts.
- Verified foreign key relationships.
- Updated ER diagram.
- Created Sprint 2 database testing report.

### 12. Future Integration

The database module can be integrated with the backend to support:

- User authentication and role-based access.
- Prescription creation and retrieval through APIs.
- Actual PDF and image uploads.
- Automated medicine information extraction.
- Prescription verification workflows.
- Multilingual reminder generation.
- Video and audio reminder management.
