# SRS Requirements Baseline

## 1. Project overview

**Project:** Doctor Prescription to Multilingual Video Reminder and Instruction Generator  
**Project ID:** 41  
**Team:** TechTitans  
**Source:** `TechTitans_SE_SRS-P41_Phase-1.pdf`, dated 06/09/2026.

The SRS describes a system that processes doctor-provided prescriptions, extracts medicine and dosage details, allows doctor verification, and uses verified details to provide multilingual medication instructions, audio/video reminders, medication scheduling and tracking, and a prototype pharmacy delivery/refill integration. It is an assistance and reminder tool; it is not intended to diagnose conditions, prescribe medicines, or replace professional medical judgment.

This document records requirements stated in the SRS. Presence here does **not** mean a requirement is implemented or verified. Requirement descriptions in the tables are original SRS statements, transcribed with minor whitespace normalization. The “Derived acceptance criteria” column contains proposed observable checks inferred from those statements; these criteria are not written as acceptance criteria in the SRS.

## 2. Functional requirements

The SRS assigns `REQ-*` identifiers to the requirements below. The derived acceptance criteria are separate from the original descriptions.

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| REQ-PRES-01 | The system shall allow an authorized Doctor to create a prescription for a registered patient. | An authorized doctor can create a prescription for a registered patient; an unauthorized user cannot. | Prescription management |
| REQ-PRES-02 | The system shall validate mandatory prescription fields before saving. | A prescription missing a mandatory field is not saved; a valid prescription can be saved. | Prescription validation |
| REQ-PRES-03 | The system shall associate each prescription with exactly one patient and one prescribing doctor. | Every saved prescription is associated with exactly one patient and one prescribing doctor. | Prescription management / data model |
| REQ-PRES-04 | The system shall maintain a prescription status such as Pending Verification, Verified, or Rejected. | A prescription’s saved and returned status reflects its verification state, including the listed examples. | Prescription workflow |
| REQ-PROC-01 | The system shall extract medicine name, dosage, frequency, timing, and duration from an uploaded prescription image. | A readable uploaded prescription containing these details yields extracted fields for each specified item. | Upload / OCR |
| REQ-PROC-02 | The system shall present extracted information to the Doctor for review and correction before it is used further. | The doctor can view and correct extracted information before downstream use. | Prescription review |
| REQ-PROC-03 | The system shall not automatically finalize a prescription without Doctor verification. | An unverified prescription cannot enter the finalized state or be used as verified information. | Verification |
| REQ-PROC-04 | The system shall log OCR failures and allow manual entry as a fallback. | OCR failure is recorded, and manual prescription entry remains available. | OCR / prescription entry |
| REQ-TRANS-01 | The system shall translate verified medication instructions into the patient's selected supported language. | Verified instructions can be generated in the patient’s selected supported language. | Translation |
| REQ-TRANS-02 | The system shall restrict language selection to the set of languages supported by the translation and Text to Speech components. | Unsupported languages cannot be selected for instruction generation. | Language management |
| REQ-TRANS-03 | The system shall preserve medicine names, dosage values, and timing accurately during translation. | Comparison of source and translated output shows medicine names, dosage values, and timing preserved. | Translation safety |
| REQ-VID-01 | The system shall generate a short video containing translated medication instructions for each verified prescription. | A verified prescription can produce a short video containing its translated instructions. | Video generation |
| REQ-VID-02 | The system shall store the generated video and link it to the corresponding prescription and patient. | The stored video is associated with the correct prescription and patient. | Video storage |
| REQ-VID-03 | The system shall allow the patient to replay a previously generated video at any time. | The patient can retrieve and replay a previously generated video associated with them. | Patient video access |
| REQ-REM-01 | The system shall generate a dosage reminder schedule from the verified prescription information. | A valid verified prescription produces a reminder schedule derived from its dosage information. | Reminder scheduling |
| REQ-REM-02 | The system shall send a notification to the patient at each scheduled dosage time. | Each scheduled dosage time results in a notification to the associated patient. | Notifications |
| REQ-REM-03 | The system shall allow the patient to mark a dose as taken or missed. | A patient can record a dose as taken and as missed. | Medication tracking |
| REQ-REM-04 | The system shall maintain a record of sent reminders and their corresponding dosage status. | Reminder records and their corresponding dosage statuses remain retrievable. | Reminder / adherence records |

