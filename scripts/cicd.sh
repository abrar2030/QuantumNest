#!/bin/bash
# QuantumNest CI/CD Enhancement Script
# This script provides additional CI/CD capabilities to complement
# the existing GitHub Actions workflow.

set -e

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# GitHub workflow directory
WORKFLOW_DIR="${PROJECT_DIR}/.github/workflows"

# Function to display help message
function show_help {
  echo -e "${BLUE}QuantumNest CI/CD Enhancement Script${NC}"
  echo "This script provides additional CI/CD capabilities for the QuantumNest project."
  echo ""
  echo "Usage: ./cicd_enhancer.sh [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  status              Check status of CI/CD configuration"
  echo "  validate            Validate CI/CD workflow files"
  echo "  local-test          Run CI tests locally before pushing"
  echo "  preview-deploy      Create a preview deployment"
  echo "  generate            Generate new workflow file from template"
  echo "  help                Display this help message"
  echo ""
  echo "Examples:"
  echo "  ./cicd_enhancer.sh status"
  echo "  ./cicd_enhancer.sh validate"
  echo "  ./cicd_enhancer.sh local-test"
  echo "  ./cicd_enhancer.sh preview-deploy"
  echo "  ./cicd_enhancer.sh generate feature-workflow"
}

# Function to check status of CI/CD configuration
function check_status {
  echo -e "${BLUE}Checking status of CI/CD configuration...${NC}"
  
  # Check if workflow directory exists
  if [ ! -d "$WORKFLOW_DIR" ]; then
    echo -e "${RED}GitHub workflow directory not found: ${WORKFLOW_DIR}${NC}"
    echo "Would you like to create it? (y/n)"
    read -r create_dir
    if [[ "$create_dir" =~ ^[Yy]$ ]]; then
      mkdir -p "$WORKFLOW_DIR"
      echo -e "${GREEN}Created workflow directory: ${WORKFLOW_DIR}${NC}"
    else
      echo "Operation cancelled."
      return 1
    fi
  else
    echo -e "${GREEN}GitHub workflow directory exists: ${WORKFLOW_DIR}${NC}"
  fi
  
  # Count workflow files
  local workflow_count=$(find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" | wc -l)
  echo "Found ${workflow_count} workflow file(s)."
  
  # List workflow files
  if [ $workflow_count -gt 0 ]; then
    echo "Workflow files:"
    find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" | while read -r file; do
      local name=$(basename "$file")
      local triggers=$(grep -E "on:|pull_request:|push:|workflow_dispatch:" "$file" | head -5 | tr -d '\n' | sed 's/  */ /g')
      echo "  - ${name} (Triggers: ${triggers}...)"
    done
  fi
  
  # Check for common CI tools configuration
  echo ""
  echo "Checking for CI tool configurations:"
  
  # ESLint
  if [ -f "${PROJECT_DIR}/.eslintrc.js" ] || [ -f "${PROJECT_DIR}/.eslintrc.json" ] || [ -f "${PROJECT_DIR}/.eslintrc.yml" ]; then
    echo -e "${GREEN}✓ ESLint configuration found${NC}"
  else
    echo -e "${YELLOW}! ESLint configuration not found at project root${NC}"
    # Check in frontend directories
    if [ -f "${PROJECT_DIR}/web-frontend/.eslintrc.js" ] || [ -f "${PROJECT_DIR}/mobile-frontend/.eslintrc.js" ]; then
      echo -e "${GREEN}  ✓ ESLint configuration found in frontend directories${NC}"
    fi
  fi
  
  # Prettier
  if [ -f "${PROJECT_DIR}/.prettierrc" ] || [ -f "${PROJECT_DIR}/.prettierrc.js" ] || [ -f "${PROJECT_DIR}/.prettierrc.json" ]; then
    echo -e "${GREEN}✓ Prettier configuration found${NC}"
  else
    echo -e "${YELLOW}! Prettier configuration not found at project root${NC}"
    # Check in frontend directories
    if [ -f "${PROJECT_DIR}/web-frontend/.prettierrc" ] || [ -f "${PROJECT_DIR}/mobile-frontend/.prettierrc" ]; then
      echo -e "${GREEN}  ✓ Prettier configuration found in frontend directories${NC}"
    fi
  fi
  
  # Jest
  if [ -f "${PROJECT_DIR}/jest.config.js" ]; then
    echo -e "${GREEN}✓ Jest configuration found${NC}"
  else
    echo -e "${YELLOW}! Jest configuration not found at project root${NC}"
    # Check in frontend directories
    if [ -f "${PROJECT_DIR}/web-frontend/jest.config.js" ] || [ -f "${PROJECT_DIR}/mobile-frontend/jest.config.js" ]; then
      echo -e "${GREEN}  ✓ Jest configuration found in frontend directories${NC}"
    fi
  fi
  
  # Python testing
  if [ -f "${PROJECT_DIR}/pytest.ini" ] || [ -d "${PROJECT_DIR}/backend/tests" ]; then
    echo -e "${GREEN}✓ Python test configuration found${NC}"
  else
    echo -e "${YELLOW}! Python test configuration not found${NC}"
  fi
  
  # Docker
  if [ -f "${PROJECT_DIR}/Dockerfile" ] || [ -f "${PROJECT_DIR}/docker-compose.yml" ]; then
    echo -e "${GREEN}✓ Docker configuration found${NC}"
  else
    echo -e "${YELLOW}! Docker configuration not found at project root${NC}"
    # Check in component directories
    if [ -f "${PROJECT_DIR}/backend/Dockerfile" ] || [ -f "${PROJECT_DIR}/web-frontend/Dockerfile" ]; then
      echo -e "${GREEN}  ✓ Docker configuration found in component directories${NC}"
    fi
  fi
  
  echo ""
  echo -e "${GREEN}CI/CD status check complete.${NC}"
}

# Function to validate CI/CD workflow files
function validate_workflows {
  echo -e "${BLUE}Validating CI/CD workflow files...${NC}"
  
  # Check if workflow directory exists
  if [ ! -d "$WORKFLOW_DIR" ]; then
    echo -e "${RED}GitHub workflow directory not found: ${WORKFLOW_DIR}${NC}"
    return 1
  fi
  
  # Count workflow files
  local workflow_count=$(find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" | wc -l)
  
  if [ $workflow_count -eq 0 ]; then
    echo -e "${YELLOW}No workflow files found in ${WORKFLOW_DIR}${NC}"
    return 1
  fi
  
  echo "Found ${workflow_count} workflow file(s) to validate."
  
  # Check if yamllint is installed
  local yamllint_available=false
  if command -v yamllint &> /dev/null; then
    yamllint_available=true
  else
    echo -e "${YELLOW}yamllint not found. Will perform basic YAML validation only.${NC}"
    echo "Consider installing yamllint for more thorough validation:"
    echo "  pip install yamllint"
  fi
  
  # Validate each workflow file
  local errors=0
  
  find "$WORKFLOW_DIR" -name "*.yml" -o -name "*.yaml" | while read -r file; do
    local name=$(basename "$file")
    echo "Validating ${name}..."
    
    # Basic YAML syntax validation using Python
    python3 -c "import yaml; yaml.safe_load(open('$file', 'r'))" 2>/dev/null
    if [ $? -ne 0 ]; then
      echo -e "${RED}  ✗ YAML syntax error in ${name}${NC}"
      python3 -c "import yaml; yaml.safe_load(open('$file', 'r'))" 2>&1 | head -5
      errors=$((errors+1))
      continue
    else
      echo -e "${GREEN}  ✓ YAML syntax is valid${NC}"
    fi
    
    # Additional validation with yamllint if available
    if [ "$yamllint_available" = true ]; then
      yamllint -d "{extends: relaxed, rules: {line-length: {max: 120}}}" "$file" > /dev/null 2>&1
      if [ $? -ne 0 ]; then
        echo -e "${YELLOW}  ! yamllint found style issues in ${name}${NC}"
        yamllint -d "{extends: relaxed, rules: {line-length: {max: 120}}}" "$file" | head -5
      else
        echo -e "${GREEN}  ✓ yamllint validation passed${NC}"
      fi
    fi
    
    # Check for common GitHub Actions workflow issues
    if ! grep -q "runs-on:" "$file"; then
      echo -e "${RED}  ✗ Missing 'runs-on' directive in ${name}${NC}"
      errors=$((errors+1))
    fi
    
    if ! grep -q "steps:" "$file"; then
      echo -e "${RED}  ✗ Missing 'steps' directive in ${name}${NC}"
      errors=$((errors+1))
    fi
    
    if ! grep -q "actions/checkout@" "$file"; then
      echo -e "${YELLOW}  ! Warning: Workflow might be missing checkout action in ${name}${NC}"
    fi
    
    echo ""
  done
  
  if [ $errors -eq 0 ]; then
    echo -e "${GREEN}All workflow files validated successfully.${NC}"
  else
    echo -e "${RED}Found ${errors} error(s) in workflow files.${NC}"
    echo "Please fix these issues to ensure proper CI/CD functionality."
  fi
}

# Function to run CI tests locally before pushing
function run_local_tests {
  echo -e "${BLUE}Running CI tests locally...${NC}"
  
  # Create a temporary directory for test results
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local results_dir="${PROJECT_DIR}/ci_test_results_${timestamp}"
  mkdir -p "$results_dir"
  
  echo "Test results will be saved to: ${results_dir}"
  
  # Run linting
  echo ""
  echo -e "${BLUE}Running linting checks...${NC}"
  
  # Check if lint-all.sh exists and is executable
  if [ -f "${PROJECT_DIR}/lint-all.sh" ] && [ -x "${PROJECT_DIR}/lint-all.sh" ]; then
    echo "Running lint-all.sh script..."
    "${PROJECT_DIR}/lint-all.sh" > "${results_dir}/lint_results.log" 2>&1
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✓ Linting passed${NC}"
    else
      echo -e "${RED}✗ Linting failed${NC}"
      echo "See ${results_dir}/lint_results.log for details"
      tail -5 "${results_dir}/lint_results.log"
    fi
  else
    echo -e "${YELLOW}! lint-all.sh not found or not executable${NC}"
    echo "Skipping linting checks."
  fi
  
  # Run frontend tests
  echo ""
  echo -e "${BLUE}Running frontend tests...${NC}"
  
  # Web Frontend tests
  if [ -d "${PROJECT_DIR}/web-frontend" ]; then
    echo "Running Web Frontend tests..."
    if [ -f "${PROJECT_DIR}/web-frontend/package.json" ]; then
      # Check if test script exists in package.json
      if grep -q '"test"' "${PROJECT_DIR}/web-frontend/package.json"; then
        (cd "${PROJECT_DIR}/web-frontend" && npm test) > "${results_dir}/web_frontend_test_results.log" 2>&1
        if [ $? -eq 0 ]; then
          echo -e "${GREEN}✓ Web Frontend tests passed${NC}"
        else
          echo -e "${RED}✗ Web Frontend tests failed${NC}"
          echo "See ${results_dir}/web_frontend_test_results.log for details"
          tail -5 "${results_dir}/web_frontend_test_results.log"
        fi
      else
        echo -e "${YELLOW}! No test script found in Web Frontend package.json${NC}"
        echo "Skipping Web Frontend tests."
      fi
    else
      echo -e "${YELLOW}! package.json not found in Web Frontend directory${NC}"
      echo "Skipping Web Frontend tests."
    fi
  else
    echo -e "${YELLOW}! Web Frontend directory not found${NC}"
    echo "Skipping Web Frontend tests."
  fi
  
  # Mobile Frontend tests
  if [ -d "${PROJECT_DIR}/mobile-frontend" ]; then
    echo "Running Mobile Frontend tests..."
    if [ -f "${PROJECT_DIR}/mobile-frontend/package.json" ]; then
      # Check if test script exists in package.json
      if grep -q '"test"' "${PROJECT_DIR}/mobile-frontend/package.json"; then
        (cd "${PROJECT_DIR}/mobile-frontend" && npm test) > "${results_dir}/mobile_frontend_test_results.log" 2>&1
        if [ $? -eq 0 ]; then
          echo -e "${GREEN}✓ Mobile Frontend tests passed${NC}"
        else
          echo -e "${RED}✗ Mobile Frontend tests failed${NC}"
          echo "See ${results_dir}/mobile_frontend_test_results.log for details"
          tail -5 "${results_dir}/mobile_frontend_test_results.log"
        fi
      else
        echo -e "${YELLOW}! No test script found in Mobile Frontend package.json${NC}"
        echo "Skipping Mobile Frontend tests."
      fi
    else
      echo -e "${YELLOW}! package.json not found in Mobile Frontend directory${NC}"
      echo "Skipping Mobile Frontend tests."
    fi
  else
    echo -e "${YELLOW}! Mobile Frontend directory not found${NC}"
    echo "Skipping Mobile Frontend tests."
  fi
  
  # Run backend tests
  echo ""
  echo -e "${BLUE}Running backend tests...${NC}"
  
  if [ -d "${PROJECT_DIR}/backend" ]; then
    echo "Running Backend tests..."
    if [ -d "${PROJECT_DIR}/backend/tests" ]; then
      # Check if pytest is available
      if command -v pytest &> /dev/null; then
        (cd "${PROJECT_DIR}/backend" && python -m pytest) > "${results_dir}/backend_test_results.log" 2>&1
        if [ $? -eq 0 ]; then
          echo -e "${GREEN}✓ Backend tests passed${NC}"
        else
          echo -e "${RED}✗ Backend tests failed${NC}"
          echo "See ${results_dir}/backend_test_results.log for details"
          tail -5 "${results_dir}/backend_test_results.log"
        fi
      else
        echo -e "${YELLOW}! pytest not found${NC}"
        echo "Skipping Backend tests."
      fi
    else
      echo -e "${YELLOW}! No tests directory found in Backend${NC}"
      echo "Skipping Backend tests."
    fi
  else
    echo -e "${YELLOW}! Backend directory not found${NC}"
    echo "Skipping Backend tests."
  fi
  
  # Run blockchain tests
  echo ""
  echo -e "${BLUE}Running blockchain tests...${NC}"
  
  if [ -d "${PROJECT_DIR}/blockchain" ]; then
    echo "Running Blockchain tests..."
    if [ -f "${PROJECT_DIR}/blockchain/package.json" ]; then
      # Check if test script exists in package.json
      if grep -q '"test"' "${PROJECT_DIR}/blockchain/package.json"; then
        (cd "${PROJECT_DIR}/blockchain" && npm test) > "${results_dir}/blockchain_test_results.log" 2>&1
        if [ $? -eq 0 ]; then
          echo -e "${GREEN}✓ Blockchain tests passed${NC}"
        else
          echo -e "${RED}✗ Blockchain tests failed${NC}"
          echo "See ${results_dir}/blockchain_test_results.log for details"
          tail -5 "${results_dir}/blockchain_test_results.log"
        fi
      else
        echo -e "${YELLOW}! No test script found in Blockchain package.json${NC}"
        echo "Skipping Blockchain tests."
      fi
    else
      echo -e "${YELLOW}! package.json not found in Blockchain directory${NC}"
      echo "Skipping Blockchain tests."
    fi
  else
    echo -e "${YELLOW}! Blockchain directory not found${NC}"
    echo "Skipping Blockchain tests."
  fi
  
  # Generate summary report
  echo ""
  echo -e "${BLUE}Generating test summary...${NC}"
  
  {
    echo "QuantumNest Local CI Test Summary"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
    
    # Linting summary
    echo "## Linting Results"
    if [ -f "${results_dir}/lint_results.log" ]; then
      if grep -q "error" "${results_dir}/lint_results.log"; then
        echo "Status: FAILED"
        echo "Errors found during linting. See lint_results.log for details."
      else
        echo "Status: PASSED"
        echo "No linting errors found."
      fi
    else
      echo "Status: SKIPPED"
      echo "Linting was not performed."
    fi
    echo ""
    
    # Web Frontend summary
    echo "## Web Frontend Test Results"
    if [ -f "${results_dir}/web_frontend_test_results.log" ]; then
      if grep -q "failed" "${results_dir}/web_frontend_test_results.log"; then
        echo "Status: FAILED"
        echo "Errors found during Web Frontend tests. See web_frontend_test_results.log for details."
      else
        echo "Status: PASSED"
        echo "All Web Frontend tests passed."
      fi
    else
      echo "Status: SKIPPED"
      echo "Web Frontend tests were not performed."
    fi
    echo ""
    
    # Mobile Frontend summary
    echo "## Mobile Frontend Test Results"
    if [ -f "${results_dir}/mobile_frontend_test_results.log" ]; then
      if grep -q "failed" "${results_dir}/mobile_frontend_test_results.log"; then
        echo "Status: FAILED"
        echo "Errors found during Mobile Frontend tests. See mobile_frontend_test_results.log for details."
      else
        echo "Status: PASSED"
        echo "All Mobile Frontend tests passed."
      fi
    else
      echo "Status: SKIPPED"
      echo "Mobile Frontend tests were not performed."
    fi
    echo ""
    
    # Backend summary
    echo "## Backend Test Results"
    if [ -f "${results_dir}/backend_test_results.log" ]; then
      if grep -q "failed" "${results_dir}/backend_test_results.log"; then
        echo "Status: FAILED"
        echo "Errors found during Backend tests. See backend_test_results.log for details."
      else
        echo "Status: PASSED"
        echo "All Backend tests passed."
      fi
    else
      echo "Status: SKIPPED"
      echo "Backend tests were not performed."
    fi
    echo ""
    
    # Blockchain summary
    echo "## Blockchain Test Results"
    if [ -f "${results_dir}/blockchain_test_results.log" ]; then
      if grep -q "failed" "${results_dir}/blockchain_test_results.log"; then
        echo "Status: FAILED"
        echo "Errors found during Blockchain tests. See blockchain_test_results.log for details."
      else
        echo "Status: PASSED"
        echo "All Blockchain tests passed."
      fi
    else
      echo "Status: SKIPPED"
      echo "Blockchain tests were not performed."
    fi
    echo ""
    
    # Overall summary
    echo "## Overall Summary"
    echo "Test run completed at: $(date)"
    echo "Results directory: ${results_dir}"
    echo ""
    echo "Recommendation:"
    if grep -q "FAILED" "${results_dir}/summary.txt"; then
      echo "DO NOT PUSH. Fix the failing tests before pushing to the repository."
    else
      echo "READY TO PUSH. All performed tests have passed."
    fi
  } > "${results_dir}/summary.txt"
  
  echo -e "${GREEN}Local CI tests completed.${NC}"
  echo "Summary report saved to: ${results_dir}/summary.txt"
  
  # Display summary
  cat "${results_dir}/summary.txt"
}

# Function to create a preview deployment
function preview_deploy {
  echo -e "${BLUE}Creating preview deployment...${NC}"
  
  # Check for required tools
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker is required for preview deployment.${NC}"
    echo "Please install docker and try again."
    return 1
  fi
  
  if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is required for preview deployment.${NC}"
    echo "Please install docker-compose and try again."
    return 1
  fi
  
  # Create a temporary directory for preview deployment
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local preview_dir="${PROJECT_DIR}/preview_deployment_${timestamp}"
  mkdir -p "$preview_dir"
  
  echo "Preview deployment will be created in: ${preview_dir}"
  
  # Create docker-compose.yml if it doesn't exist
  if [ ! -f "${PROJECT_DIR}/docker-compose.yml" ]; then
    echo "Creating docker-compose.yml for preview deployment..."
    
    cat > "${preview_dir}/docker-compose.yml" << EOF
version: '3'

services:
  # Backend service
  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile.preview
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/quantumnest
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ../backend:/app
    networks:
      - quantumnest-network

  # Web Frontend service
  web-frontend:
    build:
      context: ../web-frontend
      dockerfile: Dockerfile.preview
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ../web-frontend:/app
    networks:
      - quantumnest-network

  # Database service
  db:
    image: postgres:13
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=quantumnest
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - quantumnest-network

  # Redis service
  redis:
    image: redis:6
    ports:
      - "6379:6379"
    networks:
      - quantumnest-network

networks:
  quantumnest-network:
    driver: bridge

volumes:
  postgres-data:
EOF
    
    echo -e "${GREEN}Created docker-compose.yml for preview deployment.${NC}"
  else
    echo "Using existing docker-compose.yml for preview deployment."
    cp "${PROJECT_DIR}/docker-compose.yml" "${preview_dir}/docker-compose.yml"
  fi
  
  # Create Dockerfile.preview for backend if it doesn't exist
  if [ ! -f "${PROJECT_DIR}/backend/Dockerfile" ] && [ ! -f "${PROJECT_DIR}/backend/Dockerfile.preview" ]; then
    echo "Creating Dockerfile.preview for backend..."
    
    mkdir -p "${preview_dir}/backend"
    cat > "${preview_dir}/backend/Dockerfile.preview" << EOF
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
EOF
    
    echo -e "${GREEN}Created Dockerfile.preview for backend.${NC}"
  elif [ -f "${PROJECT_DIR}/backend/Dockerfile" ]; then
    echo "Using existing Dockerfile for backend."
    mkdir -p "${preview_dir}/backend"
    cp "${PROJECT_DIR}/backend/Dockerfile" "${preview_dir}/backend/Dockerfile.preview"
  else
    echo "Using existing Dockerfile.preview for backend."
    mkdir -p "${preview_dir}/backend"
    cp "${PROJECT_DIR}/backend/Dockerfile.preview" "${preview_dir}/backend/Dockerfile.preview"
  fi
  
  # Create Dockerfile.preview for web-frontend if it doesn't exist
  if [ ! -f "${PROJECT_DIR}/web-frontend/Dockerfile" ] && [ ! -f "${PROJECT_DIR}/web-frontend/Dockerfile.preview" ]; then
    echo "Creating Dockerfile.preview for web-frontend..."
    
    mkdir -p "${preview_dir}/web-frontend"
    cat > "${preview_dir}/web-frontend/Dockerfile.preview" << EOF
FROM node:16-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
EOF
    
    echo -e "${GREEN}Created Dockerfile.preview for web-frontend.${NC}"
  elif [ -f "${PROJECT_DIR}/web-frontend/Dockerfile" ]; then
    echo "Using existing Dockerfile for web-frontend."
    mkdir -p "${preview_dir}/web-frontend"
    cp "${PROJECT_DIR}/web-frontend/Dockerfile" "${preview_dir}/web-frontend/Dockerfile.preview"
  else
    echo "Using existing Dockerfile.preview for web-frontend."
    mkdir -p "${preview_dir}/web-frontend"
    cp "${PROJECT_DIR}/web-frontend/Dockerfile.preview" "${preview_dir}/web-frontend/Dockerfile.preview"
  fi
  
  # Create preview deployment script
  cat > "${preview_dir}/start-preview.sh" << EOF
#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "\${BLUE}Starting QuantumNest Preview Deployment...\${NC}"

# Copy Dockerfiles if they don't exist in the main project
if [ ! -f "../backend/Dockerfile.preview" ]; then
  cp "./backend/Dockerfile.preview" "../backend/Dockerfile.preview"
fi

if [ ! -f "../web-frontend/Dockerfile.preview" ]; then
  cp "./web-frontend/Dockerfile.preview" "../web-frontend/Dockerfile.preview"
fi

# Start the services
docker-compose up -d

# Check if services are running
echo -e "\${BLUE}Checking if services are running...\${NC}"
sleep 5

if docker-compose ps | grep -q "Up"; then
  echo -e "\${GREEN}Preview deployment started successfully!\${NC}"
  echo ""
  echo "Access the services at:"
  echo "  - Backend API: http://localhost:8000"
  echo "  - Web Frontend: http://localhost:3000"
  echo ""
  echo "To stop the preview deployment, run:"
  echo "  cd $(basename "$preview_dir") && docker-compose down"
else
  echo -e "\${RED}Failed to start preview deployment.\${NC}"
  echo "Check the logs for more information:"
  echo "  docker-compose logs"
fi
EOF
  
  chmod +x "${preview_dir}/start-preview.sh"
  
  echo -e "${GREEN}Preview deployment setup complete.${NC}"
  echo "To start the preview deployment, run:"
  echo "  cd ${preview_dir} && ./start-preview.sh"
}

# Function to generate new workflow file from template
function generate_workflow {
  local workflow_name=$1
  
  if [ -z "$workflow_name" ]; then
    echo -e "${RED}Error: Workflow name required.${NC}"
    echo "Usage: ./cicd_enhancer.sh generate workflow-name"
    return 1
  fi
  
  # Create workflow directory if it doesn't exist
  if [ ! -d "$WORKFLOW_DIR" ]; then
    mkdir -p "$WORKFLOW_DIR"
    echo -e "${GREEN}Created workflow directory: ${WORKFLOW_DIR}${NC}"
  fi
  
  # Check if workflow file already exists
  local workflow_file="${WORKFLOW_DIR}/${workflow_name}.yml"
  if [ -f "$workflow_file" ]; then
    echo -e "${RED}Error: Workflow file already exists: ${workflow_file}${NC}"
    echo "Please choose a different name or delete the existing file."
    return 1
  fi
  
  echo -e "${BLUE}Generating new workflow file: ${workflow_name}.yml${NC}"
  
  # Prompt for workflow type
  echo "Select workflow type:"
  echo "1. CI workflow (lint and test)"
  echo "2. CD workflow (build and deploy)"
  echo "3. Full CI/CD workflow"
  echo "4. Pull request validation"
  echo "5. Custom workflow"
  read -p "Enter your choice (1-5): " workflow_type
  
  case $workflow_type in
    1)
      # CI workflow
      cat > "$workflow_file" << EOF
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Run linting
        run: |
          npm run lint
  
  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Run tests
        run: |
          npm test
EOF
      ;;
    
    2)
      # CD workflow
      cat > "$workflow_file" << EOF
name: CD

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Build
        run: |
          npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: build/
  
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build
          path: build/
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add your deployment commands here
EOF
      ;;
    
    3)
      # Full CI/CD workflow
      cat > "$workflow_file" << EOF
