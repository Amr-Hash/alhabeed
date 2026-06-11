/** @type {import('next').NextConfig} */
const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig = {
  output: "standalone",
  // Keep trailing slashes so Django API routes (/api/.../) are not 308-redirected
  skipTrailingSlashRedirect: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "flagcdn.com" },
    ],
  },
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
    ];
  },
  async redirects() {
    return [
      {
        source: "/world-cup-groups",
        destination: "/tournament-groups",
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
