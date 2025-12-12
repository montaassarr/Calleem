/** @type {import('next').NextConfig} */
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
