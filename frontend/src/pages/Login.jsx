import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [isRegister, setIsRegister] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (isRegister) {
        // Register new user
        await api.post('/users/register', { 
          username, 
          password,
          email,
          full_name: fullName 
        })
        setIsRegister(false)
        setError('Registration successful! Please login.')
        // Clear form
        setEmail('')
        setFullName('')
      } else {
        // Login
        const res = await api.post('/users/login', new URLSearchParams({ username, password }))
        const { access_token } = res.data
        localStorage.setItem('access_token', access_token)
        navigate('/')
      }
    } catch (err) {
      console.error('Error:', err.response?.data)
      // Handle error message properly - convert to string if it's an object
      let errorMsg = `${isRegister ? 'Registration' : 'Login'} failed`
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMsg = err.response.data.detail
        } else if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail.map(e => e.msg).join(', ')
        } else {
          errorMsg = JSON.stringify(err.response.data.detail)
        }
      }
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🪒 Royal Fade AI
          </h1>
          <p className="text-gray-600">AI-Powered Barber Shop Management</p>
        </div>

        <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setIsRegister(false)}
            className={`flex-1 py-2 rounded-md font-medium transition ${
              !isRegister
                ? 'bg-white text-blue-600 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setIsRegister(true)}
            className={`flex-1 py-2 rounded-md font-medium transition ${
              isRegister
                ? 'bg-white text-blue-600 shadow'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className={`mb-4 p-3 rounded-md text-sm ${
            error.includes('successful') 
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter username"
              required
            />
          </div>

          {isRegister && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter email"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter full name"
                  required
                />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition"
          >
            {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Default credentials: admin / admin123</p>
        </div>
      </div>
    </div>
  )
}
