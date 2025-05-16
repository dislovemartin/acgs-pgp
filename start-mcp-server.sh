#!/bin/bash

# Script to start a specific MCP server

# Load environment variables
set -a
source .env
set +a

# Check if server name is provided
if [ -z "$1" ]; then
  echo "Error: Please provide an MCP server name"
  echo "Usage: ./start-mcp-server.sh <server-name>"
  echo "Available servers: $(jq -r '.mcpServers | keys | join(", ")' mcp-config.json)"
  exit 1
fi

SERVER_NAME=$1

# Check if the server exists in the configuration
if ! jq -e ".mcpServers.\"$SERVER_NAME\"" mcp-config.json > /dev/null 2>&1; then
  echo "Error: MCP server '$SERVER_NAME' not found in configuration"
  echo "Available servers: $(jq -r '.mcpServers | keys | join(", ")' mcp-config.json)"
  exit 1
fi

# Extract server configuration
COMMAND=$(jq -r ".mcpServers.\"$SERVER_NAME\".command" mcp-config.json)
ARGS=$(jq -r ".mcpServers.\"$SERVER_NAME\".args | map(@sh) | join(\" \")" mcp-config.json)
ENV_VARS=$(jq -r ".mcpServers.\"$SERVER_NAME\".env // {} | to_entries | map(\"\(.key)=\(.value | gsub(\"\\${(.+?)}\"; env[\"\\1\"] // \"\"))\" ) | join(\" \")" mcp-config.json)

# Print server information
echo "Starting MCP server: $SERVER_NAME"
echo "Command: $COMMAND"
echo "Arguments: $ARGS"
if [ -n "$ENV_VARS" ]; then
  echo "Environment variables: $ENV_VARS"
fi

# Start the server with environment variables
if [ -n "$ENV_VARS" ]; then
  eval "$ENV_VARS $COMMAND $ARGS"
else
  eval "$COMMAND $ARGS"
fi
