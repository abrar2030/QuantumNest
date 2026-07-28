# QuantumNest Web Frontend

The desktop/web experience for QuantumNest Capital — an AI-driven investment platform
with tokenized-asset support. Built with Next.js 15 (App Router) and sharing the same
design system and backend integration as `mobile-frontend`, with a desktop-first layout
(collapsible sidebar navigation, multi-column pages).

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
npm run build   # production build (also type-checks and lints)
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
│   ├── layout/                   # AppShell (sidebar), PublicShell, AuthShell, etc.
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
the sidebar (Dashboard, Portfolios, Market, AI Insights, Blockchain, and — for admins —
Admin). Signing out returns to the homepage.

## Backend integration

This app talks directly to the FastAPI backend in `code/backend`. Key endpoints used:
`POST /token`, `POST /users/`, `GET /users/me`, `GET|POST|PUT|DELETE /portfolio/...`,
`GET /market/...`, `GET /ai/...`, `GET /blockchain/...`, and `GET|PUT /admin/...`
(admin role required). See `src/lib/types.ts` for the full response shapes.

## Design system

Both `web-frontend` and `mobile-frontend` share identical CSS design tokens
(`globals.css`), Tailwind config, and UI primitives, so the two apps are visually
consistent. Only the navigation chrome and page layout density differ, tuned for each
form factor.
