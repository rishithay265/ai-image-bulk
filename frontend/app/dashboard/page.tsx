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
  FaCreditCard,
  FaChartLine,
  FaSignOutAlt,
  FaBolt,
  FaCheckCircle,
  FaTimesCircle,
  FaCoins
} from 'react-icons/fa'

export default function Dashboard() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [userData, setUserData] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

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
      await fetchUserData(session.user.id)
      await fetchStats(session.access_token)
    } catch (error) {
      console.error('Error checking user:', error)
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  const fetchUserData = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .single()

      if (error) throw error
      setUserData(data)
    } catch (error) {
      console.error('Error fetching user data:', error)
    }
  }

  const fetchStats = async (token: string) => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/dashboard/stats`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
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
              <Link href="/dashboard" className="text-blue-600 font-semibold">
                Dashboard
              </Link>
              <Link href="/api-keys" className="text-gray-700 hover:text-blue-600">
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back, {user?.email}
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Credits */}
          <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-blue-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Credits Remaining</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {userData?.credits?.toLocaleString() || 0}
                </p>
              </div>
              <FaCoins className="text-4xl text-blue-600" />
            </div>
            <Link
              href="/billing"
              className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-semibold"
            >
              Buy more →
            </Link>
          </div>

          {/* API Calls */}
          <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-green-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total API Calls</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats?.total_api_calls || 0}
                </p>
              </div>
              <FaBolt className="text-4xl text-green-600" />
            </div>
          </div>

          {/* Images Generated */}
          <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-purple-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Images Generated</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats?.total_images_generated || 0}
                </p>
              </div>
              <FaImage className="text-4xl text-purple-600" />
            </div>
          </div>

          {/* Success Rate */}
          <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-orange-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Success Rate</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">
                  {stats?.success_rate || 0}%
                </p>
              </div>
              <FaCheckCircle className="text-4xl text-orange-600" />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link
            href="/api-keys"
            className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
          >
            <FaKey className="text-3xl mb-3" />
            <h3 className="text-xl font-semibold mb-2">Manage API Keys</h3>
            <p className="text-blue-100">Create and manage your API keys</p>
          </Link>

          <Link
            href="/docs"
            className="bg-gradient-to-br from-purple-600 to-purple-700 text-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
          >
            <FaImage className="text-3xl mb-3" />
            <h3 className="text-xl font-semibold mb-2">API Documentation</h3>
            <p className="text-purple-100">Learn how to use the API</p>
          </Link>

          <Link
            href="/billing"
            className="bg-gradient-to-br from-green-600 to-green-700 text-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow"
          >
            <FaCreditCard className="text-3xl mb-3" />
            <h3 className="text-xl font-semibold mb-2">Billing & Usage</h3>
            <p className="text-green-100">View usage and purchase credits</p>
          </Link>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
          {stats?.recent_activity && stats.recent_activity.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_activity.map((activity: any, index: number) => (
                <div key={index} className="flex items-center justify-between border-b border-gray-200 pb-3">
                  <div>
                    <p className="font-semibold">
                      {activity.task_details?.providers_used?.join(', ')} generation
                    </p>
                    <p className="text-sm text-gray-600">
                      {activity.task_details?.success_count || 0} images generated
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-blue-600">-{activity.credits_used} credits</p>
                    <p className="text-sm text-gray-600">
                      {new Date(activity.timestamp * 1000).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FaChartLine className="text-4xl mx-auto mb-3 text-gray-400" />
              <p>No recent activity</p>
              <Link href="/docs" className="text-blue-600 hover:text-blue-700 font-semibold">
                Start generating images →
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
