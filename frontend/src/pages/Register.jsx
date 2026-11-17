
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowLeft,
  HeartPulse
} from 'lucide-react'

function Register() {
  const navigate = useNavigate()

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'Patient',
    date_of_birth: '',
    phone: '',
    preferred_language: '',
    address: '',
    specialization: '',
    qualification: '',
    license_number: ''
  })

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match!')
      return
    }

    if (
      formData.password.length < 8 ||
      !/[a-z]/.test(formData.password) ||
      !/[A-Z]/.test(formData.password) ||
      !/[0-9]/.test(formData.password)
    ) {
      alert(
        'Password must contain at least 8 characters, one uppercase letter, one lowercase letter and one number.'
      )
      return
    }

    const payload = {
      name: formData.name,
      email: formData.email,
      password: formData.password,
      role: formData.role
    }

    if (formData.role === 'Patient') {
      payload.date_of_birth = formData.date_of_birth
      payload.phone = formData.phone
      payload.preferred_language = formData.preferred_language
      payload.address = formData.address || null
    } else {
      payload.specialization = formData.specialization
      payload.qualification = formData.qualification || null
      payload.license_number = formData.license_number || null
    }

    setIsSubmitting(true)

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (!response.ok) {
        const errorMessage = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(', ')
          : data.detail || 'Registration failed.'

        throw new Error(errorMessage)
      }

      alert('Account created successfully! Please login.')
      navigate('/')
    } catch (error) {
      alert(error.message || 'Unable to connect to server.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="register-page">
      <div className="register-layout">

        <div className="register-left">
          <div className="register-brand">
            <HeartPulse size={28} />
            <span>MediCare</span>
          </div>

          <div className="register-welcome">
            <h1>Join MediCare</h1>
            <p>
              Create your account and take the first step
              towards smarter healthcare management.
            </p>
          </div>

          <p className="register-footer">
            Your health, our priority.
          </p>
        </div>

        <div className="register-right">
          <div className="register-form">

            <Link to="/" className="back-link">
              <ArrowLeft size={18} />
              Back to Login
            </Link>

            <div className="form-heading">
              <h2>Create Account</h2>
              <p>Fill in your details to get started</p>
            </div>

            <form onSubmit={handleSubmit}>

              <label>Full Name</label>
              <div className="input-wrapper">
                <User size={18} />
                <input
                  type="text"
                  name="name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  minLength={2}
                />
              </div>

              <label>Email Address</label>
              <div className="input-wrapper">
                <Mail size={18} />
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <label>Account Type</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="role-select"
              >
                <option value="Patient">Patient</option>
                <option value="Doctor">Doctor</option>
              </select>

              {formData.role === 'Patient' && (
                <>
                  <label>Date of Birth</label>
                  <div className="input-wrapper">
                    <input
                      type="date"
                      name="date_of_birth"
                      value={formData.date_of_birth}
                      onChange={handleChange}
                      max={new Date().toISOString().split('T')[0]}
                      required
                    />
                  </div>

                  <label>Phone Number</label>
                  <div className="input-wrapper">
                    <input
                      type="tel"
                      name="phone"
                      placeholder="Enter phone number"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <label>Preferred Language</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="preferred_language"
                      placeholder="e.g. English, Kannada"
                      value={formData.preferred_language}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <label>Address (Optional)</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="address"
                      placeholder="Enter your address"
                      value={formData.address}
                      onChange={handleChange}
                    />
                  </div>
                </>
              )}

              {formData.role === 'Doctor' && (
                <>
                  <label>Specialization</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="specialization"
                      placeholder="e.g. Cardiologist"
                      value={formData.specialization}
                      onChange={handleChange}
                      required
                    />
                  </div>

                  <label>Qualification (Optional)</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="qualification"
                      placeholder="e.g. MBBS, MD"
                      value={formData.qualification}
                      onChange={handleChange}
                    />
                  </div>

                  <label>License Number (Optional)</label>
                  <div className="input-wrapper">
                    <input
                      type="text"
                      name="license_number"
                      placeholder="Enter license number"
                      value={formData.license_number}
                      onChange={handleChange}
                    />
                  </div>
                </>
              )}

              <label>Password</label>
              <div className="input-wrapper">
                <Lock size={18} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  placeholder="Create a password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword
                    ? <EyeOff size={18} />
                    : <Eye size={18} />}
                </button>
              </div>

              <label>Confirm Password</label>
              <div className="input-wrapper">
                <Lock size={18} />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowConfirmPassword(!showConfirmPassword)
                  }
                >
                  {showConfirmPassword
                    ? <EyeOff size={18} />
                    : <Eye size={18} />}
                </button>
              </div>

              <button
                type="submit"
                className="register-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Creating Account...' : 'Create Account'}
              </button>

            </form>

            <p className="register-text">
              Already have an account? <Link to="/">Sign In</Link>
            </p>

          </div>
        </div>

      </div>
    </div>
  )
}

export default Register