### Registration and login requirements

The SRS does not assign a functional requirement ID to registration or login and does not specify registration fields, password composition, account recovery, login response details, or registration validation rules. It identifies Doctor, Patient, and System Administrator as user classes and separately states authentication/security requirements in Section 6.3. No additional registration or login requirement is inferred here.

## 3. Non-functional requirements

### 3.1 Performance requirements (Section 6.1)

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| NFR-PERF-01 | The system shall load the user dashboard within 3 seconds under normal operating conditions. | Under documented normal conditions, measured dashboard load time is no more than 3 seconds. | Dashboard / UI |
| NFR-PERF-02 | The system shall save a valid prescription within 2 seconds after submission, excluding delays caused by external services. | Measured save time is no more than 2 seconds, excluding external-service delay. | Prescription management |
| NFR-PERF-03 | The system shall process a structured prescription and display the extracted medicine information within 5 seconds under normal operating conditions. | Under documented normal conditions, extracted medicine information is displayed within 5 seconds. | Prescription processing |
| NFR-PERF-04 | The system shall initiate multilingual instruction generation within 5 seconds after the user selects a supported language, excluding external service processing time. | Instruction generation is initiated within 5 seconds, excluding external-service processing time. | Translation |
| NFR-PERF-05 | The system shall schedule a valid medication reminder within 2 seconds after receiving all required reminder information. | A valid reminder is scheduled within 2 seconds after all required information is received. | Reminder scheduling |
| NFR-PERF-06 | The system shall display an appropriate processing or progress message when video generation requires additional processing time. | When generation needs additional processing time, a processing/progress message is displayed. | Video generation / UI |
| NFR-PERF-07 | The system shall prevent accidental duplicate reminders for the same patient, medicine, date, and time. | Repeated creation for the same patient, medicine, date, and time does not create an accidental duplicate. | Reminder scheduling |
| NFR-PERF-08 | The system shall remain responsive while long-running operations such as translation and video generation are being performed. | User-facing functions remain responsive while translation or video generation is running. | Application / background processing |

### 3.2 Safety requirements (Section 6.2)

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| NFR-SAFE-01 | The system shall not independently prescribe medicines or recommend changes to a doctor's prescription. | System-generated content does not independently prescribe medicines or recommend changing the doctor’s prescription. | Safety / instructions |
| NFR-SAFE-02 | The system shall preserve the medicine name, dosage, frequency, and duration specified in the doctor's prescription. | The stored and processed values for those fields match the doctor-provided values. | Prescription processing |
| NFR-SAFE-03 | The system shall identify and report missing or invalid mandatory prescription information before processing. | Missing or invalid mandatory information is reported before processing proceeds. | Validation |
| NFR-SAFE-04 | The system shall require verification of prescription information before generating final medication instructions. | Final medication instructions cannot be generated from an unverified prescription. | Verification / instruction generation |
| NFR-SAFE-05 | The system shall clearly indicate that generated instructions are based on the provided prescription and are not a substitute for professional medical advice. | The stated disclaimer is visible with generated instructions. | Patient instructions |
| NFR-SAFE-06 | The system shall not silently modify medication names, dosage, frequency, or duration during processing or translation. | Those values match the source unless an authorized correction is made; any issue is surfaced rather than silently changed. | Processing / translation |
| NFR-SAFE-07 | If the system detects incomplete or ambiguous prescription information, it shall request verification instead of generating potentially incorrect instructions. | Incomplete or ambiguous data blocks final instructions and requests verification. | Prescription review |
| NFR-SAFE-08 | The system shall allow an authorized user to correct prescription information before generating the final video reminder. | An authorized user can correct prescription details before final video generation. | Review / video generation |
| NFR-SAFE-09 | The system shall display appropriate error messages when prescription processing fails. | A failed processing operation displays an appropriate error message. | Processing / error handling |
| NFR-SAFE-10 | The system shall not generate a medication reminder when required prescription or scheduling information is invalid. | Invalid required prescription or scheduling information prevents reminder generation. | Reminder safety |

