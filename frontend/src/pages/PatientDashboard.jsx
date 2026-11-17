
import { useState, useEffect } from 'react'

import {
  HeartPulse,
  LayoutDashboard,
  FileText,
  Pill,
  Bell,
  UserRound,
  LogOut,
  CalendarDays,
  Activity,
  Clock
} from 'lucide-react'

const API_BASE = 'http://localhost:8000'

function PatientDashboard() {
  const [activeSection, setActiveSection] = useState('dashboard')
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchPrescriptions()
  }, [])

  const fetchPrescriptions = async () => {
    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')

      const response = await fetch(`${API_BASE}/prescriptions`, {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(
          response.status === 401
            ? 'Session expired. Please login again.'
            : 'Unable to load prescriptions.'
        )
      }

      const data = await response.json()
      setPrescriptions(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('userRole')
    localStorage.removeItem('access_token')
    window.location.href = '/'
  }

  const medicines = prescriptions.flatMap((prescription) =>
    (prescription.medicines || []).map((medicine) => ({
      ...medicine,
      prescription_date: prescription.prescription_date,
      verification_status: prescription.verification_status
    }))
  )

  const renderPrescriptions = () => {
    if (loading) {
      return <p>Loading prescriptions...</p>
    }

    if (error) {
      return (
        <div className="patient-panel">
          <p>{error}</p>
          <button onClick={fetchPrescriptions}>Retry</button>
        </div>
      )
    }

    if (prescriptions.length === 0) {
      return (
        <div className="patient-panel">
          <p>No verified prescriptions available yet.</p>
        </div>
      )
    }

    return prescriptions.map((prescription) => (
      <div className="patient-panel" key={prescription.prescription_id}>
        <h3>
          <FileText /> Prescription #{prescription.prescription_id}
        </h3>

        <p>
          <strong>Doctor:</strong> {prescription.doctor_name || 'N/A'}
        </p>
        <p>
          <strong>Date:</strong> {prescription.prescription_date || 'N/A'}
        </p>
        <p>
          <strong>Status:</strong> {prescription.verification_status || 'N/A'}
        </p>

        <h4>Medicines</h4>

        {(prescription.medicines || []).length === 0 ? (
          <p>No medicine details available.</p>
        ) : (
          prescription.medicines.map((medicine) => (
            <div key={medicine.medicine_id}>
              <p><strong>{medicine.medicine_name}</strong></p>
              <p>Dosage: {medicine.dosage}</p>
              <p>Frequency: {medicine.frequency}</p>
              <p>Duration: {medicine.duration}</p>
              <p>Instructions: {medicine.instructions || 'N/A'}</p>
              <p>Medicine status: {medicine.extraction_status || 'N/A'}</p>
            </div>
          ))
        )}
      </div>
    ))
  }

  const renderMedicines = () => {
    if (loading) {
      return <p>Loading medicines...</p>
    }

    if (error) {
      return <div className="patient-panel"><p>{error}</p></div>
    }

    if (medicines.length === 0) {
      return (
        <div className="patient-panel">
          <p>No medicine details available yet.</p>
        </div>
      )
    }

    return medicines.map((medicine) => (
      <div className="patient-panel" key={medicine.medicine_id}>
        <h3><Pill /> {medicine.medicine_name}</h3>
        <p><strong>Dosage:</strong> {medicine.dosage}</p>
        <p><strong>Frequency:</strong> {medicine.frequency}</p>
        <p><strong>Duration:</strong> {medicine.duration}</p>
        <p><strong>Instructions:</strong> {medicine.instructions || 'N/A'}</p>
        <p><strong>Prescription date:</strong> {medicine.prescription_date || 'N/A'}</p>
      </div>
    ))
  }

  return (
    <div className="patient-dashboard">
      <aside className="patient-sidebar">
        <h2><HeartPulse /> MediCare</h2>

        <p className="sidebar-label">MENU</p>

        <a
          href="#"
          className={activeSection === 'dashboard' ? 'sidebar-active' : ''}
          onClick={(e) => {
            e.preventDefault()
            setActiveSection('dashboard')
          }}
        >
          <LayoutDashboard /> Dashboard
        </a>

        <a
          href="#"
          className={activeSection === 'prescriptions' ? 'sidebar-active' : ''}
          onClick={(e) => {
            e.preventDefault()
            setActiveSection('prescriptions')
            fetchPrescriptions()
          }}
        >
          <FileText /> My Prescriptions
        </a>

        <a
          href="#"
          className={activeSection === 'medicines' ? 'sidebar-active' : ''}
          onClick={(e) => {
            e.preventDefault()
            setActiveSection('medicines')
            fetchPrescriptions()
          }}
        >
          <Pill /> Medicines
        </a>

        <a
          href="#"
          className={activeSection === 'reminders' ? 'sidebar-active' : ''}
          onClick={(e) => {
            e.preventDefault()
            setActiveSection('reminders')
          }}
        >
          <Bell /> Reminders
        </a>

        <a
          href="#"
          className={activeSection === 'profile' ? 'sidebar-active' : ''}
          onClick={(e) => {
            e.preventDefault()
            setActiveSection('profile')
          }}
        >
          <UserRound /> My Profile
        </a>

        <div
          className="sidebar-logout"
          onClick={handleLogout}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleLogout()
          }}
        >
          <LogOut /> Logout
        </div>
      </aside>

      <main className="patient-main">
        <header className="patient-header">
          <div>
            <h1>Patient Dashboard</h1>
            <p>Welcome back! Here's your health overview.</p>
          </div>

          <div className="patient-avatar">
            <UserRound />
          </div>
        </header>

        {activeSection === 'dashboard' && (
          <>
            <section className="patient-welcome">
              <div>
                <h2>Hello, Patient! 👋</h2>
                <p>Stay on top of your health with MediCare.</p>
              </div>

              <HeartPulse size={55} />
            </section>

            <section className="patient-stats">
              <div className="patient-stat-card">
                <FileText />
                <h3>My Prescriptions</h3>
                <strong>{prescriptions.length}</strong>
                <p>Total prescriptions</p>
              </div>

              <div className="patient-stat-card">
                <Pill />
                <h3>My Medicines</h3>
                <strong>{medicines.length}</strong>
                <p>Active medicines</p>
              </div>

              <div className="patient-stat-card">
                <Bell />
                <h3>Reminders</h3>
                <strong>0</strong>
                <p>Pending reminders</p>
              </div>
            </section>

            <section className="patient-bottom">
              <div className="patient-panel">
                <h3><FileText /> Recent Prescriptions</h3>
                {prescriptions.length > 0 ? (
                  prescriptions.slice(0, 3).map((item) => (
                    <p key={item.prescription_id}>
                      Prescription #{item.prescription_id} - {item.verification_status}
                    </p>
                  ))
                ) : (
                  <p>{loading ? 'Loading...' : 'No prescriptions available yet.'}</p>
                )}
                <button onClick={() => setActiveSection('prescriptions')}>
                  View My Prescriptions
                </button>
              </div>

              <div className="patient-panel">
                <h3><Activity /> Health Overview</h3>
                <p><CalendarDays /> Keep your medical records updated.</p>
                <p><Clock /> Your reminders will appear here.</p>
              </div>
            </section>
          </>
        )}

        {activeSection === 'prescriptions' && (
          <section>
            <h2><FileText /> My Prescriptions</h2>
            {renderPrescriptions()}
          </section>
        )}

        {activeSection === 'medicines' && (
          <section>
            <h2><Pill /> My Medicines</h2>
            {renderMedicines()}
          </section>
        )}

        {activeSection === 'reminders' && (
          <section className="patient-panel">
            <h2><Bell /> Medicine Reminders</h2>
            <p>Medicine reminders are not available yet.</p>
          </section>
        )}

        {activeSection === 'profile' && (
          <section className="patient-panel">
            <h2><UserRound /> My Profile</h2>
            <p>Profile details will be available here.</p>
          </section>
        )}
      </main>
    </div>
  )
}

export default PatientDashboard
