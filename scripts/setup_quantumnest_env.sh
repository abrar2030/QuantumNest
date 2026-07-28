#!/bin/bash

# Setup script for QuantumNest project
# This script handles the initial setup of the project environment.

set -euo pipefail # Exit on error, exit on unset variable, fail on pipe error

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
BACKEND_DIR="$PROJECT_ROOT/code/backend"
BLOCKCHAIN_DIR="$PROJECT_ROOT/code/blockchain"
WEB_FRONTEND_DIR="$PROJECT_ROOT/web-frontend"
MOBILE_FRONTEND_DIR="$PROJECT_ROOT/mobile-frontend"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# --- Utility Functions ---

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to ensure Python virtual environment is set up and activated
ensure_venv() {
  if [ ! -d "$VENV_PATH" ]; then
    echo -e "${BLUE}Creating Python virtual environment at $VENV_PATH...${NC}"
    python3 -m venv "$VENV_PATH"
  fi
  # shellcheck disable=SC1091
  source "$VENV_PATH/bin/activate"
  echo -e "${GREEN}Virtual environment activated.${NC}"
}

# Function to install dependencies
install_dependencies() {
  echo -e "${BLUE}Installing/Updating Python dependencies...${NC}"
  pip install --upgrade pip setuptools wheel > /dev/null
  if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    pip install -r "$BACKEND_DIR/requirements.txt"
  else
    echo -e "${RED}Error: Backend requirements.txt not found at $BACKEND_DIR/requirements.txt. Skipping Python dependency install.${NC}"
  fi

  echo -e "${BLUE}Installing/Updating Node.js dependencies...${NC}"

  # Blockchain
  if [ -d "$BLOCKCHAIN_DIR" ]; then
    echo -e "${BLUE}Installing Blockchain dependencies in $BLOCKCHAIN_DIR...${NC}"
    (cd "$BLOCKCHAIN_DIR" && npm install)
  fi

  # Web Frontend
  if [ -d "$WEB_FRONTEND_DIR" ]; then
    echo -e "${BLUE}Installing Web Frontend dependencies in $WEB_FRONTEND_DIR...${NC}"
    (cd "$WEB_FRONTEND_DIR" && npm install)
  fi

  # Mobile Frontend
  if [ -d "$MOBILE_FRONTEND_DIR" ]; then
    echo -e "${BLUE}Installing Mobile Frontend dependencies in $MOBILE_FRONTEND_DIR...${NC}"
    (cd "$MOBILE_FRONTEND_DIR" && npm install)
  fi
}

# Copy a component's own .env.example to its local env file, if one doesn't
# already exist. Each component (backend, blockchain, web-frontend,
# mobile-frontend) ships its own .env.example — there is no single
# project-root env.example to fan out from.
setup_env_file() {
  local name="$1"
  local dir="$2"
  local target_filename="$3"

  if [ ! -d "$dir" ]; then
    return
  fi

  if [ -f "$dir/$target_filename" ]; then
    echo -e "${GREEN}✓ ${name} $target_filename already exists, leaving it as-is.${NC}"
    return
  fi

  if [ -f "$dir/.env.example" ]; then
    cp "$dir/.env.example" "$dir/$target_filename"
    echo -e "${GREEN}✓ Created ${name} $target_filename from .env.example${NC}"
  else
    echo -e "${RED}Warning: ${name} has no .env.example at $dir. Skipping.${NC}"
  fi
}

# Make sure the virtual environment is deactivated no matter how the script exits.
cleanup() {
  deactivate 2>/dev/null || true
}
trap cleanup EXIT

# --- Main Execution ---

echo -e "${BLUE}Starting QuantumNest project setup...${NC}"

# 1. Check for required tools
if ! command_exists python3; then
  echo -e "${RED}Error: python3 is required but not installed.${NC}"
  exit 1
fi
if ! command_exists npm; then
  echo -e "${RED}Error: npm is required but not installed.${NC}"
  exit 1
fi

# 2. Setup Environment and Dependencies
ensure_venv
install_dependencies

# 3. Create local env files from each component's own .env.example
echo -e "${BLUE}Setting up environment files...${NC}"
setup_env_file "Backend" "$BACKEND_DIR" ".env"
setup_env_file "Blockchain" "$BLOCKCHAIN_DIR" ".env"
setup_env_file "Web Frontend" "$WEB_FRONTEND_DIR" ".env.local"
setup_env_file "Mobile Frontend" "$MOBILE_FRONTEND_DIR" ".env.local"
echo -e "${GREEN}Please review the generated env files and update them with your configuration.${NC}"

# 4. Finalize
echo -e "${GREEN}QuantumNest project setup completed successfully!${NC}"
echo -e "${GREEN}You can now run the application using: ./scripts/run_quantumnest.sh${NC}"
