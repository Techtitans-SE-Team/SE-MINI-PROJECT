USE doctor_reminder_db;

-- One in-app notification per reminder per day
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    reminder_id INT NOT NULL,
    medicine_id INT NOT NULL,
    media_id INT NULL,
    message TEXT NOT NULL,
    notify_date DATE NOT NULL,
    reminder_time TIME NOT NULL,
    status VARCHAR(10) DEFAULT 'Unread',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_notification_reminder_day UNIQUE (reminder_id, notify_date),
    CONSTRAINT fk_notif_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_reminder FOREIGN KEY (reminder_id) REFERENCES medicine_reminders(reminder_id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_medicine FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_media FOREIGN KEY (media_id) REFERENCES instruction_media(media_id) ON DELETE SET NULL
) ENGINE=InnoDB;
