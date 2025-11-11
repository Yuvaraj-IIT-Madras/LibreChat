#!/bin/bash
# Run ingestion script inside the Docker network
# This allows the script to access the PostgreSQL vectordb container

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <directory_path> [additional_args]"
    echo ""
    echo "Example:"
    echo "  $0 /home/yuvaraj/Documents/Archive/Firecrawl-Simulator/firecrawl"
    exit 1
fi

TARGET_DIR="$1"
shift  # Remove first argument

if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Directory not found: $TARGET_DIR"
    exit 1
fi

# Get the absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "🚀 Starting RAG ingestion..."
echo "📂 Target directory: $TARGET_DIR"
echo ""

# Run the ingest.py script inside the rag_api container
# The container has access to the vectordb service via Docker network
docker exec -i rag_api /app/.venv/bin/python /app/ingest.py "$TARGET_DIR" "$@"

echo ""
echo "✅ Ingestion completed!"
