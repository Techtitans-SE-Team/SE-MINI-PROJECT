
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Sprint 2: Prescription Management Queries
-- Member 3: Database Development
-- File: sprint2_prescription_queries.sql
-- =====================================================

USE doctor_reminder_db;

-- 1. Retrieve all prescriptions with patient and doctor details
SELECT
    p.prescription_id,
    pu.name AS patient_name,
    du.name AS doctor_name,
    p.medicine_name,
    p.dosage,
    p.frequency,
    p.duration,
    p.prescription_date,
    p.verification_status,
    p.processing_status,
    p.status
FROM prescriptions p
JOIN patients pt ON p.patient_id = pt.patient_id
JOIN users pu ON pt.user_id = pu.user_id
JOIN doctors d ON p.doctor_id = d.doctor_id
JOIN users du ON d.user_id = du.user_id;


-- 2. Retrieve medicines extracted from a prescription
SELECT
    medicine_id,
    prescription_id,
    medicine_name,
    dosage,
    frequency,
    duration,
    instructions,
    extraction_status
FROM medicines
WHERE prescription_id = 1;


-- 3. Retrieve uploaded files for a prescription
SELECT
    file_id,
    original_file_name,
    stored_file_path,
    file_type,
    file_size,
    upload_date,
    upload_status
FROM prescription_files
WHERE prescription_id = 1;


-- 4. Update prescription processing status
UPDATE prescriptions
SET processing_status = 'Processing'
WHERE prescription_id = 1;


-- 5. Update medicine extraction status
UPDATE medicines
SET extraction_status = 'Confirmed'
WHERE medicine_id = 1;


-- 6. Update uploaded file status
UPDATE prescription_files
SET upload_status = 'Processed'
WHERE file_id = 1;


-- 7. Retrieve prescriptions awaiting verification
SELECT
    prescription_id,
    patient_id,
    doctor_id,
    medicine_name,
    verification_status,
    processing_status
FROM prescriptions
WHERE verification_status = 'Pending';


-- 8. Retrieve prescription and its associated medicines
SELECT
    p.prescription_id,
    p.medicine_name AS original_medicine,
    m.medicine_name AS extracted_medicine,
    m.dosage,
    m.extraction_status
FROM prescriptions p
LEFT JOIN medicines m
    ON p.prescription_id = m.prescription_id;
