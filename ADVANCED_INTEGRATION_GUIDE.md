# Advanced Integration & Deployment Guide
## Dynamic RAG + Agentic Data Analytics Stack v2.0

**Purpose**: Complete guide for setting up the advanced dynamic system across local, Azure, and GitHub Codespaces  
**Audience**: DevOps, Cloud Engineers, Data Scientists  
**Updated**: November 7, 2025

---

## Quick Start (5 Minutes)

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/danny-avila/LibreChat.git
cd LibreChat

# 2. Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install google-generativeai pyyaml psycopg2-binary pymongo

# 4. Set API key
export GOOGLE_KEY="your-gemini-api-key"

# 5. Analyze target project
python tech_analyzer_v2.py /path/to/target/project --generate-ignore

# 6. Generate stack
python stack_generator.py postgresql --with-monitoring

# 7. Start services
docker-compose up -d

# 8. Verify
docker-compose ps
```

---

## Complete Installation Guide

### Phase 1: Environment Preparation

#### Option A: Local Machine

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-dev python3-pip git docker.io docker-compose

# Verify installations
python3 --version  # Python 3.12+
docker --version   # Docker 20+
docker-compose --version  # v2+

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### Option B: Azure VM

```bash
# Create VM
az vm create \
  --resource-group rag-rg \
  --name rag-vm \
  --image UbuntuLTS \
  --size Standard_D4s_v3 \
  --admin-username azureuser

# Connect and setup
az vm run-command invoke \
  --resource-group rag-rg \
  --name rag-vm \
  --command-id RunShellScript \
  --scripts @setup.sh
```

#### Option C: GitHub Codespaces

```bash
# No setup needed - environment is pre-configured
# Just launch from GitHub UI:
# 1. Navigate to repository
# 2. Click "<> Code"
# 3. Select "Codespaces"
# 4. Click "Create codespace on main"
```

### Phase 2: Core System Installation

```bash
# Clone repository
git clone https://github.com/danny-avila/LibreChat.git
cd LibreChat

# Create .venv
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install additional packages
pip install \
  google-generativeai==0.3.0 \
  pyyaml==6.0 \
  psycopg2-binary==2.9.9 \
  pymongo==4.6.0 \
  requests==2.31.0 \
  pydantic==2.5.0

# Verify installation
python -c "import google.generativeai; print('✅ Gemini API ready')"
python -c "import psycopg2; print('✅ PostgreSQL driver ready')"
```

### Phase 3: Configure API Keys

```bash
# Create .env file
cat > .env << 'EOF'
# Google Gemini API (required)
GOOGLE_KEY=your-gemini-api-key-here

# Database defaults (can be overridden)
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=secure_password_123
DB_HOST=vectordb
DB_PORT=5432

# Stack configuration
DATABASE_TYPE=postgresql
ENVIRONMENT=production
SCALE=medium
ENABLE_MONITORING=true
ENABLE_CI=true

# Optional: Additional API keys
# OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
EOF

# Make it secure
chmod 600 .env

# Load environment
source .env  # Or: export $(cat .env | xargs)
```

---

## System Components & Modules

### Module 1: tech_analyzer_v2.py
**Purpose**: Intelligent technology stack detection

```bash
# Analyze single project
python tech_analyzer_v2.py /path/to/project

# Generate .documentignore
python tech_analyzer_v2.py /path/to/project --generate-ignore

# Output:
# ✅ Found: python, nodejs, postgresql, redis
# 🔧 Analyzing with LLM...
# 📊 Confidence: 92%
# 📝 Generated .documentignore (234 patterns)
```

**Detects**:
- Languages: Python, Node.js, Java, Go, Rust, PHP, .NET, Ruby
- Frameworks: Django, Flask, Express, React, Angular, Spring, etc.
- Databases: PostgreSQL, MongoDB, MySQL, Redis, Elasticsearch, ClickHouse
- Package managers: pip, npm, yarn, maven, gradle, composer, bundler, cargo
- Build tools: Docker, Maven, Gradle, Webpack, Make
- CI/CD: GitHub Actions, GitLab CI, Jenkins, CircleCI

### Module 2: dependency_mapper.py
**Purpose**: Extract and map all project dependencies

```bash
# Analyze dependencies
python dependency_mapper.py /path/to/project

# Export full report
python dependency_mapper.py /path/to/project --export

