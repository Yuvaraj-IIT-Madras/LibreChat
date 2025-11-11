# Complete Deployment Guide: RAG + Agentic Data Analytics Stack

**Version**: 1.0  
**Date**: November 7, 2025  
**Status**: Production-Ready  
**Environments**: Local, Azure Cloud, GitHub Codespaces  

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Local Deployment](#local-deployment)
5. [Azure Deployment](#azure-deployment)
6. [GitHub Codespaces Deployment](#github-codespaces-deployment)
7. [System Components](#system-components)
8. [Configuration & Setup](#configuration--setup)
9. [Validation & Testing](#validation--testing)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides step-by-step instructions for deploying a complete AI-powered system combining:

- **RAG (Retrieval-Augmented Generation)**: Intelligent document indexing and semantic search
- **Agentic Data Analytics Stack**: LibreChat with ClickHouse MCP for data exploration
- **Intelligent Filtering**: LLM-powered technology stack detection and file filtering
- **Vector Database**: PostgreSQL with pgvector for embeddings storage

### What You'll Have After Deployment

✅ **RAG System**
- Technology-aware document filtering
- Multi-format document ingestion (Python, JavaScript, PDF, HTML, Markdown, CSV)
- Semantic search across codebases
- Supports 8+ programming languages

✅ **Agentic Data Analytics Stack**
- LibreChat web interface
- ClickHouse MCP server for data analysis
- MongoDB for conversation storage
- Meilisearch for full-text search
- PostgreSQL for vector embeddings

✅ **Multi-Environment Support**
- Reproducible across local, Azure, and GitHub Codespaces
- Identical configuration management
- Environment-specific customization

---

## Architecture

### System Components Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  LibreChat UI    │  │  Query System    │  │  Analytics   │ │
│  │  (Port 3080)     │  │  (query.py)      │  │  Interface   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Intelligence Layer                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Tech Analyzer    │  │ Ingestion        │  │ LLM Engine   │ │
│  │ (tech_analyzer) │  │ (ingest.py)      │  │ (Gemini API) │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Storage & Services Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL   │  │ MongoDB      │  │ Meilisearch  │          │
│  │ + pgvector   │  │ (3080 msgs)  │  │ (search idx) │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Chat Interface** | LibreChat (Node.js/React) | Web UI for interactions |
| **AI Models** | Google Gemini | Embeddings & LLM inference |
| **Vector DB** | PostgreSQL + pgvector | Embedding storage |
| **Document Store** | MongoDB | Conversation history |
| **Search Engine** | Meilisearch | Full-text search |
| **Analytics Server** | ClickHouse MCP | Data exploration |
| **Ingestion** | Python 3.12 | Document processing |
| **Orchestration** | Docker Compose | Container management |

---

## Prerequisites

### Required Software

- **Docker & Docker Compose** (v20+)
- **Python 3.12+** (for local development)
- **Git** (for version control)
- **Node.js 18+** (for development)

### Required API Keys

1. **Google Gemini API Key**
   - Get from: https://ai.google.dev/
   - Required for: Embeddings generation, LLM analysis
   - Cost: ~$0.01 per 1M tokens

### Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 10 GB | 50+ GB |
| Network | 10 Mbps | 100+ Mbps |

### Network Requirements

- Outbound HTTPS access (for API calls)
- Localhost networking enabled
- For Azure: Cloud Shell or DevOps Agent

---

## Local Deployment

### Step 1: Clone Repository

```bash
# Clone the LibreChat project
git clone https://github.com/danny-avila/LibreChat.git
cd LibreChat

# Or if already cloned, update it
git pull origin main
```

### Step 2: Set Up Environment Variables

```bash
# Create .env file in project root
cat > .env << 'EOF'
# Google Gemini API Configuration
GOOGLE_KEY=your-gemini-api-key-here

# Database Configuration (Docker Compose managed)
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=vectordb
DB_PORT=5432

# LibreChat Configuration
NODE_ENV=production
MONGODB_URI=mongodb://chat-mongodb:27017/LibreChat
MEILI_HOST=http://chat-meilisearch:7700
MEILI_MASTER_KEY=your-meilisearch-key

# RAG Configuration
RAG_API_URL=http://rag_api:8000
EMBEDDINGS_MODEL=models/embedding-001
EMBEDDINGS_PROVIDER=google

# Optional: Additional model support
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
EOF

# Secure the .env file
chmod 600 .env
```

### Step 3: Create Python Virtual Environment

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### Step 4: Start Docker Services

```bash
# Ensure Docker daemon is running
docker --version

# Start all services (may take 2-5 minutes)
docker compose up -d

# Verify all containers are running
docker compose ps

# Expected output:
# NAME                  STATUS
# LibreChat             Up 2 hours
# chat-mongodb          Up 2 hours
# chat-meilisearch      Up 2 hours
# mcp-clickhouse        Up 2 hours
# rag_api              Up 2 hours (may restart initially)
# vectordb              Up 2 hours
```

### Step 5: Verify Database Connectivity

```bash
# Check PostgreSQL/pgvector
docker exec vectordb pg_isready

# Expected: "accepting connections"

# Check MongoDB
docker exec chat-mongodb mongo --version

# Check Meilisearch
curl http://localhost:7700/health
```

### Step 6: Copy RAG Scripts

```bash
# Copy the intelligent RAG system scripts to project root
cp tech_analyzer.py ingest.py query.py count_files.py .documentignore /home/yuvaraj/Projects/LibreChat/

# Or if using Docker volumes, ensure they're mounted
docker volume ls | grep librechat
```

### Step 7: Access the Interface

```bash
# LibreChat Web UI (once initialized)
# Open: http://localhost:3080

# RAG API (if exposed)
# Available at: http://localhost:8000/docs

# Meilisearch Admin
# Available at: http://localhost:7700

# ClickHouse MCP
# Available at: http://localhost:8001
```

### Step 8: Run Initial Tests

```bash
# Test tech analyzer
python tech_analyzer.py /path/to/test/project

# Test file counting
python count_files.py /path/to/test/project

# If everything works, proceed to ingestion
python ingest.py /path/to/test/project
```

---

## Azure Deployment

### Step 1: Prerequisites in Azure

```bash
# Install Azure CLI
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Set subscription
az account set --subscription "Your Subscription ID"

# Create resource group
az group create \
  --name rag-analytics-rg \
  --location eastus
```

### Step 2: Create Azure Container Registry

```bash
# Create ACR
az acr create \
  --resource-group rag-analytics-rg \
  --name raganalyticsacr \
  --sku Basic

# Get login credentials
az acr credential show \
  --resource-group rag-analytics-rg \
  --name raganalyticsacr
```

### Step 3: Create Azure Container Instances

```bash
# Create PostgreSQL with pgvector
az postgres flexible-server create \
  --resource-group rag-analytics-rg \
  --name rag-analytics-db \
  --admin-user dbuser \
  --admin-password YourSecurePassword123! \
  --database-name mydatabase \
  --tier Burstable \
  --sku-name Standard_B1ms

# Create Storage Account for volumes
az storage account create \
  --resource-group rag-analytics-rg \
  --name raganalyticsstorage \
  --sku Standard_LRS

# Get storage connection string
az storage account show-connection-string \
  --resource-group rag-analytics-rg \
  --name raganalyticsstorage
```

### Step 4: Deploy Docker Compose via Azure CLI

```bash
# Create container group with Docker Compose
az container create \
  --resource-group rag-analytics-rg \
  --name rag-analytics-stack \
  --image mcr.microsoft.com/azure-cli:latest \
  --environment-variables \
    GOOGLE_KEY="your-gemini-key" \
    DB_HOST="rag-analytics-db.postgres.database.azure.com" \
    DB_USER="dbuser@rag-analytics-db" \
    DB_PASSWORD="YourSecurePassword123!" \
  --ports 3080 7700 8000 8001 \
  --ip-address public \
  --dns-name-label rag-analytics
```

### Step 5: Alternatively: Deploy via App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name rag-analytics-plan \
  --resource-group rag-analytics-rg \
  --sku B2 \
  --is-linux

# Create Web App (Node.js for LibreChat)
az webapp create \
  --resource-group rag-analytics-rg \
  --plan rag-analytics-plan \
  --name rag-analytics-app \
  --runtime "node|18-lts"

# Configure deployment
az webapp config set \
  --resource-group rag-analytics-rg \
  --name rag-analytics-app \
  --startup-file "docker-compose up -d"
```

### Step 6: Set Up Azure Key Vault for Secrets

```bash
# Create Key Vault
az keyvault create \
  --resource-group rag-analytics-rg \
  --name rag-analytics-kv

# Add secrets
az keyvault secret set \
  --vault-name rag-analytics-kv \
  --name google-api-key \
  --value "your-gemini-key"

az keyvault secret set \
  --vault-name rag-analytics-kv \
  --name db-password \
  --value "YourSecurePassword123!"

# Reference in App Service
az webapp config appsettings set \
  --resource-group rag-analytics-rg \
  --name rag-analytics-app \
  --settings \
    GOOGLE_KEY="@Microsoft.KeyVault(SecretUri=https://rag-analytics-kv.vault.azure.net/secrets/google-api-key/)" \
    DB_PASSWORD="@Microsoft.KeyVault(SecretUri=https://rag-analytics-kv.vault.azure.net/secrets/db-password/)"
```

### Step 7: Configure Networking (Azure)

```bash
# Create Virtual Network
az network vnet create \
  --resource-group rag-analytics-rg \
  --name rag-analytics-vnet \
  --subnet-name rag-subnet

# Create Network Security Group
az network nsg create \
  --resource-group rag-analytics-rg \
  --name rag-analytics-nsg

# Allow necessary ports
az network nsg rule create \
  --resource-group rag-analytics-rg \
  --nsg-name rag-analytics-nsg \
  --name allow-librechat \
  --priority 100 \
  --destination-port-ranges 3080 \
  --access Allow \
  --protocol Tcp
```

### Step 8: Deploy RAG Scripts to Azure

```bash
# Option A: Upload via Azure Portal Files
# Navigate to App Service > App Service Editor > Upload Files

# Option B: Deploy via Git
git remote add azure https://rag-analytics-app.scm.azurewebsites.net/rag-analytics-app.git
git push azure main

# Option C: Deploy via Azure DevOps Pipeline
# Create .github/workflows/azure-deploy.yml
cat > .github/workflows/azure-deploy.yml << 'EOF'
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: rag-analytics-app
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
EOF
```

### Step 9: Verify Azure Deployment

```bash
# Get deployment status
az container show \
  --resource-group rag-analytics-rg \
  --name rag-analytics-stack

# Check logs
az container logs \
  --resource-group rag-analytics-rg \
  --name rag-analytics-stack

# Access web UI
# http://rag-analytics.eastus.azurecontainer.io:3080
```

---

## GitHub Codespaces Deployment

### Step 1: Prepare Repository for Codespaces

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "RAG Analytics Stack",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "remoteUser": "codespace",
  "postCreateCommand": "bash .devcontainer/setup.sh",
  "portsAttributes": {
    "3080": {
      "label": "LibreChat",
      "onAutoForward": "notify"
    },
    "5432": {
      "label": "PostgreSQL",
      "onAutoForward": "silent"
    },
    "7700": {
      "label": "Meilisearch",
      "onAutoForward": "notify"
    },
    "8000": {
      "label": "RAG API",
      "onAutoForward": "notify"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-vscode-remote.remote-containers",
        "docker"
      ]
    }
  }
}
```

Create `.devcontainer/setup.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up RAG Analytics Stack in Codespaces..."

# Update system
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Python setup
python3 -m venv /workspaces/venv
source /workspaces/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with defaults
if [ ! -f .env ]; then
  cat > .env << 'EOF'
GOOGLE_KEY=${GOOGLE_KEY:-your-key-here}
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=localhost
DB_PORT=5432
MONGODB_URI=mongodb://localhost:27017/LibreChat
MEILI_HOST=http://localhost:7700
NODE_ENV=development
EOF
fi

# Download and prepare scripts
echo "📥 Downloading RAG system files..."
mkdir -p scripts
cd scripts

# These would be downloaded from your repository
# wget https://your-repo/tech_analyzer.py
# wget https://your-repo/ingest.py
# wget https://your-repo/query.py

echo "✅ Setup complete! Run 'docker compose up -d' to start services."
```

### Step 2: Launch Codespaces

```bash
# Via GitHub Web Interface:
# 1. Navigate to repository
# 2. Click "<> Code" button
# 3. Select "Codespaces" tab
# 4. Click "Create codespace on main"

# Via CLI:
gh codespace create \
  --repo your-username/LibreChat \
  --branch main \
  --machine-type standard
```

### Step 3: Initialize Codespaces Environment

Once Codespaces is running:

```bash
# Activate Python environment
source /workspaces/venv/bin/activate

# Set up API keys
export GOOGLE_KEY="your-gemini-key"

# Verify setup
python -c "import langchain; print('✅ Python environment ready')"

# Start Docker services
docker compose up -d

# Wait for services
sleep 30

# Verify running
docker compose ps
```

### Step 4: Test Connectivity in Codespaces

```bash
# Test PostgreSQL
psql postgresql://myuser:mypassword@localhost/mydatabase -c "SELECT 1;"

# Test MongoDB
mongosh mongodb://localhost:27017/LibreChat --eval "db.version()"

# Test Meilisearch
curl http://localhost:7700/health

# Access LibreChat
# Click the URL that appears in terminal output when services are ready
# Usually: https://your-codespace-name-3080.preview.app.github.dev/
```

### Step 5: Port Forwarding in Codespaces

```bash
# View forwarded ports
gh codespace ports list

# Add port forwarding (if needed)
gh codespace ports visibility 3080:public

# Create port forwarding link
# Available at: Settings > Ports > Forwarded Ports
```

### Step 6: Run RAG Scripts in Codespaces

```bash
# Change to scripts directory
cd scripts

# Analyze a project
python tech_analyzer.py /path/to/project --update-ignore

# Ingest documents
python ingest.py /path/to/project

# Query
python query.py "Your question"
```

### Step 7: Persistent Storage (Codespaces)

```bash
# Codespaces provides persistent storage in /workspaces
# But services are stopped when codespace is closed

# To preserve database state, backup before closing:
docker compose exec -T postgresql pg_dump \
  --username=myuser \
  --no-password mydatabase > backup.sql

# Restore on next startup:
docker compose exec -T postgresql psql \
  --username=myuser \
  --no-password mydatabase < backup.sql
```

---

## System Components

### 1. Tech Analyzer (`tech_analyzer.py`)

**Purpose**: Intelligent technology detection and pattern generation

**Usage**:
```bash
# Preview patterns (no changes)
python tech_analyzer.py /path/to/project

# Apply and analyze
python tech_analyzer.py /path/to/project --update-ignore

# Output:
# ✅ Found: nodejs, python
# 🤖 Consulting LLM...
# ✅ Generated .documentignore with optimized patterns
# 📊 Files for RAG: 64 (57.14%)
```

**Supported Technologies**:
- Node.js, Python, Java, Go, Rust, PHP, .NET, Ruby

### 2. Ingestion Pipeline (`ingest.py`)

**Purpose**: Load documents and store embeddings

**Supported Formats**:
- Python (`.py`)
- JavaScript (`.js`, `.ts`)
- PDF (`.pdf`)
- HTML (`.html`, `.htm`)
- Markdown (`.md`)
- CSV (`.csv`)

**Usage**:
```bash
python ingest.py /path/to/project

# Options:
python ingest.py /path --chunk-size 500 --chunk-overlap 100
python ingest.py /path --max-files 1000
```

**Process**:
1. Respect `.documentignore` patterns
2. Load supported file types
3. Split into chunks (recursive, with overlap)
4. Generate embeddings via Gemini
5. Store in PostgreSQL/pgvector

### 3. Query System (`query.py`)

**Purpose**: Semantic search across indexed documents

**Usage**:
```bash
python query.py "How do I deploy this application?"

# Output:
# Found 5 relevant documents:
# 1. deployment.md (score: 0.87)
# 2. README.md (score: 0.84)
# ...
```

**Features**:
- Cosine similarity search
- Ranked results with scores
- Context-aware responses

### 4. File Counter (`count_files.py`)

**Purpose**: Analyze file eligibility before ingestion

**Usage**:
```bash
python count_files.py /path/to/project

# Output:
# Total Files: 847
# Files for RAG: 694 (81.94%)
# Files Ignored: 153 (18.06%)
```

### 5. Docker Services

#### PostgreSQL + pgvector
- **Purpose**: Vector database for embeddings
- **Port**: 5432
- **Volume**: postgres_data
- **Initialization**: Automatic via docker-compose

#### MongoDB
- **Purpose**: Conversation/message storage
- **Port**: 27017
- **Volume**: mongo_data
- **Collections**: conversations, messages

#### Meilisearch
- **Purpose**: Full-text search index
- **Port**: 7700
- **Volume**: meilisearch_data
- **Indexes**: documents, conversations

#### ClickHouse MCP
- **Purpose**: Data analytics and exploration
- **Port**: 8001
- **Protocol**: MCP (Model Context Protocol)

#### LibreChat
- **Purpose**: Web UI for interactions
- **Port**: 3080
- **Technology**: Node.js + React
- **Volume**: librechat_uploads

---

## Configuration & Setup

### Environment Variables

#### Critical (Required)

```bash
# Google Gemini API
GOOGLE_KEY=your-gemini-api-key

# Database
DB_HOST=vectordb
DB_PORT=5432
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
```

#### Important (Should Set)

```bash
# LibreChat
NODE_ENV=production
MONGODB_URI=mongodb://chat-mongodb:27017/LibreChat
MEILI_HOST=http://chat-meilisearch:7700

# RAG
EMBEDDINGS_MODEL=models/embedding-001
EMBEDDINGS_PROVIDER=google
```

#### Optional

```bash
# Alternative Models (if needed)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Performance Tuning
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_INGESTION_FILES=5000

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Docker Compose Customization

Edit `docker-compose.yml` to adjust:

```yaml
services:
  vectordb:
    environment:
      POSTGRES_PASSWORD: secure-password  # Change default
      POSTGRES_INITDB_ARGS: "-c max_connections=200"  # Tune for workload
    volumes:
      - postgres_data:/var/lib/postgresql/data:rw
      - ./backups:/backups:rw  # Add backup volume

  chat-mongodb:
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secure-password
    volumes:
      - mongo_data:/data/db:rw

  chat-meilisearch:
    environment:
      MEILI_ENV: production  # Use for production
      MEILI_MASTER_KEY: secure-key
    volumes:
      - meilisearch_data:/data.ms:rw
```

### Initial Configuration Steps

```bash
# 1. Start all services
docker compose up -d

# 2. Wait for initialization (2-5 minutes)
sleep 300

# 3. Create initial database schema
docker exec vectordb psql \
  -U myuser \
  -d mydatabase \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. Initialize Meilisearch indexes
docker exec chat-meilisearch \
  curl -X POST http://localhost:7700/indexes \
  -H 'Content-Type: application/json' \
  -d '{"uid": "documents", "primaryKey": "id"}'

# 5. Verify all services
docker compose ps
```

---

## Validation & Testing

### Pre-Deployment Checks

```bash
# ✅ Environment
echo "Python: $(python --version)"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker compose version)"

# ✅ API Keys
[ -z "$GOOGLE_KEY" ] && echo "❌ GOOGLE_KEY not set" || echo "✅ GOOGLE_KEY configured"

# ✅ Network
ping -c 1 8.8.8.8 > /dev/null && echo "✅ Internet connectivity" || echo "❌ No internet"

# ✅ Ports
for port in 3080 5432 27017 7700 8000 8001; do
  nc -z localhost $port && echo "✅ Port $port available" || echo "❌ Port $port in use"
done
```

### Post-Deployment Tests

```bash
# 1. Test PostgreSQL connection
python -c "
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    database='mydatabase',
    user='myuser',
    password='mypassword'
)
print('✅ PostgreSQL connected')
"

# 2. Test Gemini API
python -c "
import google.generativeai as genai
genai.configure(api_key='$GOOGLE_KEY')
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content('Hello')
print('✅ Gemini API working')
"

# 3. Test document ingestion (sample)
python tech_analyzer.py /home/yuvaraj/Projects/LibreChat
python count_files.py /home/yuvaraj/Projects/LibreChat

# 4. Test query system
python query.py "test query"

# 5. Test LibreChat Web UI
curl -s http://localhost:3080 | grep -q "LibreChat" && echo "✅ LibreChat UI active"
```

### Integration Tests

```bash
# Test entire workflow
bash << 'EOF'
set -e

echo "🧪 Running Integration Tests..."

# 1. Tech detection
echo "📱 Testing tech detection..."
python tech_analyzer.py /tmp/test-project > /tmp/test1.log

# 2. File counting
echo "📊 Testing file counting..."
python count_files.py /tmp/test-project > /tmp/test2.log

# 3. Ingestion (sample)
echo "📝 Testing ingestion..."
python ingest.py /tmp/test-project --max-files 10 > /tmp/test3.log

# 4. Query
echo "🔍 Testing query..."
python query.py "test" > /tmp/test4.log

echo "✅ All integration tests passed!"
EOF
```

### Performance Benchmarking

```bash
# Measure tech detection time
time python tech_analyzer.py /large/project

# Measure ingestion time
time python ingest.py /large/project

# Monitor resource usage during ingestion
docker stats --no-stream

# Check database size
docker exec vectordb psql \
  -U myuser -d mydatabase \
  -c "SELECT pg_size_pretty(pg_database_size('mydatabase'));"
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue 1: Docker Services Not Starting

**Symptoms**: `docker compose ps` shows "Restarting" or "Exited"

**Solutions**:
```bash
# Check logs
docker compose logs vectordb
docker compose logs chat-mongodb

# Restart specific service
docker compose restart vectordb

# Full restart
docker compose down
docker compose up -d

# Check Docker disk space
docker system df

# Clean up unused images
docker system prune -a
```

#### Issue 2: Database Connection Refused

**Symptoms**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Verify container is running
docker ps | grep vectordb

# Check PostgreSQL logs
docker compose logs vectordb | tail -50

# Test connection
docker exec vectordb psql \
  -U myuser \
  -d mydatabase \
  -c "SELECT 1;"

# If from host (may fail in Docker):
# Use docker exec or connect via container DNS
```

#### Issue 3: API Key Errors

**Symptoms**: `OpenAIError: The api_key client option must be set`

**Solutions**:
```bash
# Verify .env has key
grep GOOGLE_KEY .env

# Export to shell
export GOOGLE_KEY="your-key"

# Verify in container
docker exec rag_api env | grep GOOGLE_KEY
```

#### Issue 4: Ingestion Hangs

**Symptoms**: `python ingest.py` appears stuck

**Solutions**:
```bash
# Check memory usage
free -h
docker stats

# Check for large files
find /path -size +100M -type f

# Limit ingestion
python ingest.py /path --max-files 100

# Check database connectivity
docker exec vectordb psql -U myuser -d mydatabase -c "SELECT 1;"

# Monitor query performance
docker exec vectordb psql \
  -U myuser -d mydatabase \
  -c "SELECT query, mean_exec_time FROM pg_stat_statements LIMIT 10;"
```

#### Issue 5: Low Query Quality

**Symptoms**: Query results seem irrelevant

**Solutions**:
```bash
# Verify files were ingested
docker exec vectordb psql \
  -U myuser -d mydatabase \
  -c "SELECT COUNT(*) FROM documents;"

# Check embedding quality
python query.py "test" --verbose

# Adjust chunk size
python ingest.py /path --chunk-size 500 --chunk-overlap 100

# Re-ingest with better parameters
python ingest.py /path --force-reindex
```

### Debugging Commands

```bash
# Container inspection
docker inspect librechat  # Detailed container info

# Log inspection
docker logs -f librechat  # Follow logs in real-time
docker logs --tail 100 librechat  # Last 100 lines

# Shell access
docker exec -it vectordb bash
docker exec -it chat-mongodb mongosh

# Network testing
docker network ls
docker network inspect librechat_default

# Volume inspection
docker volume ls
docker volume inspect librechat_postgres_data
```

### Getting Help

1. **Check logs first**: `docker compose logs <service-name>`
2. **Verify configuration**: `cat .env | grep -v ^# | grep -v ^$`
3. **Test connectivity**: `docker compose exec vectordb pg_isready`
4. **Search issues**: https://github.com/danny-avila/LibreChat/issues
5. **Community forum**: Check LibreChat documentation

---

## Maintenance & Operations

### Backup & Recovery

```bash
# Backup PostgreSQL
docker exec vectordb pg_dump \
  -U myuser \
  -d mydatabase > backup-$(date +%Y%m%d).sql

# Backup MongoDB
docker exec chat-mongodb mongodump \
  --username admin \
  --authenticationDatabase admin \
  --out /backups/

# Restore PostgreSQL
docker exec -i vectordb psql \
  -U myuser \
  -d mydatabase < backup.sql

# Backup .documentignore patterns
cp .documentignore .documentignore.backup
```

### Monitoring

```bash
# Real-time resource usage
docker stats --no-stream

# Database performance
docker exec vectordb psql \
  -U myuser -d mydatabase \
  -c "\d+"  # List all tables

# Check log files
journalctl -u docker --since "1 hour ago"

# Application logs
docker compose logs -f --tail=50
```

### Updates & Upgrades

```bash
# Update docker images
docker compose pull
docker compose up -d

# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update tech analyzer and scripts
git pull origin main
cp tech_analyzer.py ingest.py query.py .
```

---

## Reference

### File Locations

| File | Location | Purpose |
|------|----------|---------|
| `.env` | Project root | Environment configuration |
| `docker-compose.yml` | Project root | Container orchestration |
| `tech_analyzer.py` | Project root | Tech detection |
| `ingest.py` | Project root | Document ingestion |
| `query.py` | Project root | Semantic search |
| `.documentignore` | Project root | Ingestion filters |
| Database backups | `./backups/` | Backup location |
| Service logs | Docker logs | Real-time service output |

### Port Reference

| Service | Port | Access |
|---------|------|--------|
| LibreChat | 3080 | http://localhost:3080 |
| PostgreSQL | 5432 | localhost:5432 |
| MongoDB | 27017 | localhost:27017 |
| Meilisearch | 7700 | http://localhost:7700 |
| RAG API | 8000 | http://localhost:8000 |
| ClickHouse MCP | 8001 | http://localhost:8001 |

### Useful Commands

```bash
# Restart all services
docker compose restart

# View service health
docker compose ps

# Execute command in container
docker compose exec <service> <command>

# View environment variables
docker compose config | grep environment

# Scale service (if defined)
docker compose up -d --scale <service>=3

# Remove all data (careful!)
docker compose down -v
```

---

## Conclusion

This deployment guide provides complete, reproducible instructions for setting up the RAG + Agentic Data Analytics Stack across local, Azure, and GitHub Codespaces environments. All configuration is managed via environment variables and docker-compose, ensuring consistency across deployments.

### Next Steps

1. **Choose your environment**: Local, Azure, or Codespaces
2. **Follow the deployment steps** for your chosen environment
3. **Run validation tests** to ensure everything is working
4. **Start ingesting documents** with `python ingest.py`
5. **Query your data** with `python query.py`
6. **Integrate with your applications** using the RAG API

### Support & Updates

For latest updates and support:
- GitHub Issues: https://github.com/danny-avila/LibreChat/issues
- Documentation: Refer to individual component docs
- Community: https://discord.gg/librechat

---

**Last Updated**: November 7, 2025  
**Status**: Production Ready  
**Version**: 1.0
