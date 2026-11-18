USE doctor_reminder_db;

-- Translated instruction text + generated audio/video for each medicine and language
CREATE TABLE IF NOT EXISTS instruction_media (
    media_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_id INT NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    language_name VARCHAR(50) NOT NULL,
    source_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    translated BOOLEAN DEFAULT TRUE,
    audio_path VARCHAR(500),
    video_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'Completed',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_media_medicine_language UNIQUE (medicine_id, language_code),
    CONSTRAINT fk_media_prescription FOREIGN KEY (prescription_id)
        REFERENCES prescriptions(prescription_id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_media_medicine FOREIGN KEY (medicine_id)
        REFERENCES medicines(medicine_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;