# Output:
# 📊 Total Dependencies: 847
# 📦 Direct: 125
# 🔗 Transitive: 722
# 🔒 Vulnerable: 3
# 📋 Report saved: dependency_report.json
```

**Supports**:
- Python: requirements.txt, pyproject.toml, Pipfile, poetry.lock
- Node.js: package.json, package-lock.json, yarn.lock
- Java: pom.xml, build.gradle
- Go: go.mod, go.sum
- PHP: composer.json, composer.lock
- Ruby: Gemfile, Gemfile.lock
- Rust: Cargo.toml

### Module 3: stack_generator.py
**Purpose**: Generate docker-compose configurations

```bash
# Generate for PostgreSQL
python stack_generator.py postgresql

# Generate with monitoring & CI
python stack_generator.py postgresql --with-monitoring --with-ci

# Generate for other databases
python stack_generator.py mongodb --with-monitoring
python stack_generator.py mysql --with-monitoring
python stack_generator.py clickhouse --with-monitoring

# Output:
# 🏗️  Generating stack...
# ✅ Generated 8 services
# 📝 docker-compose.yml
# 🔧 .env.generated
```

**Generates**:
- Core services: PostgreSQL+pgvector, Redis, Meilisearch
- Application services: API, Worker
- Database-specific services
- Monitoring: Prometheus, Grafana, ELK
- CI/CD: Gitea, Jenkins

### Module 4: config_engine.py
**Purpose**: Optimize and configure microservices

```bash
# Generate production config
python config_engine.py production postgresql --scale=large

# Generate staging config
python config_engine.py staging mongodb --scale=medium

# Generate development config
python config_engine.py development postgresql --scale=small

# Output:
# ⚙️  Generating configuration...
# 💾 Saved: config-production-postgresql.yaml
# 🔒 Security hardened
# 📊 Resources optimized
```

**Configures**:
- Resource allocation (CPU, memory)
- Auto-scaling policies
- Health checks
- Security policies (RBAC, Network policies, secrets)
- Logging and monitoring (Prometheus, Datadog, ELK)
- CI/CD integration

---

## Complete Workflow

### Workflow 1: Single Project Deployment

```bash
#!/bin/bash
set -e

TARGET_PROJECT="/path/to/target/project"
ENVIRONMENT="production"
DATABASE="postgresql"

echo "🚀 Starting dynamic deployment workflow..."

# Step 1: Analyze
echo "📱 Step 1: Analyzing project..."
python tech_analyzer_v2.py "$TARGET_PROJECT" --generate-ignore
echo "✅ Analysis complete"

# Step 2: Map dependencies
echo "📦 Step 2: Mapping dependencies..."
python dependency_mapper.py "$TARGET_PROJECT" --export
echo "✅ Dependencies mapped"

# Step 3: Generate stack
echo "🏗️  Step 3: Generating docker-compose stack..."
python stack_generator.py "$DATABASE" --with-monitoring > docker-compose.yml
echo "✅ Stack generated"

# Step 4: Optimize configuration
echo "⚙️  Step 4: Generating optimized configuration..."
python config_engine.py "$ENVIRONMENT" "$DATABASE" --scale=medium > config.yaml
echo "✅ Configuration optimized"

# Step 5: Deploy
echo "🚀 Step 5: Starting services..."
docker-compose up -d
sleep 30
echo "✅ Services started"

# Step 6: Verify
echo "🔍 Step 6: Verifying deployment..."
docker-compose ps
echo "✅ Deployment complete!"

# Step 7: Ingest documents (if applicable)
echo "📚 Step 7: Ingesting project documents..."
python ingest.py "$TARGET_PROJECT"
echo "✅ Documents ingested"

echo "🎉 Complete deployment workflow finished!"
```

### Workflow 2: Multi-Database Comparison

```bash
#!/bin/bash

PROJECT_PATH="/path/to/project"

# Analyze once
python tech_analyzer_v2.py "$PROJECT_PATH" --generate-ignore

# Generate for each database
for db in postgresql mongodb mysql clickhouse; do
    echo "Generating stack for $db..."
    
    python stack_generator.py "$db" --with-monitoring \
        > "docker-compose-$db.yml"
    
    python config_engine.py production "$db" \
        > "config-$db.yaml"
    
    echo "✅ Generated: docker-compose-$db.yml, config-$db.yaml"
done

echo "🎉 All stacks generated!"
```

### Workflow 3: Environment-Specific Deployment

```bash
#!/bin/bash

PROJECT_PATH="/path/to/project"

# Analyze
python tech_analyzer_v2.py "$PROJECT_PATH" --generate-ignore

# Generate for each environment
for env in development staging production; do
    for scale in small medium large; do
        echo "Generating $env config ($scale scale)..."
        
        python config_engine.py "$env" postgresql --scale="$scale" \
            > "config-$env-$scale.yaml"
    done
done

