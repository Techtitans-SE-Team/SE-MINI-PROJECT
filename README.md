# Doctor Prescription to Multilingual Video Reminder and Instruction Generator

## Project Overview

The Doctor Prescription to Multilingual Video Reminder and Instruction Generator is a software engineering mini project designed to help patients understand and follow their prescribed medications through digital prescription management, multilingual instructions, and video-based reminders.

The system aims to improve medication adherence by converting prescription information into understandable instructions and reminders.

## Project Objectives

- Digitize and manage doctor prescriptions.
- Extract medicine details from uploaded prescriptions.
- Generate multilingual medication instructions.
- Provide video-based medication guidance.
- Send reminders to patients according to their prescriptions.
- Improve patient understanding and medication adherence.
- Maintain secure and reliable patient and prescription information.

## Key Features

- User registration and authentication.
- Patient and doctor management.
- Prescription creation and management.
- Prescription file metadata management.
- Medicine information extraction support.
- Prescription processing and verification status tracking.
- Multilingual instruction generation.
- Video reminder generation.
- Medication reminders and notifications.
- Secure database management.

## System Workflow

1. The patient registers and logs into the system.
2. The doctor creates or uploads a prescription.
3. The system stores prescription information and uploaded file metadata.
4. Medicine details are extracted from the prescription.
5. Extracted medicine information is verified.
6. The system generates medication instructions in the selected language.
7. Video-based reminders are generated.
8. Patients receive reminders according to their medication schedules.

## Technologies Used

### Frontend
- HTML
- CSS
- JavaScript
- React (planned/integration as applicable)

### Backend
- Python
- FastAPI

### Database
- MySQL

### Development Tools
- Visual Studio Code
- Git and GitHub
- MySQL Shell
- Postman

### Future Integration
- OCR for prescription text extraction.
- Natural Language Processing for instruction generation.
- Text-to-Speech for multilingual audio.
- Video generation for medication guidance.
- Notification services for reminders.

## Repository Structure

```text
SE-MINI-PROJECT/
│
├── frontend/
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
│
├── backend/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   └── services/
│
├── database/
│   ├── schema/
│   │   ├── 01_create_roles.sql
│   │   ├── 02_create_users.sql
│   │   ├── 03_create_patients.sql
│   │   ├── 04_create_doctors.sql
│   │   ├── 05_create_prescriptions.sql
│   │   ├── 06_update_prescriptions.sql
│   │   ├── 07_create_medicines.sql
│   │   └── 08_create_prescription_files.sql
│   │
│   ├── sample_data/
│   │   └── sprint2_sample_data.sql
│   │
│   ├── queries/
│   │   ├── sprint2_prescription_queries.sql
│   │   └── sprint2_database_validation.sql
│   │
│   └── README.md
│
├── documentation/
│   ├── ER_DIAGRAM/
│   │   └── er_diagram.md
│   ├── sprint1/
│   └── sprint2/
│       └── database_testing_report.md
│
├── .gitignore
└── README.md
```

Note: The repository structure may be extended as frontend and backend modules are implemented.

## Database Implementation

The database is implemented using MySQL and is named `doctor_reminder_db`.

The database currently contains seven tables:

| Table | Purpose |
|---|---|
| `roles` | Stores user roles. |
| `users` | Stores user account information. |
| `patients` | Stores patient details. |
| `doctors` | Stores doctor details. |
| `prescriptions` | Stores prescription information and processing status. |
| `medicines` | Stores medicine details associated with prescriptions. |
| `prescription_files` | Stores uploaded prescription file metadata. |

### Sprint 1 – Database Foundation

- Created the initial database schema.
- Implemented roles and users tables.
- Implemented patient and doctor tables.
- Created the prescriptions table.
- Established primary key and foreign key relationships.

### Sprint 2 – Prescription Management

