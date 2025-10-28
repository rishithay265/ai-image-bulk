'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import toast from 'react-hot-toast'
import axios from 'axios'
import {
  FaImage,
  FaKey,
  FaPlus,
  FaTrash,
  FaCopy,
  FaEye,
  FaEyeSlash,
  FaSignOutAlt,
  FaExclamationTriangle
} from 'react-icons/fa'

export default function APIKeys() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [apiKeys, setApiKeys] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newlyCreatedKey, setNewlyCreatedKey] = useState('')

  useEffect(() => {
    checkUser()
  }, [])

  const checkUser = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()

      if (!session) {
        router.push('/login')
        return
      }

      setUser(session.user)
      await fetchAPIKeys(session.access_token)
    } catch (error) {
      console.error('Error checking user:', error)
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  const fetchAPIKeys = async (token: string) => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/auth/api-keys`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      setApiKeys(response.data.api_keys || [])
    } catch (error) {
      console.error('Error fetching API keys:', error)
      toast.error('Failed to load API keys')
    }
  }

  const createAPIKey = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a key name')
      return
    }

    setCreating(true)
    try {
      const { data: { session } } = await supabase.auth.getSession()

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/auth/generate-api-key`,
        { key_name: newKeyName },
        {
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
            'Content-Type': 'application/json',
          },
        }
      )

      setNewlyCreatedKey(response.data.api_key)
      toast.success('API key created successfully!')
      await fetchAPIKeys(session?.access_token!)
      setNewKeyName('')
    } catch (error: any) {
      console.error('Error creating API key:', error)
      toast.error(error.response?.data?.error || 'Failed to create API key')
    } finally {
      setCreating(false)
    }
  }

  const deleteAPIKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) {
      return
    }

    try {
      const { data: { session } } = await supabase.auth.getSession()

      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/auth/api-keys/${keyId}`,
        {
          headers: {
            Authorization: `Bearer ${session?.access_token}`,
          },
        }
      )

      toast.success('API key deleted successfully')
      await fetchAPIKeys(session?.access_token!)
    } catch (error) {
      console.error('Error deleting API key:', error)
      toast.error('Failed to delete API key')
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/')
    toast.success('Logged out successfully')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <FaImage className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">BIG API</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-700 hover:text-blue-600">
                Dashboard
              </Link>
              <Link href="/api-keys" className="text-blue-600 font-semibold">
                API Keys
              </Link>
              <Link href="/docs" className="text-gray-700 hover:text-blue-600">
                Docs
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 text-gray-700 hover:text-red-600"
              >
                <FaSignOutAlt />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
            <p className="text-gray-600 mt-1">
              Manage your API keys for accessing the BIG API
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center gap-2"
          >
            <FaPlus />
            Create API Key
          </button>
        </div>

        {/* Warning */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <FaExclamationTriangle className="text-yellow-600 text-xl mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-900">Keep your API keys secure!</h3>
            <p className="text-yellow-800 text-sm mt-1">
              Never share your API keys publicly or commit them to version control.
              Treat them like passwords.
            </p>
          </div>
        </div>

        {/* API Keys List */}
        <div className="bg-white rounded-xl shadow-lg">
          {apiKeys.length === 0 ? (
            <div className="p-12 text-center">
              <FaKey className="text-6xl text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No API Keys Yet</h3>
              <p className="text-gray-600 mb-6">
                Create your first API key to start generating images
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700"
              >
                Create Your First API Key
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {apiKeys.map((key) => (
                <div key={key.id} className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{key.name}</h3>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            key.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {key.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <code className="bg-gray-100 px-3 py-1 rounded font-mono text-sm">
                          {key.key_preview}
                        </code>
                        <button
                          onClick={() => copyToClipboard(key.key_preview)}
                          className="text-blue-600 hover:text-blue-700"
                          title="Copy key preview"
                        >
                          <FaCopy />
                        </button>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        <span>Created: {new Date(key.created_at).toLocaleDateString()}</span>
                        {key.last_used_at && (
                          <span className="ml-4">
                            Last used: {new Date(key.last_used_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => deleteAPIKey(key.id)}
                      className="ml-4 text-red-600 hover:text-red-700 p-2"
                      title="Delete API key"
                    >
                      <FaTrash />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create API Key Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Create New API Key</h2>

            {newlyCreatedKey ? (
              <div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <p className="text-green-900 font-semibold mb-2">API Key Created!</p>
                  <p className="text-green-700 text-sm">
                    Make sure to copy your API key now. You won't be able to see it again!
                  </p>
                </div>

                <div className="bg-gray-100 rounded-lg p-4 mb-4">
                  <code className="text-sm break-all">{newlyCreatedKey}</code>
                </div>

                <button
                  onClick={() => {
                    copyToClipboard(newlyCreatedKey)
                    toast.success('API key copied to clipboard!')
                  }}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 mb-2 flex items-center justify-center gap-2"
                >
                  <FaCopy />
                  Copy API Key
                </button>

                <button
                  onClick={() => {
                    setShowCreateModal(false)
                    setNewlyCreatedKey('')
                  }}
                  className="w-full bg-gray-200 text-gray-900 py-2 rounded-lg font-semibold hover:bg-gray-300"
                >
                  Done
                </button>
              </div>
            ) : (
              <div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Key Name
                  </label>
                  <input
                    type="text"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                    placeholder="e.g., Production API Key"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={createAPIKey}
                    disabled={creating}
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                  >
                    {creating ? 'Creating...' : 'Create'}
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateModal(false)
                      setNewKeyName('')
                    }}
                    className="flex-1 bg-gray-200 text-gray-900 py-2 rounded-lg font-semibold hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
