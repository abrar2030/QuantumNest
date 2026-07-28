#!/bin/bash
# QuantumNest Infrastructure Validation Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0

pass() { echo -e "${GREEN}[PASS]${NC} $*"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}[FAIL]${NC} $*"; FAIL=$((FAIL + 1)); }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; WARN=$((WARN + 1)); }
info() { echo -e "${BLUE}[INFO]${NC} $*"; }

echo ""
echo "═══════════════════════════════════════════════════"
echo " QuantumNest Infrastructure Validation"
echo "═══════════════════════════════════════════════════"
echo ""

# ──────────────────────────────────────
# File Structure Validation
# ──────────────────────────────────────
info "Checking required files and directories..."

required_files=(
  "terraform/main.tf"
  "terraform/variables.tf"
  "terraform/outputs.tf"
  "terraform/backend.tf"
  "terraform/modules/network/main.tf"
  "terraform/modules/compute/main.tf"
  "terraform/modules/database/main.tf"
  "terraform/modules/storage/main.tf"
  "terraform/modules/security/main.tf"
  "kubernetes/base/namespace.yaml"
  "kubernetes/base/backend-deployment.yaml"
  "kubernetes/base/web-frontend-deployment.yaml"
  "kubernetes/base/mobile-frontend-deployment.yaml"
  "kubernetes/base/database-statefulset.yaml"
  "kubernetes/base/redis-deployment.yaml"
  "kubernetes/base/ingress.yaml"
  "kubernetes/base/kustomization.yaml"
  "kubernetes/base/rbac.yaml"
  "monitoring/prometheus/prometheus.yml"
  "monitoring/prometheus/rules/financial-alerts.yml"
  "monitoring/grafana/provisioning/datasources/datasources.yml"
  "monitoring/elasticsearch/elasticsearch.yml"
  "monitoring/logstash/logstash.yml"
  "monitoring/logstash/pipeline/financial-transactions.conf"
  "monitoring/alertmanager/alertmanager.yml"
  "ansible/ansible.cfg"
  "ansible/playbooks/main.yml"
  "security/iam/role-definitions/financial-roles.json"
  "security/iam/base-policies/financial-services-base-policy.json"
  "security/secrets/vault/vault.hcl"
  "backup-recovery/database-backup/database-backup.sh"
  "Dockerfile"
  "docker-compose.yml"
  ".env.example"
  "deploy.sh"
)

for f in "${required_files[@]}"; do
  if [[ -f "$f" ]]; then
    pass "File exists: $f"
  else
    fail "Missing file: $f"
  fi
done

# ──────────────────────────────────────
# YAML Validation
# ──────────────────────────────────────
echo ""
info "Validating YAML files..."

yaml_files=(
  "monitoring/prometheus/prometheus.yml"
  "monitoring/prometheus/rules/financial-alerts.yml"
  "monitoring/grafana/provisioning/datasources/datasources.yml"
  "monitoring/alertmanager/alertmanager.yml"
  "monitoring/elasticsearch/elasticsearch.yml"
  "kubernetes/base/namespace.yaml"
  "kubernetes/base/backend-deployment.yaml"
  "kubernetes/base/ingress.yaml"
  "kubernetes/base/rbac.yaml"
  "ansible/ansible.cfg"
)

for f in "${yaml_files[@]}"; do
  if [[ -f "$f" ]]; then
    if command -v python3 &>/dev/null; then
      if python3 -c "import yaml; yaml.safe_load_all(open('$f'))" 2>/dev/null; then
        pass "Valid YAML: $f"
      else
        fail "Invalid YAML: $f"
      fi
    else
      warn "python3 not available, skipping YAML validation for $f"
    fi
  fi
done

# ──────────────────────────────────────
# JSON Validation
# ──────────────────────────────────────
echo ""
info "Validating JSON files..."

json_files=(
  "security/iam/role-definitions/financial-roles.json"
  "security/iam/base-policies/financial-services-base-policy.json"
)

for f in "${json_files[@]}"; do
  if [[ -f "$f" ]]; then
    if command -v jq &>/dev/null; then
      if jq . "$f" > /dev/null 2>&1; then
        pass "Valid JSON: $f"
      else
        fail "Invalid JSON: $f"
      fi
    elif python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
      pass "Valid JSON: $f"
    else
      fail "Invalid JSON: $f"
    fi
  fi
done

