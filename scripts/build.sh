#!/bin/bash

# Build script for QuantumNest project
# This script builds both frontends for production and prepares the backend environment.

set -euo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
BACKEND_DIR="$PROJECT_ROOT/code/backend"
FRONTEND_DIR="$PROJECT_ROOT/web-frontend"
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
  if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    pip install -r "$BACKEND_DIR/requirements.txt" > /dev/null
  else
    echo -e "${RED}Error: Backend requirements.txt not found at $BACKEND_DIR/requirements.txt.${NC}"
    exit 1
  fi

  echo -e "${BLUE}Installing/Updating Node.js dependencies in $FRONTEND_DIR...${NC}"
  if [ -d "$FRONTEND_DIR" ]; then
    (cd "$FRONTEND_DIR" && npm install > /dev/null)
  else
    echo -e "${RED}Error: Web Frontend directory $FRONTEND_DIR not found.${NC}"
    exit 1
  fi

  echo -e "${BLUE}Installing/Updating Node.js dependencies in $MOBILE_FRONTEND_DIR...${NC}"
  if [ -d "$MOBILE_FRONTEND_DIR" ]; then
    (cd "$MOBILE_FRONTEND_DIR" && npm install > /dev/null)
  else
    echo -e "${RED}Error: Mobile Frontend directory $MOBILE_FRONTEND_DIR not found.${NC}"
    exit 1
  fi
}

# Make sure the virtual environment is deactivated no matter how the script exits.
cleanup() {
  deactivate 2>/dev/null || true
}
trap cleanup EXIT

# --- Main Execution ---

echo -e "${BLUE}Starting QuantumNest build process...${NC}"

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

# 3. Build Web Frontend
echo -e "${BLUE}Building Web Frontend for production...${NC}"
if [ ! -d "$FRONTEND_DIR" ]; then
  echo -e "${RED}Error: Web Frontend directory $FRONTEND_DIR not found.${NC}"
  exit 1
fi
(cd "$FRONTEND_DIR" && npm run build)
echo -e "${GREEN}Web Frontend build completed successfully.${NC}"

# 4. Build Mobile Frontend
echo -e "${BLUE}Building Mobile Frontend for production...${NC}"
if [ ! -d "$MOBILE_FRONTEND_DIR" ]; then
  echo -e "${RED}Error: Mobile Frontend directory $MOBILE_FRONTEND_DIR not found.${NC}"
  exit 1
fi
(cd "$MOBILE_FRONTEND_DIR" && npm run build)
echo -e "${GREEN}Mobile Frontend build completed successfully.${NC}"

# 5. Sanity-check the backend (byte-compile to catch syntax errors)
echo -e "${BLUE}Verifying backend...${NC}"
find "$BACKEND_DIR/app" -name "*.py" -print0 | xargs -0 python3 -m py_compile
echo -e "${GREEN}Backend environment ready.${NC}"

echo -e "${GREEN}QuantumNest build process completed!${NC}"
