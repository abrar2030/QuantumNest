#!/bin/bash

# QuantumNest Project Setup Script (Comprehensive)

# Exit immediately if a command exits with a non-zero status.
set -e

# Prerequisites (ensure these are installed):
# - Node.js (v16+ for frontend, also for blockchain component)
# - npm (Node package manager)
# - Python 3.10+ (for backend - script will use python3.11)
# - pip (Python package installer)
# - PostgreSQL (for backend database)
# - Ethereum wallet (MetaMask, WalletConnect, or Coinbase Wallet) for blockchain interaction

echo "Starting QuantumNest project setup..."

PROJECT_DIR="/home/ubuntu/projects_extracted/QuantumNest"

if [ ! -d "${PROJECT_DIR}" ]; then
  echo "Error: Project directory ${PROJECT_DIR} not found."
  echo "Please ensure the project is extracted correctly."
  exit 1
fi

cd "${PROJECT_DIR}"
echo "Changed directory to $(pwd)"

# --- Backend Setup (FastAPI/Python) ---
echo ""
echo "Setting up QuantumNest Backend..."
BACKEND_DIR_QN="${PROJECT_DIR}/backend"

if [ ! -d "${BACKEND_DIR_QN}" ]; then
    echo "Error: Backend directory ${BACKEND_DIR_QN} not found. Skipping backend setup."
else
    cd "${BACKEND_DIR_QN}"
    echo "Changed directory to $(pwd) for backend setup."

    if [ ! -f "requirements.txt" ]; then
        echo "Warning: requirements.txt not found in ${BACKEND_DIR_QN} as per README instructions."
        echo "The README mentions 'pip install -r requirements.txt' for the backend."
        echo "Please ensure backend dependencies are manually identified and installed, or the requirements.txt is created."
        echo "A Python virtual environment will still be created as per README instructions."
    fi

    echo "Creating Python virtual environment for backend (venv_quantumnest_backend_py)..."
    # README specifies `python -m venv venv` and `source venv/bin/activate`
    if ! python3.11 -m venv venv; then # Using the name 'venv' as per README
        echo "Failed to create backend virtual environment. Please check your Python installation."
    else
        source venv/bin/activate
        echo "Backend Python virtual environment 'venv' created and activated."
        
        if [ -f "requirements.txt" ]; then
            echo "Installing backend Python dependencies from requirements.txt..."
            pip3 install -r requirements.txt
            echo "Backend dependencies installed."
        else
            echo "Skipping pip install for backend as requirements.txt was not found."
        fi
        
        echo "To activate the backend virtual environment later, run: source ${BACKEND_DIR_QN}/venv/bin/activate"
        echo "To start the backend server (from project root after activating venv): npm run backend:dev (as per README)"
        deactivate
        echo "Backend Python virtual environment deactivated."
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Web Frontend Setup (Next.js/Node.js) ---
# README refers to 'frontend/' but 'web-frontend/' directory was found with a package.json
echo ""
echo "Setting up QuantumNest Web Frontend..."
WEB_FRONTEND_DIR_QN="${PROJECT_DIR}/web-frontend"
# The README project structure shows 'frontend/', but the `ls` output showed 'web-frontend/'
# The find command also showed 'web-frontend/package.json'

if [ ! -d "${WEB_FRONTEND_DIR_QN}" ]; then
    # Fallback to 'frontend/' if 'web-frontend/' doesn't exist, as per README structure diagram
    if [ -d "${PROJECT_DIR}/frontend" ]; then
        WEB_FRONTEND_DIR_QN="${PROJECT_DIR}/frontend"
        echo "Note: Using ${WEB_FRONTEND_DIR_QN} as 'web-frontend' directory was not found."
    else
        echo "Error: Web Frontend directory (neither ${PROJECT_DIR}/web-frontend nor ${PROJECT_DIR}/frontend) not found. Skipping Web Frontend setup."
        WEB_FRONTEND_DIR_QN=""
    fi
fi