### 3.3 Security requirements (Section 6.3)

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| NFR-SEC-01 | The system shall require authentication before allowing users to access protected functionality. | An unauthenticated request to protected functionality is denied. | Authentication |
| NFR-SEC-02 | The system shall implement role-based access control for Doctor, Patient, and Administrator users. | Each of the three roles is limited to its permitted functions. | Authorization / RBAC |
| NFR-SEC-03 | The system shall restrict doctors to authorized patient and prescription records. | A doctor’s request for an unauthorized patient or prescription record is denied. | Doctor authorization |
| NFR-SEC-04 | Patients shall only be permitted to access their own prescription, generated instructions, and reminder information. | A patient cannot retrieve another patient’s prescription, instruction, or reminder information. | Patient authorization / privacy |
| NFR-SEC-05 | User passwords shall not be stored in plain text. | Persisted account records contain no plaintext password. | Credential storage |
| NFR-SEC-06 | The deployed system shall use HTTPS for communication between the client and server. | Deployed client/server communications use HTTPS. | Communications / deployment |
| NFR-SEC-07 | The system shall validate and sanitize user inputs to reduce security risks caused by malicious or invalid input. | Invalid or malicious input is rejected or handled safely without unintended effects. | Input validation |
| NFR-SEC-08 | The system shall prevent unauthorized users from accessing prescription records through manipulated requests. | Changing identifiers or request parameters does not expose unauthorized prescription records. | Access control |
| NFR-SEC-09 | The system shall implement session management to prevent unauthorized access through expired or inactive sessions. | Expired or inactive sessions cannot access protected functions. | Session management |
| NFR-SEC-10 | The system shall maintain audit records for important operations such as prescription creation, modification, and deletion. | Audit records are available for important operations, including the examples listed. | Audit logging |
| NFR-SEC-11 | Sensitive patient and prescription information shall be protected against unauthorized access during storage and transmission. | Evidence demonstrates protections for sensitive data at rest and in transit. | Data protection |
| NFR-SEC-12 | Access to administrative functions shall be restricted to authenticated administrators. | Non-administrators and unauthenticated users are denied administrative access. | Administrator authorization |

