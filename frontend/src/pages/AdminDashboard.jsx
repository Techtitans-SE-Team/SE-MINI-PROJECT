
import {
  HeartPulse,
  LayoutDashboard,
  Users,
  UserRound,
  FileText,
  ShieldCheck,
  LogOut,
  Activity,
  UserPlus,
  ClipboardList
} from 'lucide-react'

function AdminDashboard() {

  const handleLogout = () => {
    localStorage.removeItem('userRole')
    window.location.href = '/'
  }

  return (
    <div className="patient-dashboard">
      <aside className="patient-sidebar">
        <h2><HeartPulse /> MediCare</h2>

        <p className="sidebar-label">ADMIN MENU</p>

        <a className="sidebar-active">
          <LayoutDashboard /> Dashboard
        </a>

        <a><Users /> Manage Users</a>
        <a><FileText /> Prescriptions</a>
        <a><ShieldCheck /> Verification</a>
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
            <h1>Admin Dashboard</h1>
            <p>Welcome to MediCare administration.</p>
          </div>

          <div className="patient-avatar">
            <UserRound />
          </div>
        </header>

        <section className="patient-welcome">
          <div>
            <h2>Hello, Admin! 👋</h2>
            <p>Manage users and monitor the healthcare platform.</p>
          </div>

          <ShieldCheck size={55} />
        </section>

        <section className="patient-stats">
          <div className="patient-stat-card">
            <Users />
            <h3>Total Users</h3>
            <strong>0</strong>
            <p>Registered users</p>
          </div>

          <div className="patient-stat-card">
            <UserPlus />
            <h3>Doctors</h3>
            <strong>0</strong>
            <p>Registered doctors</p>
          </div>

          <div className="patient-stat-card">
            <FileText />
            <h3>Prescriptions</h3>
            <strong>0</strong>
            <p>Total prescriptions</p>
          </div>
        </section>

        <section className="patient-bottom">
          <div className="patient-panel">
            <h3><Activity /> System Overview</h3>
            <p>Platform is ready for administration.</p>
          </div>

          <div className="patient-panel">
            <h3><ClipboardList /> Admin Activities</h3>
            <p>No recent activities available.</p>
          </div>
        </section>
      </main>
    </div>
  )
}

export default AdminDashboard
