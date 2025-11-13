import { useEffect, useState } from 'react'
import api from '../lib/api'
import LoadingSpinner from '../components/LoadingSpinner'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

export default function Conversations() {
  const [conversations, setConversations] = useState([])
  const [selectedConvo, setSelectedConvo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const res = await api.get('/conversations/')
      setConversations(res.data)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    } finally {
      setLoading(false)
    }
  }

  const filteredConversations = conversations.filter(convo =>
    convo.phone_number?.includes(searchQuery) ||
    convo.messages?.some(msg => 
      msg.message?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  )

  if (loading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Conversations</h1>
        <div className="text-sm text-gray-600">
          {conversations.length} total conversations
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4">
        <input
          type="text"
          placeholder="Search by phone number or message content..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Conversations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversations List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h2 className="font-semibold text-gray-900">All Conversations</h2>
          </div>
          <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
            {filteredConversations.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p className="text-lg">No conversations found</p>
              </div>
            ) : (
              filteredConversations.map((convo) => (
                <div
                  key={convo.id}
                  onClick={() => setSelectedConvo(convo)}
                  className={`p-4 hover:bg-gray-50 cursor-pointer transition ${
                    selectedConvo?.id === convo.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="font-medium text-gray-900">{convo.phone_number}</div>
                    <div className="text-xs text-gray-500">
                      {convo.updated_at ? dayjs(convo.updated_at).fromNow() : 'Recently'}
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">
                    {convo.state ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                        {convo.state}
                      </span>
                    ) : null}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {convo.messages?.length || 0} messages
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Conversation Detail */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h2 className="font-semibold text-gray-900">
              {selectedConvo ? `Chat with ${selectedConvo.phone_number}` : 'Select a conversation'}
            </h2>
          </div>
          <div className="p-4 max-h-[600px] overflow-y-auto">
            {!selectedConvo ? (
              <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                <svg className="w-20 h-20 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p className="text-lg">Select a conversation to view details</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Conversation Metadata */}
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-gray-600">Phone:</span>
                      <span className="ml-2 font-medium">{selectedConvo.phone_number}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">State:</span>
                      <span className="ml-2 font-medium">{selectedConvo.state || 'Unknown'}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Started:</span>
                      <span className="ml-2 font-medium">
                        {selectedConvo.created_at ? dayjs(selectedConvo.created_at).format('MMM DD, YYYY HH:mm') : 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Last Update:</span>
                      <span className="ml-2 font-medium">
                        {selectedConvo.updated_at ? dayjs(selectedConvo.updated_at).fromNow() : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Messages */}
                <div className="space-y-3">
                  {selectedConvo.messages && selectedConvo.messages.length > 0 ? (
                    selectedConvo.messages.map((msg, idx) => (
                      <div
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg px-4 py-2 ${
                            msg.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <div className="text-xs opacity-75 mb-1">
                            {msg.role === 'user' ? 'Customer' : 'AI Assistant'}
                          </div>
                          <div className="text-sm">{msg.message || msg.content}</div>
                          <div className="text-xs opacity-75 mt-1">
                            {msg.timestamp ? dayjs(msg.timestamp).format('HH:mm') : ''}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-center text-gray-500 py-8">No messages in this conversation</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
