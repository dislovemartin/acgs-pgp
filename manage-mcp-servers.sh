#!/bin/bash

# Script to manage MCP servers (list, stop, restart)

# Function to list running MCP servers
list_servers() {
  echo "Running MCP servers:"
  if [ -f .mcp-pids ]; then
    while read -r LINE; do
      SERVER_NAME=$(echo "$LINE" | cut -d':' -f1)
      PID=$(echo "$LINE" | cut -d':' -f2)
      if ps -p $PID > /dev/null; then
        echo "  $SERVER_NAME (PID: $PID) - Running"
      else
        echo "  $SERVER_NAME (PID: $PID) - Not running (crashed or stopped)"
      fi
    done < .mcp-pids
  else
    echo "  No MCP servers are currently running"
  fi
}

# Function to stop a specific MCP server
stop_server() {
  SERVER_NAME=$1
  if [ -f .mcp-pids ]; then
    SERVER_LINE=$(grep "^$SERVER_NAME:" .mcp-pids)
    if [ -n "$SERVER_LINE" ]; then
      PID=$(echo "$SERVER_LINE" | cut -d':' -f2)
      echo "Stopping $SERVER_NAME (PID: $PID)..."
      kill $PID 2>/dev/null || true
      sed -i "/^$SERVER_NAME:/d" .mcp-pids
      echo "$SERVER_NAME stopped"
    else
      echo "Error: MCP server '$SERVER_NAME' is not running"
    fi
  else
    echo "Error: No MCP servers are currently running"
  fi
}

# Function to stop all MCP servers
stop_all_servers() {
  echo "Stopping all MCP servers..."
  if [ -f .mcp-pids ]; then
    while read -r LINE; do
      SERVER_NAME=$(echo "$LINE" | cut -d':' -f1)
      PID=$(echo "$LINE" | cut -d':' -f2)
      echo "Stopping $SERVER_NAME (PID: $PID)..."
      kill $PID 2>/dev/null || true
    done < .mcp-pids
    rm .mcp-pids
    echo "All MCP servers stopped"
  else
    echo "No MCP servers are currently running"
  fi
}

# Function to restart a specific MCP server
restart_server() {
  SERVER_NAME=$1
  echo "Restarting $SERVER_NAME..."
  stop_server "$SERVER_NAME"
  
  # Start the server again
  mkdir -p logs
  ./start-mcp-server.sh "$SERVER_NAME" > "logs/mcp-$SERVER_NAME.log" 2>&1 &
  PID=$!
  echo "$SERVER_NAME started with PID $PID"
  echo "$SERVER_NAME:$PID" >> .mcp-pids
}

# Check command
case "$1" in
  list)
    list_servers
    ;;
  stop)
    if [ -z "$2" ]; then
      stop_all_servers
    else
      stop_server "$2"
    fi
    ;;
  restart)
    if [ -z "$2" ]; then
      echo "Error: Please specify a server to restart"
      echo "Usage: $0 restart <server-name>"
      exit 1
    else
      restart_server "$2"
    fi
    ;;
  *)
    echo "Usage: $0 {list|stop|restart} [server-name]"
    echo "  list              - List all running MCP servers"
    echo "  stop [server]     - Stop a specific MCP server or all if none specified"
    echo "  restart <server>  - Restart a specific MCP server"
    echo ""
    echo "Available servers: $(jq -r '.mcpServers | keys | join(", ")' mcp-config.json)"
    exit 1
    ;;
esac

exit 0
