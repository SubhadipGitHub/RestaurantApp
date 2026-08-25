/** @type {import('next').NextConfig} */

// The browser only ever talks to this origin; API calls are proxied to the
// backend from here. That keeps the session cookie first-party and removes
// CORS from the picture entirely.
//
// Read at BUILD time, so changing it on the host requires a redeploy. The
// fallback matters: an undefined value would produce the destination string
// "undefined/:path*", which fails Next's validation and breaks the build.
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'lh3.googleusercontent.com' },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        // Proxied API responses are session-scoped and must never be cached
        // at the edge.
        source: '/api/backend/:path*',
        headers: [
          { key: 'Cache-Control', value: 'no-store' },
          { key: 'x-vercel-enable-rewrite-caching', value: '0' },
        ],
      },
    ];
  },
};

export default nextConfig;
