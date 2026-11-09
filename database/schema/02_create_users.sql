
-- =====================================================
-- Project: Doctor Prescription to Multilingual Video
-- Reminder and Instruction Generator
-- Member 3: Database Development
-- File: 02_create_users.sql
-- Purpose: Create Roles and Users tables
-- =====================================================

USE doctor_reminder_db;

-- Step 1: Create Roles table
CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Step 2: Insert default roles
INSERT IGNORE INTO roles (role_name)
VALUES
    ('Doctor'),
    ('Patient'),
    ('Admin');

-- Step 3: Create Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_roles
        FOREIGN KEY (role_id)
        REFERENCES roles(role_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Step 4: Display table structure
DESCRIBE roles;
DESCRIBE users;

-- Step 5: Display available roles
SELECT * FROM roles;
