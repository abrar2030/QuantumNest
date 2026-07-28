#!/bin/bash

# Linting and Fixing Script for QuantumNest Project
# This script is designed to be run from the project root (QuantumNest/).
#
# Linters routinely exit non-zero simply because they found something to
# report (that's normal, expected behavior, not a script error) — so this
# script does NOT use `set -e` around tool invocations. Every tool runs
# through to completion; a summary of what passed/failed is printed at the
# end, and the script's own exit code reflects whether any checker reported
# unresolved issues.

set -uo pipefail

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"
BACKEND_DIR="$PROJECT_ROOT/code/backend"
WEB_FRONTEND_DIR="$PROJECT_ROOT/web-frontend"
MOBILE_FRONTEND_DIR="$PROJECT_ROOT/mobile-frontend"
BLOCKCHAIN_DIR="$PROJECT_ROOT/code/blockchain"

PYTHON_DIRS=("$BACKEND_DIR")
JS_DIRS=("$WEB_FRONTEND_DIR/src" "$MOBILE_FRONTEND_DIR/src" "$BLOCKCHAIN_DIR")
YAML_DIRS=("$PROJECT_ROOT/infrastructure/kubernetes" "$PROJECT_ROOT/infrastructure/ansible" "$PROJECT_ROOT/.github/workflows")
TERRAFORM_DIRS=("$PROJECT_ROOT/infrastructure/terraform")

# --- Utility Functions ---

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Track results as "Step Name:STATUS" so we can print a summary at the end.
declare -a RESULTS=()
OVERALL_STATUS=0

# Runs a step, records PASSED/ISSUES/SKIPPED under `label`, and always
# continues to the next step regardless of outcome.
run_step() {
  local label="$1"
  shift
  echo "----------------------------------------"
  echo "Running: ${label}"
  if "$@"; then
    RESULTS+=("${label}:PASSED")
  else
    RESULTS+=("${label}:ISSUES FOUND")
    OVERALL_STATUS=1
  fi
}

skip_step() {
  local label="$1"
  local reason="$2"
  echo "Skipping ${label}: ${reason}"
  RESULTS+=("${label}:SKIPPED (${reason})")
}

# Function to ensure Python virtual environment is set up and activated
ensure_venv() {
  echo "Ensuring Python virtual environment is set up..."
  if [ ! -d "$VENV_PATH" ]; then
    echo "Creating Python virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
  fi

  # shellcheck disable=SC1091
  source "$VENV_PATH/bin/activate"
  echo "Virtual environment activated."

  echo "Installing/Updating Python dependencies from requirements.txt..."
  pip install --upgrade pip setuptools wheel > /dev/null
  if [ -f "$BACKEND_DIR/requirements.txt" ]; then
    pip install -r "$BACKEND_DIR/requirements.txt" > /dev/null
  else
    echo "Warning: $BACKEND_DIR/requirements.txt not found. Skipping main dependency install."
  fi

  echo "Installing/Updating Python linting tools..."
  pip install --upgrade black isort flake8 pylint pyyaml > /dev/null
}

# Function to ensure Node.js dependencies are installed
ensure_node_deps() {
  echo "Ensuring Node.js dependencies are installed..."

  if [ -d "$WEB_FRONTEND_DIR" ]; then
    echo "Installing Web Frontend dependencies in $WEB_FRONTEND_DIR..."
    (cd "$WEB_FRONTEND_DIR" && npm install > /dev/null)
  fi

  if [ -d "$MOBILE_FRONTEND_DIR" ]; then
    echo "Installing Mobile Frontend dependencies in $MOBILE_FRONTEND_DIR..."
    (cd "$MOBILE_FRONTEND_DIR" && npm install > /dev/null)
  fi

  if [ -d "$BLOCKCHAIN_DIR" ]; then
    echo "Installing Blockchain dependencies in $BLOCKCHAIN_DIR..."
    (cd "$BLOCKCHAIN_DIR" && npm install > /dev/null)
  fi
}

# Make sure the virtual environment is deactivated no matter how the script exits.
cleanup() {
  deactivate 2>/dev/null || true
}
trap cleanup EXIT

# --- Main Execution ---

echo "----------------------------------------"
echo "Starting linting and fixing process for QuantumNest..."
echo "----------------------------------------"

