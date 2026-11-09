
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Sprint 2: Sample Data
-- Member 3: Database Development
-- File: sprint2_sample_data.sql
-- Purpose: Insert sample medicine and uploaded file data
-- =====================================================

USE doctor_reminder_db;

-- Insert extracted medicine details for prescription ID 1
INSERT INTO medicines (
    prescription_id,
    medicine_name,
    dosage,
    frequency,
    duration,
    instructions,
    extraction_status
)
SELECT
    prescription_id,
    medicine_name,
    dosage,
    frequency,
    duration,
    instructions,
    'Extracted'
FROM prescriptions
WHERE prescription_id = 1
AND NOT EXISTS (
    SELECT 1
    FROM medicines
    WHERE prescription_id = 1
);

-- Insert sample uploaded-file metadata
INSERT INTO prescription_files (
    prescription_id,
    original_file_name,
    stored_file_path,
    file_type,
    file_size,
    upload_status
)
SELECT
    1,
    'sample_prescription.pdf',
    'uploads/prescriptions/sample_prescription.pdf',
    'application/pdf',
    102400,
    'Uploaded'
WHERE EXISTS (
    SELECT 1
    FROM prescriptions
    WHERE prescription_id = 1
)
AND NOT EXISTS (
    SELECT 1
    FROM prescription_files
    WHERE prescription_id = 1
);

-- Display inserted medicine records
SELECT * FROM medicines;

-- Display uploaded prescription file metadata
SELECT * FROM prescription_files;
