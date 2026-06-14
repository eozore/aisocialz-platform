import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // API base URL para o BFF (svc-cockpit-api)
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

export default nextConfig;