### 3.4 Software quality requirements (Section 6.4)

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| NFR-QUAL-01 | The system shall provide a simple and consistent user interface for doctors and patients. | Review of doctor and patient screens confirms consistent controls and layout. | User interface |
| NFR-QUAL-02 | The system shall provide clear and meaningful error messages for invalid or incomplete inputs. | Invalid or incomplete input produces an understandable error message. | Validation / UI |
| NFR-QUAL-03 | The major functions of the system shall be understandable to users without requiring specialized technical knowledge. | Representative users can understand major functions without specialized technical knowledge. | Usability |
| NFR-QUAL-04 | The system shall provide clear navigation between prescription, instruction, video, and reminder functionalities. | Users can navigate between the named functions using clear navigation. | Navigation / UI |
| NFR-QUAL-05 | The system shall preserve successfully stored prescription information during normal application failures. | A successfully stored prescription remains available after a normal application failure. | Persistence / reliability |
| NFR-QUAL-06 | The system shall handle unavailable translation, text-to-speech, video-generation, or notification services gracefully. | Unavailable external services produce a handled outcome and appropriate system/user response. | External service integration |
| NFR-QUAL-07 | The system shall display an appropriate failure message when an operation is unsuccessful instead of displaying a false success message. | Failed operations are reported as failures, not as successes. | Error handling |
| NFR-QUAL-08 | The system shall use modular components so that prescription processing, translation, video generation, and reminder management can be modified independently. | The named components can be modified independently without changing unrelated components. | Architecture / maintainability |
| NFR-QUAL-09 | The source code shall follow agreed coding standards and include appropriate documentation. | Review confirms adherence to the agreed standards and the presence of appropriate documentation. | Development process |
| NFR-QUAL-10 | Changes to one major module should have minimal impact on other independent modules. | A change to a module does not require unnecessary changes to other independent modules. | Architecture / maintainability |
| NFR-QUAL-11 | Major system modules shall have testable interfaces for unit and integration testing. | Major modules can be exercised through interfaces suitable for unit and integration testing. | Testability |
| NFR-QUAL-12 | Functional and nonfunctional requirements shall be mapped to corresponding test cases through the Requirement Traceability Matrix. | Each functional and non-functional requirement has a corresponding RTM test-case reference. | Testability / traceability |
| NFR-QUAL-13 | The architecture shall allow additional Indian languages to be added without major modification to existing prescription-processing functionality. | A language can be added without major modification to prescription processing. | Internationalization / architecture |
| NFR-QUAL-14 | The reminder component shall support multiple medicines and multiple scheduled reminders for a patient. | One patient can be associated with multiple medicines and multiple scheduled reminders. | Reminder management |
| NFR-QUAL-15 | The application shall be deployable using Docker to provide a consistent execution environment. | The application can be deployed and started using Docker configuration. | Deployment / portability |
| NFR-QUAL-16 | The system shall be available to authorized users whenever the application services are operational. | Authorized users can access the system while its application services are operational. | Availability |
| NFR-QUAL-17 | Temporary failure of an external service shall not cause permanent loss of prescription information. | Prescription information remains available after a temporary external-service failure. | Reliability / data persistence |

## 4. Security and privacy requirements

This section groups requirements already listed in Section 3.3 and Section 5 of this baseline; the IDs and original descriptions are not new requirements.

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| NFR-SEC-01 | The system shall require authentication before allowing users to access protected functionality. | Unauthenticated protected requests are denied. | Authentication |
| NFR-SEC-02 | The system shall implement role-based access control for Doctor, Patient, and Administrator users. | Access follows role permissions. | Authorization |
| NFR-SEC-03 | The system shall restrict doctors to authorized patient and prescription records. | Unauthorized record requests are denied. | Doctor authorization |
| NFR-SEC-04 | Patients shall only be permitted to access their own prescription, generated instructions, and reminder information. | Cross-patient access is denied. | Patient authorization |
| NFR-SEC-05 | User passwords shall not be stored in plain text. | No plaintext password is persisted. | Credential storage |
| NFR-SEC-06 | The deployed system shall use HTTPS for communication between the client and server. | Deployed client/server communication uses HTTPS. | Communications |
| NFR-SEC-07 | The system shall validate and sanitize user inputs to reduce security risks caused by malicious or invalid input. | Invalid or malicious input is safely rejected or handled. | Input validation |
| NFR-SEC-08 | The system shall prevent unauthorized users from accessing prescription records through manipulated requests. | Manipulated requests cannot bypass access controls. | Access control |
| NFR-SEC-09 | The system shall implement session management to prevent unauthorized access through expired or inactive sessions. | Expired/inactive sessions are denied. | Session management |
| NFR-SEC-10 | The system shall maintain audit records for important operations such as prescription creation, modification, and deletion. | Important operations have audit records. | Audit logging |
| NFR-SEC-11 | Sensitive patient and prescription information shall be protected against unauthorized access during storage and transmission. | Controls protect sensitive data at rest and in transit. | Data protection |
| NFR-SEC-12 | Access to administrative functions shall be restricted to authenticated administrators. | Only authenticated administrators can access admin functions. | Admin authorization |
| OR-PRIV-01 | The system shall collect only information required to provide its intended functionality. | Collected information is limited to what intended functionality requires. | Privacy / data collection |
| OR-PRIV-02 | Patient and prescription information shall not be displayed to unauthorized users. | Unauthorized users cannot view patient/prescription information. | Access control |
| OR-PRIV-03 | The system shall implement access controls for stored patient information. | Stored patient data access is authorization-checked. | Data access |
| OR-PRIV-04 | Generated videos containing patient-specific information shall only be accessible to authorized users. | Unauthorized users cannot retrieve patient-specific videos. | Video privacy |
| OR-PRIV-05 | The system shall follow the project's defined data retention and deletion policy. | A project policy exists and the system follows it. | Data lifecycle |
| OR-PRIV-06 | Patient information shall not be unnecessarily shared with external services. | External calls do not include unnecessary patient information. | External integrations |
| OR-PRIV-07 | Data transmitted to external services, where required, shall be limited to the information necessary for the requested operation. | External-service payloads contain only operation-required data. | External integrations |

