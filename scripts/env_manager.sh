#!/bin/bash
# QuantumNest Environment Manager
# This script automates environment variable management across all components
# of the QuantumNest project, ensuring consistent configuration.
#
# Env file locations (matches each component's own convention):
#   web-frontend/.env.local     mobile-frontend/.env.local   (Next.js apps)
#   code/backend/.env                                        (FastAPI/dotenv)
#   code/blockchain/.env                                     (Hardhat/dotenv)

set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Component directories
WEB_FRONTEND_DIR="${PROJECT_DIR}/web-frontend"
MOBILE_FRONTEND_DIR="${PROJECT_DIR}/mobile-frontend"
BACKEND_DIR="${PROJECT_DIR}/code/backend"
BLOCKCHAIN_DIR="${PROJECT_DIR}/code/blockchain"

# Env file names, one per component (see header comment for why these differ)
WEB_FRONTEND_ENV="${WEB_FRONTEND_DIR}/.env.local"
MOBILE_FRONTEND_ENV="${MOBILE_FRONTEND_DIR}/.env.local"
BACKEND_ENV="${BACKEND_DIR}/.env"
BLOCKCHAIN_ENV="${BLOCKCHAIN_DIR}/.env"

# Function to display help message
function show_help {
  echo -e "${BLUE}QuantumNest Environment Manager${NC}"
  echo "This script helps manage environment variables across all QuantumNest components."
  echo ""
  echo "Usage: ./env_manager.sh [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  status              Check status of environment files across components"
  echo "  template            Generate template env files for all components"
  echo "  sync                Synchronize common variables across components"
  echo "  backup              Backup all environment files"
  echo "  restore [TIMESTAMP] Restore environment files from backup"
  echo "  validate            Validate environment files for required variables"
  echo "  help                Display this help message"
  echo ""
  echo "Examples:"
  echo "  ./env_manager.sh status"
  echo "  ./env_manager.sh template"
  echo "  ./env_manager.sh backup"
  echo "  ./env_manager.sh restore 20250522_081530"
}

# Function to count variables in an env file (non-comment, non-blank lines)
count_vars() {
  grep -v '^#' "$1" | grep -c -v '^[[:space:]]*$' || true
}

# Function to check status of environment files
function check_status {
  echo -e "${BLUE}Checking environment file status across components...${NC}"

  local missing=0

  for entry in "Web Frontend:${WEB_FRONTEND_ENV}" "Mobile Frontend:${MOBILE_FRONTEND_ENV}" \
               "Backend:${BACKEND_ENV}" "Blockchain:${BLOCKCHAIN_ENV}"; do
    local name="${entry%%:*}"
    local path="${entry#*:}"
    if [ -f "$path" ]; then
      echo -e "${GREEN}✓ ${name} env file exists${NC}"
      echo "  Location: ${path}"
      echo "  Variables: $(count_vars "$path")"
    else
      echo -e "${RED}✗ ${name} env file missing${NC}"
      echo "  Expected location: ${path}"
      missing=$((missing + 1))
    fi
  done

  echo ""
  if [ "$missing" -eq 0 ]; then
    echo -e "${GREEN}All environment files are present.${NC}"
  else
    echo -e "${YELLOW}${missing} environment file(s) missing.${NC}"
    echo "Run './env_manager.sh template' to generate template files."
  fi
}

# Copies a component's own .env.example to its runtime env file. Each
# component owns the authoritative list of variables it needs, so we copy
# from there instead of maintaining a second, easily-outdated copy in this
# script. Falls back to a minimal inline template only if .env.example is
# missing entirely.
generate_template_for() {
  local name="$1"
  local component_dir="$2"
  local target_env="$3"
  local fallback_content="$4"

  if [ ! -d "$component_dir" ]; then
    echo -e "${YELLOW}! ${name} directory not found at ${component_dir}, skipping${NC}"
    return
  fi

  if [ -f "$target_env" ]; then
    echo -e "${YELLOW}! ${name} env file already exists, skipping${NC}"
    return
  fi

  if [ -f "${component_dir}/.env.example" ]; then
    cp "${component_dir}/.env.example" "$target_env"
    echo -e "${GREEN}✓ Created ${name} env file from .env.example${NC}"
  else
    printf '%s\n' "$fallback_content" > "$target_env"
    echo -e "${GREEN}✓ Created ${name} env file from built-in fallback template (${name} has no .env.example)${NC}"
  fi
}

