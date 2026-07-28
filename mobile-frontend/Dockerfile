# ── Stage 1: Dependencies ─────────────────────────────────────────────────────
FROM node:20-slim AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ── Stage 2: Builder ──────────────────────────────────────────────────────────
FROM node:20-slim AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# NEXT_PUBLIC_* variables are inlined into the client bundle at build time,
# so the backend URL must be supplied as a build arg, not a runtime env var.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_TELEMETRY_DISABLED=1

# Note: this uses the standard `next build` (not standalone output) so as not
# to interfere with this app's other deployment path via
# @opennextjs/cloudflare (`npm run build:worker`), which expects a regular
# Next.js build. That means the runtime stage below ships full node_modules.
RUN npm run build

# ── Stage 3: Runtime ──────────────────────────────────────────────────────────
FROM node:20-slim AS runtime

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd --system --gid 1001 nodejs \
 && useradd --system --uid 1001 --gid nodejs nextjs

COPY --from=deps    --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
COPY --from=builder --chown=nextjs:nodejs /app/next.config.ts ./next.config.ts

USER nextjs

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

EXPOSE 3000

CMD ["npx", "next", "start", "-p", "3000"]
