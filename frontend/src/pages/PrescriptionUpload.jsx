
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  HeartPulse,
  ArrowLeft,
  Upload,
  FileText,
  UserRound,
  CalendarDays,
  LogOut
} from 'lucide-react'

function PrescriptionUpload() {
  const navigate = useNavigate()

  const [patients, setPatients] = useState([])
  const [patientId, setPatientId] = useState('')
  const [prescriptionDate, setPrescriptionDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const token = localStorage.getItem('access_token')

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await fetch('http://localhost:8000/patients', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error('Patients load aagalilla')
        }

        const data = await response.json()
        setPatients(data)
      } catch (error) {
        setMessage(error.message)
      }
    }

    if (token) fetchPatients()
    else setMessage('Please login using backend authentication.')
  }, [token])

  const handleUpload = async (e) => {
    e.preventDefault()
    setMessage('')

    if (!patientId || !file) {
      setMessage('Patient mattu prescription file select maadi.')
      return
    }

    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'application/pdf'
    ]

    if (!allowedTypes.includes(file.type)) {
      setMessage('JPG, PNG athava PDF file maatra upload maadi.')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setMessage('File size 5 MB ginta kammi irbeku.')
      return
    }

    const formData = new FormData()
    formData.append('patient_id', patientId)
    formData.append('prescription_date', prescriptionDate)
    formData.append('file', file)

    try {
      setLoading(true)

      const response = await fetch(
        'http://localhost:8000/prescriptions/upload',
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed')
      }

      setMessage(`OCR Status: ${data.ocr_status}. ${data.message}`)
      setFile(null)
      setPatientId('')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.clear()
    navigate('/')
  }

  return (
    <div className="upload-page">
      <header className="upload-header">
        <h2><HeartPulse /> MediCare</h2>
        <button onClick={handleLogout}>
          <LogOut size={18} /> Logout
        </button>
      </header>

      <main className="upload-container">
        <button className="back-button" onClick={() => navigate('/doctor-dashboard')}>
          <ArrowLeft size={18} /> Back to Dashboard
        </button>

        <section className="upload-card">
          <div className="upload-title">
            <FileText size={30} />
            <div>
              <h1>Upload Prescription</h1>
              <p>Upload patient prescription for OCR processing.</p>
            </div>
          </div>

          <form onSubmit={handleUpload}>
            <label><UserRound size={17} /> Select Patient</label>
            <select
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              required
            >
              <option value="">Choose a patient</option>
              {patients.map((patient) => (
                <option key={patient.patient_id} value={patient.patient_id}>
                  {patient.name} (ID: {patient.patient_id})
                </option>
              ))}
            </select>

            <label><CalendarDays size={17} /> Prescription Date</label>
            <input
              type="date"
              value={prescriptionDate}
              max={new Date().toISOString().split('T')[0]}
              onChange={(e) => setPrescriptionDate(e.target.value)}
              required
            />

            <label><Upload size={17} /> Prescription File</label>
            <div className="file-area">
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.pdf"
                onChange={(e) => setFile(e.target.files[0] || null)}
                required
              />
              <p>Supported: JPG, PNG, PDF | Maximum size: 5 MB</p>
              {file && <p>Selected: {file.name}</p>}
            </div>

            {message && <p className="upload-message">{message}</p>}

            <button className="upload-submit" type="submit" disabled={loading}>
              {loading ? 'Uploading...' : 'Upload Prescription'}
            </button>
          </form>
        </section>
      </main>
    </div>
  )
}

export default PrescriptionUpload
