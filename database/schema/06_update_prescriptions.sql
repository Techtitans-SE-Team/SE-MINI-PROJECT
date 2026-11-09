
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Sprint 2: Prescription Management
-- Member 3: Database Development
-- File: 06_update_prescriptions.sql
-- Purpose: Add prescription processing status
-- =====================================================

USE doctor_reminder_db;

-- Add processing status to existing prescriptions
ALTER TABLE prescriptions
ADD COLUMN processing_status ENUM(
    'Uploaded',
    'Processing',
    'Pending Verification',
    'Verified',
    'Rejected'
) NOT NULL DEFAULT 'Pending Verification'
AFTER verification_status;

-- Verify the updated table structure
DESCRIBE prescriptions;

-- Display existing prescription records
SELECT
    prescription_id,
    patient_id,
    doctor_id,
    medicine_name,
    verification_status,
    processing_status,
    status
FROM prescriptions;
