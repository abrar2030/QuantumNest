# Ansible Configuration Management

## Prerequisites

- Ansible 2.14+
- SSH access to target servers
- sudo privileges on target servers

## Setup

### 1. Install Ansible

```bash
# On macOS
brew install ansible

# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y ansible

# Via pip
pip install ansible ansible-lint
```

### 2. Install Required Collections

```bash
ansible-galaxy collection install -r requirements.yml
```

### 3. Configure Inventory

```bash
# Copy example inventory
cp inventory/hosts.example.yml inventory/hosts.yml

# Edit with your server IPs
vi inventory/hosts.yml
```

### 4. Configure Vault (for secrets)

```bash
# Create vault file
cp group_vars/all/vault.example.yml group_vars/all/vault.yml

# Encrypt it
ansible-vault encrypt group_vars/all/vault.yml

# Edit encrypted file
ansible-vault edit group_vars/all/vault.yml
```

## Running Playbooks

### Dry Run (Check Mode)

```bash
# Check what would be changed
ansible-playbook playbooks/main.yml --check --diff

# Check specific hosts
ansible-playbook playbooks/main.yml --check --limit webservers
```

### Execute Playbooks

```bash
# Run on all hosts
ansible-playbook playbooks/main.yml

# Run with vault password
ansible-playbook playbooks/main.yml --ask-vault-pass

# Or use vault password file
ansible-playbook playbooks/main.yml --vault-password-file ~/.vault_pass

# Run on specific hosts
ansible-playbook playbooks/main.yml --limit databases

# Run with tags
ansible-playbook playbooks/main.yml --tags "webserver"
```

### Ad-hoc Commands

```bash
# Ping all hosts
ansible all -m ping

# Check disk space
ansible all -m shell -a "df -h"

# Restart service
ansible webservers -m service -a "name=nginx state=restarted" --become
```

## Linting and Validation

```bash
# Lint playbooks
ansible-lint playbooks/

# Check playbook syntax
ansible-playbook playbooks/main.yml --syntax-check

# List tasks
ansible-playbook playbooks/main.yml --list-tasks

# List hosts
ansible-playbook playbooks/main.yml --list-hosts
```

## Directory Structure

```
ansible/
├── ansible.cfg              # Ansible configuration
├── inventory/
│   ├── hosts.yml           # Inventory file (git-ignored)
│   └── hosts.example.yml   # Inventory template
├── group_vars/
│   └── all/
│       └── vault.yml       # Encrypted secrets (git-ignored)
├── playbooks/
│   └── main.yml            # Main playbook
└── roles/
    ├── common/             # Common tasks for all servers
    ├── webserver/          # Web server configuration
    └── database/           # Database configuration
```

## Troubleshooting

```bash
# Verbose output
ansible-playbook playbooks/main.yml -v    # verbose
ansible-playbook playbooks/main.yml -vv   # more verbose
ansible-playbook playbooks/main.yml -vvv  # even more verbose

# Debug variables
ansible all -m debug -a "var=hostvars[inventory_hostname]"

# Test connectivity
ansible all -m ping -vvv
```
