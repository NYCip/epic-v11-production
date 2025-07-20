/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://epic.pos.com',
  },
  async rewrites() {
    return [
      {
        source: '/api/control/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/control/:path*`,
      },
      {
        source: '/api/agno/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/agno/:path*`,
      },
    ]
  },
}

module.exports = nextConfig