# 1. Environment Setup
ensure_venv
ensure_node_deps

# 2. Python Linting
echo "----------------------------------------"
echo "Running Python linting tools..."

for dir in "${PYTHON_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "Processing Python files in $dir..."
    run_step "black ($dir)" python3 -m black "$dir"
    run_step "isort ($dir)" python3 -m isort "$dir"
    run_step "flake8 ($dir)" python3 -m flake8 "$dir"
    run_step "pylint ($dir)" bash -c \
      "find '$dir' -type f -name '*.py' -print0 | xargs -0 python3 -m pylint --disable=C0111,C0103,C0303,W0621,C0301,W0612,W0611,R0913,R0914,R0915"
  else
    skip_step "Python lint ($dir)" "directory not found"
  fi
done

# 3. JavaScript/TypeScript Linting
echo "----------------------------------------"
echo "Running JavaScript/TypeScript linting tools..."

for dir in "${JS_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "Processing JavaScript/TypeScript files in $dir..."
    run_step "eslint ($dir)" bash -c "cd '$dir' && npx eslint . --ext .js,.jsx,.ts,.tsx --fix"
    run_step "prettier ($dir)" bash -c \
      "cd '$dir' && npx prettier --write '**/*.{js,jsx,ts,tsx,json,css,scss,md}' --ignore-unknown"
  else
    skip_step "JS/TS lint ($dir)" "directory not found"
  fi
done

# 4. YAML Linting
echo "----------------------------------------"
echo "Running YAML linting tools..."

validate_yaml_with_python() {
  local dir="$1"
  local failed=0
  while IFS= read -r -d '' file; do
    if ! python3 -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]))" "$file"; then
      echo "Invalid YAML: $file"
      failed=1
    fi
  done < <(find "$dir" -type f \( -name "*.yaml" -o -name "*.yml" \) -print0)
  return "$failed"
}

for dir in "${YAML_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    if command_exists yamllint; then
      run_step "yamllint ($dir)" yamllint "$dir"
    else
      run_step "YAML validation ($dir)" validate_yaml_with_python "$dir"
    fi
  else
    skip_step "YAML lint ($dir)" "directory not found"
  fi
done

# 5. Terraform Linting
echo "----------------------------------------"
echo "Running Terraform linting tools..."

if command_exists terraform; then
  for dir in "${TERRAFORM_DIRS[@]}"; do
    if [ -d "$dir" ]; then
      echo "Processing Terraform files in $dir..."
      run_step "terraform fmt ($dir)" bash -c "cd '$dir' && terraform fmt -recursive"
      run_step "terraform validate ($dir)" bash -c \
        "cd '$dir' && terraform init -backend=false -input=false >/dev/null && terraform validate"
    else
      skip_step "Terraform ($dir)" "directory not found"
    fi
  done
else
  skip_step "Terraform linting" "terraform not installed"
fi

# 6. Common Fixes for All File Types
echo "----------------------------------------"
echo "Applying common fixes to all file types (trailing whitespace, final newline)..."

fix_whitespace_and_newline() {
  local file="$1"
  sed -i 's/[ \t]*$//' "$file"
  if [ -s "$file" ] && [ -n "$(tail -c1 "$file")" ]; then
    echo "" >> "$file"
  fi
}

while IFS= read -r -d '' file; do
  fix_whitespace_and_newline "$file"
done < <(find "$PROJECT_ROOT" -type f \
  \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \
     -o -name "*.yaml" -o -name "*.yml" -o -name "*.tf" -o -name "*.tfvars" \) \
  -not -path "*/node_modules/*" -not -path "*/venv/*" -not -path "*/dist/*" \
  -not -path "*/.next/*" -not -path "*/build/*" -not -path "*/.git/*" \
  -print0)

echo "Common fixes completed."

# 7. Summary
echo "----------------------------------------"
echo "Lint Summary"
echo "----------------------------------------"
for result in "${RESULTS[@]}"; do
  echo "$result"
done

echo "----------------------------------------"
if [ "$OVERALL_STATUS" -eq 0 ]; then
  echo "Linting and fixing process for QuantumNest completed: no unresolved issues!"
else
  echo "Linting and fixing process for QuantumNest completed with unresolved issues (see summary above)."
fi
echo "----------------------------------------"

exit "$OVERALL_STATUS"
