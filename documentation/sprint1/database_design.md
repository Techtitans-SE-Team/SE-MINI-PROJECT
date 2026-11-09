
# Database Design Documentation
## Doctor Prescription to Multilingual Video Reminder and Instruction Generator

### 1. Project Overview

The Doctor Prescription Reminder System is designed to store and manage doctor, patient, user, and prescription information.

The database supports prescription creation, retrieval, verification status tracking, and the relationships between doctors and patients.

Database Name: doctor_reminder_db

Database Management System: MySQL

Storage Engine: InnoDB

### 2. Database Objectives

- Store user login and role information.
- Maintain patient profiles.
- Maintain doctor profiles.
- Store medicine prescription details.
- Connect prescriptions with the correct patients and doctors.
- Track prescription verification status.
- Retrieve prescription information when required.

### 3. Database Tables

The database contains five tables.

#### 3.1 Roles Table

Purpose: Stores the different roles supported by the system.

| Column | Data Type | Description |
|---|---|---|
| role_id | INT | Primary key |
| role_name | VARCHAR(30) | Unique role name |

Sample roles:
- Doctor
- Patient
- Admin

#### 3.2 Users Table

Purpose: Stores basic user and authentication information.

| Column | Data Type | Description |
|---|---|---|
| user_id | INT | Primary key |
| name | VARCHAR(100) | User name |
| email | VARCHAR(150) | Unique email |
| password_hash | VARCHAR(255) | Hashed password |
| role_id | INT | Foreign key |
| created_at | TIMESTAMP | Account creation time |

#### 3.3 Patients Table

Purpose: Stores patient profile information.

| Column | Data Type | Description |
|---|---|---|
| patient_id | INT | Primary key |
| user_id | INT | Unique foreign key |
| date_of_birth | DATE | Patient date of birth |
| phone | VARCHAR(15) | Contact number |
| preferred_language | VARCHAR(50) | Preferred language |
| address | VARCHAR(255) | Patient address |
| status | ENUM | Active or Inactive |
| created_at | TIMESTAMP | Profile creation time |

#### 3.4 Doctors Table

Purpose: Stores doctor profile information.

| Column | Data Type | Description |
|---|---|---|
| doctor_id | INT | Primary key |
| user_id | INT | Unique foreign key |
| specialization | VARCHAR(100) | Medical specialization |
| qualification | VARCHAR(100) | Doctor qualification |
| license_number | VARCHAR(50) | Unique license number |
| created_at | TIMESTAMP | Profile creation time |

#### 3.5 Prescriptions Table

Purpose: Stores prescription and medicine information.

| Column | Data Type | Description |
|---|---|---|
| prescription_id | INT | Primary key |
| patient_id | INT | Foreign key |
| doctor_id | INT | Foreign key |
| medicine_name | VARCHAR(150) | Medicine name |
| dosage | VARCHAR(100) | Medicine dosage |
| frequency | VARCHAR(100) | Medicine frequency |
| duration | VARCHAR(100) | Prescription duration |
| instructions | TEXT | Additional instructions |
| prescription_date | DATE | Prescription date |
| verification_status | ENUM | Pending, Verified, Rejected |
| status | ENUM | Active, Completed, Cancelled |
| created_at | TIMESTAMP | Record creation time |

### 4. Primary Keys

Primary keys uniquely identify records in each table.

- roles: role_id
- users: user_id
- patients: patient_id
- doctors: doctor_id
- prescriptions: prescription_id

### 5. Foreign Keys and Relationships

The database uses foreign keys to maintain referential integrity.

| Child Table | Foreign Key | Parent Table |
|---|---|---|
| users | role_id | roles |
| patients | user_id | users |
| doctors | user_id | users |
| prescriptions | patient_id | patients |
| prescriptions | doctor_id | doctors |

Relationship descriptions:

1. One role can be assigned to multiple users.
2. A user can have one patient profile.
3. A user can have one doctor profile.
4. One patient can have multiple prescriptions.
5. One doctor can create multiple prescriptions.

### 6. Database Constraints

The database implements the following constraints:

- PRIMARY KEY: Uniquely identifies each record.
- FOREIGN KEY: Maintains relationships between tables.
- NOT NULL: Ensures mandatory fields contain values.
- UNIQUE: Prevents duplicate emails and profile associations.
- ENUM: Restricts status fields to predefined values.
- AUTO_INCREMENT: Automatically generates IDs.
- DEFAULT: Assigns default values where applicable.

### 7. Prescription Verification

The prescription verification workflow uses three statuses:

1. Pending: Prescription is awaiting verification.
2. Verified: Prescription has been reviewed and verified.
3. Rejected: Prescription has been rejected.

New prescriptions receive the Pending status by default.

The system must not use unverified prescription information to generate final patient instructions or reminders.

### 8. Sample Database Records

Sample records were inserted for testing:

User 1:
- Name: Dr. Arun Kumar
- Role: Doctor

User 2:
- Name: Priya Sharma
- Role: Patient

Patient profile:
- Patient ID: 1
- Preferred language: English

Doctor profile:
- Doctor ID: 1
- Specialization: General Medicine

Prescription:
- Prescription ID: 1
- Medicine: Paracetamol
- Dosage: 500 mg
- Frequency: Twice a day
- Duration: 5 days
- Verification status: Pending

These are illustrative test records.

### 9. Database Testing

The following operations were tested successfully:

1. Database creation.
2. Table creation.
3. Sample user insertion.
4. Patient profile insertion.
5. Doctor profile insertion.
6. Prescription insertion.
7. Prescription retrieval.
8. Retrieval using patient ID.
9. Retrieval using doctor ID.
10. Patient and doctor details using JOIN.
11. Pending prescription retrieval.
12. Prescription count.
13. Mandatory-field validation.
14. Verification-status count.

The verification update query was prepared but not executed.

### 10. Conclusion

The database module has been designed and implemented using MySQL.

It contains five core tables with primary keys, foreign keys, constraints, and relationships.

Sample records and SQL queries were tested successfully. The database provides the foundation for prescription management and future integration with the backend, multilingual processing, and reminder generation modules.
