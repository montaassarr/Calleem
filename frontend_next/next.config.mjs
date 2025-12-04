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
    // In Docker, API_URL is set to http://backend:8000
    // Outside Docker, fallback to localhost:8000
    const backendUrl = process.env.API_URL || 'http://localhost:8000';

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