## 5. Accessibility requirements

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| OR-ACC-01 | The system shall use readable text and clearly identifiable interface controls. | Key screens have readable text and identifiable controls. | User interface |
| OR-ACC-02 | Important information shall not be communicated using colour alone. | Important states remain distinguishable without colour. | User interface |
| OR-ACC-03 | Video instructions should contain readable on-screen text along with audio where applicable. | Applicable videos include readable text with audio. | Video / accessibility |
| OR-ACC-04 | The system shall provide clear and understandable error messages. | Error conditions show understandable messages. | Error handling |
| OR-ACC-05 | The major web functions should support keyboard-based navigation where feasible. | Major functions support keyboard navigation where feasible. | Web accessibility |
| OR-ACC-06 | The system shall use simple and understandable language for patient-facing instructions. | Patient-facing instructions use simple, understandable language. | Patient instructions |

## 6. Other requirements: database and internationalization

### 6.1 Database requirements (Section 7.1)

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| OR-DB-01 | The system shall maintain a unique identifier for each registered user. | No two registered users share the same user identifier. | Database / users |
| OR-DB-02 | Each prescription shall have a unique prescription identifier. | No two prescriptions share the same prescription identifier. | Database / prescriptions |
| OR-DB-03 | Each prescription shall be associated with the corresponding patient and authorized doctor. | Each stored prescription references the corresponding patient and authorized doctor. | Database / prescriptions |
| OR-DB-04 | Each reminder shall be associated with the corresponding patient, prescription, medicine, and scheduled time. | Each reminder record has valid references to the specified patient, prescription, medicine, and time. | Database / reminders |
| OR-DB-05 | The database shall maintain appropriate relationships between users, patients, prescriptions, medicines, reminders, and generated videos. | The database represents and preserves the stated entity relationships. | Database / data model |
| OR-DB-06 | The system shall validate mandatory database fields before storing records. | A record missing a mandatory field is not stored. | Database validation |
| OR-DB-07 | The system shall prevent unauthorized modification or deletion of stored prescription information. | Unauthorized modification and deletion attempts are denied. | Data access control |
| OR-DB-08 | The system shall support backup and recovery procedures for important application data in the deployed environment. | A backup/recovery procedure exists and can restore important deployed data. | Operations / database |

### 6.2 Internationalization and multilingual requirements (Section 7.2)

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| OR-I18N-01 | The system shall support multiple Indian languages selected by the user. | Users can select from the supported Indian languages. | Internationalization |
| OR-I18N-02 | The selected language shall be applied consistently to generated medication instructions. | Generated instructions use the user’s selected supported language. | Translation |
| OR-I18N-03 | The system shall use Unicode-compatible data storage and processing for supported languages. | Supported-language text survives storage and processing without corruption. | Data / internationalization |
| OR-I18N-04 | The system shall allow additional supported languages to be added without redesigning the entire system. | An additional language can be added without redesigning the entire system. | Architecture / internationalization |
| OR-I18N-05 | If a requested language is unavailable, the system shall clearly notify the user and display the available language options. | The user is informed that the requested language is unavailable and sees available options. | Language selection |
| OR-I18N-06 | Translation shall preserve important medication information such as medicine name, dosage, frequency, and duration. | Translated output preserves those fields from the verified source. | Translation safety |
| OR-I18N-07 | Generated multilingual content shall be checked for missing or incorrectly translated information before final output. | A check identifies missing or incorrect content before final output. | Translation quality |

