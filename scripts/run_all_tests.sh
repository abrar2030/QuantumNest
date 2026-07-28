#!/bin/bash

# Run All Tests script for QuantumNest project
# This script executes all unit, integration, and contract tests across the project.
#
# Unlike a plain `set -e` script, this runner intentionally keeps going even if
# one test suite fails, so a single broken suite doesn't hide failures (or
# successes) in the others. A combined summary is printed at the end, and the
# script exits non-zero if any suite failed.

set -uo pipefail

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

# Function to install dependencies. Failing to install deps for one component
# shouldn't prevent us from at least attempting the others.
install_dependencies() {
  echo -e "${BLUE}Installing/Updating Python dependencies...${NC}"
  if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    pip install -r "$BACKEND_DIR/requirements.txt" > /dev/null
  else
    echo -e "${RED}Error: Backend requirements.txt not found at $BACKEND_DIR/requirements.txt.${NC}"
  fi

  echo -e "${BLUE}Installing/Updating Node.js dependencies...${NC}"

  if [ -d "$BLOCKCHAIN_DIR" ]; then
    echo -e "${BLUE}Installing Blockchain dependencies in $BLOCKCHAIN_DIR...${NC}"
    (cd "$BLOCKCHAIN_DIR" && npm install > /dev/null)
  fi

  if [ -d "$WEB_FRONTEND_DIR" ]; then
    echo -e "${BLUE}Installing Web Frontend dependencies in $WEB_FRONTEND_DIR...${NC}"
    (cd "$WEB_FRONTEND_DIR" && npm install > /dev/null)
  fi

  if [ -d "$MOBILE_FRONTEND_DIR" ]; then
    echo -e "${BLUE}Installing Mobile Frontend dependencies in $MOBILE_FRONTEND_DIR...${NC}"
    (cd "$MOBILE_FRONTEND_DIR" && npm install > /dev/null)
  fi
}

# Track results as "Suite Name:STATUS" strings so we can print a summary table
# at the end regardless of how many suites failed.
declare -a RESULTS=()
OVERALL_STATUS=0

# Runs `command` inside `dir` and records the outcome under `label`, without
# letting a failure stop the rest of the script.
run_suite() {
  local label="$1"
  local dir="$2"
  shift 2

  echo -e "\n${BLUE}Running ${label}...${NC}"

  if [ ! -d "$dir" ]; then
    echo -e "${RED}Skipped: directory $dir not found.${NC}"
    RESULTS+=("${label}:SKIPPED (directory not found)")
    return
  fi

  if (cd "$dir" && "$@"); then
    echo -e "${GREEN}${label} passed.${NC}"
    RESULTS+=("${label}:PASSED")
  else
    echo -e "${RED}${label} FAILED.${NC}"
    RESULTS+=("${label}:FAILED")
    OVERALL_STATUS=1
  fi
}

# Make sure the virtual environment is deactivated no matter how the script exits.
cleanup() {
  deactivate 2>/dev/null || true
}
trap cleanup EXIT

# --- Main Execution ---

echo -e "${BLUE}Starting QuantumNest comprehensive test run...${NC}"

# 1. Setup Environment and Dependencies
ensure_venv
install_dependencies

# 2. Run every suite, continuing even if one fails
run_suite "Backend Tests" "$BACKEND_DIR" pytest
run_suite "Blockchain Tests" "$BLOCKCHAIN_DIR" npx hardhat test
run_suite "Web Frontend Tests" "$WEB_FRONTEND_DIR" npm test
run_suite "Mobile Frontend Tests" "$MOBILE_FRONTEND_DIR" npm test

# 3. Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
for result in "${RESULTS[@]}"; do
  name="${result%%:*}"
  status="${result#*:}"
  if [ "$status" = "PASSED" ]; then
    echo -e "${GREEN}✓ ${name}: ${status}${NC}"
  elif [ "$status" = "FAILED" ]; then
    echo -e "${RED}✗ ${name}: ${status}${NC}"
  else
    echo -e "${BLUE}– ${name}: ${status}${NC}"
  fi
done

if [ "$OVERALL_STATUS" -eq 0 ]; then
  echo -e "\n${GREEN}QuantumNest comprehensive test run completed: all suites passed!${NC}"
else
  echo -e "\n${RED}QuantumNest comprehensive test run completed with failures.${NC}"
fi

exit "$OVERALL_STATUS"
