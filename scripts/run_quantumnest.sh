#!/bin/bash

# Run script for QuantumNest project
# This script starts the backend, local blockchain node, and both frontends
# (web on :3000, mobile on :3001) for local development.
# It is designed to be run from the project root (QuantumNest/).

set -euo pipefail # Exit on error, exit on unset variable, fail on pipe error

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
BACKEND_DIR="$PROJECT_ROOT/code/backend"
BLOCKCHAIN_DIR="$PROJECT_ROOT/code/blockchain"
WEB_FRONTEND_DIR="$PROJECT_ROOT/web-frontend"
MOBILE_FRONTEND_DIR="$PROJECT_ROOT/mobile-frontend"

WEB_FRONTEND_PORT=3000
MOBILE_FRONTEND_PORT=3001
BACKEND_PORT=8000

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

  if [ -d "$BLOCKCHAIN_DIR" ]; then
    echo -e "${BLUE}Installing/Updating Node.js dependencies in $BLOCKCHAIN_DIR...${NC}"
    (cd "$BLOCKCHAIN_DIR" && npm install > /dev/null)
  else
    echo -e "${RED}Warning: Blockchain directory $BLOCKCHAIN_DIR not found. Skipping.${NC}"
  fi

  echo -e "${BLUE}Installing/Updating Node.js dependencies in $WEB_FRONTEND_DIR...${NC}"
  if [ -d "$WEB_FRONTEND_DIR" ]; then
    (cd "$WEB_FRONTEND_DIR" && npm install > /dev/null)
  else
    echo -e "${RED}Error: Web Frontend directory $WEB_FRONTEND_DIR not found.${NC}"
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

# Ensure a component has a local env file to run with, copying from its
# .env.example if one doesn't already exist. Never overwrites an existing file.
ensure_env_file() {
  local dir="$1"
  local filename="$2"
  if [ ! -f "$dir/$filename" ] && [ -f "$dir/.env.example" ]; then
    cp "$dir/.env.example" "$dir/$filename"
    echo -e "${BLUE}Created $dir/$filename from .env.example${NC}"
  fi
}

# --- Main Execution ---

echo -e "${BLUE}Starting QuantumNest application...${NC}"

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
ensure_env_file "$WEB_FRONTEND_DIR" ".env.local"
ensure_env_file "$MOBILE_FRONTEND_DIR" ".env.local"
ensure_env_file "$BACKEND_DIR" ".env"

# PIDs of background services, populated as they start.
BACKEND_PID=""
BLOCKCHAIN_PID=""
WEB_FRONTEND_PID=""
MOBILE_FRONTEND_PID=""

# 3. Start Backend Server
echo -e "${BLUE}Starting backend server on port ${BACKEND_PORT}...${NC}"
(cd "$BACKEND_DIR" && python3 run_flask.py) &
BACKEND_PID=$!

# 4. Start Local Blockchain Node (Hardhat)
if [ -d "$BLOCKCHAIN_DIR" ]; then
  echo -e "${BLUE}Starting local blockchain node...${NC}"
  (cd "$BLOCKCHAIN_DIR" && npx hardhat node) &
  BLOCKCHAIN_PID=$!
else
  echo -e "${RED}Warning: Blockchain directory not found. Skipping blockchain node.${NC}"
fi

# Wait for backend and blockchain to initialize (simple sleep for demonstration)
echo -e "${BLUE}Waiting for services to initialize...${NC}"
sleep 8

# 5. Start Web Frontend (dev server)
echo -e "${BLUE}Starting web frontend on port ${WEB_FRONTEND_PORT}...${NC}"
(cd "$WEB_FRONTEND_DIR" && npm run dev -- -p "$WEB_FRONTEND_PORT") &
WEB_FRONTEND_PID=$!

# 6. Start Mobile Frontend (dev server, separate port)
echo -e "${BLUE}Starting mobile frontend on port ${MOBILE_FRONTEND_PORT}...${NC}"
(cd "$MOBILE_FRONTEND_DIR" && npm run dev -- -p "$MOBILE_FRONTEND_PORT") &
MOBILE_FRONTEND_PID=$!

# 7. Handle graceful shutdown
function cleanup {
  echo -e "\n${BLUE}Stopping services...${NC}"
  for pid in "$MOBILE_FRONTEND_PID" "$WEB_FRONTEND_PID" "$BLOCKCHAIN_PID" "$BACKEND_PID"; do
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  deactivate 2>/dev/null || true
  echo -e "${GREEN}All services stopped${NC}"
  exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${GREEN}QuantumNest application is running!${NC}"
echo -e "${GREEN}Backend running with PID: ${BACKEND_PID} (http://localhost:${BACKEND_PORT}, docs at /docs)${NC}"
[ -n "$BLOCKCHAIN_PID" ] && echo -e "${GREEN}Blockchain node running with PID: ${BLOCKCHAIN_PID} (http://localhost:8545)${NC}"
echo -e "${GREEN}Web frontend running with PID: ${WEB_FRONTEND_PID} (http://localhost:${WEB_FRONTEND_PORT})${NC}"
echo -e "${GREEN}Mobile frontend running with PID: ${MOBILE_FRONTEND_PID} (http://localhost:${MOBILE_FRONTEND_PORT})${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"

# Keep script running
wait
