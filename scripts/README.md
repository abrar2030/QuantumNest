# QuantumNest Automation Scripts

Shell scripts that support the development workflow for the QuantumNest
monorepo: environment setup, running the full stack locally, building for
production, linting, testing, dependency health checks, and log aggregation.

All scripts are designed to be run from anywhere inside the repository — each
resolves the project root relative to its own location — but the typical
pattern is:

```bash
cd QuantumNest
./scripts/<script_name>.sh [command] [args]
```

Scripts are executable in git, but if permissions are ever lost, restore them
with:

```bash
chmod +x scripts/*.sh
```

## Scripts Overview

### 1. Setup (`setup_quantumnest_env.sh`)

One-shot setup for a fresh clone: creates the Python virtual environment,
installs backend, blockchain, and both frontends' dependencies, and creates
each component's local env file (`.env` / `.env.local`) from its own
`.env.example` if one doesn't already exist.

```bash
./scripts/setup_quantumnest_env.sh
```

### 2. Run (`run_quantumnest.sh`)

Starts the full stack for local development: the FastAPI backend
(`code/backend`, via `run_flask.py` on port 8000), a local Hardhat blockchain
node (`code/blockchain`, port 8545), the web frontend in dev mode
(`web-frontend`, port 3000), and the mobile frontend in dev mode
(`mobile-frontend`, port 3001). Press `Ctrl+C` to stop everything.

```bash
./scripts/run_quantumnest.sh
```

### 3. Build (`build.sh`)

Installs dependencies and produces a production build of both frontends
(`npm run build`), and byte-compiles the backend to catch syntax errors. Does
not start any servers.

```bash
./scripts/build.sh
```

### 4. Lint (`lint-all.sh`)

Runs formatters and linters across the whole project and auto-fixes what it
can:

- Python (`code/backend`): black, isort, flake8, pylint
- JS/TS (`web-frontend/src`, `mobile-frontend/src`, `code/blockchain`): eslint
  --fix, prettier --write
- YAML (`infrastructure/kubernetes`, `infrastructure/ansible`,
  `.github/workflows`): yamllint if installed, otherwise a Python-based
  validity check
- Terraform (`infrastructure/terraform`): `terraform fmt` + `terraform
validate`, if terraform is installed
- All text/code files: trims trailing whitespace and ensures a final newline

Every tool runs to completion regardless of what earlier tools reported (a
linter finding issues is normal, not a reason to stop early). A summary is
printed at the end, and the script exits non-zero only if some checker still
has unresolved findings.

```bash
./scripts/lint-all.sh
```

### 5. Test (`run_all_tests.sh`)

Runs the full test suite for every component — backend (`pytest`), blockchain
(`npx hardhat test`), and both frontends (`npm test`) — regardless of whether
an earlier suite failed, then prints a pass/fail summary. Exits non-zero if
any suite failed.

```bash
./scripts/run_all_tests.sh
```

### 6. Environment Variable Manager (`env_manager.sh`)

Manages the four components' local env files (`web-frontend/.env.local`,
`mobile-frontend/.env.local`, `code/backend/.env`, `code/blockchain/.env`).

**Commands:**

- `status` — check which env files exist and how many variables each has
- `template` — create any missing env files from each component's own
  `.env.example`
- `sync` — point both frontends' `NEXT_PUBLIC_API_URL` at the backend's actual
  port, and make sure the backend's `ALLOWED_ORIGINS` includes both frontends'
  dev server URLs
- `backup` — copy all four env files into a timestamped folder under
  `env_backups/`
- `restore [TIMESTAMP]` — restore env files from a previous backup
- `validate` — check that each env file has the variables the app actually
  reads (e.g. `NEXT_PUBLIC_API_URL` for the frontends; `SECRET_KEY`,
  `DATABASE_URL`, `PORT`, `ALLOWED_ORIGINS` for the backend)
- `help` — display usage

```bash
./scripts/env_manager.sh status
./scripts/env_manager.sh template
./scripts/env_manager.sh sync
./scripts/env_manager.sh backup
./scripts/env_manager.sh restore 20260716_035107
./scripts/env_manager.sh validate
```

### 7. Dependency Health Checker (`dependency_checker.sh`)

Reports on dependency health across all four components (backend, blockchain,
web-frontend, mobile-frontend). Reports are written to `dependency_reports/`.

**Commands:**

- `check` — versions of installed tools, and each component's dependency list
- `outdated` — `npm outdated` / `pip list --outdated` per component
- `security` — `npm audit` per Node component, `safety check` for the backend
- `report` — a single comprehensive report combining the above plus full
  `package.json` / `requirements.txt` contents
- `fix [component]` — reinstall dependencies cleanly (`npm ci`, `pip install
-r requirements.txt`) for one component, or all of them if none is
  specified (asks for confirmation)
- `help` — display usage

```bash
./scripts/dependency_checker.sh check
./scripts/dependency_checker.sh outdated
./scripts/dependency_checker.sh security
./scripts/dependency_checker.sh report
./scripts/dependency_checker.sh fix web-frontend
```

### 8. Log Aggregator (`log_aggregator.sh`)

Collects, searches, and analyzes log files from all four components. None of
the components write log files by default — this tool looks for a `logs/`
subdirectory in each one (`web-frontend/logs`, `mobile-frontend/logs`,
`code/backend/logs`, `code/blockchain/logs`), so redirect a component's
output there if you want to use it, e.g.:

```bash
cd code/backend && mkdir -p logs && python3 run_flask.py >> logs/app.log 2>&1
```

**Commands:**

- `collect` — copy each component's `logs/` into a timestamped folder under
  the project's own `logs/` directory
- `watch` — tail all four components' `logs/app.log` (or `node.log` for the
  blockchain node) side-by-side in a tmux session (requires tmux)
- `clean [days]` — delete collected log bundles older than N days (default 7)
- `search [term]` — grep across all collected log bundles
- `analyze` — summarize errors/warnings in the most recent collected bundle
- `help` — display usage

```bash
./scripts/log_aggregator.sh collect
./scripts/log_aggregator.sh watch
./scripts/log_aggregator.sh clean 14
./scripts/log_aggregator.sh search "database connection"
./scripts/log_aggregator.sh analyze
```

## Suggested workflow

1. `./scripts/setup_quantumnest_env.sh` — first-time setup after cloning
2. `./scripts/env_manager.sh validate` — confirm env files are configured
3. `./scripts/run_quantumnest.sh` — run everything locally
4. `./scripts/lint-all.sh` and `./scripts/run_all_tests.sh` — before pushing
   changes
5. `./scripts/dependency_checker.sh check` — periodically, to catch
   dependency drift
6. `./scripts/build.sh` — produce a production build

## Requirements

- Bash, Python 3, Node.js + npm
- Standard Unix utilities (find, grep, sed, xargs)
- Optional: tmux (for `log_aggregator.sh watch`), terraform and yamllint (for
  the corresponding checks in `lint-all.sh`; both are skipped gracefully if
  not installed)
