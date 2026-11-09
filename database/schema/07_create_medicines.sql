
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Sprint 2: Prescription Management
-- Member 3: Database Development
-- File: 07_create_medicines.sql
-- Purpose: Store extracted medicine details
-- =====================================================

USE doctor_reminder_db;

CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,

    prescription_id INT NOT NULL,

    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100) NOT NULL,
    instructions TEXT,

    extraction_status ENUM(
        'Extracted',
        'Needs Review',
        'Confirmed'
    ) DEFAULT 'Extracted',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_medicines_prescriptions
        FOREIGN KEY (prescription_id)
        REFERENCES prescriptions(prescription_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE

) ENGINE=InnoDB;

-- Verify the table structure
DESCRIBE medicines;

-- Verify the foreign key relationship
SHOW CREATE TABLE medicines;
