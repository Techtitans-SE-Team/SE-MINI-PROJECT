
-- ============================================
-- Doctor Prescription Reminder System
-- Prescription Queries and Testing
-- ============================================

USE doctor_reminder_db;

-- TEST 1: Retrieve all prescriptions
SELECT
    prescription_id,
    patient_id,
    doctor_id,
    medicine_name,
    dosage,
    frequency,
    duration,
    instructions,
    prescription_date,
    verification_status,
    status
FROM prescriptions;

-- TEST 2: Retrieve prescriptions with patient and doctor names
SELECT
    pr.prescription_id,
    pu.name AS patient_name,
    du.name AS doctor_name,
    pr.medicine_name,
    pr.dosage,
    pr.frequency,
    pr.duration,
    pr.verification_status
FROM prescriptions pr
JOIN patients p
    ON pr.patient_id = p.patient_id
JOIN users pu
    ON p.user_id = pu.user_id
JOIN doctors d
    ON pr.doctor_id = d.doctor_id
JOIN users du
    ON d.user_id = du.user_id;

-- TEST 3: Retrieve prescriptions for a particular patient
SELECT *
FROM prescriptions
WHERE patient_id = 1;

-- TEST 4: Retrieve prescriptions created by a particular doctor
SELECT *
FROM prescriptions
WHERE doctor_id = 1;

-- TEST 5: Retrieve prescriptions awaiting verification
SELECT *
FROM prescriptions
WHERE verification_status = 'Pending';

-- TEST 6: Count total prescriptions
SELECT COUNT(*) AS total_prescriptions
FROM prescriptions;

-- TEST 7: Validate mandatory fields in stored records
SELECT
    prescription_id,
    CASE
        WHEN patient_id IS NULL
          OR doctor_id IS NULL
          OR medicine_name IS NULL
          OR dosage IS NULL
          OR frequency IS NULL
          OR duration IS NULL
          OR prescription_date IS NULL
        THEN 'Missing mandatory field'
        ELSE 'All mandatory fields present'
    END AS validation_result
FROM prescriptions;

-- TEST 8: Count prescriptions by verification status
SELECT
    verification_status,
    COUNT(*) AS total
FROM prescriptions
GROUP BY verification_status;

-- TEST 9: Update verification status only after authorized review
-- Do not execute this automatically.
-- UPDATE prescriptions
-- SET verification_status = 'Verified'
-- WHERE prescription_id = 1;

-- TEST 10: Confirm prescription and verification status
SELECT
    prescription_id,
    verification_status,
    status
FROM prescriptions;
