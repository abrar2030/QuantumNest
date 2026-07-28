#!/bin/bash
# QuantumNest Infrastructure Deployment Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

print_header() {
  echo ""
  echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║   QuantumNest Infrastructure Deployment      ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
  echo ""
}

check_dependencies() {
  local missing=()
  for cmd in terraform kubectl helm aws ansible; do
    if ! command -v "$cmd" &>/dev/null; then
      missing+=("$cmd")
    fi
  done
  if [[ ${#missing[@]} -gt 0 ]]; then
    log_warn "Missing tools: ${missing[*]}"
    log_warn "Run via Docker: docker compose run --rm infra-tools"
  fi
}

validate_environment() {
  local env="${1:-}"
  if [[ -z "$env" ]]; then
    log_error "Environment not specified. Use: dev, staging, or prod"
    exit 1
  fi
  if [[ ! "$env" =~ ^(dev|staging|prod)$ ]]; then
    log_error "Invalid environment: $env. Must be dev, staging, or prod"
    exit 1
  fi
}

deploy_terraform() {
  local action="$1"
  local env="${2:-dev}"
  log_info "=== Terraform ${action} [${env}] ==="

  local tfvars_file="${SCRIPT_DIR}/terraform/environments/${env}/terraform.tfvars"
  if [[ ! -f "$tfvars_file" ]]; then
    log_error "tfvars not found: $tfvars_file"
    exit 1
  fi

  cd "${SCRIPT_DIR}/terraform"
  terraform init -upgrade

  case "$action" in
    plan)
      terraform plan -var-file="$tfvars_file" -out="${env}.tfplan"
      log_success "Plan saved to terraform/${env}.tfplan"
      ;;
    apply)
      if [[ "$env" == "prod" ]]; then
        log_warn "⚠️  Applying to PRODUCTION. This is irreversible."
        read -r -p "Type 'yes-prod' to confirm: " confirm
        [[ "$confirm" == "yes-prod" ]] || { log_info "Aborted."; exit 0; }
      fi
      if [[ -f "${env}.tfplan" ]]; then
        terraform apply "${env}.tfplan"
      else
        terraform apply -var-file="$tfvars_file" -auto-approve
      fi
      log_success "Terraform applied for ${env}"
      ;;
    destroy)
      log_warn "⚠️  DESTROY requested for ${env}"
      [[ "$env" == "prod" ]] && { log_error "Destroy on prod is blocked."; exit 1; }
      read -r -p "Type 'destroy' to confirm: " confirm
      [[ "$confirm" == "destroy" ]] || { log_info "Aborted."; exit 0; }
      terraform destroy -var-file="$tfvars_file" -auto-approve
      log_success "Infrastructure destroyed for ${env}"
      ;;
    *)
      log_error "Unknown terraform action: $action"; exit 1 ;;
  esac
  cd "$SCRIPT_DIR"
}

deploy_kubernetes() {
  local mode="$1"
  local env="${2:-dev}"
  log_info "=== Kubernetes ${mode} [${env}] ==="

  if ! kubectl cluster-info &>/dev/null; then
    log_error "Cannot connect to Kubernetes cluster"
    exit 1
  fi

  local overlay_dir="${SCRIPT_DIR}/kubernetes/environments/${env}"
  if [[ ! -d "$overlay_dir" ]]; then
    log_warn "No environment overlay at ${overlay_dir}, using base"
    overlay_dir="${SCRIPT_DIR}/kubernetes/base"
  fi

  case "$mode" in
    dry-run)
      kubectl apply -k "$overlay_dir" --dry-run=client
      log_success "Dry-run passed"
      ;;
    apply)
      kubectl apply -k "$overlay_dir"
      kubectl rollout status deployment/quantumnest-backend -n "quantumnest-${env}" --timeout=300s
      kubectl rollout status deployment/quantumnest-web-frontend -n "quantumnest-${env}" --timeout=300s
      kubectl rollout status deployment/quantumnest-mobile-frontend -n "quantumnest-${env}" --timeout=300s
      log_success "Kubernetes deployed for ${env}"
      ;;
    status)
      kubectl get pods,svc,ingress -n "quantumnest-${env}"
      ;;
    *)
      log_error "Unknown kubernetes mode: $mode"; exit 1 ;;
  esac
}

