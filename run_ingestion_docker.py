#!/usr/bin/env python3
"""
Docker-aware ingestion runner
Runs ingest.py with proper Docker network access to vectordb
"""

import subprocess
import sys
import os
import tempfile
import shutil

def run_ingestion_in_docker(target_dir, source_script_dir):
    """Run ingestion inside a temporary Python container with access to vectordb"""
    
    if not os.path.isdir(target_dir):
        print(f"❌ Directory not found: {target_dir}")
        sys.exit(1)
    
    target_dir = os.path.abspath(target_dir)
    source_script_dir = os.path.abspath(source_script_dir)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   DOCKER-BASED RAG INGESTION                            ║
╚══════════════════════════════════════════════════════════════════════════╝

📂 Target Directory: {target_dir}
📁 Scripts Location: {source_script_dir}

Running ingestion inside Docker network to access vectordb...
""")
    
    # Create a docker run command that:
    # 1. Uses Python 3.12 image
    # 2. Mounts the target directory
    # 3. Mounts the script directory
    # 4. Connects to the librechat network
    # 5. Installs dependencies and runs ingest.py
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{target_dir}:/data:ro",  # Read-only target data
        "-v", f"{source_script_dir}:/scripts",  # Script files
        "--network", "librechat_default",  # Connect to Docker network
        "python:3.12-slim",
        "bash", "-c", f"""
set -e
echo "📦 Installing dependencies..."
pip install -q \
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
    unstructured

echo "📝 Copying .env from scripts directory..."
if [ -f /scripts/.env ]; then
    cp /scripts/.env /tmp/.env
fi

echo "🚀 Starting ingestion..."
cd /scripts
python ingest.py /data
""",
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Ingestion completed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ingestion failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n❌ Error running ingestion: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_ingestion_docker.py <target_directory>")
        print("")
        print("Example:")
        print("  python run_ingestion_docker.py /home/yuvaraj/Documents/Archive/Firecrawl-Simulator/firecrawl")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    exit_code = run_ingestion_in_docker(target_dir, script_dir)
    sys.exit(exit_code)
