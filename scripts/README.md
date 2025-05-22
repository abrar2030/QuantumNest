# QuantumNest Automation Scripts

This collection of automation scripts enhances the development workflow and project management for the QuantumNest repository. These scripts complement the existing automation while adding new capabilities to streamline development, testing, and deployment processes.

## Scripts Overview

### 1. Environment Variable Manager (`env_manager.sh`)

Manages environment variables across all QuantumNest components, ensuring consistent configuration.

**Features:**
- Check status of environment files across components
- Generate template .env files for all components
- Synchronize common variables across components
- Backup and restore environment files
- Validate environment files for required variables

**Usage:**
```bash
./env_manager.sh [COMMAND]
```

**Commands:**
- `status` - Check status of environment files across components
- `template` - Generate template .env files for all components
- `sync` - Synchronize common variables across components
- `backup` - Backup all environment files
- `restore [TIMESTAMP]` - Restore environment files from backup
- `validate` - Validate environment files for required variables
- `help` - Display help message

### 2. Log Aggregator (`log_aggregator.sh`)

Collects and aggregates logs from all QuantumNest components for easier debugging and monitoring.

**Features:**
- Collect logs from all components
- Watch logs in real-time
- Clean old logs
- Search for terms across all logs
- Analyze logs for errors and warnings

**Usage:**
```bash
./log_aggregator.sh [COMMAND]
```

**Commands:**
- `collect` - Collect logs from all components
- `watch` - Watch logs in real-time (requires tmux)
- `clean [days]` - Clean logs older than specified days (default: 7)
- `search [term]` - Search for a term across all logs
- `analyze` - Analyze logs for errors and warnings
- `help` - Display help message

### 3. Dependency Health Checker (`dependency_checker.sh`)

Checks the health and versions of all dependencies across the QuantumNest project components.

**Features:**
- Check all dependencies across components
- Check for outdated dependencies
- Run security audit on dependencies
- Generate comprehensive dependency report
- Fix dependency issues

**Usage:**
```bash
./dependency_checker.sh [COMMAND]
```

**Commands:**
- `check` - Check all dependencies across components
- `outdated` - Check for outdated dependencies
- `security` - Run security audit on dependencies
- `report` - Generate comprehensive dependency report
- `fix [component]` - Attempt to fix dependency issues (optional: specify component)
- `help` - Display help message

### 4. CI/CD Enhancer (`cicd_enhancer.sh`)

Provides additional CI/CD capabilities to complement the existing GitHub Actions workflow.

**Features:**
- Check status of CI/CD configuration
- Validate CI/CD workflow files
- Run CI tests locally before pushing
- Create preview deployments
- Generate new workflow files from templates

**Usage:**
```bash
./cicd_enhancer.sh [COMMAND]
```

**Commands:**
- `status` - Check status of CI/CD configuration
- `validate` - Validate CI/CD workflow files
- `local-test` - Run CI tests locally before pushing
- `preview-deploy` - Create a preview deployment
- `generate` - Generate new workflow file from template
- `help` - Display help message

## Installation

1. Extract the zip file to your QuantumNest project directory:
   ```bash
   unzip quantumnest_automation_scripts.zip -d /path/to/QuantumNest/
   ```

2. Make the scripts executable:
   ```bash
   chmod +x /path/to/QuantumNest/automation_scripts/*.sh
   ```

3. Run the scripts from the automation_scripts directory:
   ```bash
   cd /path/to/QuantumNest/automation_scripts
   ./script_name.sh command
   ```

## Integration with Existing Scripts

These automation scripts complement the existing scripts in the QuantumNest repository:

- `lint-all.sh` - The dependency checker can be used alongside this to ensure dependencies are healthy before linting
- `run_quantumnest.sh` - The environment variable manager ensures proper configuration before running the application
- `setup_quantumnest_env.sh` - The dependency checker can verify all dependencies are correctly installed after setup

## Best Practices

1. Run the environment variable manager before starting development to ensure proper configuration
2. Use the log aggregator to troubleshoot issues across components
3. Run the dependency checker regularly to keep dependencies up-to-date and secure
4. Use the CI/CD enhancer to test changes locally before pushing to the repository

## Requirements

- Bash shell environment
- Access to the QuantumNest repository
- Standard Unix utilities (find, grep, sed, etc.)
- Optional: tmux (for log watching functionality)
- Optional: yamllint (for enhanced CI/CD workflow validation)
