#!/bin/bash
# QuantumNest Log Aggregator
# This script collects and aggregates logs from all QuantumNest components
# for easier debugging and monitoring.

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

# Log directory
LOG_DIR="${PROJECT_DIR}/logs"
mkdir -p "$LOG_DIR"

# Function to display help message
function show_help {
  echo -e "${BLUE}QuantumNest Log Aggregator${NC}"
  echo "This script collects and aggregates logs from all QuantumNest components."
  echo ""
  echo "Usage: ./log_aggregator.sh [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  collect              Collect logs from all components"
  echo "  watch                Watch logs in real-time (requires tmux)"
  echo "  clean [days]         Clean logs older than specified days (default: 7)"
  echo "  search [term]        Search for a term across all logs"
  echo "  analyze              Analyze logs for errors and warnings"
  echo "  help                 Display this help message"
  echo ""
  echo "Examples:"
  echo "  ./log_aggregator.sh collect"
  echo "  ./log_aggregator.sh watch"
  echo "  ./log_aggregator.sh clean 14"
  echo "  ./log_aggregator.sh search \"database connection\""
  echo "  ./log_aggregator.sh analyze"
}

# Function to collect logs from all components
function collect_logs {
  local timestamp=$(date +%Y%m%d_%H%M%S)
  echo -e "${BLUE}Collecting logs from all components...${NC}"
  
  # Create timestamp directory
  local collection_dir="${LOG_DIR}/${timestamp}"
  mkdir -p "$collection_dir"
  
  # Collect Web Frontend logs
  echo "Collecting Web Frontend logs..."
  if [ -d "${WEB_FRONTEND_DIR}/.next/logs" ]; then
    cp -r "${WEB_FRONTEND_DIR}/.next/logs" "${collection_dir}/web-frontend"
    echo -e "${GREEN}✓ Web Frontend logs collected${NC}"
  else
    echo -e "${YELLOW}! No Web Frontend logs found${NC}"
  fi
  
  # Collect Mobile Frontend logs
  echo "Collecting Mobile Frontend logs..."
  if [ -d "${MOBILE_FRONTEND_DIR}/.expo/logs" ]; then
    cp -r "${MOBILE_FRONTEND_DIR}/.expo/logs" "${collection_dir}/mobile-frontend"
    echo -e "${GREEN}✓ Mobile Frontend logs collected${NC}"
  else
    echo -e "${YELLOW}! No Mobile Frontend logs found${NC}"
  fi
  
  # Collect Backend logs
  echo "Collecting Backend logs..."
  if [ -d "${BACKEND_DIR}/logs" ]; then
    cp -r "${BACKEND_DIR}/logs" "${collection_dir}/backend"
    echo -e "${GREEN}✓ Backend logs collected${NC}"
  else
    echo -e "${YELLOW}! No Backend logs found${NC}"
  fi
  
  # Collect Blockchain logs
  echo "Collecting Blockchain logs..."
  if [ -d "${BLOCKCHAIN_DIR}/logs" ]; then
    cp -r "${BLOCKCHAIN_DIR}/logs" "${collection_dir}/blockchain"
    echo -e "${GREEN}✓ Blockchain logs collected${NC}"
  else
    echo -e "${YELLOW}! No Blockchain logs found${NC}"
  fi
  
  # Create a summary file
  echo "Creating log summary..."
  {
    echo "QuantumNest Log Collection"
    echo "Timestamp: $(date)"
    echo "Collection ID: ${timestamp}"
    echo ""
    echo "Components:"
    
    if [ -d "${collection_dir}/web-frontend" ]; then
      echo "- Web Frontend: $(find "${collection_dir}/web-frontend" -type f | wc -l) files"
    else
      echo "- Web Frontend: No logs"
    fi
    
    if [ -d "${collection_dir}/mobile-frontend" ]; then
      echo "- Mobile Frontend: $(find "${collection_dir}/mobile-frontend" -type f | wc -l) files"
    else
      echo "- Mobile Frontend: No logs"
    fi
    
    if [ -d "${collection_dir}/backend" ]; then
      echo "- Backend: $(find "${collection_dir}/backend" -type f | wc -l) files"
    else
      echo "- Backend: No logs"
    fi
    
    if [ -d "${collection_dir}/blockchain" ]; then
      echo "- Blockchain: $(find "${collection_dir}/blockchain" -type f | wc -l) files"
    else
      echo "- Blockchain: No logs"
    fi
  } > "${collection_dir}/summary.txt"
  
  echo -e "${GREEN}Log collection complete: ${collection_dir}${NC}"
  echo "Summary file created: ${collection_dir}/summary.txt"
}

