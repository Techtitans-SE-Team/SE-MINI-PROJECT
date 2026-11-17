
import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8000'

function PrescriptionReview() {
  const [patients, setPatients] = useState([])
  const [patientId, setPatientId] = useState('')
  const [prescriptionDate, setPrescriptionDate] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)

  const [prescription, setPrescription] = useState(null)
  const [medicines, setMedicines] = useState([])

  const [newMedicine, setNewMedicine] = useState({
    medicine_name: '',
    dosage: '',
    frequency: '',
    duration: '',
    instructions: ''
  })

  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const getHeaders = () => {
    const token = localStorage.getItem('access_token')

    return token
      ? { Authorization: `Bearer ${token}` }
      : {}
  }

  const apiRequest = async (url, options = {}) => {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        ...getHeaders(),
        ...options.headers
      }
    })

    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Request failed')
    }

    return data
  }

  // Load active patients
  useEffect(() => {
    const loadPatients = async () => {
      try {
        const data = await apiRequest('/patients')
        setPatients(data)
      } catch (err) {
        setError(err.message)
      }
    }

    loadPatients()
  }, [])

  // Upload prescription
  const handleUpload = async (e) => {
    e.preventDefault()

    setError('')
    setMessage('')

    if (!patientId || !selectedFile) {
      setError('Please select a patient and prescription file.')
      return
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5 MB.')
      return
    }

    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('patient_id', patientId)
      formData.append('file', selectedFile)

      if (prescriptionDate) {
        formData.append('prescription_date', prescriptionDate)
      }

      const data = await apiRequest('/prescriptions/upload', {
        method: 'POST',
        body: formData
      })

      setPrescription(data)
      setMedicines(data.medicines || [])
      setMessage(data.message || 'Prescription uploaded successfully.')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Update medicine fields
  const handleMedicineChange = (index, field, value) => {
    setMedicines((previous) =>
      previous.map((medicine, i) =>
        i === index
          ? { ...medicine, [field]: value }
          : medicine
      )
    )
  }

  // Handle new medicine form
  const handleNewMedicineChange = (field, value) => {
    setNewMedicine((previous) => ({
      ...previous,
      [field]: value
    }))
  }

  // Add medicine manually
  const handleAddMedicine = async (e) => {
    e.preventDefault()

    if (!prescription?.prescription_id) return

    if (!newMedicine.medicine_name.trim()) {
      setError('Please enter medicine name.')
      return
    }

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const data = await apiRequest(
        `/prescriptions/${prescription.prescription_id}/medicines`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newMedicine)
        }
      )

      setMedicines((previous) => [...previous, data])

      setNewMedicine({
        medicine_name: '',
        dosage: '',
        frequency: '',
        duration: '',
        instructions: ''
      })

      setMessage('Medicine added successfully.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  // Save edited medicine
  const saveMedicine = async (medicine) => {
    if (!prescription?.prescription_id) return

    setSaving(true)
    setError('')
    setMessage('')

    try {
      const updated = await apiRequest(
        `/prescriptions/${prescription.prescription_id}/medicines/${medicine.medicine_id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            medicine_name: medicine.medicine_name,
            dosage: medicine.dosage,
            frequency: medicine.frequency,
            duration: medicine.duration,
            instructions: medicine.instructions
          })
        }
      )

      setMedicines((previous) =>
        previous.map((item) =>
          item.medicine_id === updated.medicine_id ? updated : item
        )
      )

      setMessage('Medicine details updated successfully.')
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  // Reprocess prescription using OCR
  const handleReprocess = async () => {
    if (!prescription?.prescription_id) return

    setLoading(true)
    setError('')
    setMessage('')

    try {
      const data = await apiRequest(
        `/prescriptions/${prescription.prescription_id}/reprocess`,
        { method: 'POST' }
      )

      setPrescription(data)
      setMedicines(data.medicines || [])
      setMessage(data.message || 'Prescription reprocessed.')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Verify or reject prescription
  const handleDecision = async (action) => {
    if (!prescription?.prescription_id) return

    const confirmation = window.confirm(
      `Are you sure you want to ${action} this prescription?`
    )

    if (!confirmation) return

    setLoading(true)
    setError('')
    setMessage('')

    try {
      const data = await apiRequest(
        `/prescriptions/${prescription.prescription_id}/verify`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ action })
        }
      )

      setPrescription(data)
      setMedicines(data.medicines || medicines)

      setMessage(
        action === 'verify'
          ? 'Prescription verified successfully.'
          : 'Prescription rejected.'
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <h1>Prescription Review</h1>

      <p style={styles.subtitle}>
        Upload prescriptions, review OCR results and verify medicine details.
      </p>

      {error && <div style={styles.error}>{error}</div>}
      {message && <div style={styles.success}>{message}</div>}

      {/* Upload Section */}
      <section style={styles.card}>
        <h2>Upload Prescription</h2>

        <form onSubmit={handleUpload}>
          <label style={styles.label}>Select Patient</label>

          <select
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            style={styles.input}
            required
          >
            <option value="">Choose a patient</option>

            {patients.map((patient) => (
              <option
                key={patient.patient_id}
                value={patient.patient_id}
              >
                {patient.name} ({patient.patient_id})
              </option>
            ))}
          </select>

          <label style={styles.label}>Prescription Date</label>

          <input
            type="date"
            value={prescriptionDate}
            onChange={(e) => setPrescriptionDate(e.target.value)}
            style={styles.input}
          />

          <label style={styles.label}>Prescription File</label>

          <input
            type="file"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={(e) => setSelectedFile(e.target.files[0])}
            style={styles.input}
            required
          />

          <p style={styles.hint}>
            Accepted formats: JPG, JPEG, PNG, PDF. Maximum size: 5 MB.
          </p>

          <button
            type="submit"
            disabled={loading}
            style={styles.primaryButton}
          >
            {loading ? 'Uploading...' : 'Upload & Extract Medicines'}
          </button>
        </form>
      </section>

      {/* OCR Result Section */}
      {prescription && (
        <section style={styles.card}>
          <h2>OCR Review</h2>

          <p>
            <strong>Prescription ID:</strong>{' '}
            {prescription.prescription_id}
          </p>

          <p>
            <strong>OCR Status:</strong>{' '}
            {prescription.ocr_status || 'Not available'}
          </p>

          <p>
            <strong>Message:</strong>{' '}
            {prescription.message || 'No message'}
          </p>

          <button
            type="button"
            onClick={handleReprocess}
            disabled={loading}
            style={styles.secondaryButton}
          >
            Reprocess OCR
          </button>

          <h3>Extracted Medicines</h3>

          {medicines.length === 0 ? (
            <p>No medicines found. You can enter them manually below.</p>
          ) : (
            medicines.map((medicine, index) => (
              <div
                key={medicine.medicine_id}
                style={styles.medicineCard}
              >
                <h3>Medicine {index + 1}</h3>

                <label style={styles.label}>Medicine Name</label>
                <input
                  value={medicine.medicine_name || ''}
                  onChange={(e) =>
                    handleMedicineChange(
                      index,
                      'medicine_name',
                      e.target.value
                    )
                  }
                  style={styles.input}
                />

                <label style={styles.label}>Dosage</label>
                <input
                  value={medicine.dosage || ''}
                  onChange={(e) =>
                    handleMedicineChange(index, 'dosage', e.target.value)
                  }
                  style={styles.input}
                />

                <label style={styles.label}>Frequency</label>
                <input
                  value={medicine.frequency || ''}
                  onChange={(e) =>
                    handleMedicineChange(index, 'frequency', e.target.value)
                  }
                  style={styles.input}
                />

                <label style={styles.label}>Duration</label>
                <input
                  value={medicine.duration || ''}
                  onChange={(e) =>
                    handleMedicineChange(index, 'duration', e.target.value)
                  }
                  style={styles.input}
                />

                <label style={styles.label}>Instructions</label>
                <textarea
                  value={medicine.instructions || ''}
                  onChange={(e) =>
                    handleMedicineChange(
                      index,
                      'instructions',
                      e.target.value
                    )
                  }
                  style={styles.input}
                />

                <button
                  type="button"
                  onClick={() => saveMedicine(medicine)}
                  disabled={saving}
                  style={styles.secondaryButton}
                >
                  {saving ? 'Saving...' : 'Save Medicine'}
                </button>
              </div>
            ))
          )}

          {/* Manual Medicine Entry */}
          <div style={styles.medicineCard}>
            <h3>Enter Medicines Manually</h3>

            <form onSubmit={handleAddMedicine}>
              <label style={styles.label}>Medicine Name *</label>
              <input
                type="text"
                placeholder="Enter medicine name"
                value={newMedicine.medicine_name}
                onChange={(e) =>
                  handleNewMedicineChange('medicine_name', e.target.value)
                }
                style={styles.input}
                required
              />

              <label style={styles.label}>Dosage</label>
              <input
                type="text"
                placeholder="Example: 500 mg"
                value={newMedicine.dosage}
                onChange={(e) =>
                  handleNewMedicineChange('dosage', e.target.value)
                }
                style={styles.input}
              />

              <label style={styles.label}>Frequency</label>
              <input
                type="text"
                placeholder="Example: Twice a day"
                value={newMedicine.frequency}
                onChange={(e) =>
                  handleNewMedicineChange('frequency', e.target.value)
                }
                style={styles.input}
              />

              <label style={styles.label}>Duration</label>
              <input
                type="text"
                placeholder="Example: 5 days"
                value={newMedicine.duration}
                onChange={(e) =>
                  handleNewMedicineChange('duration', e.target.value)
                }
                style={styles.input}
              />

              <label style={styles.label}>Instructions</label>
              <textarea
                placeholder="Example: After food"
                value={newMedicine.instructions}
                onChange={(e) =>
                  handleNewMedicineChange('instructions', e.target.value)
                }
                style={styles.input}
              />

              <button
                type="submit"
                disabled={saving}
                style={styles.primaryButton}
              >
                {saving ? 'Adding...' : 'Add Medicine'}
              </button>
            </form>
          </div>

          {/* Verify / Reject */}
          <div style={styles.actions}>
            <button
              type="button"
              onClick={() => handleDecision('verify')}
              disabled={loading || medicines.length === 0}
              style={styles.verifyButton}
            >
              Verify Prescription
            </button>

            <button
              type="button"
              onClick={() => handleDecision('reject')}
              disabled={loading}
              style={styles.rejectButton}
            >
              Reject Prescription
            </button>
          </div>
        </section>
      )}
    </div>
  )
}

const styles = {
  page: {
    padding: '30px',
    maxWidth: '1000px',
    margin: '0 auto',
    color: '#1f2937'
  },
  subtitle: {
    color: '#64748b',
    marginBottom: '25px'
  },
  card: {
    background: '#ffffff',
    padding: '25px',
    borderRadius: '12px',
    marginBottom: '25px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.08)'
  },
  label: {
    display: 'block',
    marginTop: '15px',
    marginBottom: '7px',
    fontWeight: '600'
  },
  input: {
    width: '100%',
    padding: '11px',
    border: '1px solid #cbd5e1',
    borderRadius: '7px',
    boxSizing: 'border-box',
    fontSize: '14px'
  },
  hint: {
    color: '#64748b',
    fontSize: '13px'
  },
  primaryButton: {
    background: '#2563eb',
    color: 'white',
    padding: '12px 20px',
    border: 'none',
    borderRadius: '7px',
    marginTop: '15px',
    cursor: 'pointer'
  },
  secondaryButton: {
    background: '#475569',
    color: 'white',
    padding: '10px 16px',
    border: 'none',
    borderRadius: '7px',
    marginTop: '15px',
    cursor: 'pointer'
  },
  medicineCard: {
    border: '1px solid #e2e8f0',
    borderRadius: '9px',
    padding: '18px',
    marginTop: '15px'
  },
  actions: {
    display: 'flex',
    gap: '12px',
    marginTop: '25px',
    flexWrap: 'wrap'
  },
  verifyButton: {
    background: '#16a34a',
    color: 'white',
    padding: '12px 20px',
    border: 'none',
    borderRadius: '7px',
    cursor: 'pointer'
  },
  rejectButton: {
    background: '#dc2626',
    color: 'white',
    padding: '12px 20px',
    border: 'none',
    borderRadius: '7px',
    cursor: 'pointer'
  },
  error: {
    background: '#fee2e2',
    color: '#b91c1c',
    padding: '12px',
    borderRadius: '7px',
    marginBottom: '15px'
  },
  success: {
    background: '#dcfce7',
    color: '#166534',
    padding: '12px',
    borderRadius: '7px',
    marginBottom: '15px'
  }
}

export default PrescriptionReview
