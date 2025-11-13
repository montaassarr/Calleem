import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
  const navigate = useNavigate()
  const token = localStorage.getItem('access_token')

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    navigate('/login')
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              🪒 Royal Fade AI
            </Link>
          </div>
          
          {token && (
            <nav className="flex space-x-6">
              <Link
                to="/"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                Dashboard
              </Link>
              <Link
                to="/appointments"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                Appointments
              </Link>
              <Link
                to="/conversations"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                Conversations
              </Link>
              <Link
                to="/services"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                Services
              </Link>
              <button
                onClick={handleLogout}
                className="text-red-600 hover:text-red-700 px-3 py-2 rounded-md text-sm font-medium transition"
              >
                Logout
              </button>
            </nav>
          )}
        </div>
      </div>
    </header>
  )
}
