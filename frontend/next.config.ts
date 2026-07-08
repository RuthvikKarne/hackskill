import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for production Docker builds
  // Required for the multi-stage Dockerfile (runner stage uses node server.js)
  output: "standalone",

  // Recommended production settings
  poweredByHeader: false,
  reactStrictMode: true,

  // Image optimisation domains (add your production domain here)
  images: {
    domains: [],
    remotePatterns: [],
  },
};

export default nextConfig;
