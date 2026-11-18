
import { useState } from 'react'
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useNavigate,
  Navigate
} from 'react-router-dom'

import {
  HeartPulse,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Stethoscope,
  UserRound,
  ShieldCheck
} from 'lucide-react'

import Register from './pages/Register'
import PatientDashboard from './pages/PatientDashboard'
import DoctorDashboard from './pages/DoctorDashboard'
import AdminDashboard from './pages/AdminDashboard'
import PrescriptionUpload from './pages/PrescriptionUpload'
import PrescriptionReview from './pages/PrescriptionReview'

import './App.css'

// Check whether the user has the correct role
function ProtectedRoute({ allowedRole, children }) {
  const loggedInRole = localStorage.getItem('userRole')

  if (!loggedInRole) {
    return <Navigate to="/" replace />
  }

  if (loggedInRole !== allowedRole) {
    return <Navigate to="/" replace />
  }

  return children
}

function Login() {
  const navigate = useNavigate()

  const [role, setRole] = useState('Patient')
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault()
    setMessage('')

    if (!email || !password) {
      setMessage('Please enter your email and password.')
      return
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (!response.ok) {
        setMessage(data.detail || 'Login failed. Please check your credentials.')
        return
      }

      if (data.role !== role) {
        setMessage(`This account is registered as ${data.role}. Please select the correct role.`)
        return
      }

      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('userRole', data.role)
      localStorage.setItem('userId', data.user_id)
      localStorage.setItem('userName', data.name)

      if (data.role === 'Patient') {
        navigate('/patient-dashboard')
      } else if (data.role === 'Doctor') {
        navigate('/doctor-dashboard')
      } else if (data.role === 'Admin') {
        navigate('/admin-dashboard')
      }

    } catch (error) {
      setMessage('Unable to connect to server. Please make sure the backend is running.')
    }
  }

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="brand">
          <div className="brand-icon">
            <HeartPulse size={28} />
          </div>
          <span>MediCare</span>
        </div>

        <div className="welcome-content">
          <div className="welcome-tag">YOUR HEALTH, OUR PRIORITY</div>
          <h1>Healthcare made<br />simpler and smarter.</h1>
          <p>
            Manage prescriptions, access medical information
            and stay connected with your healthcare team.
          </p>

          <div className="feature-list">
            <div><HeartPulse /> Better healthcare management</div>
            <div><Lock /> Secure medical information</div>
            <div><UserRound /> Connected care for everyone</div>
          </div>
        </div>

        <p className="left-footer">
          © 2026 MediCare. All rights reserved.
        </p>
      </div>

      <div className="login-right">
        <div className="login-card">
          <div className="mobile-brand">
            <HeartPulse size={28} /> MediCare
          </div>

          <div className="login-heading">
            <span className="welcome-tag">WELCOME BACK</span>
            <h2>Sign in to your account</h2>
            <p>Please enter your details to continue.</p>
          </div>

          <form onSubmit={handleLogin}>
            <label>Select your role</label>

            <div className="role-options">
              <button
                type="button"
                className={role === 'Patient' ? 'role-btn active' : 'role-btn'}
                onClick={() => setRole('Patient')}
              >
                <UserRound size={19} />
                Patient
              </button>

              <button
                type="button"
                className={role === 'Doctor' ? 'role-btn active' : 'role-btn'}
                onClick={() => setRole('Doctor')}
              >
                <Stethoscope size={19} />
                Doctor
              </button>

              <button
                type="button"
                className={role === 'Admin' ? 'role-btn active' : 'role-btn'}
                onClick={() => setRole('Admin')}
              >
                <ShieldCheck size={19} />
                Admin
              </button>
            </div>

            <label htmlFor="email">Email address</label>
            <div className="input-wrapper">
              <Mail size={19} />
              <input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock size={19} />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
              </button>
            </div>

            <div className="login-options">
              <label className="remember">
                <input type="checkbox" /> Remember me
              </label>
              <span className="forgot">Forgot password?</span>
            </div>

            {message && <p className="form-message">{message}</p>}

            <button type="submit" className="login-button">
              Sign In
            </button>
          </form>

          <p className="register-text">
            Don't have an account? <Link to="/register">Register here</Link>
          </p>

          <p className="security-note">
            Your medical information is protected and secure.
          </p>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/patient-dashboard"
          element={
            <ProtectedRoute allowedRole="Patient">
              <PatientDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/doctor-dashboard"
          element={
            <ProtectedRoute allowedRole="Doctor">
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/prescription-upload"
          element={
            <ProtectedRoute allowedRole="Doctor">
              <PrescriptionUpload />
            </ProtectedRoute>
          }
        />

        <Route
          path="/prescription-review"
          element={
            <ProtectedRoute allowedRole="Doctor">
              <PrescriptionReview />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin-dashboard"
          element={
            <ProtectedRoute allowedRole="Admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App