if [ -n "${WEB_FRONTEND_DIR_QN}" ] && [ -d "${WEB_FRONTEND_DIR_QN}" ]; then
    cd "${WEB_FRONTEND_DIR_QN}"
    echo "Changed directory to $(pwd) for Web Frontend setup."

    if [ ! -f "package.json" ]; then
        echo "Error: package.json not found in ${WEB_FRONTEND_DIR_QN}. Cannot install Web Frontend dependencies."
    else
        echo "Installing Web Frontend Node.js dependencies using npm..."
        if ! command -v npm &> /dev/null; then echo "npm command not found."; else npm install; fi
        echo "Web Frontend dependencies installed."
        echo "To start the Web Frontend development server (from project root): npm run frontend:dev (as per README)"
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Mobile Frontend Setup (Next.js/Node.js) ---
echo ""
echo "Setting up QuantumNest Mobile Frontend..."
MOBILE_FRONTEND_DIR_QN="${PROJECT_DIR}/mobile-frontend"

if [ ! -d "${MOBILE_FRONTEND_DIR_QN}" ]; then
    echo "Error: Mobile Frontend directory ${MOBILE_FRONTEND_DIR_QN} not found. Skipping Mobile Frontend setup."
else
    cd "${MOBILE_FRONTEND_DIR_QN}"
    echo "Changed directory to $(pwd) for Mobile Frontend setup."

    if [ ! -f "package.json" ]; then
        echo "Error: package.json not found in ${MOBILE_FRONTEND_DIR_QN}. Cannot install Mobile Frontend dependencies."
    else
        echo "Installing Mobile Frontend Node.js dependencies using pnpm (as indicated by packageManager in package.json)..."
        if ! command -v pnpm &> /dev/null; then 
            echo "pnpm command not found. Attempting to install pnpm globally using npm..."
            if command -v npm &> /dev/null; then 
                sudo npm install -g pnpm
                if ! command -v pnpm &> /dev/null; then 
                    echo "Failed to install pnpm. Please install pnpm manually and re-run or install dependencies manually."
                else
                    echo "pnpm installed successfully. Proceeding with dependency installation."
                    pnpm install
                    echo "Mobile Frontend dependencies installed using pnpm."
                fi
            else 
                echo "npm command not found. Cannot install pnpm. Please install pnpm manually and re-run or install dependencies manually."
            fi
        else
            pnpm install
            echo "Mobile Frontend dependencies installed using pnpm."
        fi
        echo "To start the Mobile Frontend development server (from ${MOBILE_FRONTEND_DIR_QN}): pnpm dev (as per package.json)"
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Blockchain Setup (Node.js/Hardhat) ---
echo ""
echo "Setting up QuantumNest Blockchain component..."
BLOCKCHAIN_DIR_QN="${PROJECT_DIR}/blockchain"

if [ ! -d "${BLOCKCHAIN_DIR_QN}" ]; then
    echo "Error: Blockchain directory ${BLOCKCHAIN_DIR_QN} not found. Skipping blockchain setup."
else
    cd "${BLOCKCHAIN_DIR_QN}"
    echo "Changed directory to $(pwd) for blockchain setup."

    if [ ! -f "package.json" ]; then
        echo "Error: package.json not found in ${BLOCKCHAIN_DIR_QN}. Cannot install blockchain dependencies."
    else
        echo "Installing blockchain Node.js dependencies using npm..."
        if ! command -v npm &> /dev/null; then echo "npm command not found."; else npm install; fi
        echo "Blockchain dependencies installed."
        echo "To compile smart contracts (from project root): npm run blockchain:compile (as per README)"
        echo "To deploy smart contracts to Goerli (from project root): npm run blockchain:deploy:goerli (as per README)"
    fi
    cd "${PROJECT_DIR}" # Return to the main project directory
fi

# --- Environment Variables ---
echo ""
echo "Reminder: Set up environment variables."
echo "Create .env files in both 'web-frontend' (or 'frontend') and 'blockchain' directories based on the provided .env.example files."

# --- PostgreSQL Setup Reminder ---
echo ""
echo "Reminder: Ensure PostgreSQL is installed, running, and configured for the backend."
echo "Database connection details will likely be needed in the backend's environment or configuration."

echo ""
echo "QuantumNest project setup script finished."
echo "Please ensure all prerequisites (Node.js, Python, pip, npm, pnpm, PostgreSQL, Ethereum Wallet) are installed and configured."
echo "Review the project's README.md and the instructions above for running different components."