## 7. Legal and domain requirements

| Original ID | Original SRS requirement description | Derived acceptance criteria (not in SRS) | Related module |
|---|---|---|---|
| BR-01 | Only an authenticated and authorized doctor shall be permitted to create or modify a patient's prescription. | Unauthorized roles/doctors cannot create or modify the prescription. | Authorization |
| BR-02 | A patient shall only be permitted to view their own prescription and reminder information. | A patient cannot view another patient’s prescription or reminder. | Patient privacy |
| BR-03 | The system shall use the medication information supplied in the doctor's prescription as the source for generating instructions. | Generated instructions trace to the doctor-supplied medication information. | Instruction generation |
| BR-04 | The system shall not automatically modify a doctor's prescribed dosage. | Automated processing preserves the supplied dosage. | Prescription integrity |
| BR-05 | A reminder shall require valid medicine, frequency, and scheduling information. | Missing/invalid required information blocks reminder creation. | Reminder validation |
| BR-06 | Only languages supported by the system shall be available for instruction generation. | Unsupported languages are unavailable for generation. | Language selection |
| BR-07 | A generated video shall correspond to the selected patient, prescription, medicine, and language. | Video associations match those entities and language. | Video generation |
| BR-08 | Invalid or cancelled prescriptions shall not generate new medication reminders. | Invalid/cancelled prescriptions cannot produce new reminders. | Reminder management |
| BR-09 | If prescription information is incomplete or ambiguous, the system shall request verification before generating instructions. | Incomplete/ambiguous data blocks instructions pending verification. | Verification |
| BR-10 | The system shall maintain records of important prescription and reminder activities for accountability and troubleshooting. | Important activities have retrievable records. | Audit logging |
| BR-11 | The system shall treat the doctor's prescription as the authoritative source of medication information. | Downstream medication information derives from the doctor’s prescription. | Prescription integrity |
| BR-12 | The system shall not provide medical diagnosis or independently recommend medication. | System output does not diagnose or independently recommend medication. | Safety / domain rules |
| OR-LEGAL-01 | The system shall clearly communicate that it does not independently diagnose medical conditions or prescribe medicines. | This limitation is clearly communicated to users. | Safety / user communication |
| OR-LEGAL-02 | The system shall preserve the original prescription information provided by an authorized user. | Stored/processed source information matches the authorized input. | Prescription integrity |
| OR-LEGAL-03 | Patient information shall be handled according to applicable privacy and data-protection requirements. | Applicable requirements are identified and handling is documented against them. | Privacy / governance |
| OR-LEGAL-04 | Third-party translation, text-to-speech, notification, and video-generation services shall be used according to their applicable terms and data-handling policies. | Applicable service terms and data-handling policies are reviewed and followed. | External integrations |
| OR-LEGAL-05 | The system shall not claim medical certification unless the required certification has actually been obtained. | No unsupported medical certification claim appears. | Product communication |
| OR-LEGAL-06 | The project team shall consider applicable healthcare, privacy, accessibility, and software regulations before deployment beyond the academic prototype. | A pre-deployment review records consideration of these regulation areas. | Deployment / governance |

## 8. Use cases UC-01 to UC-08

These are **use case identifiers, not functional requirement identifiers**. The SRS use case text is summarized below; no `REQ-*` IDs are assigned to these use cases.