# Function to watch logs in real-time
function watch_logs {
  # Check if tmux is installed
  if ! command -v tmux &> /dev/null; then
    echo -e "${RED}Error: tmux is required for watching logs.${NC}"
    echo "Please install tmux and try again."
    return 1
  fi
  
  echo -e "${BLUE}Setting up log watching with tmux...${NC}"
  
  # Create a new tmux session
  tmux new-session -d -s quantumnest_logs
  
  # Set up panes for each component
  tmux split-window -h -t quantumnest_logs
  tmux split-window -v -t quantumnest_logs:0.0
  tmux split-window -v -t quantumnest_logs:0.1
  
  # Web Frontend logs
  if [ -f "${WEB_FRONTEND_DIR}/.next/logs/nextjs.log" ]; then
    tmux send-keys -t quantumnest_logs:0.0 "echo -e '${BLUE}Web Frontend Logs${NC}' && tail -f ${WEB_FRONTEND_DIR}/.next/logs/nextjs.log" C-m
  else
    tmux send-keys -t quantumnest_logs:0.0 "echo -e '${YELLOW}Web Frontend Logs (not found)${NC}'" C-m
  fi
  
  # Mobile Frontend logs
  if [ -f "${MOBILE_FRONTEND_DIR}/.expo/logs/metro.log" ]; then
    tmux send-keys -t quantumnest_logs:0.1 "echo -e '${BLUE}Mobile Frontend Logs${NC}' && tail -f ${MOBILE_FRONTEND_DIR}/.expo/logs/metro.log" C-m
  else
    tmux send-keys -t quantumnest_logs:0.1 "echo -e '${YELLOW}Mobile Frontend Logs (not found)${NC}'" C-m
  fi
  
  # Backend logs
  if [ -f "${BACKEND_DIR}/logs/app.log" ]; then
    tmux send-keys -t quantumnest_logs:0.2 "echo -e '${BLUE}Backend Logs${NC}' && tail -f ${BACKEND_DIR}/logs/app.log" C-m
  else
    tmux send-keys -t quantumnest_logs:0.2 "echo -e '${YELLOW}Backend Logs (not found)${NC}'" C-m
  fi
  
  # Blockchain logs
  if [ -f "${BLOCKCHAIN_DIR}/logs/node.log" ]; then
    tmux send-keys -t quantumnest_logs:0.3 "echo -e '${BLUE}Blockchain Logs${NC}' && tail -f ${BLOCKCHAIN_DIR}/logs/node.log" C-m
  else
    tmux send-keys -t quantumnest_logs:0.3 "echo -e '${YELLOW}Blockchain Logs (not found)${NC}'" C-m
  fi
  
  # Attach to the session
  echo -e "${GREEN}Log watching session created.${NC}"
  echo "Attaching to tmux session. Press Ctrl+B then D to detach."
  echo "To reattach later, run: tmux attach -t quantumnest_logs"
  sleep 2
  tmux attach -t quantumnest_logs
}

