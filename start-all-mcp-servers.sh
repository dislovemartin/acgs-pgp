#!/bin/bash

# Script to start all MCP servers defined in the configuration

# Load environment variables
set -a
source .env
set +a

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install jq first."
  echo "On Ubuntu/Debian: sudo apt-get install jq"
  echo "On macOS: brew install jq"
  exit 1
fi

# Get all server names from the configuration
SERVER_NAMES=$(jq -r '.mcpServers | keys | join(" ")' mcp-config.json)

echo "Starting all MCP servers: $SERVER_NAMES"
echo "Press Ctrl+C to stop all servers"

# Start each server in the background
for SERVER_NAME in $SERVER_NAMES; do
  echo "Starting $SERVER_NAME in the background..."
  ./start-mcp-server.sh "$SERVER_NAME" > "logs/mcp-$SERVER_NAME.log" 2>&1 &
  PID=$!
  echo "$SERVER_NAME started with PID $PID"
  echo "$SERVER_NAME:$PID" >> .mcp-pids
done

# Function to clean up on exit
cleanup() {
  echo "Stopping all MCP servers..."
  if [ -f .mcp-pids ]; then
    while read -r LINE; do
      SERVER_NAME=$(echo "$LINE" | cut -d':' -f1)
      PID=$(echo "$LINE" | cut -d':' -f2)
      echo "Stopping $SERVER_NAME (PID: $PID)..."
      kill $PID 2>/dev/null || true
    done < .mcp-pids
    rm .mcp-pids
  fi
  echo "All MCP servers stopped"
  exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Create logs directory if it doesn't exist
mkdir -p logs

# Wait for Ctrl+C
echo "All MCP servers started. Check logs in the logs directory."
echo "Press Ctrl+C to stop all servers"
while true; do
  sleep 1
done