| Use case ID | Name / actor | SRS flow, outcome, and exception behaviour | Derived acceptance criteria (not in SRS) |
|---|---|---|---|
| UC-01 | Upload Prescription — Doctor | Precondition: Doctor is logged in and selected a registered patient. Doctor uploads an image or enters prescription details manually; system stores and processes it. Postcondition: a new prescription is Pending Verification. If unreadable or upload fails, system displays an error and asks the Doctor to retry. | With a logged-in Doctor and registered patient, submission creates a Pending Verification prescription; unreadable input/upload failure shows an error and retry prompt. |
| UC-02 | Verify Extracted Information — Doctor | Precondition: prescription is processed and medicine/dosage information extracted. Doctor reviews and corrects medicine, dosage, frequency, and timing, then confirms. Postcondition: status becomes Verified and it is available for translation/reminder generation. Missing/invalid required fields prevent confirmation and are highlighted. | Correctable fields are shown to the Doctor; valid information can be verified; missing/invalid fields block confirmation and are identified. |
| UC-03 | Select Language — Patient | Precondition: Patient is registered and logged in. Patient selects a preferred supported Indian language; system saves it for future translation/video generation. Unsupported language results in a message and available-language list. | Supported selection is saved; unsupported selection is reported with available choices. |
| UC-04 | Generate Reminder Video — System (after verification) | Precondition: prescription verified and patient language known. System translates instructions, generates audio with TTS, then generates a short video. Video is stored and made available to patient. If translation/TTS/video fails, system logs error and retries or notifies administrator. | A verified prescription and known language lead to a linked stored video; service failure is logged and triggers retry or administrator notification. |
| UC-05 | Schedule Reminder — Patient (system action) | Precondition: verified prescription with dosage/timing exists. System reads schedule, creates entries for each scheduled dose, and sends notifications at scheduled times. Schedule conflict is flagged for review. | Valid schedule creates reminder entries and queues notifications; a conflict is flagged. |
| UC-06 | Track Medication — Patient | Precondition: at least one reminder has been sent. Patient marks a dose taken or missed; system updates adherence record. If no response, dose is marked missed after scheduled window closes. | Patient updates the dose status and record changes; no response through the scheduled window results in missed status. |
| UC-07 | Manage Users — System Administrator | Precondition: Administrator is logged in with administrative privileges. Administrator searches/adds a user and updates role/access/status; system saves changes. Missing required fields cause rejection and validation message. | Authorized administrator can save valid changes; missing required fields are rejected with validation feedback. |
| UC-08 | Request Pharmacy Delivery — Patient | Precondition: verified prescription exists and patient wants medicine delivery/refill. System forwards request to pharmacy service/mock integration and displays confirmation status. Request record status may be Requested, Confirmed, or Failed. If service unavailable, request is stored Pending and patient notified. | Eligible request is forwarded and status displayed/stored; service unavailability stores Pending and notifies patient. |

## 9. Requirements without explicit acceptance criteria

The SRS states requirements but does not provide a formal acceptance-criteria section. All acceptance criteria in this baseline are derived checks, not source text. In particular:

- Registration and login flows have no functional requirement IDs or field-level acceptance criteria in the SRS.
- Qualitative terms such as “simple,” “appropriate,” “gracefully,” and “minimal impact” have no defined measurement method or threshold.
- OR-PRIV-05 refers to a project-defined retention/deletion policy, but the SRS does not state the retention period or deletion rules.
- Security and privacy requirements do not define detailed implementation mechanisms or verification procedures.
- Performance requirements state time limits but do not define hardware, load, dataset size, or a full test profile for “normal operating conditions.”
- Requirements dependent on external OCR, translation, text-to-speech, video, notifications, and pharmacy services do not specify provider-level acceptance measures.

## 10. SRS extraction limitations

- The source PDF has 26 pages. Text was extracted from all pages using macOS PDFKit.
- The extracted text is readable overall, but table-column order and some continuation headings are flattened, particularly on page 12 and the Appendix B/C pages (24–26). The source PDF visual layout should be consulted if exact table placement is material.
- Page 8 contains a stray extracted character and a split dependency-table layout; the dependency meanings remain readable in context.
- No requirement text was intentionally added from repository implementation or other documents. Where the SRS did not state a requirement ID or acceptance criterion, this baseline says so explicitly.
- This is a requirements baseline only. It makes no claim that any requirement is implemented, tested, or satisfied.
