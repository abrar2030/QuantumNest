#!/bin/bash

# Run script for QuantumNest project
# This script starts the backend, blockchain, and frontend components

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting QuantumNest application...${NC}"

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo -e "${BLUE}Creating Python virtual environment...${NC}"
  python3 -m venv venv
fi

# Start backend server
echo -e "${BLUE}Starting backend server...${NC}"
cd backend
source ../venv/bin/activate
pip install -r requirements.txt > /dev/null
python app.py &
BACKEND_PID=$!
cd ..

# Start blockchain node
echo -e "${BLUE}Starting blockchain node...${NC}"
cd blockchain
npm install > /dev/null
npm run node &
BLOCKCHAIN_PID=$!
cd ..

# Wait for backend and blockchain to initialize
echo -e "${BLUE}Waiting for services to initialize...${NC}"
sleep 8

# Start frontend
echo -e "${BLUE}Starting frontend...${NC}"
cd frontend
npm install > /dev/null
npm start &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}QuantumNest application is running!${NC}"
echo -e "${GREEN}Backend running with PID: ${BACKEND_PID}${NC}"
echo -e "${GREEN}Blockchain node running with PID: ${BLOCKCHAIN_PID}${NC}"
echo -e "${GREEN}Frontend running with PID: ${FRONTEND_PID}${NC}"
echo -e "${GREEN}Access the application at: http://localhost:3000${NC}"
echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"

# Handle graceful shutdown
function cleanup {
  echo -e "${BLUE}Stopping services...${NC}"
  kill $FRONTEND_PID
  kill $BLOCKCHAIN_PID
  kill $BACKEND_PID
  echo -e "${GREEN}All services stopped${NC}"
  exit 0
}

trap cleanup SIGINT

# Keep script running
wait