- Added prescription processing status tracking.
- Created the medicines table.
- Created the prescription_files table.
- Added sample prescription and medicine data.
- Implemented prescription retrieval and update queries.
- Added database validation queries.
- Updated the Entity Relationship Diagram.
- Prepared a database testing report.

### Database Status

The database schema, relationships, sample data, and validation queries have been implemented and tested.

Actual prescription file uploading, OCR-based medicine extraction, and automated processing require integration with the backend application.

## Database Documentation

The following documentation is available in the repository:

- [Database Setup and Documentation](database/README.md)
- [Entity Relationship Diagram](documentation/ER_DIAGRAM/er_diagram.md)
- [Sprint 1 Database Design](documentation/sprint1/database_design.md)
- [Sprint 2 Database Testing Report](documentation/sprint2/database_testing_report.md)

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- MySQL Server
- Git
- Visual Studio Code

### 1. Clone the Repository

```bash
git clone https://github.com/Techtitans-SE-Team/SE-MINI-PROJECT.git
```

### 2. Navigate to the Project Directory

```bash
cd SE-MINI-PROJECT
```

### 3. Configure the Database

Create the database in MySQL:

```sql
CREATE DATABASE doctor_reminder_db;
```

Execute the SQL schema files in the correct order from the `database/schema/` directory.

Refer to `database/README.md` for the complete database setup instructions.

### 4. Configure Environment Variables

Create a `.env` file in the appropriate backend directory and configure the required database credentials.

Example:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=doctor_reminder_db
DB_PORT=3306
```

Do not commit actual passwords or sensitive credentials to GitHub.

### 5. Install Backend Dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

### 6. Run the Application

Follow the frontend and backend setup instructions as those modules become available.

## Testing

Database testing includes:

- Table creation verification.
- Primary key and foreign key validation.
- Prescription and medicine retrieval.
- Prescription file metadata retrieval.
- Processing and verification status updates.
- Sample data insertion.
- Join query validation.
- Database relationship testing.

Detailed results are documented in:

`documentation/sprint2/database_testing_report.md`

## Security and Quality Considerations

- Store passwords securely using password hashing.
- Validate user inputs.
- Use database constraints to maintain data integrity.
- Protect sensitive patient and prescription information.
- Keep database credentials in environment variables.
- Apply role-based access control.
- Verify extracted medicine details before using them to generate patient instructions.

## Team Responsibilities

| Team Member | Responsibility |
|---|---|
| Asha | Quality, Security & Traceability Lead |
| Chaya | Requirements Coordinator |
| Ananya Dharani AP | Requirements Analyst |
| Aarti Panchal | System / Requirements Designer |

## Project Status

### Completed

- [x] Sprint 1 database design and implementation.
- [x] Roles, users, patients, and doctors tables.
- [x] Prescription table implementation.
- [x] Sprint 2 prescription processing status updates.
- [x] Medicines table implementation.
- [x] Prescription file metadata table implementation.
- [x] Sample data insertion.
- [x] Prescription retrieval and update queries.
- [x] Database validation and testing.
- [x] Updated Entity Relationship Diagram.
- [x] Sprint 2 database testing documentation.
- [x] Database README documentation.

### Pending / Future Integration

- [ ] Complete frontend implementation.
- [ ] Complete backend integration.
- [ ] Actual prescription file upload functionality.
- [ ] OCR-based medicine extraction.
- [ ] Medicine extraction verification workflow.
- [ ] Multilingual instruction generation.
- [ ] Video reminder generation.
- [ ] Medication reminder notifications.
- [ ] End-to-end system testing.

## Development Practices

- Follow a modular project structure.
- Use Git branches for individual development tasks.
- Commit changes with meaningful messages.
- Create pull requests for code review.
- Maintain documentation for every sprint.
- Test changes before merging them into the main branch.

## License

This project is developed for academic purposes as part of the Software Engineering Mini Project at PES University, Bangalore.

---

Developed by Team Tech Titans.
