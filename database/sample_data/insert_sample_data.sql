
-- ============================================
-- Doctor Prescription Reminder System
-- Insert Sample Data
-- ============================================

USE doctor_reminder_db;

-- 1. Insert sample Doctor user
INSERT INTO users (name, email, password_hash, role_id)
SELECT
    'Dr. Arun Kumar',
    'arun.doctor@example.com',
    'DEMO_HASH_NOT_FOR_LOGIN',
    role_id
FROM roles
WHERE role_name = 'Doctor'
AND NOT EXISTS (
    SELECT 1 FROM users
    WHERE email = 'arun.doctor@example.com'
);

-- 2. Insert sample Patient user
INSERT INTO users (name, email, password_hash, role_id)
SELECT
    'Priya Sharma',
    'priya.patient@example.com',
    'DEMO_HASH_NOT_FOR_LOGIN',
    role_id
FROM roles
WHERE role_name = 'Patient'
AND NOT EXISTS (
    SELECT 1 FROM users
    WHERE email = 'priya.patient@example.com'
);

-- 3. Insert Patient profile
INSERT INTO patients (
    user_id,
    date_of_birth,
    phone,
    preferred_language,
    address
)
SELECT
    user_id,
    '2003-05-15',
    '9876543210',
    'English',
    'Chennai, Tamil Nadu'
FROM users
WHERE email = 'priya.patient@example.com'
AND NOT EXISTS (
    SELECT 1 FROM patients
    WHERE user_id = users.user_id
);

-- 4. Insert Doctor profile
INSERT INTO doctors (
    user_id,
    specialization,
    qualification,
    license_number
)
SELECT
    user_id,
    'General Medicine',
    'MBBS',
    'TN-MED-2026-001'
FROM users
WHERE email = 'arun.doctor@example.com'
AND NOT EXISTS (
    SELECT 1 FROM doctors
    WHERE user_id = users.user_id
);

-- 5. Insert sample Prescription
INSERT INTO prescriptions (
    patient_id,
    doctor_id,
    medicine_name,
    dosage,
    frequency,
    duration,
    instructions,
    prescription_date
)
SELECT
    p.patient_id,
    d.doctor_id,
    'Paracetamol',
    '500 mg',
    'Twice a day',
    '5 days',
    'Take after food',
    '2026-11-09'
FROM patients p
JOIN users pu ON p.user_id = pu.user_id
JOIN doctors d ON d.user_id = (
    SELECT user_id
    FROM users
    WHERE email = 'arun.doctor@example.com'
)
WHERE pu.email = 'priya.patient@example.com'
AND NOT EXISTS (
    SELECT 1
    FROM prescriptions pr
    WHERE pr.patient_id = p.patient_id
      AND pr.doctor_id = d.doctor_id
      AND pr.medicine_name = 'Paracetamol'
      AND pr.prescription_date = '2026-11-09'
);

-- 6. Verify inserted records
SELECT * FROM users;
SELECT * FROM patients;
SELECT * FROM doctors;
SELECT * FROM prescriptions;
