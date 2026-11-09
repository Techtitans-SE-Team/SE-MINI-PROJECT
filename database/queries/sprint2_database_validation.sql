
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Sprint 2: Database Validation
-- Member 3: Database Development
-- File: sprint2_database_validation.sql
-- =====================================================

USE doctor_reminder_db;

-- Test 1: Display all database tables
SHOW TABLES;

-- Test 2: Count records in important tables
SELECT 'prescriptions' AS table_name, COUNT(*) AS total_records
FROM prescriptions
UNION ALL
SELECT 'medicines', COUNT(*) FROM medicines
UNION ALL
SELECT 'prescription_files', COUNT(*) FROM prescription_files;

-- Test 3: Verify prescription-medicine relationship
SELECT
    p.prescription_id,
    p.medicine_name AS prescription_medicine,
    m.medicine_name AS extracted_medicine,
    m.extraction_status
FROM prescriptions p
LEFT JOIN medicines m
    ON p.prescription_id = m.prescription_id;

-- Test 4: Verify prescription-file relationship
SELECT
    p.prescription_id,
    pf.original_file_name,
    pf.upload_status
FROM prescriptions p
LEFT JOIN prescription_files pf
    ON p.prescription_id = pf.prescription_id;

-- Test 5: Verify foreign key constraints
SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'doctor_reminder_db'
AND TABLE_NAME IN (
    'medicines',
    'prescription_files'
)
AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Test 6: Check current prescription processing status
SELECT
    prescription_id,
    verification_status,
    processing_status,
    status
FROM prescriptions;
