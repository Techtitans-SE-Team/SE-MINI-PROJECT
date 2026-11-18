
import {
  HeartPulse,
  LayoutDashboard,
  FileText,
  Users,
  UserRound,
  LogOut,
  CalendarDays,
  Clock,
  PlusCircle,
  ClipboardCheck
} from 'lucide-react'

import { useNavigate } from 'react-router-dom'

function DoctorDashboard() {
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('userRole')
    localStorage.removeItem('access_token')
    window.location.href = '/'
  }

  return (
    <div className="patient-dashboard">
      <aside className="patient-sidebar">
        <h2><HeartPulse /> MediCare</h2>
        <p className="sidebar-label">DOCTOR MENU</p>

        <a className="sidebar-active">
          <LayoutDashboard /> Dashboard
        </a>

        <a><Users /> My Patients</a>

        <a onClick={() => navigate('/prescription-upload')}>
          <FileText /> Prescriptions
        </a>

        <a onClick={() => navigate('/prescription-review')}>
          <ClipboardCheck /> Review Prescriptions
        </a>

        <a><CalendarDays /> Appointments</a>
        <a><UserRound /> My Profile</a>

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
            <h1>Doctor Dashboard</h1>
            <p>Welcome back, Doctor! Here's your overview.</p>
          </div>

          <div className="patient-avatar">
            <UserRound />
          </div>
        </header>

        <section className="patient-welcome">
          <div>
            <h2>Hello, Doctor! 👋</h2>
            <p>Manage your patients and prescriptions with MediCare.</p>
          </div>

          <HeartPulse size={55} />
        </section>

        <section className="patient-stats">
          <div className="patient-stat-card">
            <Users />
            <h3>Total Patients</h3>
            <strong>0</strong>
            <p>Registered patients</p>
          </div>

          <div className="patient-stat-card">
            <FileText />
            <h3>Prescriptions</h3>
            <strong>0</strong>
            <p>Prescriptions created</p>
          </div>

          <div className="patient-stat-card">
            <CalendarDays />
            <h3>Appointments</h3>
            <strong>0</strong>
            <p>Upcoming appointments</p>
          </div>
        </section>

        <section className="patient-bottom">
          <div className="patient-panel">
            <h3><ClipboardCheck /> Recent Activity</h3>
            <p>No recent activity available.</p>
          </div>

          <div className="patient-panel">
            <h3><PlusCircle /> Quick Actions</h3>

            <p
              onClick={() => navigate('/prescription-upload')}
              style={{ cursor: 'pointer' }}
            >
              <FileText /> Create a prescription
            </p>

            <p
              onClick={() => navigate('/prescription-review')}
              style={{ cursor: 'pointer' }}
            >
              <ClipboardCheck /> Review prescriptions
            </p>

            <p><Users /> View patient records</p>
            <p><Clock /> Manage appointments</p>
          </div>
        </section>
      </main>
    </div>
  )
}

export default DoctorDashboard