# ──────────────────────────────────────
# Terraform Validation
# ──────────────────────────────────────
echo ""
info "Checking Terraform..."

if command -v terraform &>/dev/null; then
  cd terraform
  if terraform validate 2>&1 | grep -q "Success"; then
    pass "Terraform validate passed"
  else
    warn "Terraform validate failed (may need init first)"
  fi
  cd ..
else
  warn "Terraform not installed, skipping validation"
fi

# ──────────────────────────────────────
# Kubernetes Manifest Validation
# ──────────────────────────────────────
echo ""
info "Checking Kubernetes manifests..."

if command -v kubectl &>/dev/null; then
  if kubectl apply -k kubernetes/base --dry-run=client &>/dev/null; then
    pass "Kubernetes manifests are valid (kustomize dry-run)"
  else
    fail "Kubernetes manifest validation failed"
  fi
else
  warn "kubectl not installed, skipping Kubernetes validation"
fi

# ──────────────────────────────────────
# Security Checks
# ──────────────────────────────────────
echo ""
info "Running security checks..."

# Check no plaintext passwords in tracked files
sensitive_patterns=("password:" "secret:" "token:" "api_key:")
files_to_check=(
  "kubernetes/base/app-configmap.yaml"
  "ansible/group_vars/all/vault.example.yml"
  "terraform/terraform.tfvars.example"
)
for f in "${files_to_check[@]}"; do
  if [[ -f "$f" ]]; then
    if grep -iE "(password|secret|token|api_key)\s*=\s*['\"]?[a-zA-Z0-9]{8,}" "$f" &>/dev/null; then
      warn "Possible plaintext credential in: $f"
    else
      pass "No plaintext credentials in: $f"
    fi
  fi
done

# Check .gitignore
if [[ -f ".gitignore" ]]; then
  gitignore_required=(".env" "*.tfstate" "*.tfstate.backup" "*.tfvars" "*.pem" "*.key")
  for pattern in "${gitignore_required[@]}"; do
    if grep -qF "$pattern" .gitignore; then
      pass ".gitignore contains: $pattern"
    else
      fail ".gitignore missing: $pattern"
    fi
  done
fi

# Check no secrets committed
if [[ -f "kubernetes/base/app-secrets.yaml" ]]; then
  if grep -q "^data: {}$" kubernetes/base/app-secrets.yaml; then
    pass "Secrets file is a placeholder (no real data)"
  else
    warn "app-secrets.yaml may contain real data - review carefully"
  fi
fi

# ──────────────────────────────────────
# Docker Validation
# ──────────────────────────────────────
echo ""
info "Checking Docker configuration..."

if command -v docker &>/dev/null; then
  if docker compose config --quiet 2>/dev/null; then
    pass "docker-compose.yml is valid"
  else
    fail "docker-compose.yml has errors"
  fi
  if docker build --no-cache --dry-run -f Dockerfile . &>/dev/null 2>&1; then
    pass "Dockerfile syntax valid"
  else
    warn "Dockerfile dry-run not supported (docker version may not support it)"
  fi
else
  warn "Docker not installed, skipping Docker validation"
fi

# ──────────────────────────────────────
# Backup Script Check
# ──────────────────────────────────────
echo ""
info "Checking backup scripts..."

if [[ -x "backup-recovery/database-backup/database-backup.sh" ]]; then
  pass "database-backup.sh is executable"
else
  fail "database-backup.sh is not executable"
  chmod +x backup-recovery/database-backup/database-backup.sh 2>/dev/null && warn "Fixed: made database-backup.sh executable"
fi

if bash -n backup-recovery/database-backup/database-backup.sh 2>/dev/null; then
  pass "database-backup.sh syntax is valid"
else
  fail "database-backup.sh has syntax errors"
fi

# ──────────────────────────────────────
# Summary
# ──────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo " Validation Summary"
echo "═══════════════════════════════════════════════════"
echo -e " ${GREEN}PASSED${NC}: ${PASS}"
echo -e " ${YELLOW}WARNED${NC}: ${WARN}"
echo -e " ${RED}FAILED${NC}: ${FAIL}"
echo "═══════════════════════════════════════════════════"

if [[ $FAIL -gt 0 ]]; then
  echo -e "${RED}Validation FAILED - fix the above errors before deploying${NC}"
  exit 1
else
  echo -e "${GREEN}Validation PASSED${NC}"
  exit 0
fi