echo "✅ Generated all environment configurations!"
```

---

## Azure Deployment

### Step 1: Prepare Azure Resources

```bash
# Set variables
RESOURCE_GROUP="rag-stack-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="ragstacksa"
ACR_NAME="ragstackacr"

# Create resource group
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

# Create storage account
az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$STORAGE_ACCOUNT" \
  --sku Standard_LRS

# Create Azure Container Registry
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic

# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group "$RESOURCE_GROUP" \
  --name rag-db \
  --admin-user pgadmin \
  --admin-password "P@ssw0rd123!" \
  --database-name ragdb \
  --tier Burstable \
  --sku-name Standard_B2s

echo "✅ Azure resources created!"
```

### Step 2: Generate Configuration

```bash
# Analyze project locally
python tech_analyzer_v2.py /path/to/project --generate-ignore

# Generate stack
python stack_generator.py postgresql --with-monitoring

# Generate optimized config
python config_engine.py production postgresql --scale=large

# Verify files
ls -la docker-compose.yml config-production-postgresql.yaml .env.generated
```

### Step 3: Push to Azure Container Registry

```bash
# Login to ACR
az acr login --name ragstackacr

# Build and push images (if needed)
docker tag my-api:latest ragstackacr.azurecr.io/my-api:latest
docker push ragstackacr.azurecr.io/my-api:latest

# Or use docker-compose with ACR
az acr build --registry ragstackacr --file Dockerfile .
```

### Step 4: Deploy to Azure Container Instances

```bash
# Create container group from docker-compose
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name rag-stack-aci \
  --image-registry-login-server ragstackacr.azurecr.io \
  --registry-username "$(az acr credential show -n ragstackacr --query username -o tsv)" \
  --registry-password "$(az acr credential show -n ragstackacr --query passwords[0].value -o tsv)" \
  --ports 3080 5432 7700 8000 \
  --environment-variables \
    GOOGLE_KEY="$GOOGLE_KEY" \
    DATABASE_URL="postgresql://pgadmin:P@ssw0rd123!@rag-db.postgres.database.azure.com:5432/ragdb"

# Verify
az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name rag-stack-aci \
  --query "{FQDN:ipAddress.fqdn,State:containers[0].instanceView.currentState.state}"
```

### Step 5: Deploy to Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create \
  --resource-group "$RESOURCE_GROUP" \
  --name rag-aks \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard \
  --attach-acr ragstackacr

# Get credentials
az aks get-credentials \
  --resource-group "$RESOURCE_GROUP" \
  --name rag-aks \
  --overwrite-existing

# Convert docker-compose to Kubernetes
# Using kompose (install: go install github.com/kubernetes/kompose@latest)
kompose convert -f docker-compose.yml -o k8s-manifests/

# Deploy to Kubernetes
kubectl apply -f config-production-postgresql.yaml
kubectl apply -f k8s-manifests/

# Verify
kubectl get pods -n default
kubectl port-forward svc/librechat 3080:3080
```

---

## GitHub Codespaces Setup

### Step 1: Configure Codespaces

Create `.devcontainer/devcontainer.json`:

```json
{
  "name": "RAG Dynamic Stack",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/git:latest": {}
  },
  "remoteUser": "codespace",
  "postCreateCommand": "bash .devcontainer/setup.sh",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-vscode-remote.remote-containers",
        "docker"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/opt/conda/envs/myenv/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true
      }
    }
  },
  "portsAttributes": {
    "3000": { "label": "Application", "onAutoForward": "notify" },
    "3080": { "label": "LibreChat", "onAutoForward": "notify" },
    "5432": { "label": "PostgreSQL", "onAutoForward": "silent" },
    "7700": { "label": "Meilisearch", "onAutoForward": "notify" },
    "8000": { "label": "RAG API", "onAutoForward": "notify" },
    "8001": { "label": "ClickHouse MCP", "onAutoForward": "notify" }
  }
}
```

Create `.devcontainer/setup.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up RAG Dynamic Stack in Codespaces..."

# Update system
sudo apt-get update
sudo apt-get install -y postgresql-client curl

# Python setup
python3 -m venv /workspaces/.venv
source /workspaces/.venv/bin/activate
pip install --upgrade pip setuptools
pip install -r /workspaces/requirements.txt
pip install google-generativeai pyyaml psycopg2-binary pymongo

# Create environment file
if [ ! -f /workspaces/.env ]; then
  cat > /workspaces/.env << 'EOF'
GOOGLE_KEY=${GOOGLE_KEY:-your-key}
DATABASE_TYPE=postgresql
ENVIRONMENT=development
SCALE=medium
EOF
fi

# Docker setup (already available in codespaces)
docker --version

echo "✅ Setup complete!"
echo "📝 Configure GOOGLE_KEY in .env"
echo "🚀 Run: docker-compose up -d"
```

