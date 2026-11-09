
-- =====================================================
-- Project: Doctor Prescription Reminder
-- Member 3: Database Development
-- File: 04_create_doctors.sql
-- Purpose: Store doctor profile information
-- =====================================================

USE doctor_reminder_db;

-- Create Doctors table
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(100),
    license_number VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_doctors_users
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Display doctor table structure
DESCRIBE doctors;
