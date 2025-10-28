'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { FaRocket, FaImage, FaBolt, FaDollarSign, FaCheckCircle, FaCode } from 'react-icons/fa'

export default function Home() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setUser(session.user)
      }
    })
  }, [])

  const providers = [
    { name: 'DALL-E 3', credits: 10, quality: 'High' },
    { name: 'Imagen 4 Ultra', credits: 12, quality: 'Ultra' },
    { name: 'GPT Image 1', credits: 11, quality: 'Ultra' },
    { name: 'Ideogram V3', credits: 9, quality: 'High' },
    { name: 'FLUX Kontext', credits: 8, quality: 'High' },
    { name: 'Seedream 4', credits: 8, quality: 'High (4K)' },
    { name: 'And 9 more...', credits: 5-7, quality: 'Medium-High' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <FaImage className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-2xl font-bold text-gray-900">BIG API</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="#features" className="text-gray-700 hover:text-blue-600">
                Features
              </Link>
              <Link href="#pricing" className="text-gray-700 hover:text-blue-600">
                Pricing
              </Link>
              <Link href="/docs" className="text-gray-700 hover:text-blue-600">
                Docs
              </Link>
              {user ? (
                <Link
                  href="/dashboard"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Dashboard
                </Link>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-gray-700 hover:text-blue-600"
                  >
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 mb-6">
            Generate Images at <span className="text-blue-600">Scale</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Unified API gateway to 15+ state-of-the-art AI image generation models.
            One endpoint, multiple providers, infinite possibilities.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href={user ? "/dashboard" : "/signup"}
              className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-700 flex items-center gap-2"
            >
              <FaRocket />
              {user ? "Go to Dashboard" : "Get Started Free"}
            </Link>
            <Link
              href="/docs"
              className="bg-white border-2 border-blue-600 text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-blue-50 flex items-center gap-2"
            >
              <FaCode />
              View Docs
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-4xl font-bold text-blue-600">15+</div>
            <div className="text-gray-600 mt-2">AI Providers</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-4xl font-bold text-purple-600">4K</div>
            <div className="text-gray-600 mt-2">Max Resolution</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-4xl font-bold text-green-600">99.9%</div>
            <div className="text-gray-600 mt-2">Uptime</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-lg text-center">
            <div className="text-4xl font-bold text-orange-600">&lt;2s</div>
            <div className="text-gray-600 mt-2">Avg Response</div>
          </div>
        </div>
      </div>

      {/* Features */}
      <div id="features" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12">Powerful Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <FaBolt className="text-blue-600 text-2xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
              <p className="text-gray-600">
                Synchronous processing optimized for Vercel. Get results in seconds, not minutes.
              </p>
            </div>
            <div className="p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <FaImage className="text-purple-600 text-2xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Multiple Providers</h3>
              <p className="text-gray-600">
                Access DALL-E, Imagen, FLUX, Seedream, Ideogram, and more from one API.
              </p>
            </div>
            <div className="p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <FaDollarSign className="text-green-600 text-2xl" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Pay As You Go</h3>
              <p className="text-gray-600">
                Transparent credit-based pricing. Only pay for what you use, no hidden fees.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Providers */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-center mb-12">Supported Providers</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {providers.map((provider, index) => (
            <div key={index} className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold">{provider.name}</h3>
                <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
                  {provider.credits} credits
                </span>
              </div>
              <p className="text-gray-600 text-sm">{provider.quality} Quality</p>
            </div>
          ))}
        </div>
      </div>

      {/* Pricing */}
      <div id="pricing" className="bg-gradient-to-br from-blue-600 to-purple-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12 text-white">Simple Pricing</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free */}
            <div className="bg-white rounded-xl shadow-xl p-8">
              <h3 className="text-2xl font-bold mb-4">Free</h3>
              <div className="text-4xl font-bold mb-6">
                $0<span className="text-lg text-gray-600">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  100 credits on signup
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  10 requests/minute
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  Basic providers
                </li>
              </ul>
              <Link
                href="/signup"
                className="block w-full bg-gray-200 text-gray-900 text-center py-3 rounded-lg font-semibold hover:bg-gray-300"
              >
                Get Started
              </Link>
            </div>

            {/* Pro */}
            <div className="bg-blue-600 text-white rounded-xl shadow-xl p-8 transform scale-105 border-4 border-yellow-400">
              <div className="bg-yellow-400 text-gray-900 px-3 py-1 rounded-full text-sm font-bold inline-block mb-4">
                POPULAR
              </div>
              <h3 className="text-2xl font-bold mb-4">Pro</h3>
              <div className="text-4xl font-bold mb-6">
                $99<span className="text-lg text-blue-200">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <FaCheckCircle />
                  25,000 credits/month
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle />
                  120 requests/minute
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle />
                  All providers
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle />
                  Priority support
                </li>
              </ul>
              <Link
                href="/signup"
                className="block w-full bg-white text-blue-600 text-center py-3 rounded-lg font-semibold hover:bg-gray-100"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Starter */}
            <div className="bg-white rounded-xl shadow-xl p-8">
              <h3 className="text-2xl font-bold mb-4">Starter</h3>
              <div className="text-4xl font-bold mb-6">
                $29<span className="text-lg text-gray-600">/mo</span>
              </div>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  5,000 credits/month
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  60 requests/minute
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  All providers
                </li>
                <li className="flex items-center gap-2">
                  <FaCheckCircle className="text-green-600" />
                  Email support
                </li>
              </ul>
              <Link
                href="/signup"
                className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg font-semibold hover:bg-blue-700"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <FaImage className="h-8 w-8" />
                <span className="ml-2 text-xl font-bold">BIG API</span>
              </div>
              <p className="text-gray-400">
                Unified gateway to AI image generation.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/pricing">Pricing</Link></li>
                <li><Link href="/docs">Documentation</Link></li>
                <li><Link href="/api-reference">API Reference</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about">About</Link></li>
                <li><Link href="/blog">Blog</Link></li>
                <li><Link href="/careers">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/privacy">Privacy</Link></li>
                <li><Link href="/terms">Terms</Link></li>
                <li><Link href="/security">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 BIG API. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
