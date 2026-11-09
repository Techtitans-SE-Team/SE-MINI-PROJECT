
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Sprint 2: Prescription Management
-- Member 3: Database Development
-- File: 08_create_prescription_files.sql
-- Purpose: Store uploaded prescription file metadata
-- =====================================================

USE doctor_reminder_db;

CREATE TABLE IF NOT EXISTS prescription_files (
    file_id INT AUTO_INCREMENT PRIMARY KEY,

    prescription_id INT NOT NULL,

    original_file_name VARCHAR(255) NOT NULL,
    stored_file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,

    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    upload_status ENUM(
        'Uploaded',
        'Processing',
        'Processed',
        'Failed'
    ) DEFAULT 'Uploaded',

    CONSTRAINT fk_prescription_files_prescriptions
        FOREIGN KEY (prescription_id)
        REFERENCES prescriptions(prescription_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE

) ENGINE=InnoDB;

-- Verify table structure
DESCRIBE prescription_files;

-- Verify foreign key relationship
SHOW CREATE TABLE prescription_files;
