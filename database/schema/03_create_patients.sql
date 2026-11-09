
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Member 3: Database Development
-- File: 03_create_patients.sql
-- Purpose: Store patient profile information
-- =====================================================

USE doctor_reminder_db;

CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    preferred_language VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    status ENUM('Active', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_patients_users
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Display patient table structure
DESCRIBE patients;
