/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // FIXED: Removed deprecated `swcMinify` option (enabled by default in Next.js 14,
  // setting it explicitly causes a build warning).
  webpack: (config) => {
    config.resolve.fallback = { fs: false, net: false, tls: false };
    return config;
  },
};

module.exports = nextConfig;
