# Doctor Prescription to Multilingual Video Reminder and Instruction Generator

**Project ID:** 41\
**Course:** Software Engineering -- JACKFRUIT Mini Project\
**Department:** Computer Science and Engineering, PES University,
Bangalore

## Project Overview

The **Doctor Prescription to Multilingual Video Reminder and Instruction
Generator** converts doctor prescriptions into easy-to-understand
multilingual medication reminders.

The system processes a prescription, extracts medicine name, dosage,
frequency, timing, and duration, and generates short video/audio
reminders for patients. It supports multiple Indian languages and
includes a prototype pharmacy delivery/refill integration.

## Objectives

-   Extract medicine and dosage information from prescriptions using
    OCR.
-   Allow authorized doctors to upload/enter and verify prescription
    information.
-   Provide medication instructions in supported Indian languages.
-   Generate short video and audio medication reminders.
-   Schedule dosage and timing alerts.
-   Track basic medication status such as taken, missed, or pending.
-   Provide a prototype pharmacy delivery/refill interface.
-   Protect patient and prescription information.

## Key Features

### Prescription Processing

-   Prescription upload/input
-   OCR-based text extraction
-   Medicine, dosage, frequency, timing, and duration extraction
-   Verification and correction of extracted information

### Multilingual Instructions

-   Patient language selection
-   Translation of medication instructions into supported Indian
    languages

### Video and Audio Reminders

-   Reminder script generation
-   Text-to-Speech audio generation
-   Short video/avatar-based reminder generation

### Reminder and Tracking

-   Scheduled medication alerts
-   Taken/missed/pending dose tracking
-   Reminder history

### Pharmacy Integration

-   Prototype medicine delivery/refill request interface
-   Mock integration when a real pharmacy API is unavailable

## Users

  -----------------------------------------------------------------------
  User                                Main Responsibilities
  ----------------------------------- -----------------------------------
  Doctor                              Create/upload prescriptions and
                                      verify extracted medication
                                      information

  Patient                             Select language, view instructions,
                                      receive reminders, and track
                                      medication

  System Administrator                Manage users, configuration,
                                      supported languages, and
                                      maintenance
  -----------------------------------------------------------------------

## High-Level Workflow

``` text
Doctor Prescription
        ↓
Upload / Input
        ↓
OCR & Information Extraction
        ↓
Medicine + Dosage + Timing
        ↓
Verification
        ↓
Language Selection
        ↓
Translation
        ↓
Reminder Script
        ↓
Text-to-Speech + Video Generation
        ↓
Scheduled Reminder
        ↓
Medication Tracking
        ↓
Pharmacy Delivery / Refill (Prototype)
```

## Technology and Tools

The final technology stack will be decided by the project team. The
project guidelines identify tools such as:

-   Git and GitHub -- version control
-   Jenkins -- CI/CD
-   Docker -- containerization
-   Pytest/JUnit/gTest or equivalent -- testing
-   SonarQube or equivalent -- static code analysis
-   Jira or similar -- agile planning and bug tracking

The implementation may also use an application backend, database, OCR
component, translation service/model, Text-to-Speech service,
video/avatar component, and notification/scheduling mechanism.

## Repository Structure

``` text
project-41/
├── frontend/
├── backend/
├── ocr/
├── translation/
├── video_generation/
├── reminders/
├── database/
├── tests/
├── docs/
│   ├── SRS/
│   ├── Architecture/
│   └── Design/
├── .github/
│   └── workflows/
├── README.md
└── requirements.txt
```

The exact structure can be changed according to the team's
implementation.

## Setup

### Prerequisites

Install the tools and runtimes required by the final implementation,
such as Git, the selected backend/frontend runtime, database, and Docker
if used.

### Clone

``` bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd <YOUR-REPOSITORY-NAME>
```

### Environment Variables

Store API keys, database credentials, and other secrets in environment
variables or GitHub Secrets.

Example:

``` text
OCR_API_KEY=your_key
TRANSLATION_API_KEY=your_key
TTS_API_KEY=your_key
DATABASE_URL=your_database_url
```

**Never commit API keys, passwords, tokens, or other secrets to
GitHub.**

## Testing

Testing should cover:

-   Prescription upload/input
-   OCR extraction
-   Medicine and dosage extraction
-   Prescription verification
-   Language selection and translation
-   Reminder script generation
-   Audio/video generation
-   Reminder scheduling
-   Medication tracking
-   Pharmacy/refill prototype
-   Authentication and authorization
-   Error handling

The team should maintain unit, integration, and system test
documentation.

## Software Engineering Practices

The project follows the JACKFRUIT Software Engineering requirements,
including:

-   Agile methodology
-   Git/GitHub version control
-   User stories and backlog
-   Pull requests and code reviews
-   Unit testing and code coverage
-   CI/CD pipeline
-   Static code analysis
-   Security validation
-   Requirements traceability
-   Architecture and design documentation

Every team member must contribute to implementation; Git commits are
used to demonstrate individual contribution.

## Security and Privacy

Patient and prescription information is sensitive. The system should:

-   Use authentication and role-based authorization.
-   Restrict access to patient and prescription records.
-   Validate user input.
-   Protect API keys and credentials.
-   Use secure communication in deployment.
-   Avoid exposing patient information in logs or the public repository.

## Important Limitation

This is an academic Software Engineering mini-project prototype. The
system assists patients in following **verified prescription
information** and does not independently diagnose conditions or
prescribe or change medicines. OCR and generated instructions should be
verified before final reminder generation.

## Documentation

The repository should contain project documentation such as:

-   Software Requirements Specification (SRS)
-   Project plan
-   Architecture specification
-   Software design specification
-   Use case/analysis models
-   Test plan and test reports
-   Requirement Traceability Matrix
-   Maintenance plan

## Team Members & Roles

| Team Member | Role / Assigned Functionality |
|---|---|
| **Asha** | **Quality, Security & Traceability Lead** — Non-functional requirements, security, quality, other requirements, glossary, field layouts, reports, and requirement traceability |
| **Chaya** | **Project Lead / Requirements Coordinator** — Overall requirements coordination, project documentation, and SRS contribution |
| **Ananya Dharani AP** | **Requirements Analyst** — Requirements analysis, product functions, overall description, assumptions/dependencies, and requirements documentation |
| **Aarti Panchal** | **System / Requirements Designer** — External interfaces, analysis/use-case models, system features, and functional requirements |

Every team member is responsible for contributing to implementation and maintaining evidence of individual contribution through Git commits and pull requests.

## Project Status

**Status:** Development / Prototype

-   [ ] Requirements and SRS
-   [ ] Architecture and design
-   [ ] Database design
-   [ ] UI development
-   [ ] OCR/prescription processing
-   [ ] Translation
-   [ ] Video/audio generation
-   [ ] Reminder scheduling
-   [ ] Medication tracking
-   [ ] Pharmacy integration prototype
-   [ ] Unit/integration/system testing
-   [ ] CI/CD
-   [ ] Final documentation
-   [ ] Final demonstration

## License

This project is developed as part of the Software Engineering JACKFRUIT
Mini Project at PES University.