# Function to generate template env files
function generate_templates {
  echo -e "${BLUE}Generating template environment files...${NC}"

  generate_template_for "Web Frontend" "$WEB_FRONTEND_DIR" "$WEB_FRONTEND_ENV" \
"# QuantumNest Web Frontend Environment Variables
# Generated on $(date)
NEXT_PUBLIC_API_URL=http://localhost:8000"

  generate_template_for "Mobile Frontend" "$MOBILE_FRONTEND_DIR" "$MOBILE_FRONTEND_ENV" \
"# QuantumNest Mobile Frontend Environment Variables
# Generated on $(date)
NEXT_PUBLIC_API_URL=http://localhost:8000"

  generate_template_for "Backend" "$BACKEND_DIR" "$BACKEND_ENV" \
"# QuantumNest Backend Environment Variables
# Generated on $(date)
ENVIRONMENT=development
DEBUG=false
SECRET_KEY=change-me-to-a-random-64-char-hex-string-in-production
API_SECRET_KEY=change-me-too
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./quantumnest.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
HOST=0.0.0.0
PORT=8000"

  generate_template_for "Blockchain" "$BLOCKCHAIN_DIR" "$BLOCKCHAIN_ENV" \
"# QuantumNest Blockchain Environment Variables
# Generated on $(date)
ETHEREUM_RPC_URL=http://localhost:8545
INFURA_API_KEY=
PRIVATE_KEY=
ETHERSCAN_API_KEY=
NETWORK=hardhat
CHAIN_ID=31337"

  echo -e "${GREEN}Template generation complete.${NC}"
  echo "Edit these files with your actual configuration values."
}

# Function to synchronize common variables across components
function sync_variables {
  echo -e "${BLUE}Synchronizing common environment variables across components...${NC}"

  local missing=0
  [ ! -f "$WEB_FRONTEND_ENV" ] && missing=$((missing + 1))
  [ ! -f "$MOBILE_FRONTEND_ENV" ] && missing=$((missing + 1))
  [ ! -f "$BACKEND_ENV" ] && missing=$((missing + 1))

  if [ "$missing" -gt 0 ]; then
    echo -e "${RED}Error: Some env files are missing.${NC}"
    echo "Run './env_manager.sh status' to check status."
    echo "Run './env_manager.sh template' to generate missing files."
    return 1
  fi

  # Extract backend port (falls back to 8000 if unset/commented out)
  local backend_port
  backend_port=$(grep "^PORT=" "$BACKEND_ENV" | tail -n1 | cut -d= -f2)
  if [ -z "$backend_port" ]; then
    backend_port=8000
    echo -e "${YELLOW}! Backend PORT not found, using default: 8000${NC}"
  fi

  # Point both frontends at the backend's actual port.
  if grep -q "^NEXT_PUBLIC_API_URL=" "$WEB_FRONTEND_ENV"; then
    sed -i "s|^NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:${backend_port}|" "$WEB_FRONTEND_ENV"
  else
    echo "NEXT_PUBLIC_API_URL=http://localhost:${backend_port}" >> "$WEB_FRONTEND_ENV"
  fi

  if grep -q "^NEXT_PUBLIC_API_URL=" "$MOBILE_FRONTEND_ENV"; then
    sed -i "s|^NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:${backend_port}|" "$MOBILE_FRONTEND_ENV"
  else
    echo "NEXT_PUBLIC_API_URL=http://localhost:${backend_port}" >> "$MOBILE_FRONTEND_ENV"
  fi

  # Make sure the backend accepts requests from both frontends' dev servers.
  local web_port=3000
  local mobile_port=3001
  if grep -q "^ALLOWED_ORIGINS=" "$BACKEND_ENV"; then
    sed -i "s|^ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=http://localhost:${web_port},http://localhost:${mobile_port}|" "$BACKEND_ENV"
  else
    echo "ALLOWED_ORIGINS=http://localhost:${web_port},http://localhost:${mobile_port}" >> "$BACKEND_ENV"
  fi

  echo -e "${GREEN}Environment variables synchronized successfully.${NC}"
}

