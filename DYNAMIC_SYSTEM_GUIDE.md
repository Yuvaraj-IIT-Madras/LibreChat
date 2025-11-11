# Dynamic RAG + Agentic Data Analytics Stack Guide

**Version**: 2.0  
**Status**: Production-Ready with LLM-Driven Configuration  
**Last Updated**: November 7, 2025

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Installation & Setup](#installation--setup)
4. [Dynamic Configuration](#dynamic-configuration)
5. [Usage Examples](#usage-examples)
6. [Azure Deployment](#azure-deployment)
7. [GitHub Codespaces Setup](#github-codespaces-setup)
8. [Advanced Configurations](#advanced-configurations)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Architecture Overview

### Dynamic Stack Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                     INPUT LAYER                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │ Project Analysis │  │ Tech Detection   │  │ Dependencies │   │
│  │ (Folder/Files)   │  │ (Frameworks)     │  │ (Libraries)  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────┬───────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────────┐
│                    ANALYSIS LAYER (LLM-Powered)                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  tech_analyzer_v2.py - Intelligent Tech Stack Detection     │ │
│  │  - Language identification                                   │ │
│  │  - Framework detection                                       │ │
│  │  - Dependency mapping                                        │ │
│  │  - Confidence scoring                                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  dependency_mapper.py - Multi-Package Manager Support        │ │
│  │  - npm, pip, maven, gradle, composer, bundler, cargo        │ │
│  │  - Direct and transitive dependency extraction               │ │
│  │  - License and vulnerability checking                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────────┐
│                  GENERATION LAYER (Configuration)                 │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  stack_generator.py - Docker Compose Generation              │ │
│  │  - Database-specific configurations                          │ │
│  │  - Microservice orchestration                                │ │
│  │  - Environment optimization                                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  config_engine.py - Intelligent Configuration                │ │
│  │  - LLM-driven optimization recommendations                   │ │
│  │  - Resource allocation                                       │ │
│  │  - Security and observability setup                          │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT LAYER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │  docker-compose  │  │  .env.generated  │  │  Config Files│   │
│  │  (Orchestration) │  │  (Environment)   │  │  (Services)  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└─────────────────┬───────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────────┐
│                   RUNTIME LAYER                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │  Microservices   │  │  Databases       │  │  Infrastructure
│  │  (API, Workers)  │  │  (PostgreSQL+PG │  │  (Cache, Queue,│
│  │                  │  │   Vector, etc)   │  │   Search)     │
│  └──────────────────┘  └──────────────────┘  └──────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

---

## System Components

### Core Modules

#### 1. **tech_analyzer_v2.py** - Advanced Technology Detection
```python
Purpose: Intelligently detect tech stack from codebase
Capabilities:
  - 8+ language detection (Python, Node.js, Java, Go, Rust, PHP, .NET, Ruby)
  - Framework and library identification
  - Package manager detection
  - LLM-powered confidence scoring
  - Automated .documentignore generation

Output:
  - TechStack dataclass with confidence scores
  - List of Dependency nodes
  - .documentignore patterns for RAG optimization
```

**Key Features:**
- Pattern-based detection (file extensions, config files)
- File content analysis for deeper insights
- LLM enhancement for ambiguous cases
- Multi-package manager support

#### 2. **dependency_mapper.py** - Comprehensive Dependency Analysis
```python
Purpose: Extract and map all dependencies
Supported Package Managers:
  - Python: pip, poetry, pipenv
  - Node.js: npm, yarn, pnpm
  - Java: Maven, Gradle
  - Go: go mod, go sum
  - PHP: Composer
  - Ruby: Bundler
  - Rust: Cargo

Output:
  - Dependency graph with transitive relationships
  - License information
  - Vulnerability reports
  - Size estimation
```

#### 3. **stack_generator.py** - Dynamic Docker Configuration
```python
Purpose: Generate optimized docker-compose configurations
Generates:
  - Core services (PostgreSQL+pgvector, Redis, Meilisearch)
  - Framework-specific services
  - Monitoring and logging infrastructure
  - CI/CD pipelines
  - Database-specific configurations

Database Support:
  - PostgreSQL (with pgvector)
  - MongoDB
  - MySQL
  - ClickHouse
  - Redis
  - Elasticsearch
```

#### 4. **config_engine.py** - Intelligent Configuration
```python
Purpose: Dynamically generate microservice configurations
Configures:
  - Resource allocation (CPU, memory)
  - Auto-scaling policies
  - Health checks
  - Security policies
  - Logging and monitoring
  - Network policies

Parameters:
  - Tech Stack Analysis
  - Database Type
  - Environment (dev, staging, prod)
  - Scale (small, medium, large, xlarge)
```

---

## Installation & Setup

### Prerequisites

```bash
# System requirements
- Python 3.12+
- Docker & Docker Compose v20+
- Git
- 8GB+ RAM (for analysis)
- 50GB+ free disk space

# Python packages
pip install google-generativeai psycopg2-binary pymongo pyyaml
```

### Step 1: Install Dynamic System

```bash
# Clone/prepare repository
cd /path/to/LibreChat

# Copy all dynamic modules
cp tech_analyzer_v2.py dependency_mapper.py stack_generator.py config_engine.py .

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install google-generativeai pyyaml psycopg2-binary pymongo
```

### Step 2: Configure Environment

```bash
# Set Google Gemini API key
export GOOGLE_KEY="your-gemini-api-key"

# Or create .env file
cat > .env << 'EOF'
GOOGLE_KEY=your-gemini-api-key
DATABASE_TYPE=postgresql
ENVIRONMENT=production
SCALE=medium
EOF
```

### Step 3: Analyze Your Project

```bash
# Analyze project structure
python tech_analyzer_v2.py /path/to/target/project --generate-ignore

# Output will show:
# ✅ Detected Technologies
# 📦 Extracted Dependencies
# 🔧 Generated .documentignore
```

---

## Dynamic Configuration

### Workflow: From Analysis to Deployment

#### Step 1: Technology Analysis

```bash
# Analyze the target project
analyzer = AdvancedTechAnalyzer()
tech_stack = analyzer.analyze_project("/path/to/project")
dependencies = analyzer.extract_dependencies("/path/to/project")
analyzer.generate_documentignore("/path/to/project")

# Output:
# {
#   "languages": ["python", "nodejs"],
#   "frameworks": ["Django", "Express.js"],
#   "databases": ["postgresql", "redis"],
#   "confidence": 0.92,
#   ...
# }
```

#### Step 2: Dependency Extraction

```bash
# Map all dependencies
mapper = DependencyMapper()
report = mapper.analyze_project("/path/to/project")

# Report includes:
# - Total: 847 dependencies
# - Direct: 125
# - Transitive: 722
# - By Package Manager breakdown
# - License information
# - Vulnerability alerts
```

#### Step 3: Stack Generation

```bash
# Generate docker-compose configuration
from config_engine import DatabaseType

generator = DynamicStackGenerator()

# Generate for specific database
config = generator.generate_stack(
    tech_stack=tech_stack,
    database_type=DatabaseType.POSTGRESQL,
    enable_monitoring=True,
    enable_ci_cd=True
)

# Generate environment file
generator.save_docker_compose(config, "docker-compose.yml")
generator.save_env_file(".env.generated")
```

#### Step 4: Configuration Optimization

```bash
# Generate optimized configurations
from config_engine import ConfigurationEngine, DatabaseType

engine = ConfigurationEngine()

# Generate for specific environment/scale
config = engine.generate_config(
    tech_stack_analysis=tech_stack.to_dict(),
    database_type=DatabaseType.POSTGRESQL,
    environment="production",
    scale="medium"
)

# Save as YAML
engine.save_config("production-postgresql", "config-prod.yaml")
```

---

## Usage Examples

### Example 1: Analyze Python/Django Project

```bash
#!/bin/bash

PROJECT_PATH="/path/to/django-app"

# Step 1: Analyze
python tech_analyzer_v2.py $PROJECT_PATH --generate-ignore

# Step 2: Extract dependencies
python dependency_mapper.py $PROJECT_PATH --export

# Expected Output:
# ✅ Found: Python, Django, PostgreSQL, Redis
# 📦 Total Dependencies: 234
# 🔒 Vulnerable Packages: 0
# ✅ Generated .documentignore
```

### Example 2: Generate Stack for ClickHouse Analytics

```bash
from tech_analyzer_v2 import AdvancedTechAnalyzer
from stack_generator import DynamicStackGenerator
from config_engine import ConfigurationEngine, DatabaseType

# Analyze project
analyzer = AdvancedTechAnalyzer()
tech_stack = analyzer.analyze_project("/path/to/analytics-app")

# Generate stack for ClickHouse
generator = DynamicStackGenerator()
config = generator.generate_stack(
    tech_stack=tech_stack,
    database_type="clickhouse",
    enable_monitoring=True
)

# Configure for analytics workload
engine = ConfigurationEngine()
optimized = engine.generate_config(
    tech_stack_analysis=tech_stack.to_dict(),
    database_type=DatabaseType.CLICKHOUSE,
    environment="production",
    scale="large"
)

# Save configurations
generator.save_docker_compose(config)
engine.save_config("production-clickhouse", "config-analytics.yaml")
```

### Example 3: Multi-Database Setup

```bash
from config_engine import ConfigurationEngine, DatabaseType

engine = ConfigurationEngine()

# Generate configs for multiple databases
databases = [
    DatabaseType.POSTGRESQL,
    DatabaseType.MONGODB,
    DatabaseType.CLICKHOUSE
]

for db in databases:
    config = engine.generate_config(
        tech_stack_analysis=tech_stack.to_dict(),
        database_type=db,
        environment="production"
    )
    
    key = f"production-{db.value}"
    engine.save_config(key, f"config-{db.value}.yaml")
```

---

## Azure Deployment

### Step 1: Prepare Azure Resources

```bash
# Create resource group
az group create \
  --name rag-dynamic-rg \
  --location eastus

# Create Key Vault for secrets
az keyvault create \
  --name rag-dynamic-kv \
  --resource-group rag-dynamic-rg

# Store API key
az keyvault secret set \
  --vault-name rag-dynamic-kv \
  --name google-api-key \
  --value "your-gemini-key"
```

### Step 2: Generate Configuration

```bash
# On local machine, generate configuration
python tech_analyzer_v2.py /path/to/project --generate-ignore
python stack_generator.py postgresql --with-monitoring > docker-compose.yml
python config_engine.py production postgresql --scale=large > config-prod.yaml
```

### Step 3: Deploy to Azure Container Instances

```bash
# Upload configuration to Azure
az storage blob upload \
  --account-name ragstorageaccount \
  --container-name configs \
  --name docker-compose.yml \
  --file docker-compose.yml

# Create container group
az container create \
  --resource-group rag-dynamic-rg \
  --name rag-stack \
  --image docker.io/library/docker:latest \
  --ports 3080 5432 7700 8000 \
  --environment-variables \
    GOOGLE_KEY="@Microsoft.KeyVault(SecretUri=https://rag-dynamic-kv.vault.azure.net/secrets/google-api-key/)" \
  --volumes config:/config
```

### Step 4: Deploy to Azure Kubernetes Service

```bash
# Convert docker-compose to Kubernetes manifests
# Using Kompose or manual conversion

# Apply configurations
kubectl apply -f config-prod.yaml

# Verify deployment
kubectl get pods -n rag-system
kubectl logs -f deployment/api-service
```

---

## GitHub Codespaces Setup

### Step 1: Create Devcontainer Configuration

`.devcontainer/devcontainer.json`:
```json
{
  "name": "RAG Dynamic Stack",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "postCreateCommand": "bash .devcontainer/setup.sh",
  "forwardPorts": [3080, 5432, 7700, 8000],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "docker"
      ]
    }
  }
}
```

### Step 2: Setup Script

`.devcontainer/setup.sh`:
```bash
#!/bin/bash
set -e

# Install Python dependencies
pip install -r requirements.txt
pip install google-generativeai pyyaml

# Download dynamic modules
wget https://your-repo/tech_analyzer_v2.py
wget https://your-repo/dependency_mapper.py
wget https://your-repo/stack_generator.py
wget https://your-repo/config_engine.py

# Start services
docker compose up -d

echo "✅ Setup complete!"
```

### Step 3: Launch and Use

```bash
# Launch Codespaces from GitHub UI
# Or via CLI:
gh codespace create --repo your-username/LibreChat

# Once running:
source .venv/bin/activate
export GOOGLE_KEY="your-key"

# Analyze project
python tech_analyzer_v2.py /workspaces/target-project
```

---

## Advanced Configurations

### Custom Tech Stack Detection

```python
from tech_analyzer_v2 import AdvancedTechAnalyzer

analyzer = AdvancedTechAnalyzer()

# Add custom patterns
analyzer.patterns["custom_tech"] = {
    "markers": ["custom.config", "*.custom"],
    "package_manager": ["custom-pm"],
    "config_files": ["custom.config"]
}

# Analyze with custom patterns
tech_stack = analyzer.analyze_project("/path/to/project")
```

### Custom Microservice Configuration

```python
from config_engine import ConfigurationEngine, MicroserviceConfig

engine = ConfigurationEngine()

# Create custom microservice
custom_service = MicroserviceConfig(
    name="ml-service",
    image="tensorflow/tensorflow:latest",
    port=5000,
    environment={
        "MODEL_PATH": "/models/model.pkl",
        "GPU_ENABLED": "true"
    },
    resources={
        "requests": {"cpu": "2000m", "memory": "8Gi"},
        "limits": {"cpu": "4000m", "memory": "16Gi"}
    },
    # ... other config
)

# Add to services
engine.services["ml_service"] = custom_service
```

### Multi-Region Deployment

```python
# Generate configs for multiple regions
from config_engine import ConfigurationEngine

engine = ConfigurationEngine()

regions = ["eastus", "westus", "northeurope"]
environments = ["production", "staging"]

for region in regions:
    for env in environments:
        config = engine.generate_config(
            tech_stack,
            database_type=DatabaseType.POSTGRESQL,
            environment=env,
            scale="medium"
        )
        
        key = f"{region}-{env}"
        engine.save_config(key, f"config-{key}.yaml")
```

---

## Troubleshooting

### Issue 1: LLM Analysis Hangs

**Symptoms**: `python tech_analyzer_v2.py` appears stuck

**Solutions**:
```bash
# Check API key
echo $GOOGLE_KEY

# Test API connectivity
python -c "import google.generativeai as genai; genai.configure(api_key='$GOOGLE_KEY'); print('OK')"

# Set timeout
export GOOGLE_API_TIMEOUT=30

# Run with debug logging
python -u tech_analyzer_v2.py /path --debug 2>&1 | tee debug.log
```

### Issue 2: Dependency Extraction Fails

**Symptoms**: `DependencyMapper` returns empty results

**Solutions**:
```bash
# Verify package files exist
find /path -name "package.json" -o -name "requirements.txt" -o -name "pom.xml"

# Check file permissions
ls -la /path/package.json

# Test individual parsers
python -c "from dependency_mapper import DependencyMapper; m = DependencyMapper(); m._extract_nodejs('/path')"
```

### Issue 3: Docker Compose Generation Issues

**Symptoms**: `docker-compose.yml` missing services or invalid YAML

**Solutions**:
```bash
# Validate generated YAML
docker-compose -f docker-compose.yml config

# Check environment
cat .env.generated

# Regenerate with verbose logging
python -u stack_generator.py postgresql --verbose > stack_gen.log 2>&1
```

---

## Best Practices

### 1. Always Validate Analysis Results

```bash
# Before deploying, review detected tech stack
python tech_analyzer_v2.py /path/to/project

# Verify confidence scores are > 0.7
# Check if any important technologies are missed
```

### 2. Test in Development First

```bash
# Generate for development
python config_engine.py development postgresql --scale=small

# Test with docker-compose
docker-compose -f docker-compose.dev.yml up

# Verify all services are healthy
docker-compose ps
```

### 3. Use Environment-Specific Configurations

```bash
# Generate for each environment
for env in development staging production; do
    python config_engine.py $env postgresql
done

# Use appropriate config for deployment
docker-compose -f config-${ENV}.yaml up
```

### 4. Keep Dependencies Updated

```bash
# Regularly check for updates
python dependency_mapper.py /path --export

# Review vulnerability reports
grep -i "vulnerable" dependency_report.json

# Update security findings
python dependency_mapper.py /path --check-vulnerabilities
```

### 5. Monitor Configuration Changes

```bash
# Version control configurations
git add config-*.yaml docker-compose.yml .documentignore
git commit -m "Update dynamic configs"

# Track changes
git diff config-*.yaml
```

---

## Integration with RAG System

### Automatic Document Filtering

The `.documentignore` generated by `tech_analyzer_v2.py` automatically:

1. **Excludes dependency folders**
   - node_modules, venv, vendor, target, etc.

2. **Excludes build artifacts**
   - *.pyc, __pycache__, dist, build, etc.

3. **Excludes IDE files**
   - .vscode, .idea, *.swp, etc.

4. **Optimizes for RAG indexing**
   - Only source files are processed
   - Reduces ingestion time by 80%+
   - Improves semantic search quality

### Usage in Ingestion Pipeline

```python
from tech_analyzer_v2 import AdvancedTechAnalyzer
from adaptive_rag import AdaptiveRAGPipeline

# Analyze and generate ignore patterns
analyzer = AdvancedTechAnalyzer()
analyzer.analyze_project("/path/to/project")
ignore_file = analyzer.generate_documentignore("/path/to/project")

# Ingest with optimized patterns
pipeline = AdaptiveRAGPipeline()
pipeline.ingest_project(
    "/path/to/project",
    ignore_patterns_file=ignore_file,
    tech_stack=analyzer.detected_stack
)
```

---

## Summary

This dynamic system provides:

✅ **Intelligent Detection** - LLM-powered technology and dependency identification
✅ **Automatic Configuration** - Generate docker-compose files tailored to your stack
✅ **Multi-Environment Support** - Different configs for dev, staging, production
✅ **Database Flexibility** - Support for PostgreSQL, MongoDB, MySQL, ClickHouse, etc.
✅ **Optimization** - LLM recommendations for performance and security
✅ **RAG Integration** - Automatic .documentignore generation
✅ **Cloud Ready** - Azure, AWS, GCP compatible configurations

---

**Next Steps:**

1. Analyze your project: `python tech_analyzer_v2.py /path`
2. Generate stack: `python stack_generator.py postgresql`
3. Optimize config: `python config_engine.py production postgresql`
4. Deploy: `docker-compose up -d`
5. Query your data: `python query.py "your question"`

For questions or issues, refer to the troubleshooting section or check logs in your deployment environment.