name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Run linting
        run: |
          npm run lint
  
  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Run tests
        run: |
          npm test
  
  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Build
        run: |
          npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: build/
  
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build
          path: build/
      
      - name: Deploy to staging
        run: |
          echo "Deploying to staging..."
          # Add your staging deployment commands here
  
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build
          path: build/
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add your production deployment commands here
EOF
      ;;
    
    4)
      # Pull request validation
      cat > "$workflow_file" << EOF
name: Pull Request Validation

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  validate:
    name: Validate PR
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
      
      - name: Install dependencies
        run: |
          npm ci
      
      - name: Run linting
        run: |
          npm run lint
      
      - name: Run tests
        run: |
          npm test
      
      - name: Check build
        run: |
          npm run build
EOF
      ;;
    
    5)
      # Custom workflow (minimal template)
      cat > "$workflow_file" << EOF
name: Custom Workflow

on:
  # Customize triggers as needed
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  custom-job:
    name: Custom Job
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Add your custom steps here
      - name: Custom Step
        run: |
          echo "Add your commands here"
EOF
      ;;
    
    *)
      echo -e "${RED}Invalid choice. Please select a number between 1 and 5.${NC}"
      rm -f "$workflow_file"
      return 1
      ;;
  esac
  
  echo -e "${GREEN}Workflow file generated: ${workflow_file}${NC}"
  echo "Please review and customize the workflow file as needed."
}

# Main script execution
case "$1" in
  status)
    check_status
    ;;
  validate)
    validate_workflows
    ;;
  local-test)
    run_local_tests
    ;;
  preview-deploy)
    preview_deploy
    ;;
  generate)
    generate_workflow "$2"
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
