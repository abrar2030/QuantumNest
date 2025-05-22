#!/bin/bash
# QuantumNest Environment Manager
# This script automates environment variable management across all components
# of the QuantumNest project, ensuring consistent configuration.

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
BACKEND_DIR="${PROJECT_DIR}/backend"
BLOCKCHAIN_DIR="${PROJECT_DIR}/blockchain"

# Function to display help message
function show_help {
  echo -e "${BLUE}QuantumNest Environment Manager${NC}"
  echo "This script helps manage environment variables across all QuantumNest components."
  echo ""
  echo "Usage: ./env_manager.sh [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  status              Check status of environment files across components"
  echo "  template            Generate template .env files for all components"
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

# Function to check status of environment files
function check_status {
  echo -e "${BLUE}Checking environment file status across components...${NC}"
  
  local missing=0
  
  # Check web frontend
  if [ -f "${WEB_FRONTEND_DIR}/.env" ]; then
    echo -e "${GREEN}✓ Web Frontend .env file exists${NC}"
    echo "  Location: ${WEB_FRONTEND_DIR}/.env"
    echo "  Variables: $(grep -v '^#' "${WEB_FRONTEND_DIR}/.env" | grep -v '^$' | wc -l)"
  else
    echo -e "${RED}✗ Web Frontend .env file missing${NC}"
    echo "  Expected location: ${WEB_FRONTEND_DIR}/.env"
    missing=$((missing+1))
  fi
  
  # Check mobile frontend
  if [ -f "${MOBILE_FRONTEND_DIR}/.env" ]; then
    echo -e "${GREEN}✓ Mobile Frontend .env file exists${NC}"
    echo "  Location: ${MOBILE_FRONTEND_DIR}/.env"
    echo "  Variables: $(grep -v '^#' "${MOBILE_FRONTEND_DIR}/.env" | grep -v '^$' | wc -l)"
  else
    echo -e "${RED}✗ Mobile Frontend .env file missing${NC}"
    echo "  Expected location: ${MOBILE_FRONTEND_DIR}/.env"
    missing=$((missing+1))
  fi
  
  # Check backend
  if [ -f "${BACKEND_DIR}/.env" ]; then
    echo -e "${GREEN}✓ Backend .env file exists${NC}"
    echo "  Location: ${BACKEND_DIR}/.env"
    echo "  Variables: $(grep -v '^#' "${BACKEND_DIR}/.env" | grep -v '^$' | wc -l)"
  else
    echo -e "${RED}✗ Backend .env file missing${NC}"
    echo "  Expected location: ${BACKEND_DIR}/.env"
    missing=$((missing+1))
  fi
  
  # Check blockchain
  if [ -f "${BLOCKCHAIN_DIR}/.env" ]; then
    echo -e "${GREEN}✓ Blockchain .env file exists${NC}"
    echo "  Location: ${BLOCKCHAIN_DIR}/.env"
    echo "  Variables: $(grep -v '^#' "${BLOCKCHAIN_DIR}/.env" | grep -v '^$' | wc -l)"
  else
    echo -e "${RED}✗ Blockchain .env file missing${NC}"
    echo "  Expected location: ${BLOCKCHAIN_DIR}/.env"
    missing=$((missing+1))
  fi
  
  echo ""
  if [ $missing -eq 0 ]; then
    echo -e "${GREEN}All environment files are present.${NC}"
  else
    echo -e "${YELLOW}$missing environment file(s) missing.${NC}"
    echo "Run './env_manager.sh template' to generate template files."
  fi
}

# Function to generate template .env files
function generate_templates {
  echo -e "${BLUE}Generating template .env files...${NC}"
  
  # Web Frontend template
  if [ ! -f "${WEB_FRONTEND_DIR}/.env" ]; then
    cat > "${WEB_FRONTEND_DIR}/.env" << EOF
# QuantumNest Web Frontend Environment Variables
# Generated on $(date)

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws

# Blockchain Configuration
NEXT_PUBLIC_BLOCKCHAIN_NETWORK=localhost
NEXT_PUBLIC_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000

# Authentication
NEXT_PUBLIC_AUTH_DOMAIN=quantumnest.auth.com
NEXT_PUBLIC_AUTH_CLIENT_ID=your_client_id

# Analytics
NEXT_PUBLIC_ANALYTICS_ID=UA-XXXXXXXXX-X

# Feature Flags
NEXT_PUBLIC_ENABLE_PREDICTIONS=true
NEXT_PUBLIC_ENABLE_SOCIAL_FEATURES=true
EOF
    echo -e "${GREEN}✓ Created Web Frontend template .env file${NC}"
  else
    echo -e "${YELLOW}! Web Frontend .env already exists, skipping${NC}"
  fi
  
  # Mobile Frontend template
  if [ ! -f "${MOBILE_FRONTEND_DIR}/.env" ]; then
    cat > "${MOBILE_FRONTEND_DIR}/.env" << EOF
# QuantumNest Mobile Frontend Environment Variables
# Generated on $(date)

# API Configuration
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws

# Blockchain Configuration
EXPO_PUBLIC_BLOCKCHAIN_NETWORK=localhost
EXPO_PUBLIC_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000

# Authentication
EXPO_PUBLIC_AUTH_DOMAIN=quantumnest.auth.com
EXPO_PUBLIC_AUTH_CLIENT_ID=your_client_id

# Analytics
EXPO_PUBLIC_ANALYTICS_ID=UA-XXXXXXXXX-X

# Feature Flags
EXPO_PUBLIC_ENABLE_BIOMETRICS=true
EXPO_PUBLIC_ENABLE_PUSH_NOTIFICATIONS=true
EOF
    echo -e "${GREEN}✓ Created Mobile Frontend template .env file${NC}"
  else
    echo -e "${YELLOW}! Mobile Frontend .env already exists, skipping${NC}"
  fi
  
  # Backend template
  if [ ! -f "${BACKEND_DIR}/.env" ]; then
    cat > "${BACKEND_DIR}/.env" << EOF
# QuantumNest Backend Environment Variables
# Generated on $(date)

# Server Configuration
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:19000

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/quantumnest
REDIS_URL=redis://localhost:6379/0

# Authentication
JWT_SECRET=change_this_to_a_secure_random_string
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400

# Blockchain Configuration
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000
WALLET_PRIVATE_KEY=0000000000000000000000000000000000000000000000000000000000000000

# External Services
AI_MODEL_ENDPOINT=http://localhost:8001/predict
MARKET_DATA_API_KEY=your_api_key_here
EOF
    echo -e "${GREEN}✓ Created Backend template .env file${NC}"
  else
    echo -e "${YELLOW}! Backend .env already exists, skipping${NC}"
  fi
  
  # Blockchain template
  if [ ! -f "${BLOCKCHAIN_DIR}/.env" ]; then
    cat > "${BLOCKCHAIN_DIR}/.env" << EOF
# QuantumNest Blockchain Environment Variables
# Generated on $(date)

# Network Configuration
NETWORK=localhost
CHAIN_ID=1337

# Deployment
PRIVATE_KEY=0000000000000000000000000000000000000000000000000000000000000000
INFURA_API_KEY=your_infura_api_key
ETHERSCAN_API_KEY=your_etherscan_api_key

# Gas Settings
GAS_PRICE=auto
GAS_LIMIT=6000000

# Contract Settings
OWNER_ADDRESS=0x0000000000000000000000000000000000000000
INITIAL_SUPPLY=1000000
EOF
    echo -e "${GREEN}✓ Created Blockchain template .env file${NC}"
  else
    echo -e "${YELLOW}! Blockchain .env already exists, skipping${NC}"
  fi
  
  echo -e "${GREEN}Template generation complete.${NC}"
  echo "Edit these files with your actual configuration values."
}

# Function to synchronize common variables across components
function sync_variables {
  echo -e "${BLUE}Synchronizing common environment variables across components...${NC}"
  
  # Check if all .env files exist
  local missing=0
  [ ! -f "${WEB_FRONTEND_DIR}/.env" ] && missing=$((missing+1))
  [ ! -f "${MOBILE_FRONTEND_DIR}/.env" ] && missing=$((missing+1))
  [ ! -f "${BACKEND_DIR}/.env" ] && missing=$((missing+1))
  [ ! -f "${BLOCKCHAIN_DIR}/.env" ] && missing=$((missing+1))
  
  if [ $missing -gt 0 ]; then
    echo -e "${RED}Error: Some .env files are missing.${NC}"
    echo "Run './env_manager.sh status' to check status."
    echo "Run './env_manager.sh template' to generate missing files."
    return 1
  fi
  
  # Extract backend API URL
  local BACKEND_PORT=$(grep "^PORT=" "${BACKEND_DIR}/.env" | cut -d= -f2)
  if [ -z "$BACKEND_PORT" ]; then
    BACKEND_PORT=8000
    echo -e "${YELLOW}! Backend PORT not found, using default: 8000${NC}"
  fi
  
  # Update API URLs in frontend .env files
  sed -i "s|^NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}|" "${WEB_FRONTEND_DIR}/.env"
  sed -i "s|^NEXT_PUBLIC_WEBSOCKET_URL=.*|NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:${BACKEND_PORT}/ws|" "${WEB_FRONTEND_DIR}/.env"
  
  sed -i "s|^EXPO_PUBLIC_API_URL=.*|EXPO_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}|" "${MOBILE_FRONTEND_DIR}/.env"
  sed -i "s|^EXPO_PUBLIC_WEBSOCKET_URL=.*|EXPO_PUBLIC_WEBSOCKET_URL=ws://localhost:${BACKEND_PORT}/ws|" "${MOBILE_FRONTEND_DIR}/.env"
  
  # Extract blockchain contract address
  local CONTRACT_ADDRESS=$(grep "^CONTRACT_ADDRESS=" "${BACKEND_DIR}/.env" | cut -d= -f2)
  if [ -n "$CONTRACT_ADDRESS" ]; then
    sed -i "s|^NEXT_PUBLIC_CONTRACT_ADDRESS=.*|NEXT_PUBLIC_CONTRACT_ADDRESS=${CONTRACT_ADDRESS}|" "${WEB_FRONTEND_DIR}/.env"
    sed -i "s|^EXPO_PUBLIC_CONTRACT_ADDRESS=.*|EXPO_PUBLIC_CONTRACT_ADDRESS=${CONTRACT_ADDRESS}|" "${MOBILE_FRONTEND_DIR}/.env"
  fi
  
  # Update CORS origins in backend to include frontend URLs
  local WEB_PORT=3000
  local MOBILE_PORT=19000
  sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:${WEB_PORT},http://localhost:${MOBILE_PORT}|" "${BACKEND_DIR}/.env"
  
  echo -e "${GREEN}Environment variables synchronized successfully.${NC}"
}

# Function to backup environment files
function backup_env_files {
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local backup_dir="${PROJECT_DIR}/env_backups/${timestamp}"
  
  echo -e "${BLUE}Backing up environment files to ${backup_dir}...${NC}"
  
  mkdir -p "${backup_dir}"
  
  # Backup each .env file if it exists
  [ -f "${WEB_FRONTEND_DIR}/.env" ] && cp "${WEB_FRONTEND_DIR}/.env" "${backup_dir}/web-frontend.env"
  [ -f "${MOBILE_FRONTEND_DIR}/.env" ] && cp "${MOBILE_FRONTEND_DIR}/.env" "${backup_dir}/mobile-frontend.env"
  [ -f "${BACKEND_DIR}/.env" ] && cp "${BACKEND_DIR}/.env" "${backup_dir}/backend.env"
  [ -f "${BLOCKCHAIN_DIR}/.env" ] && cp "${BLOCKCHAIN_DIR}/.env" "${backup_dir}/blockchain.env"
  
  echo -e "${GREEN}Backup completed: ${backup_dir}${NC}"
}

# Function to restore environment files from backup
function restore_env_files {
  local timestamp=$1
  
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
  
  # Restore each .env file if backup exists
  [ -f "${backup_dir}/web-frontend.env" ] && cp "${backup_dir}/web-frontend.env" "${WEB_FRONTEND_DIR}/.env"
  [ -f "${backup_dir}/mobile-frontend.env" ] && cp "${backup_dir}/mobile-frontend.env" "${MOBILE_FRONTEND_DIR}/.env"
  [ -f "${backup_dir}/backend.env" ] && cp "${backup_dir}/backend.env" "${BACKEND_DIR}/.env"
  [ -f "${backup_dir}/blockchain.env" ] && cp "${backup_dir}/blockchain.env" "${BLOCKCHAIN_DIR}/.env"
  
  echo -e "${GREEN}Restore completed from backup: ${timestamp}${NC}"
}

# Function to validate environment files for required variables
function validate_env_files {
  echo -e "${BLUE}Validating environment files for required variables...${NC}"
  
  local errors=0
  
  # Web Frontend required variables
  if [ -f "${WEB_FRONTEND_DIR}/.env" ]; then
    echo "Checking Web Frontend .env..."
    local web_required=("NEXT_PUBLIC_API_URL" "NEXT_PUBLIC_BLOCKCHAIN_NETWORK")
    for var in "${web_required[@]}"; do
      if ! grep -q "^${var}=" "${WEB_FRONTEND_DIR}/.env"; then
        echo -e "${RED}  Missing required variable: ${var}${NC}"
        errors=$((errors+1))
      fi
    done
  else
    echo -e "${RED}Web Frontend .env file missing${NC}"
    errors=$((errors+1))
  fi
  
  # Mobile Frontend required variables
  if [ -f "${MOBILE_FRONTEND_DIR}/.env" ]; then
    echo "Checking Mobile Frontend .env..."
    local mobile_required=("EXPO_PUBLIC_API_URL" "EXPO_PUBLIC_BLOCKCHAIN_NETWORK")
    for var in "${mobile_required[@]}"; do
      if ! grep -q "^${var}=" "${MOBILE_FRONTEND_DIR}/.env"; then
        echo -e "${RED}  Missing required variable: ${var}${NC}"
        errors=$((errors+1))
      fi
    done
  else
    echo -e "${RED}Mobile Frontend .env file missing${NC}"
    errors=$((errors+1))
  fi
  
  # Backend required variables
  if [ -f "${BACKEND_DIR}/.env" ]; then
    echo "Checking Backend .env..."
    local backend_required=("PORT" "DATABASE_URL" "JWT_SECRET")
    for var in "${backend_required[@]}"; do
      if ! grep -q "^${var}=" "${BACKEND_DIR}/.env"; then
        echo -e "${RED}  Missing required variable: ${var}${NC}"
        errors=$((errors+1))
      fi
    done
  else
    echo -e "${RED}Backend .env file missing${NC}"
    errors=$((errors+1))
  fi
  
  # Blockchain required variables
  if [ -f "${BLOCKCHAIN_DIR}/.env" ]; then
    echo "Checking Blockchain .env..."
    local blockchain_required=("NETWORK" "PRIVATE_KEY")
    for var in "${blockchain_required[@]}"; do
      if ! grep -q "^${var}=" "${BLOCKCHAIN_DIR}/.env"; then
        echo -e "${RED}  Missing required variable: ${var}${NC}"
        errors=$((errors+1))
      fi
    done
  else
    echo -e "${RED}Blockchain .env file missing${NC}"
    errors=$((errors+1))
  fi
  
  echo ""
  if [ $errors -eq 0 ]; then
    echo -e "${GREEN}All environment files validated successfully.${NC}"
  else
    echo -e "${RED}Found ${errors} issues with environment files.${NC}"
    echo "Please fix these issues to ensure proper application functionality."
  fi
}

# Main script execution
case "$1" in
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
    restore_env_files "$2"
    ;;
  validate)
    validate_env_files
    ;;
  help|--help|-h)
    show_help
    ;;
  *)
    echo -e "${RED}Error: Unknown command '$1'${NC}"
    show_help
    exit 1
    ;;
esac