### Step 2: Launch Codespaces

```bash
# Via GitHub CLI
gh codespace create \
  --repo your-username/LibreChat \
  --branch main \
  --machine-type standard

# Or use GitHub UI:
# 1. Go to https://github.com/your-username/LibreChat
# 2. Click "<> Code"
# 3. Select "Codespaces"
# 4. Click "Create codespace on main"
```

### Step 3: Use in Codespaces

```bash
# Once codespace is running

# Activate venv
source /workspaces/.venv/bin/activate

# Set API key
export GOOGLE_KEY="your-key"

# Analyze project
python /workspaces/tech_analyzer_v2.py /workspaces/target-project --generate-ignore

# Generate stack
python /workspaces/stack_generator.py postgresql --with-monitoring

# Start services
docker-compose up -d

# Access services
# LibreChat: https://codespace-name-3080.preview.app.github.dev
# API: https://codespace-name-8000.preview.app.github.dev
```

---

## Advanced Usage

### Using with LLM for Intelligent Optimization

```python
from tech_analyzer_v2 import AdvancedTechAnalyzer
from stack_generator import DynamicStackGenerator

# Analyze
analyzer = AdvancedTechAnalyzer()
tech_stack = analyzer.analyze_project("/path/to/project")

# Print analysis
print(analyzer.get_stack_summary())

# Generate stack with LLM optimizations
generator = DynamicStackGenerator()
config = generator.generate_stack(
    tech_stack,
    database_type="postgresql",
    enable_monitoring=True
)

# Get LLM optimization recommendations
optimizations = generator.generate_llm_optimizations()
print(f"Recommended optimizations: {optimizations}")

# Save configuration
generator.save_docker_compose(config)
generator.save_env_file()
```

### Custom Microservice Configuration

```python
from config_engine import ConfigurationEngine, DatabaseType, MicroserviceConfig

engine = ConfigurationEngine()

# Generate base config
config = engine.generate_config(
    tech_stack,
    database_type=DatabaseType.POSTGRESQL,
    environment="production",
    scale="large"
)

# Add custom service
custom_service = MicroserviceConfig(
    name="custom-ml-service",
    image="tensorflow/tensorflow:gpu",
    port=5000,
    # ... full configuration
)

# Save
engine.save_config("production-postgresql", "config-custom.yaml")
```

---

## Monitoring & Troubleshooting

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs vectordb
docker-compose logs rag_api

# Real-time monitoring
docker stats --no-stream

# Database connectivity
docker exec vectordb pg_isready -U myuser

# API health
curl http://localhost:8000/health

# LibreChat UI
curl http://localhost:3080
```

### Debugging

```bash
# Enable debug logging
export DEBUG=true
python tech_analyzer_v2.py /path --debug 2>&1 | tee debug.log

# Check environment
printenv | grep -E "GOOGLE|DATABASE|DOCKER"

# Validate configurations
docker-compose config > docker-compose.resolved.yml
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"

# Test individual modules
python -m pytest tests/ -v
```

---

## Summary & Next Steps

### ✅ You Now Have

1. **Advanced Tech Detection** - LLM-powered analysis
2. **Dependency Mapping** - Multi-package manager support
3. **Dynamic Stack Generation** - Auto-configured docker-compose
4. **Configuration Engine** - Environment and scale-specific settings
5. **Multi-Cloud Support** - Local, Azure, GitHub Codespaces ready

### 🚀 Next Steps

1. **Analyze your project**: `python tech_analyzer_v2.py /path`
2. **Map dependencies**: `python dependency_mapper.py /path`
3. **Generate stack**: `python stack_generator.py postgresql`
4. **Deploy**: `docker-compose up -d`
5. **Start querying**: `python query.py "your question"`

### 📚 Additional Resources

- [COMPLETE_DEPLOYMENT_GUIDE.md](./COMPLETE_DEPLOYMENT_GUIDE.md) - Detailed deployment guide
- [DYNAMIC_SYSTEM_GUIDE.md](./DYNAMIC_SYSTEM_GUIDE.md) - System architecture and advanced usage
- [GitHub Issues](https://github.com/danny-avila/LibreChat/issues) - Community support
- [LibreChat Documentation](https://docs.librechat.ai) - Official docs

---

**Questions or Issues?** Check the troubleshooting guides or open a GitHub issue with logs and configuration details.

Happy deploying! 🎉
