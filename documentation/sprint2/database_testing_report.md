
# Sprint 2 - Database Testing Report

## Project
Doctor Prescription Reminder

## Team
Tech Titans

## Module
Database Development - Member 3

## 1. Objective

The objective of Sprint 2 database testing is to verify the updated prescription management structure, medicine extraction records, uploaded prescription file metadata, and database relationships.

## 2. Database Environment

- Database: doctor_reminder_db
- DBMS: MySQL 8.0
- Interface: MySQL Shell
- Connection: localhost:3306

## 3. Database Changes

The following changes were implemented:

1. Added processing_status to the prescriptions table.
2. Created the medicines table to store extracted medicine details.
3. Created the prescription_files table to store uploaded file metadata.
4. Added foreign key relationships between prescriptions and the two new tables.
5. Created sample data and prescription management queries.

## 4. Testing Results

| Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|
| Display database tables | All 7 tables displayed | All 7 tables displayed | Passed |
| Prescription record count | Existing records available | 1 record | Passed |
| Medicine record count | Medicine record available | 1 record | Passed |
| File record count | File metadata available | 1 record | Passed |
| Retrieve prescription and medicine | Related records displayed | Paracetamol displayed | Passed |
| Retrieve prescription file | File metadata displayed | sample_prescription.pdf displayed | Passed |
| Medicine foreign key | References prescriptions | Constraint verified | Passed |
| File foreign key | References prescriptions | Constraint verified | Passed |
| Update processing status | Status updated | Processing | Passed |
| Update extraction status | Status updated | Confirmed | Passed |
| Update file status | Status updated | Processed | Passed |

## 5. Sample Test Data

### Prescription

- Prescription ID: 1
- Patient ID: 1
- Doctor ID: 1
- Medicine: Paracetamol
- Dosage: 500 mg
- Frequency: Twice a day
- Duration: 5 days

### Extracted Medicine

- Medicine ID: 1
- Medicine Name: Paracetamol
- Extraction Status: Confirmed

### Uploaded File Metadata

- File ID: 1
- File Name: sample_prescription.pdf
- File Type: application/pdf
- File Size: 102400 bytes
- Upload Status: Processed

## 6. Database Relationships

- One prescription can have multiple medicine records.
- One prescription can have multiple uploaded file records.
- Medicines reference prescriptions through a foreign key.
- Prescription files reference prescriptions through a foreign key.

## 7. Testing Conclusion

The Sprint 2 database validation queries executed successfully.

All seven database tables were verified. The new medicines and prescription_files tables were created successfully, and their foreign key relationships with the prescriptions table were confirmed.

Sample records were inserted and retrieved successfully. The prescription management update queries also executed successfully.

The database structure is ready for further backend integration and application-level testing.

Note: Actual PDF/image upload and medicine extraction functionality must be tested through the backend application. The current database tests verify sample metadata and records only.
