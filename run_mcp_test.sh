#!/bin/bash
# Quick test script for MCP server

echo "Testing MCP Server for Django Todo App"
echo "========================================"
echo ""

cd "$(dirname "$0")"

if [ ! -d "venv-mcp" ]; then
    echo "Error: venv-mcp directory not found"
    echo "Please ensure the MCP virtual environment is set up"
    exit 1
fi

source venv-mcp/bin/activate
python test_mcp.py
