import type { NextConfig } from 'next';

const config: NextConfig = {
  // Static export for Cloudflare Workers static assets (wrangler.jsonc serves ./out; headers live in public/_headers).
  output: 'export',
};

export default config;