# Function to backup environment files
function backup_env_files {
  local timestamp
  timestamp=$(date +%Y%m%d_%H%M%S)
  local backup_dir="${PROJECT_DIR}/env_backups/${timestamp}"

  echo -e "${BLUE}Backing up environment files to ${backup_dir}...${NC}"

  mkdir -p "$backup_dir"

  [ -f "$WEB_FRONTEND_ENV" ] && cp "$WEB_FRONTEND_ENV" "${backup_dir}/web-frontend.env"
  [ -f "$MOBILE_FRONTEND_ENV" ] && cp "$MOBILE_FRONTEND_ENV" "${backup_dir}/mobile-frontend.env"
  [ -f "$BACKEND_ENV" ] && cp "$BACKEND_ENV" "${backup_dir}/backend.env"
  [ -f "$BLOCKCHAIN_ENV" ] && cp "$BLOCKCHAIN_ENV" "${backup_dir}/blockchain.env"

  echo -e "${GREEN}Backup completed: ${backup_dir}${NC}"
}

# Function to restore environment files from backup
function restore_env_files {
  local timestamp="${1:-}"

  if [ -z "$timestamp" ]; then
    echo -e "${RED}Error: Timestamp required for restore.${NC}"
    echo "Available backups:"
    ls -1 "${PROJECT_DIR}/env_backups/" 2>/dev/null || echo "  No backups found."
    return 1
  fi

  local backup_dir="${PROJECT_DIR}/env_backups/${timestamp}"

  if [ ! -d "$backup_dir" ]; then
    echo -e "${RED}Error: Backup directory not found: ${backup_dir}${NC}"
    echo "Available backups:"
    ls -1 "${PROJECT_DIR}/env_backups/" 2>/dev/null || echo "  No backups found."
    return 1
  fi

  echo -e "${BLUE}Restoring environment files from ${backup_dir}...${NC}"

  [ -f "${backup_dir}/web-frontend.env" ] && cp "${backup_dir}/web-frontend.env" "$WEB_FRONTEND_ENV"
  [ -f "${backup_dir}/mobile-frontend.env" ] && cp "${backup_dir}/mobile-frontend.env" "$MOBILE_FRONTEND_ENV"
  [ -f "${backup_dir}/backend.env" ] && cp "${backup_dir}/backend.env" "$BACKEND_ENV"
  [ -f "${backup_dir}/blockchain.env" ] && cp "${backup_dir}/blockchain.env" "$BLOCKCHAIN_ENV"

  echo -e "${GREEN}Restore completed from backup: ${timestamp}${NC}"
}

# Function to validate environment files for required variables
function validate_env_files {
  echo -e "${BLUE}Validating environment files for required variables...${NC}"

  local errors=0

  for entry in "Web Frontend:${WEB_FRONTEND_ENV}:NEXT_PUBLIC_API_URL" \
               "Mobile Frontend:${MOBILE_FRONTEND_ENV}:NEXT_PUBLIC_API_URL" \
               "Backend:${BACKEND_ENV}:PORT DATABASE_URL SECRET_KEY ALLOWED_ORIGINS" \
               "Blockchain:${BLOCKCHAIN_ENV}:NETWORK PRIVATE_KEY"; do
    local name path required
    name="${entry%%:*}"
    local rest="${entry#*:}"
    path="${rest%%:*}"
    required="${rest#*:}"

    if [ -f "$path" ]; then
      echo "Checking ${name} env file..."
      for var in $required; do
        if ! grep -q "^${var}=" "$path"; then
          echo -e "${RED}  Missing required variable: ${var}${NC}"
          errors=$((errors + 1))
        fi
      done
    else
      echo -e "${RED}${name} env file missing${NC}"
      errors=$((errors + 1))
    fi
  done

  echo ""
  if [ "$errors" -eq 0 ]; then
    echo -e "${GREEN}All environment files validated successfully.${NC}"
  else
    echo -e "${RED}Found ${errors} issue(s) with environment files.${NC}"
    echo "Please fix these issues to ensure proper application functionality."
    return 1
  fi
}

# Main script execution
case "${1:-help}" in
  status)
    check_status
    ;;
  template)
    generate_templates
    ;;
  sync)
    sync_variables
    ;;
  backup)
    backup_env_files
    ;;
  restore)
    restore_env_files "${2:-}"
    ;;
  validate)
    validate_env_files
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    echo -e "${RED}Error: Unknown command '${1}'${NC}"
    show_help
    exit 1
    ;;
esac