# Function to clean old logs
function clean_logs {
  local days=${1:-7}
  
  if ! [[ "$days" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: Days must be a positive number.${NC}"
    return 1
  fi
  
  echo -e "${BLUE}Cleaning logs older than ${days} days...${NC}"
  
  # Find and remove old log collections
  local old_collections=$(find "$LOG_DIR" -maxdepth 1 -type d -mtime +$days | grep -v "^$LOG_DIR$")
  local count=$(echo "$old_collections" | grep -v '^$' | wc -l)
  
  if [ $count -eq 0 ]; then
    echo -e "${GREEN}No log collections older than ${days} days found.${NC}"
    return 0
  fi
  
  echo -e "${YELLOW}Found ${count} log collection(s) older than ${days} days.${NC}"
  echo "The following directories will be removed:"
  echo "$old_collections"
  
  read -p "Continue? (y/n): " confirm
  if [ "$confirm" != "y" ]; then
    echo "Operation cancelled."
    return 0
  fi
  
  echo "$old_collections" | xargs rm -rf
  echo -e "${GREEN}Cleaned ${count} old log collection(s).${NC}"
}

# Function to search across all logs
function search_logs {
  local term="$1"
  
  if [ -z "$term" ]; then
    echo -e "${RED}Error: Search term required.${NC}"
    echo "Usage: ./log_aggregator.sh search \"your search term\""
    return 1
  fi
  
  echo -e "${BLUE}Searching for '${term}' across all logs...${NC}"
  
  # Create results directory
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local results_dir="${LOG_DIR}/search_${timestamp}"
  mkdir -p "$results_dir"
  
  # Search in all log collections
  local collections=$(find "$LOG_DIR" -maxdepth 1 -type d | grep -v "^$LOG_DIR$" | grep -v "search_")
  
  if [ -z "$collections" ]; then
    echo -e "${YELLOW}No log collections found.${NC}"
    echo "Run './log_aggregator.sh collect' to collect logs first."
    rm -rf "$results_dir"
    return 1
  fi
  
  echo "Searching in $(echo "$collections" | wc -l) log collection(s)..."
  
  {
    echo "QuantumNest Log Search Results"
    echo "Search Term: ${term}"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
  } > "${results_dir}/results.txt"
  
  local total_matches=0
  
  for collection in $collections; do
    local collection_name=$(basename "$collection")
    echo "Searching in collection: ${collection_name}"
    
    {
      echo "Collection: ${collection_name}"
      echo "----------------------------------------"
    } >> "${results_dir}/results.txt"
    
    local matches=$(grep -r --include="*.log" "$term" "$collection" 2>/dev/null)
    local match_count=$(echo "$matches" | grep -v '^$' | wc -l)
    total_matches=$((total_matches + match_count))
    
    if [ $match_count -eq 0 ]; then
      echo "  No matches found."
      echo "No matches found." >> "${results_dir}/results.txt"
    else
      echo "  Found ${match_count} matches."
      echo "$matches" >> "${results_dir}/results.txt"
    fi
    
    echo "" >> "${results_dir}/results.txt"
    echo "----------------------------------------" >> "${results_dir}/results.txt"
    echo "" >> "${results_dir}/results.txt"
  done
  
  echo -e "${GREEN}Search complete. Found ${total_matches} total matches.${NC}"
  echo "Results saved to: ${results_dir}/results.txt"
}

# Function to analyze logs for errors and warnings
function analyze_logs {
  echo -e "${BLUE}Analyzing logs for errors and warnings...${NC}"
  
  # Create analysis directory
  local timestamp=$(date +%Y%m%d_%H%M%S)
  local analysis_dir="${LOG_DIR}/analysis_${timestamp}"
  mkdir -p "$analysis_dir"
  
  # Find the most recent log collection
  local latest_collection=$(find "$LOG_DIR" -maxdepth 1 -type d | grep -v "^$LOG_DIR$" | grep -v "search_" | grep -v "analysis_" | sort -r | head -n 1)
  
  if [ -z "$latest_collection" ]; then
    echo -e "${YELLOW}No log collections found.${NC}"
    echo "Run './log_aggregator.sh collect' to collect logs first."
    rm -rf "$analysis_dir"
    return 1
  fi
  
  echo "Analyzing most recent log collection: $(basename "$latest_collection")"
  
  {
    echo "QuantumNest Log Analysis"
    echo "Collection: $(basename "$latest_collection")"
    echo "Timestamp: $(date)"
    echo "----------------------------------------"
    echo ""
  } > "${analysis_dir}/analysis.txt"
  
  # Analyze errors
  echo "Analyzing errors..."
  {
    echo "## ERROR ANALYSIS"
    echo "----------------------------------------"
    
    local error_count=$(grep -r -i "error" "$latest_collection" 2>/dev/null | wc -l)
    echo "Total errors found: ${error_count}"
    echo ""
    
    if [ $error_count -gt 0 ]; then
      echo "### Most common errors:"
      grep -r -i "error" "$latest_collection" 2>/dev/null | sort | uniq -c | sort -nr | head -n 10
      echo ""
      
      echo "### Error distribution by component:"
      echo "- Web Frontend: $(grep -r -i "error" "${latest_collection}/web-frontend" 2>/dev/null | wc -l)"
      echo "- Mobile Frontend: $(grep -r -i "error" "${latest_collection}/mobile-frontend" 2>/dev/null | wc -l)"
      echo "- Backend: $(grep -r -i "error" "${latest_collection}/backend" 2>/dev/null | wc -l)"
      echo "- Blockchain: $(grep -r -i "error" "${latest_collection}/blockchain" 2>/dev/null | wc -l)"
    fi
    
    echo ""
  } >> "${analysis_dir}/analysis.txt"
  
  # Analyze warnings
  echo "Analyzing warnings..."
  {
    echo "## WARNING ANALYSIS"
    echo "----------------------------------------"
    
    local warning_count=$(grep -r -i "warning" "$latest_collection" 2>/dev/null | wc -l)
    echo "Total warnings found: ${warning_count}"
    echo ""
    
    if [ $warning_count -gt 0 ]; then
      echo "### Most common warnings:"
      grep -r -i "warning" "$latest_collection" 2>/dev/null | sort | uniq -c | sort -nr | head -n 10
      echo ""
      
      echo "### Warning distribution by component:"
      echo "- Web Frontend: $(grep -r -i "warning" "${latest_collection}/web-frontend" 2>/dev/null | wc -l)"
      echo "- Mobile Frontend: $(grep -r -i "warning" "${latest_collection}/mobile-frontend" 2>/dev/null | wc -l)"
      echo "- Backend: $(grep -r -i "warning" "${latest_collection}/backend" 2>/dev/null | wc -l)"
      echo "- Blockchain: $(grep -r -i "warning" "${latest_collection}/blockchain" 2>/dev/null | wc -l)"
    fi
    
    echo ""
  } >> "${analysis_dir}/analysis.txt"
  
  # Performance analysis
  echo "Analyzing performance indicators..."
  {
    echo "## PERFORMANCE ANALYSIS"
    echo "----------------------------------------"
    
    # Look for response time indicators
    local response_times=$(grep -r -i "response time\|latency\|took [0-9]" "$latest_collection" 2>/dev/null)
    if [ -n "$response_times" ]; then
      echo "### Response time indicators:"
      echo "$response_times" | head -n 20
      echo ""
    fi
    
    # Look for memory usage
    local memory_usage=$(grep -r -i "memory\|heap\|ram" "$latest_collection" 2>/dev/null)
    if [ -n "$memory_usage" ]; then
      echo "### Memory usage indicators:"
      echo "$memory_usage" | head -n 20
      echo ""
    fi
    
    echo ""
  } >> "${analysis_dir}/analysis.txt"
  
  echo -e "${GREEN}Analysis complete.${NC}"
  echo "Results saved to: ${analysis_dir}/analysis.txt"
}

# Main script execution
case "$1" in
  collect)
    collect_logs
    ;;
  watch)
    watch_logs
    ;;
  clean)
    clean_logs "$2"
    ;;
  search)
    search_logs "$2"
    ;;
  analyze)
    analyze_logs
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
