import type { NextConfig } from "next";

/** Dev-only: proxy /api to FastAPI on localhost or an explicit remote URL from env. */
function normalizeExternalApiBase(raw: string | undefined): string | null {
  if (!raw?.trim()) return null;
  const base = raw.trim().replace(/\/$/, "");
  if (base.includes("127.0.0.1") || base.includes("localhost")) return null;
  try {
    new URL(base);
    return base;
  } catch {
    return null;
  }
}

const nextConfig: NextConfig = {
  async rewrites() {
    if (process.env.NODE_ENV !== "development") {
      return [];
    }

    const remoteDev =
      normalizeExternalApiBase(process.env.ARTEMIS_API_PROXY_TARGET) ??
      normalizeExternalApiBase(process.env.ARTEMIS_EXTERNAL_API_URL);

    if (remoteDev) {
      return [
        {
          source: "/api/:path*",
          destination: `${remoteDev}/api/:path*`,
        },
      ];
    }

    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
