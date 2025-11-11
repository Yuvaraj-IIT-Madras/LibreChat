#!/usr/bin/env python3
"""
Host-based RAG ingestion with Docker bridge network access
Uses SSH tunnel or direct connection as fallback
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def setup_port_forward():
    """Set up port forwarding from host to container"""
    print("🔌 Setting up port forwarding...")
    try:
        # Check if port 5432 is already forwarded
        result = subprocess.run(
            ["docker", "port", "vectordb", "5432"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Port forwarding already configured")
            return True
        else:
            print("⚠️  Port not forwarded, attempting to use docker exec...")
            return False
    except Exception as e:
        print(f"⚠️  Could not check port forwarding: {e}")
        return False

def run_ingestion_in_container():
    """Run ingestion inside a dedicated container with access to vectordb"""
    print("🐳 Running ingestion in Docker container...")
    
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if not os.path.isdir(target_dir):
        print(f"❌ Directory not found: {target_dir}")
        sys.exit(1)
    
    target_dir = os.path.abspath(target_dir)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║              FIRECRAWL PROJECT - RAG INGESTION                        ║
╚═══════════════════════════════════════════════════════════════════════╝

📂 Directory: {target_dir}
🐳 Method: Docker container with network bridge
🗄️  Database: PostgreSQL with pgvector

Starting ingestion...
""")
    
    # Build docker exec command
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{target_dir}:/data:ro",
        "-v", f"{script_dir}:/scripts",
        "--network", "librechat_default",
        "-e", f"DB_HOST=vectordb",
        "-e", f"DB_PORT=5432",
        "-e", f"DB_NAME=mydatabase",
        "-e", f"DB_USER=myuser",
        "-e", f"DB_PASSWORD=mypassword",
        "-e", f"GOOGLE_KEY={os.getenv('GOOGLE_KEY', '')}",
        "python:3.12-slim",
        "bash", "-c", """
set -e

# Install dependencies
echo "📦 Installing dependencies..."
pip install --quiet \
    langchain \
    langchain-community \
    langchain-text-splitters \
    langchain-google-genai \
    psycopg2-binary \
    pgvector \
    pathspec \
    python-dotenv \
    pdf2image \
    pillow \
    unstructured \
    chardet

# Run ingestion
echo "🚀 Starting RAG ingestion..."
cd /scripts
python3 << 'EOF'
import sys
import os
sys.path.insert(0, '/scripts')

# Make sure env vars are set
os.environ.setdefault('DB_HOST', 'vectordb')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_NAME', 'mydatabase')
os.environ.setdefault('DB_USER', 'myuser')
os.environ.setdefault('DB_PASSWORD', 'mypassword')

# Import and run ingest
from ingest import main
sys.argv = ['ingest.py', '/data']
main() if 'main' in dir() else exec(open('ingest.py').read())
EOF
"""
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Ingestion completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ingestion failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ingest_via_docker.py <directory_path>")
        print("")
        print("Example:")
        print("  python3 ingest_via_docker.py /home/yuvaraj/Documents/Archive/Firecrawl-Simulator/firecrawl")
        sys.exit(1)
    
    sys.exit(run_ingestion_in_container())
