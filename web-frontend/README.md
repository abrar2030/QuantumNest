# QuantumNest Web Frontend

The desktop/web experience for QuantumNest Capital, an AI-driven investment platform
with tokenized-asset support. Built with Next.js 15 (App Router) and sharing the same
design system and backend integration as `mobile-frontend`, with a desktop-first layout
(collapsible sidebar navigation, multi-column pages).

## Tech stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- **TailwindCSS** with a shared design-token system (`src/app/globals.css`)
- **Radix UI / shadcn-style components** (`src/components/ui`)
- **recharts** and **chart.js** for charts, **ethers.js** for wallet connectivity
- **react-hook-form + zod** for form validation
- **sonner** for toasts, **next-themes** for dark/light mode (dark by default)

## Getting started

```bash
npm install
npm run dev   # http://localhost:3000
```

The app requires the FastAPI backend in `../code/backend` to be running (see that
project's README).

### Environment variables

There is currently no `.env.example` committed in this directory (`.gitignore` excludes
`.env*` files), so create `.env.local` yourself if you need to point at a backend other
than the default:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`NEXT_PUBLIC_API_URL` is the only environment variable the app reads (see
`src/lib/api.tsx`). If it is not set, the app falls back to `http://localhost:8000`
automatically, so local development against a locally running backend works without
any `.env.local` file at all. Because it is a `NEXT_PUBLIC_*` variable it is inlined
into the client bundle at build time, so for a production build it must be set before
running `npm run build`, not just at runtime.

### Build & test

```bash
npm run build   # production build (also type-checks and lints)
npm start       # serve the production build
npm test        # jest unit tests
npm run lint     # ESLint only
```

Two ESLint config files exist in this directory: `eslint.config.mjs` (flat config,
used by the installed ESLint 9 and by `next lint`) and a legacy `.eslintrc.js`. The
flat config is the one actually applied; the legacy file is unused and can be removed
if you want to tidy the directory.

## App structure

```
src/
├── app/
│   ├── page.tsx                  # Public marketing homepage (app entry point)
│   ├── auth/                     # login, register, forgot-password, reset-password
│   ├── dashboard/                # Post-login overview
│   ├── portfolio/                # Portfolio list + /[id] detail
│   ├── market-analysis/          # Market overview + asset browser
│   ├── recommendations/          # AI market outlook, portfolio insights, sentiment, risk
│   ├── blockchain-explorer/      # Wallet, contracts, transactions, tokenized assets
│   ├── admin/                    # Admin console (role-gated)
│   ├── profile/ settings/        # Account management
│   ├── privacy/ terms/           # Static legal pages
│   ├── layout.tsx                # Root layout, fonts, metadata
│   ├── providers.tsx             # Theme, API, auth, and blockchain context providers
│   └── globals.css               # Design tokens and base styles (shared with mobile-frontend)
├── components/
│   ├── layout/                   # AppShell (sidebar), PublicShell, AuthShell, footer, user menu
│   ├── finance/                  # StatCard, charts, page header, empty/error states
│   ├── portfolio/                # Create-portfolio and add-asset dialogs
│   ├── auth/                     # ProtectedRoute / GuestRoute guards
│   └── ui/                       # shadcn-style primitives
├── lib/
│   ├── api.tsx                   # Typed fetch client (auth header, error handling)
│   ├── auth-context.tsx          # Login/register/logout backed by /token + /users
│   ├── blockchain.tsx            # MetaMask/EIP-1193 wallet context
│   ├── types.ts                  # TypeScript types mirroring backend Pydantic schemas
│   ├── nav-items.ts              # Sidebar navigation items, including the admin-only entry
│   ├── settings.ts               # Local, browser-only account settings helpers
│   ├── utils.ts                  # Shared helpers (className merging, formatting)
│   └── __tests__/                # Jest tests for api.tsx and utils.ts
└── hooks/
    ├── use-asset-catalog.ts      # Shared asset lookup used across pages
    └── use-mobile.tsx            # Responsive breakpoint hook
```

`styles/globals.css` at the project root is a stale, unused file left over from an
earlier layout. It is not imported anywhere; the active stylesheet is
`src/app/globals.css`. It is safe to delete.

## Navigation flow

The app always starts at the public **homepage** (`/`). From there, users sign up or
sign in (`/auth/register`, `/auth/login`), which redirects to `/dashboard`. Authenticated
pages are wrapped in `<AppShell>`, which enforces auth via `<ProtectedRoute>` and renders
the sidebar (Dashboard, Portfolios, Market, AI Insights, Blockchain, and, for admins,
Admin). Signing out returns to the homepage.

## Backend integration

This app talks directly to the FastAPI backend in `code/backend`. Key endpoints used:
`POST /token`, `POST /users/`, `GET /users/me`, `POST /users/password-reset/request`,
`POST /users/password-reset/confirm`, `GET|POST|PUT|DELETE /portfolio/...`,
`GET /market/...`, `GET /ai/...`, `GET /blockchain/...`, and `GET|POST|PUT /admin/...`
(admin role required). See `src/lib/types.ts` for the full response shapes.

## Design system

Both `web-frontend` and `mobile-frontend` share byte-identical CSS design tokens
(`globals.css`) and Tailwind config, so the two apps are visually consistent. Only the
navigation chrome and page layout density differ, tuned for each form factor.

## Docker

A multi-stage `Dockerfile` is included (dependencies, build, then a minimal
`node:20-slim` runtime running as a non-root user, using Next's `output: "standalone"`
mode). Build with:

```bash
docker build --build-arg NEXT_PUBLIC_API_URL=https://your-api.example.com -t quantumnest-web .
```

Note: the final stage copies a `public/` directory into the image, but this project
does not currently have one. Add a `public/` folder (even with just a placeholder file)
before running `docker build`, or remove that `COPY` line from the Dockerfile if you do
not need one.
