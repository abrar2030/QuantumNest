# QuantumNest Mobile Frontend

The mobile-optimized Progressive Web App (PWA) for QuantumNest Capital — an AI-driven
investment platform with tokenized-asset support. Built with Next.js 15 (App Router)
and sharing the same design system and backend integration as `web-frontend`, with a
mobile-first layout (bottom tab navigation, single-column pages).

## Tech stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- **TailwindCSS** with a shared design-token system (`src/app/globals.css`)
- **Radix UI / shadcn-style components** (`src/components/ui`)
- **recharts** for charts, **ethers.js** for wallet connectivity
- **react-hook-form + zod** for form validation
- **sonner** for toasts, **next-themes** for dark/light mode

## Getting started

```bash
npm install
cp .env.example .env.local   # then set NEXT_PUBLIC_API_URL
npm run dev                  # http://localhost:3000
```

The app requires the FastAPI backend in `../code/backend` to be running (see that
project's README). Set `NEXT_PUBLIC_API_URL` to point at it, e.g.:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Build & test

```bash
npm run build   # production build
npm start       # serve the production build
npm test        # jest unit tests
```

## App structure

```
src/
├── app/
│   ├── page.tsx                 # Public marketing homepage (app entry point)
│   ├── auth/                    # login, register, forgot-password, reset-password
│   ├── dashboard/                # Post-login overview
│   ├── portfolio/                # Portfolio list + /[id] detail
│   ├── market-analysis/          # Market overview + asset browser
│   ├── recommendations/          # AI market outlook, portfolio insights, sentiment, risk
│   ├── blockchain-explorer/      # Wallet, contracts, transactions, tokenized assets
│   ├── admin/                    # Admin console (role-gated)
│   ├── profile/ settings/        # Account management
│   └── privacy/ terms/           # Static legal pages
├── components/
│   ├── layout/                   # AppShell (bottom nav), PublicShell, AuthShell, etc.
│   ├── finance/                  # StatCard, charts, empty/error states
│   ├── portfolio/                # Create-portfolio & add-asset dialogs
│   ├── auth/                     # ProtectedRoute / GuestRoute guards
│   └── ui/                       # shadcn-style primitives
├── lib/
│   ├── api.tsx                   # Typed fetch client (auth header, error handling)
│   ├── auth-context.tsx          # Login/register/logout backed by /token + /users
│   ├── types.ts                  # TypeScript types mirroring backend Pydantic schemas
│   └── blockchain.tsx            # MetaMask/EIP-1193 wallet context
└── hooks/use-asset-catalog.ts    # Shared asset lookup used across pages
```

## Navigation flow

The app always starts at the public **homepage** (`/`). From there, users sign up or
sign in (`/auth/register`, `/auth/login`), which redirects to `/dashboard`. Authenticated
pages are wrapped in `<AppShell>`, which enforces auth via `<ProtectedRoute>` and renders
the bottom tab bar (Dashboard, Portfolio, Market, AI, More). The "More" sheet holds
Blockchain Explorer, Profile, Settings, and (for admins) the Admin console.

## Backend integration

This app talks directly to the FastAPI backend in `code/backend` — no separate mobile
API. Key endpoints used: `POST /token`, `POST /users/`, `GET /users/me`,
`GET|POST|PUT|DELETE /portfolio/...`, `GET /market/...`, `GET /ai/...`,
`GET /blockchain/...`, and `GET|PUT /admin/...` (admin role required). See
`src/lib/types.ts` for the full response shapes.

## Optional: Cloudflare Workers deployment

This project can also be deployed as a Cloudflare Worker via `@opennextjs/cloudflare`:

```bash
npm run build:worker
npm run preview     # local Workers runtime preview
```

Cloudflare-specific bindings live in `wrangler.toml`. This path is optional — the app
runs anywhere Next.js runs (Node.js server, Vercel, Docker, etc.) via `npm start`.
