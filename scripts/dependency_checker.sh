#!/bin/bash
# QuantumNest Dependency Health Checker
# This script checks the health and versions of all dependencies
# across the QuantumNest project components.

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

# Output directory for reports
REPORTS_DIR="${PROJECT_DIR}/dependency_reports"
mkdir -p "$REPORTS_DIR"

# Function to display help message
function show_help {
  echo -e "${BLUE}QuantumNest Dependency Health Checker${NC}"
  echo "This script checks the health and versions of all dependencies across components."
  echo ""
  echo "Usage: ./dependency_checker.sh [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  check                Check all dependencies across components"
  echo "  outdated             Check for outdated dependencies"
  echo "  security             Run security audit on dependencies"
  echo "  report               Generate comprehensive dependency report"
  echo "  fix [component]      Attempt to fix dependency issues (optional: specify component)"
  echo "  help                 Display this help message"
  echo ""
  echo "Examples:"
  echo "  ./dependency_checker.sh check"
  echo "  ./dependency_checker.sh outdated"
  echo "  ./dependency_checker.sh security"
  echo "  ./dependency_checker.sh report"
  echo "  ./dependency_checker.sh fix web-frontend"
}

# Function to check if a command exists
function command_exists {
  command -v "$1" &> /dev/null
}

# Function to check all dependencies
function check_dependencies {
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local report_file="${REPORTS_DIR}/dependency_check_${timestamp}.txt"
  
  echo -e "${BLUE}Checking dependencies across all components...${NC}"
  
  {
    echo "QuantumNest Dependency Check Report"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
  } > "$report_file"
  
  # Check Node.js and npm versions
  echo "Checking Node.js environment..."
  {
    echo "## Node.js Environment"
    echo "----------------------------------------"
    
    if command_exists node; then
      echo "Node.js: $(node --version)"
    else
      echo "Node.js: Not installed"
    fi
    
    if command_exists npm; then
      echo "npm: $(npm --version)"
    else
      echo "npm: Not installed"
    fi
    
    if command_exists pnpm; then
      echo "pnpm: $(pnpm --version)"
    else
      echo "pnpm: Not installed"
    fi
    
    if command_exists yarn; then
      echo "yarn: $(yarn --version)"
    else
      echo "yarn: Not installed"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Python environment
  echo "Checking Python environment..."
  {
    echo "## Python Environment"
    echo "----------------------------------------"
    
    if command_exists python3; then
      echo "Python: $(python3 --version)"
    else
      echo "Python: Not installed"
    fi
    
    if command_exists pip3; then
      echo "pip: $(pip3 --version)"
    else
      echo "pip: Not installed"
    fi
    
    if [ -d "${PROJECT_DIR}/venv" ]; then
      echo "Virtual environment: Present at ${PROJECT_DIR}/venv"
    else
      echo "Virtual environment: Not found"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Web Frontend dependencies
  echo "Checking Web Frontend dependencies..."
  {
    echo "## Web Frontend Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${WEB_FRONTEND_DIR}/package.json" ]; then
      echo "package.json: Present"
      
      if [ -d "${WEB_FRONTEND_DIR}/node_modules" ]; then
        echo "node_modules: Present"
        echo "Installed packages: $(find "${WEB_FRONTEND_DIR}/node_modules" -maxdepth 1 -type d | wc -l) (including node_modules itself)"
      else
        echo "node_modules: Not found (dependencies not installed)"
      fi
      
      # Extract and display key dependencies
      echo ""
      echo "Key dependencies:"
      grep -A 20 '"dependencies"' "${WEB_FRONTEND_DIR}/package.json" | grep -v '"dependencies"' | grep -v '}' | sed 's/[",]//g' | sed 's/^ *//g'
    else
      echo "package.json: Not found"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Mobile Frontend dependencies
  echo "Checking Mobile Frontend dependencies..."
  {
    echo "## Mobile Frontend Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
      echo "package.json: Present"
      
      if [ -d "${MOBILE_FRONTEND_DIR}/node_modules" ]; then
        echo "node_modules: Present"
        echo "Installed packages: $(find "${MOBILE_FRONTEND_DIR}/node_modules" -maxdepth 1 -type d | wc -l) (including node_modules itself)"
      else
        echo "node_modules: Not found (dependencies not installed)"
      fi
      
      # Extract and display key dependencies
      echo ""
      echo "Key dependencies:"
      grep -A 20 '"dependencies"' "${MOBILE_FRONTEND_DIR}/package.json" | grep -v '"dependencies"' | grep -v '}' | sed 's/[",]//g' | sed 's/^ *//g'
    else
      echo "package.json: Not found"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Backend dependencies
  echo "Checking Backend dependencies..."
  {
    echo "## Backend Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
      echo "requirements.txt: Present"
      echo "Required packages: $(wc -l < "${BACKEND_DIR}/requirements.txt")"
      
      if [ -d "${PROJECT_DIR}/venv" ]; then
        echo ""
        echo "Installed packages (top 10):"
        source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && pip list --format=columns | head -n 12 || echo "Could not activate virtual environment"
        deactivate 2>/dev/null || true
      else
        echo "Virtual environment not found, cannot check installed packages"
      fi
    else
      echo "requirements.txt: Not found"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Blockchain dependencies
  echo "Checking Blockchain dependencies..."
  {
    echo "## Blockchain Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${BLOCKCHAIN_DIR}/package.json" ]; then
      echo "package.json: Present"
      
      if [ -d "${BLOCKCHAIN_DIR}/node_modules" ]; then
        echo "node_modules: Present"
        echo "Installed packages: $(find "${BLOCKCHAIN_DIR}/node_modules" -maxdepth 1 -type d | wc -l) (including node_modules itself)"
      else
        echo "node_modules: Not found (dependencies not installed)"
      fi
      
      # Extract and display key dependencies
      echo ""
      echo "Key dependencies:"
      grep -A 20 '"dependencies"' "${BLOCKCHAIN_DIR}/package.json" | grep -v '"dependencies"' | grep -v '}' | sed 's/[",]//g' | sed 's/^ *//g'
    else
      echo "package.json: Not found"
    fi
    
    echo ""
  } >> "$report_file"
  
  echo -e "${GREEN}Dependency check complete.${NC}"
  echo "Report saved to: $report_file"
}

# Function to check for outdated dependencies
function check_outdated_dependencies {
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local report_file="${REPORTS_DIR}/outdated_dependencies_${timestamp}.txt"
  
  echo -e "${BLUE}Checking for outdated dependencies...${NC}"
  
  {
    echo "QuantumNest Outdated Dependencies Report"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
  } > "$report_file"
  
  # Check Web Frontend outdated dependencies
  echo "Checking Web Frontend outdated dependencies..."
  {
    echo "## Web Frontend Outdated Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${WEB_FRONTEND_DIR}/package.json" ]; then
      if [ -d "${WEB_FRONTEND_DIR}/node_modules" ]; then
        echo "Running npm outdated in ${WEB_FRONTEND_DIR}..."
        echo ""
        (cd "${WEB_FRONTEND_DIR}" && npm outdated --depth=0) || echo "Failed to check outdated dependencies"
      else
        echo "node_modules not found. Please run 'npm install' in ${WEB_FRONTEND_DIR} first."
      fi
    else
      echo "package.json not found in ${WEB_FRONTEND_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Mobile Frontend outdated dependencies
  echo "Checking Mobile Frontend outdated dependencies..."
  {
    echo "## Mobile Frontend Outdated Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
      if [ -d "${MOBILE_FRONTEND_DIR}/node_modules" ]; then
        echo "Running pnpm outdated in ${MOBILE_FRONTEND_DIR}..."
        echo ""
        if command_exists pnpm; then
          (cd "${MOBILE_FRONTEND_DIR}" && pnpm outdated) || echo "Failed to check outdated dependencies"
        else
          echo "pnpm not installed. Please install pnpm or use npm/yarn instead."
        fi
      else
        echo "node_modules not found. Please run 'pnpm install' in ${MOBILE_FRONTEND_DIR} first."
      fi
    else
      echo "package.json not found in ${MOBILE_FRONTEND_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Backend outdated dependencies
  echo "Checking Backend outdated dependencies..."
  {
    echo "## Backend Outdated Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
      if [ -d "${PROJECT_DIR}/venv" ]; then
        echo "Checking outdated Python packages..."
        echo ""
        source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && pip list --outdated || echo "Could not activate virtual environment"
        deactivate 2>/dev/null || true
      else
        echo "Virtual environment not found. Please run 'python -m venv venv' in ${PROJECT_DIR} first."
      fi
    else
      echo "requirements.txt not found in ${BACKEND_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Check Blockchain outdated dependencies
  echo "Checking Blockchain outdated dependencies..."
  {
    echo "## Blockchain Outdated Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${BLOCKCHAIN_DIR}/package.json" ]; then
      if [ -d "${BLOCKCHAIN_DIR}/node_modules" ]; then
        echo "Running npm outdated in ${BLOCKCHAIN_DIR}..."
        echo ""
        (cd "${BLOCKCHAIN_DIR}" && npm outdated --depth=0) || echo "Failed to check outdated dependencies"
      else
        echo "node_modules not found. Please run 'npm install' in ${BLOCKCHAIN_DIR} first."
      fi
    else
      echo "package.json not found in ${BLOCKCHAIN_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  echo -e "${GREEN}Outdated dependency check complete.${NC}"
  echo "Report saved to: $report_file"
}

# Function to run security audit on dependencies
function security_audit {
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local report_file="${REPORTS_DIR}/security_audit_${timestamp}.txt"
  
  echo -e "${BLUE}Running security audit on dependencies...${NC}"
  
  {
    echo "QuantumNest Security Audit Report"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
  } > "$report_file"
  
  # Audit Web Frontend dependencies
  echo "Auditing Web Frontend dependencies..."
  {
    echo "## Web Frontend Security Audit"
    echo "----------------------------------------"
    
    if [ -f "${WEB_FRONTEND_DIR}/package.json" ]; then
      if [ -d "${WEB_FRONTEND_DIR}/node_modules" ]; then
        echo "Running npm audit in ${WEB_FRONTEND_DIR}..."
        echo ""
        (cd "${WEB_FRONTEND_DIR}" && npm audit) || echo "Vulnerabilities found or audit failed"
      else
        echo "node_modules not found. Please run 'npm install' in ${WEB_FRONTEND_DIR} first."
      fi
    else
      echo "package.json not found in ${WEB_FRONTEND_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Audit Mobile Frontend dependencies
  echo "Auditing Mobile Frontend dependencies..."
  {
    echo "## Mobile Frontend Security Audit"
    echo "----------------------------------------"
    
    if [ -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
      if [ -d "${MOBILE_FRONTEND_DIR}/node_modules" ]; then
        echo "Running pnpm audit in ${MOBILE_FRONTEND_DIR}..."
        echo ""
        if command_exists pnpm; then
          (cd "${MOBILE_FRONTEND_DIR}" && pnpm audit) || echo "Vulnerabilities found or audit failed"
        else
          echo "pnpm not installed. Please install pnpm or use npm/yarn instead."
        fi
      else
        echo "node_modules not found. Please run 'pnpm install' in ${MOBILE_FRONTEND_DIR} first."
      fi
    else
      echo "package.json not found in ${MOBILE_FRONTEND_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Audit Backend dependencies
  echo "Auditing Backend dependencies..."
  {
    echo "## Backend Security Audit"
    echo "----------------------------------------"
    
    if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
      if [ -d "${PROJECT_DIR}/venv" ]; then
        echo "Checking Python packages with safety..."
        echo ""
        if command_exists safety; then
          source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && safety check || echo "Vulnerabilities found or safety check failed"
          deactivate 2>/dev/null || true
        else
          echo "safety not installed. Installing safety..."
          source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && pip install safety && safety check || echo "Could not install or run safety"
          deactivate 2>/dev/null || true
        fi
      else
        echo "Virtual environment not found. Please run 'python -m venv venv' in ${PROJECT_DIR} first."
      fi
    else
      echo "requirements.txt not found in ${BACKEND_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Audit Blockchain dependencies
  echo "Auditing Blockchain dependencies..."
  {
    echo "## Blockchain Security Audit"
    echo "----------------------------------------"
    
    if [ -f "${BLOCKCHAIN_DIR}/package.json" ]; then
      if [ -d "${BLOCKCHAIN_DIR}/node_modules" ]; then
        echo "Running npm audit in ${BLOCKCHAIN_DIR}..."
        echo ""
        (cd "${BLOCKCHAIN_DIR}" && npm audit) || echo "Vulnerabilities found or audit failed"
      else
        echo "node_modules not found. Please run 'npm install' in ${BLOCKCHAIN_DIR} first."
      fi
    else
      echo "package.json not found in ${BLOCKCHAIN_DIR}"
    fi
    
    echo ""
  } >> "$report_file"
  
  echo -e "${GREEN}Security audit complete.${NC}"
  echo "Report saved to: $report_file"
}

# Function to generate comprehensive dependency report
function generate_report {
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local report_file="${REPORTS_DIR}/comprehensive_report_${timestamp}.txt"
  
  echo -e "${BLUE}Generating comprehensive dependency report...${NC}"
  
  {
    echo "QuantumNest Comprehensive Dependency Report"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
    echo "This report provides a comprehensive overview of all dependencies"
    echo "across the QuantumNest project components."
    echo ""
  } > "$report_file"
  
  # System information
  {
    echo "## System Information"
    echo "----------------------------------------"
    echo "Operating System: $(uname -s) $(uname -r)"
    echo "Architecture: $(uname -m)"
    echo ""
    
    if command_exists node; then
      echo "Node.js: $(node --version)"
    else
      echo "Node.js: Not installed"
    fi
    
    if command_exists npm; then
      echo "npm: $(npm --version)"
    else
      echo "npm: Not installed"
    fi
    
    if command_exists pnpm; then
      echo "pnpm: $(pnpm --version)"
    else
      echo "pnpm: Not installed"
    fi
    
    if command_exists yarn; then
      echo "yarn: $(yarn --version)"
    else
      echo "yarn: Not installed"
    fi
    
    if command_exists python3; then
      echo "Python: $(python3 --version)"
    else
      echo "Python: Not installed"
    fi
    
    if command_exists pip3; then
      echo "pip: $(pip3 --version)"
    else
      echo "pip: Not installed"
    fi
    
    echo ""
  } >> "$report_file"
  
  # Web Frontend dependencies
  {
    echo "## Web Frontend Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${WEB_FRONTEND_DIR}/package.json" ]; then
      echo "### package.json"
      echo "```json"
      cat "${WEB_FRONTEND_DIR}/package.json"
      echo "```"
      echo ""
      
      if [ -d "${WEB_FRONTEND_DIR}/node_modules" ]; then
        echo "### Installed Dependencies"
        echo "Total packages: $(find "${WEB_FRONTEND_DIR}/node_modules" -maxdepth 1 -type d | wc -l) (including node_modules itself)"
        echo ""
        
        echo "### Top-level Dependencies"
        (cd "${WEB_FRONTEND_DIR}" && npm list --depth=0) || echo "Failed to list dependencies"
        echo ""
      else
        echo "node_modules not found. Dependencies not installed."
        echo ""
      fi
    else
      echo "package.json not found in ${WEB_FRONTEND_DIR}"
      echo ""
    fi
  } >> "$report_file"
  
  # Mobile Frontend dependencies
  {
    echo "## Mobile Frontend Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
      echo "### package.json"
      echo "```json"
      cat "${MOBILE_FRONTEND_DIR}/package.json"
      echo "```"
      echo ""
      
      if [ -d "${MOBILE_FRONTEND_DIR}/node_modules" ]; then
        echo "### Installed Dependencies"
        echo "Total packages: $(find "${MOBILE_FRONTEND_DIR}/node_modules" -maxdepth 1 -type d | wc -l) (including node_modules itself)"
        echo ""
        
        echo "### Top-level Dependencies"
        if command_exists pnpm; then
          (cd "${MOBILE_FRONTEND_DIR}" && pnpm list) || echo "Failed to list dependencies"
        else
          echo "pnpm not installed. Cannot list dependencies."
        fi
        echo ""
      else
        echo "node_modules not found. Dependencies not installed."
        echo ""
      fi
    else
      echo "package.json not found in ${MOBILE_FRONTEND_DIR}"
      echo ""
    fi
  } >> "$report_file"
  
  # Backend dependencies
  {
    echo "## Backend Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
      echo "### requirements.txt"
      echo "```"
      cat "${BACKEND_DIR}/requirements.txt"
      echo "```"
      echo ""
      
      if [ -d "${PROJECT_DIR}/venv" ]; then
        echo "### Installed Packages"
        source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && pip list || echo "Could not activate virtual environment"
        deactivate 2>/dev/null || true
        echo ""
      else
        echo "Virtual environment not found. Cannot list installed packages."
        echo ""
      fi
    else
      echo "requirements.txt not found in ${BACKEND_DIR}"
      echo ""
    fi
  } >> "$report_file"
  
  # Blockchain dependencies
  {
    echo "## Blockchain Dependencies"
    echo "----------------------------------------"
    
    if [ -f "${BLOCKCHAIN_DIR}/package.json" ]; then
      echo "### package.json"
      echo "```json"
      cat "${BLOCKCHAIN_DIR}/package.json"
      echo "```"
      echo ""
      
      if [ -d "${BLOCKCHAIN_DIR}/node_modules" ]; then
        echo "### Installed Dependencies"
        echo "Total packages: $(find "${BLOCKCHAIN_DIR}/node_modules" -maxdepth 1 -type d | wc -l) (including node_modules itself)"
        echo ""
        
        echo "### Top-level Dependencies"
        (cd "${BLOCKCHAIN_DIR}" && npm list --depth=0) || echo "Failed to list dependencies"
        echo ""
      else
        echo "node_modules not found. Dependencies not installed."
        echo ""
      fi
    else
      echo "package.json not found in ${BLOCKCHAIN_DIR}"
      echo ""
    fi
  } >> "$report_file"
  
  # Dependency visualization
  {
    echo "## Dependency Visualization"
    echo "----------------------------------------"
    echo "To visualize dependencies, consider using tools like:"
    echo "- npm-dependency-graph"
    echo "- dependency-cruiser"
    echo "- pipdeptree (for Python)"
    echo ""
    echo "Example commands:"
    echo "```bash"
    echo "# For JavaScript/TypeScript projects"
    echo "npx dependency-cruiser --output-type dot web-frontend | dot -T svg > web-frontend-dependencies.svg"
    echo ""
    echo "# For Python projects"
    echo "pip install pipdeptree"
    echo "pipdeptree --graph-output svg > backend-dependencies.svg"
    echo "```"
    echo ""
  } >> "$report_file"
  
  # Recommendations
  {
    echo "## Recommendations"
    echo "----------------------------------------"
    echo "1. Regularly update dependencies to benefit from security patches and new features"
    echo "2. Use dependency locking (package-lock.json, yarn.lock, pnpm-lock.yaml, pip-compile)"
    echo "3. Run security audits before deploying to production"
    echo "4. Consider using tools like Dependabot or Renovate for automated updates"
    echo "5. Implement a dependency update policy (e.g., weekly, monthly)"
    echo ""
  } >> "$report_file"
  
  echo -e "${GREEN}Comprehensive report generated.${NC}"
  echo "Report saved to: $report_file"
}

# Function to attempt to fix dependency issues
function fix_dependencies {
  local component=$1
  
  if [ -z "$component" ]; then
    echo -e "${YELLOW}No component specified, will attempt to fix all components.${NC}"
    read -p "Continue? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
      echo "Operation cancelled."
      return 0
    fi
    
    echo -e "${BLUE}Attempting to fix dependencies for all components...${NC}"
    
    # Fix Web Frontend
    echo "Fixing Web Frontend dependencies..."
    if [ -f "${WEB_FRONTEND_DIR}/package.json" ]; then
      (cd "${WEB_FRONTEND_DIR}" && npm ci) || echo "Failed to fix Web Frontend dependencies"
    else
      echo "package.json not found in ${WEB_FRONTEND_DIR}"
    fi
    
    # Fix Mobile Frontend
    echo "Fixing Mobile Frontend dependencies..."
    if [ -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
      if command_exists pnpm; then
        (cd "${MOBILE_FRONTEND_DIR}" && pnpm install --frozen-lockfile) || echo "Failed to fix Mobile Frontend dependencies"
      else
        echo "pnpm not installed. Please install pnpm or use npm/yarn instead."
      fi
    else
      echo "package.json not found in ${MOBILE_FRONTEND_DIR}"
    fi
    
    # Fix Backend
    echo "Fixing Backend dependencies..."
    if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
      if [ ! -d "${PROJECT_DIR}/venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "${PROJECT_DIR}/venv"
      fi
      source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && pip install -r "${BACKEND_DIR}/requirements.txt" || echo "Failed to fix Backend dependencies"
      deactivate 2>/dev/null || true
    else
      echo "requirements.txt not found in ${BACKEND_DIR}"
    fi
    
    # Fix Blockchain
    echo "Fixing Blockchain dependencies..."
    if [ -f "${BLOCKCHAIN_DIR}/package.json" ]; then
      (cd "${BLOCKCHAIN_DIR}" && npm ci) || echo "Failed to fix Blockchain dependencies"
    else
      echo "package.json not found in ${BLOCKCHAIN_DIR}"
    fi
    
    echo -e "${GREEN}Dependency fixing attempts completed.${NC}"
    echo "Run './dependency_checker.sh check' to verify the results."
    
  else
    # Fix specific component
    case "$component" in
      web-frontend|web|frontend)
        echo -e "${BLUE}Attempting to fix Web Frontend dependencies...${NC}"
        if [ -f "${WEB_FRONTEND_DIR}/package.json" ]; then
          (cd "${WEB_FRONTEND_DIR}" && npm ci) || echo "Failed to fix Web Frontend dependencies"
        else
          echo "package.json not found in ${WEB_FRONTEND_DIR}"
        fi
        ;;
      
      mobile-frontend|mobile)
        echo -e "${BLUE}Attempting to fix Mobile Frontend dependencies...${NC}"
        if [ -f "${MOBILE_FRONTEND_DIR}/package.json" ]; then
          if command_exists pnpm; then
            (cd "${MOBILE_FRONTEND_DIR}" && pnpm install --frozen-lockfile) || echo "Failed to fix Mobile Frontend dependencies"
          else
            echo "pnpm not installed. Please install pnpm or use npm/yarn instead."
          fi
        else
          echo "package.json not found in ${MOBILE_FRONTEND_DIR}"
        fi
        ;;
      
      backend|api)
        echo -e "${BLUE}Attempting to fix Backend dependencies...${NC}"
        if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
          if [ ! -d "${PROJECT_DIR}/venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv "${PROJECT_DIR}/venv"
          fi
          source "${PROJECT_DIR}/venv/bin/activate" 2>/dev/null && pip install -r "${BACKEND_DIR}/requirements.txt" || echo "Failed to fix Backend dependencies"
          deactivate 2>/dev/null || true
        else
          echo "requirements.txt not found in ${BACKEND_DIR}"
        fi
        ;;
      
      blockchain|contracts)
        echo -e "${BLUE}Attempting to fix Blockchain dependencies...${NC}"
        if [ -f "${BLOCKCHAIN_DIR}/package.json" ]; then
          (cd "${BLOCKCHAIN_DIR}" && npm ci) || echo "Failed to fix Blockchain dependencies"
        else
          echo "package.json not found in ${BLOCKCHAIN_DIR}"
        fi
        ;;
      
      *)
        echo -e "${RED}Unknown component: ${component}${NC}"
        echo "Available components: web-frontend, mobile-frontend, backend, blockchain"
        return 1
        ;;
    esac
    
    echo -e "${GREEN}Dependency fixing attempt completed.${NC}"
    echo "Run './dependency_checker.sh check' to verify the results."
  fi
}

# Main script execution
case "$1" in
  check)
    check_dependencies
    ;;
  outdated)
    check_outdated_dependencies
    ;;
  security)
    security_audit
    ;;
  report)
    generate_report
    ;;
  fix)
    fix_dependencies "$2"
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
