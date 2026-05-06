/** @type {import('next').NextConfig} */

const securityHeaders = [
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' data: https://fonts.gstatic.com",
      "img-src 'self' data: blob: https:",
      "connect-src 'self' http://localhost:8000 ws://localhost:8000 https://*.onrender.com wss://*.onrender.com https://calleem.tech wss://calleem.tech https://api.vapi.ai wss://api.vapi.ai http://localhost:3000 ws://localhost:3000",
      "frame-ancestors 'self'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join('; '),
  },
]

const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  output: 'standalone',
  async rewrites() {
    // For server-side rewrites in Docker, use API_URL (backend service name)
    // For client-side, NEXT_PUBLIC_API_URL will be used directly
    // Priority: API_URL (Docker internal) > NEXT_PUBLIC_API_URL > localhost
    const backendUrl = process.env.API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      'http://localhost:8000';

    // Check for placeholder URLs
    if (backendUrl.includes('your-railway-url')) {
      console.warn('⚠️  API URL contains placeholder value. Please set NEXT_PUBLIC_API_URL in Vercel environment variables.');
    }

    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },
  async redirects() {
    return [
      {
        source: '/dashboard/voice-agent/settings',
        destination: '/dashboard/settings/ai',
        permanent: true,
      },
      {
        source: '/dashboard/settings/services',
        destination: '/dashboard/services',
        permanent: true,
      },
      {
        source: '/dashboard/integrations',
        destination: '/dashboard/settings/api-keys',
        permanent: true,
      },
    ];
  },
}

export default nextConfig
