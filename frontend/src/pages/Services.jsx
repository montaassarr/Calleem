import { useEffect, useState } from 'react'
import api from '../lib/api'
import Modal from '../components/Modal'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Services() {
  const [services, setServices] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingService, setEditingService] = useState(null)
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    duration: '',
    is_active: true
  })

  useEffect(() => {
    loadServices()
  }, [])

  const loadServices = async () => {
    try {
      const res = await api.get('/services/')
      setServices(res.data)
    } catch (err) {
      console.error('Failed to load services:', err)
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setEditingService(null)
    setFormData({
      name: '',
      description: '',
      price: '',
      duration: '',
      is_active: true
    })
    setShowModal(true)
  }

  const openEditModal = (service) => {
    setEditingService(service)
    setFormData({
      name: service.name || '',
      description: service.description || '',
      price: service.price || '',
      duration: service.duration || '',
      is_active: service.is_active !== false
    })
    setShowModal(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        ...formData,
        price: parseFloat(formData.price),
        duration: parseInt(formData.duration)
      }

      if (editingService) {
        await api.put(`/services/${editingService.id}`, payload)
      } else {
        await api.post('/services/', payload)
      }
      setShowModal(false)
      loadServices()
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save service')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this service?')) return
    try {
      await api.delete(`/services/${id}`)
      loadServices()
    } catch (err) {
      alert('Failed to delete service')
    }
  }

  const toggleActive = async (service) => {
    try {
      await api.put(`/services/${service.id}`, {
        ...service,
        is_active: !service.is_active
      })
      loadServices()
    } catch (err) {
      alert('Failed to update service status')
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Services</h1>
        <button
          onClick={openCreateModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition font-medium"
        >
          + Add Service
        </button>
      </div>

      {/* Services Grid */}
      {services.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <p className="text-lg text-gray-500">No services found</p>
          <button
            onClick={openCreateModal}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Add your first service
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service) => (
            <div
              key={service.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition overflow-hidden"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-xl font-semibold text-gray-900">{service.name}</h3>
                  <button
                    onClick={() => toggleActive(service)}
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      service.is_active !== false
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {service.is_active !== false ? 'Active' : 'Inactive'}
                  </button>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                  {service.description || 'No description'}
                </p>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm">
                    <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-semibold text-gray-900">${service.price}</span>
                  </div>

                  <div className="flex items-center text-sm">
                    <svg className="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-gray-700">{service.duration} minutes</span>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={() => openEditModal(service)}
                    className="flex-1 bg-blue-50 text-blue-600 py-2 px-3 rounded-md hover:bg-blue-100 transition text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(service.id)}
                    className="flex-1 bg-red-50 text-red-600 py-2 px-3 rounded-md hover:bg-red-100 transition text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={editingService ? 'Edit Service' : 'Add New Service'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Service Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Haircut, Beard Trim"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="3"
              placeholder="Describe the service..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price ($)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="25.00"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (min)
              </label>
              <input
                type="number"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="30"
                required
              />
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
              Service is active and available for booking
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowModal(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            >
              {editingService ? 'Update Service' : 'Add Service'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