deploy_monitoring() {
  local action="${1:-up}"
  log_info "=== Monitoring Stack [${action}] ==="

  if [[ ! -f "${SCRIPT_DIR}/.env" ]]; then
    log_warn ".env file not found. Copy .env.example to .env and fill in values."
    exit 1
  fi

  case "$action" in
    up)
      docker compose --env-file .env up -d prometheus alertmanager grafana elasticsearch kibana logstash node-exporter cadvisor
      log_success "Monitoring stack started"
      log_info "Grafana:       http://localhost:${GRAFANA_PORT:-3030}"
      log_info "Prometheus:    http://localhost:${PROMETHEUS_PORT:-9090}"
      log_info "Kibana:        http://localhost:${KIBANA_PORT:-5601}"
      log_info "Alertmanager:  http://localhost:${ALERTMANAGER_PORT:-9093}"
      ;;
    down)
      docker compose down
      log_success "Monitoring stack stopped"
      ;;
    logs)
      docker compose logs -f --tail=100
      ;;
    status)
      docker compose ps
      ;;
    *)
      log_error "Unknown monitoring action: $action"; exit 1 ;;
  esac
}

run_ansible() {
  local mode="$1"
  local env="${2:-dev}"
  log_info "=== Ansible ${mode} [${env}] ==="

  local inventory="${SCRIPT_DIR}/ansible/inventory/hosts.yml"
  local playbook="${SCRIPT_DIR}/ansible/playbooks/main.yml"

  if [[ ! -f "$inventory" ]]; then
    log_error "Inventory not found: $inventory"; exit 1
  fi

  case "$mode" in
    check)
      ansible-playbook -i "$inventory" "$playbook" --check --diff -e "environment=${env}"
      ;;
    apply)
      ansible-playbook -i "$inventory" "$playbook" -e "environment=${env}"
      log_success "Ansible playbook executed"
      ;;
    *)
      log_error "Unknown ansible mode: $mode"; exit 1 ;;
  esac
}

print_menu() {
  echo "Usage: $0 <command> [options]"
  echo ""
  echo "Commands:"
  echo "  terraform plan   <env>     - Plan Terraform changes"
  echo "  terraform apply  <env>     - Apply Terraform changes"
  echo "  terraform destroy <env>    - Destroy infrastructure (non-prod only)"
  echo "  kubernetes dry-run <env>   - Dry-run Kubernetes manifests"
  echo "  kubernetes apply  <env>    - Apply Kubernetes manifests"
  echo "  kubernetes status <env>    - Show Kubernetes resource status"
  echo "  monitoring up              - Start monitoring stack (Docker Compose)"
  echo "  monitoring down            - Stop monitoring stack"
  echo "  monitoring logs            - Tail monitoring logs"
  echo "  monitoring status          - Show monitoring stack status"
  echo "  ansible check  <env>       - Check Ansible playbook (dry-run)"
  echo "  ansible apply  <env>       - Run Ansible playbook"
  echo "  validate                   - Run infrastructure validation"
  echo ""
  echo "Environments: dev, staging, prod"
  echo ""
  echo "Examples:"
  echo "  $0 terraform plan dev"
  echo "  $0 kubernetes apply staging"
  echo "  $0 monitoring up"
}

# Main
print_header
check_dependencies

case "${1:-help}" in
  terraform)
    validate_environment "${3:-dev}"
    deploy_terraform "${2:-plan}" "${3:-dev}"
    ;;
  kubernetes|k8s)
    deploy_kubernetes "${2:-dry-run}" "${3:-dev}"
    ;;
  monitoring)
    deploy_monitoring "${2:-up}"
    ;;
  ansible)
    run_ansible "${2:-check}" "${3:-dev}"
    ;;
  validate)
    bash "${SCRIPT_DIR}/validate_infrastructure.sh"
    ;;
  help|--help|-h|"")
    print_menu
    ;;
  *)
    log_error "Unknown command: ${1}"
    print_menu
    exit 1
    ;;
esac
