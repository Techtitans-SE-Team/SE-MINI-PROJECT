
# Database Module
## Doctor Prescription Reminder System

### 1. Overview

This folder contains the MySQL database module for the Doctor Prescription Reminder System.

It manages user roles, user accounts, patient profiles, doctor profiles, and prescriptions.

### 2. Technologies Used

- Database: MySQL
- Storage Engine: InnoDB
- Query Language: SQL
- Database Name: doctor_reminder_db

### 3. Folder Structure

```text
database/
├── schema/
│   ├── 01_create_database.sql
│   ├── 02_create_users.sql
│   ├── 03_create_patients.sql
│   ├── 04_create_doctors.sql
│   └── 05_create_prescriptions.sql
├── sample_data/
│   └── insert_sample_data.sql
├── queries/
│   └── prescription_queries.sql
└── README.md

documentation/
├── ER_DIAGRAM/
│   └── er_diagram.md
└── sprint1/
    └── database_design.md
```

### 4. Database Tables

| Table | Description |
|---|---|
| roles | Stores user roles |
| users | Stores user account details |
| patients | Stores patient profiles |
| doctors | Stores doctor profiles |
| prescriptions | Stores prescription details |

### 5. Database Setup Instructions

1. Install MySQL Server and MySQL Shell.
2. Connect to MySQL Shell in SQL mode.
3. Execute the following schema files in order:

```sql
\source "database/schema/01_create_database.sql"
\source "database/schema/02_create_users.sql"
\source "database/schema/03_create_patients.sql"
\source "database/schema/04_create_doctors.sql"
\source "database/schema/05_create_prescriptions.sql"
```

Replace relative paths with full file paths if required.

### 6. Insert Sample Data

After creating all tables, execute:

```sql
\source "database/sample_data/insert_sample_data.sql"
```

This inserts sample users, patient and doctor profiles, and a prescription for testing.

### 7. Run Prescription Queries

Execute:

```sql
\source "database/queries/prescription_queries.sql"
```

The file includes queries for:

- Retrieving all prescriptions.
- Retrieving patient and doctor details.
- Searching prescriptions by patient.
- Searching prescriptions by doctor.
- Finding pending prescriptions.
- Counting prescriptions.
- Checking mandatory fields.
- Checking verification status.

### 8. Database Verification

Run:

```sql
USE doctor_reminder_db;
SHOW TABLES;
DESCRIBE prescriptions;
```

### 9. Important Notes

- Execute schema files in the specified order.
- Sample data is intended only for development and testing.
- Sample password values are placeholders, not valid authentication hashes.
- Actual passwords must be securely hashed by the backend.
- Prescription information must be verified before generating patient instructions or reminders.
- Sample medicine information is not medical advice.

### 10. Implementation Status

Completed database components:

- Database creation.
- Roles and users management.
- Patient profile table.
- Doctor profile table.
- Prescription management table.
- Primary and foreign key relationships.
- Sample data insertion.
- Prescription retrieval queries.
- Mandatory-field constraints.
- Verification status tracking.
- SQL query testing.
- Database design documentation.
- ER diagram.

### 11. Future Integration

The database module can be integrated with the backend to support:

- User authentication and role-based access.
- Prescription creation and retrieval through APIs.
- Prescription verification.
- Multilingual reminder generation.
- Video and audio reminder management.
