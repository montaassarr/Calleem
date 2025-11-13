import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [todayAppointments, setTodayAppointments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      const [statsRes, appointmentsRes] = await Promise.all([
        api.get('/appointments/stats'),
        api.get('/appointments/')
      ])
      
      setStats(statsRes.data)
      
      // Filter today's appointments
      const today = new Date().toISOString().split('T')[0]
      const todayAppts = appointmentsRes.data.filter(apt => 
        apt.scheduled_time?.startsWith(today)
      ).slice(0, 5)
      setTodayAppointments(todayAppts)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-600">
          {new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Appointments</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">
                {stats?.total_appointments || 0}
              </p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Confirmed</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {stats?.by_status?.confirmed || 0}
              </p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">
                {stats?.by_status?.pending || 0}
              </p>
            </div>
            <div className="bg-yellow-100 rounded-full p-3">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Cancelled</p>
              <p className="text-3xl font-bold text-red-600 mt-2">
                {stats?.by_status?.cancelled || 0}
              </p>
            </div>
            <div className="bg-red-100 rounded-full p-3">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Today's Appointments */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Today's Appointments</h2>
            <Link to="/appointments" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              View All →
            </Link>
          </div>
        </div>
        <div className="p-6">
          {todayAppointments.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No appointments scheduled for today</p>
          ) : (
            <div className="space-y-4">
              {todayAppointments.map((apt) => (
                <div key={apt.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                  <div className="flex items-center space-x-4">
                    <div className="bg-blue-100 rounded-full p-2">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{apt.customer_name || 'Unknown'}</p>
                      <p className="text-sm text-gray-600">{apt.customer_phone}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      {apt.scheduled_time ? new Date(apt.scheduled_time).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                      }) : 'Not scheduled'}
                    </p>
                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                      apt.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                      apt.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                      apt.status === 'cancelled' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {apt.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/appointments"
          className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white hover:shadow-xl transition transform hover:-translate-y-1"
        >
          <h3 className="text-lg font-semibold mb-2">Manage Appointments</h3>
          <p className="text-blue-100 text-sm">View, create, and manage all appointments</p>
        </Link>

        <Link
          to="/conversations"
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white hover:shadow-xl transition transform hover:-translate-y-1"
        >
          <h3 className="text-lg font-semibold mb-2">View Conversations</h3>
          <p className="text-purple-100 text-sm">Review AI chat history with customers</p>
        </Link>

        <Link
          to="/services"
          className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white hover:shadow-xl transition transform hover:-translate-y-1"
        >
          <h3 className="text-lg font-semibold mb-2">Manage Services</h3>
          <p className="text-green-100 text-sm">Update services, pricing, and durations</p>
        </Link>
      </div>
    </div>
  )
}
