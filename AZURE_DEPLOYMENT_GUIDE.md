# 🚀 LibreChat + Agentic Analytics + Playwright E2E - Azure Deployment Guide

## 📋 Executive Summary

This comprehensive guide enables you to deploy the complete LibreChat ecosystem to Microsoft Azure, including:

1. **LibreChat Application** - AI chat platform with multi-model support
2. **Agentic Analytics Data Stack** - LLM-powered, database-agnostic analytics system
3. **Playwright E2E Testing** - Automated testing with Inspector and MCP integration
4. **Supporting Services** - MongoDB, PostgreSQL (pgvector), Redis, Meilisearch

**Deployment Options:**
- Azure Container Instances (ACI) - Quick deployment, lower cost
- Azure Kubernetes Service (AKS) - Production-grade, scalable
- Azure Container Apps - Serverless, auto-scaling

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AZURE DEPLOYMENT ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND TIER (Azure Front Door / Application Gateway)                       │
│  ├─ SSL/TLS Termination                                                       │
│  ├─ WAF (Web Application Firewall)                                            │
│  ├─ CDN Integration                                                           │
│  └─ Load Balancing                                                            │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  APPLICATION TIER                                                              │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  LibreChat API (Node.js)                                   │               │
│  │  - Azure Container Instances / AKS / Container Apps        │               │
│  │  - Auto-scaling enabled                                    │               │
│  │  - Health checks configured                                │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  LibreChat Client (React/Vite)                             │               │
│  │  - Served from Azure Static Web Apps or App Service        │               │
│  │  - Azure CDN for global distribution                       │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  RAG API (Python/FastAPI)                                  │               │
│  │  - Azure Container Instance                                │               │
│  │  - Connected to pgvector database                          │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  AGENTIC ANALYTICS TIER (Database-Agnostic LLM System)                        │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Tech Analyzer (tech_analyzer_v2.py)                       │               │
│  │  - Azure Function / Container Instance                     │               │
│  │  - Gemini API integration                                  │               │
│  │  - Detects tech stack: Python, Node.js, Java, etc.         │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Dependency Mapper (dependency_mapper.py)                  │               │
│  │  - Generates .documentignore patterns                      │               │
│  │  - Multi-package manager support                           │               │
│  │  - LLM-powered intelligent filtering                       │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Stack Generator (stack_generator.py)                      │               │
│  │  - Database-aware microservice generation                  │               │
│  │  - Supports: PostgreSQL, MongoDB, MySQL, ClickHouse        │               │
│  │  - Dynamic docker-compose generation                       │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Config Engine (config_engine.py)                          │               │
│  │  - LLM recommendations for stack configuration             │               │
│  │  - Resource allocation and security setup                  │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Database Adapter Registry (database_adapter_registry.py)  │               │
│  │  - Universal database adapter interface                    │               │
│  │  - Pre-tested: PostgreSQL, MongoDB, MySQL, Redis           │               │
│  │  - LLM fallback for any database                           │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  RAG Pipeline (rag_pipeline.py)                            │               │
│  │  - Document ingestion and chunking                         │               │
│  │  - Vector search with pgvector                             │               │
│  │  - Semantic search capabilities                            │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  DATA TIER (Azure Managed Services)                                           │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Database for PostgreSQL Flexible Server             │               │
│  │  - pgvector extension enabled                              │               │
│  │  - High availability (Zone Redundant)                      │               │
│  │  - Automated backups (35 days retention)                   │               │
│  │  - Point-in-time restore                                   │               │
│  │  SKU: General Purpose, 4 vCores, 16GB RAM                  │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Cosmos DB for MongoDB (Alternative)                 │               │
│  │  - MongoDB-compatible API                                  │               │
│  │  - Global distribution                                     │               │
│  │  - Automatic indexing                                      │               │
│  │  - Serverless or provisioned throughput                    │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Cache for Redis (Premium Tier)                      │               │
│  │  - Session storage and caching                             │               │
│  │  - Cluster mode enabled                                    │               │
│  │  - Zone redundancy                                         │               │
│  │  - 6GB cache size                                          │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Meilisearch (Self-hosted on ACI)                          │               │
│  │  - Document search engine                                  │               │
│  │  - Azure Files for data persistence                        │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  STORAGE TIER                                                                  │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Blob Storage (Hot Tier)                             │               │
│  │  - File uploads (images, documents, PDFs)                  │               │
│  │  - Avatar images                                           │               │
│  │  - Application logs                                        │               │
│  │  - Lifecycle management policies                           │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Files (Premium Tier)                                │               │
│  │  - Shared configuration files                              │               │
│  │  - Database backups                                        │               │
│  │  - Screenshot storage (E2E tests)                          │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  TESTING & MONITORING TIER                                                     │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Playwright E2E Testing Environment                        │               │
│  │  - Azure Container Instance with GUI support               │               │
│  │  - VNC server for visual debugging                         │               │
│  │  - PWDEBUG mode with Inspector                             │               │
│  │  - MCP event streaming to Azure Event Hub                  │               │
│  │  - Screenshot upload to Blob Storage                       │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Application Insights                                │               │
│  │  - Real-time application monitoring                        │               │
│  │  - Distributed tracing                                     │               │
│  │  - Performance metrics                                     │               │
│  │  - Custom events and logs                                  │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Log Analytics Workspace                             │               │
│  │  - Centralized logging                                     │               │
│  │  - KQL queries for analysis                                │               │
│  │  - Alerting rules                                          │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Monitor                                              │               │
│  │  - Metrics and alerts                                      │               │
│  │  - Autoscaling triggers                                    │               │
│  │  - Action groups for notifications                         │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  SECURITY & NETWORKING                                                         │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Virtual Network (VNet)                              │               │
│  │  - Private subnets for databases                           │               │
│  │  - Public subnet for Application Gateway                   │               │
│  │  - Network Security Groups (NSGs)                          │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Key Vault                                           │               │
│  │  - API keys (OpenAI, Gemini, Anthropic)                    │               │
│  │  - Database credentials                                    │               │
│  │  - SSL certificates                                        │               │
│  │  - Managed identities for access                           │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Private Link                                        │               │
│  │  - Private endpoints for databases                         │               │
│  │  - Secure communication within VNet                        │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure DDoS Protection (Standard)                          │               │
│  │  - Always-on traffic monitoring                            │               │
│  │  - Automatic attack mitigation                             │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  CI/CD & DevOps                                                                │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure DevOps / GitHub Actions                             │               │
│  │  - Automated builds and deployments                        │               │
│  │  - E2E test execution in pipeline                          │               │
│  │  - Blue-green deployment strategy                          │               │
│  └────────────────────────────────────────────────────────────┘               │
│  ┌────────────────────────────────────────────────────────────┐               │
│  │  Azure Container Registry (ACR)                            │               │
│  │  - Docker image storage                                    │               │
│  │  - Geo-replication for fast pulls                          │               │
│  │  - Security scanning enabled                               │               │
│  └────────────────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Tools

```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Docker (for local testing)
curl -fsSL https://get.docker.com | sudo bash

# Node.js 20+ (for LibreChat)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs

# Python 3.11+ (for Agentic Analytics)
sudo apt install -y python3.11 python3.11-venv python3-pip

# Playwright (for E2E testing)
npm install -g playwright
playwright install --with-deps

# Terraform (optional, for IaC)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Azure Account Requirements

- **Subscription**: Active Azure subscription with Owner or Contributor role
- **Resource Quota**: Ensure sufficient quota for:
  - 10+ vCPUs for Container Instances
  - 1 Azure Database for PostgreSQL Flexible Server
  - 1 Azure Cache for Redis
  - 100GB Blob Storage
- **Service Principal**: For automated deployments (optional)
- **Budget Alerts**: Recommended to set up cost monitoring

### API Keys Required

```bash
# AI Model Providers (at least one required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_KEY=AI...  # For Gemini (required for Agentic Analytics)

# Optional Services
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/
```

---

## 🎯 Deployment Strategy Selection

### Option 1: Azure Container Instances (ACI) - **Recommended for POC/Dev**

**Pros:**
- ✅ Fastest deployment (~15 minutes)
- ✅ Pay-per-second billing
- ✅ No cluster management
- ✅ Simple configuration

**Cons:**
- ⚠️ Less control over networking
- ⚠️ Limited scaling options
- ⚠️ No built-in load balancing

**Cost Estimate:** ~$150-250/month

**Use Case:** Development, Testing, Small Teams

---

### Option 2: Azure Kubernetes Service (AKS) - **Recommended for Production**

**Pros:**
- ✅ Production-grade orchestration
- ✅ Auto-scaling (HPA and cluster autoscaler)
- ✅ Advanced networking (Calico, Azure CNI)
- ✅ Built-in monitoring and logging
- ✅ Rolling updates and rollbacks

**Cons:**
- ⚠️ More complex setup (~45 minutes)
- ⚠️ Requires Kubernetes knowledge
- ⚠️ Higher baseline cost

**Cost Estimate:** ~$400-800/month

**Use Case:** Production, High Availability, Scalable Applications

---

### Option 3: Azure Container Apps - **Recommended for Serverless**

**Pros:**
- ✅ Serverless, event-driven
- ✅ Scale to zero capability
- ✅ Built-in Dapr integration
- ✅ Simple HTTPS ingress

**Cons:**
- ⚠️ Less control than AKS
- ⚠️ Still in active development
- ⚠️ Limited customization

**Cost Estimate:** ~$100-300/month (with scale-to-zero)

**Use Case:** Sporadic Usage, Cost Optimization, Microservices

---

## 🚀 Deployment Guide - Azure Container Instances (Quick Start)

### Step 1: Azure Login and Setup

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group
RESOURCE_GROUP="librechat-prod"
LOCATION="eastus"

az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --tags environment=production app=librechat
```

### Step 2: Create Azure Services

#### 2.1 Azure Database for PostgreSQL (with pgvector)

```bash
PG_SERVER_NAME="librechat-postgres-$(openssl rand -hex 4)"
PG_ADMIN_USER="librechat_admin"
PG_ADMIN_PASSWORD="$(openssl rand -base64 24)"
PG_DATABASE="librechat"

# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$PG_SERVER_NAME" \
  --location "$LOCATION" \
  --admin-user "$PG_ADMIN_USER" \
  --admin-password "$PG_ADMIN_PASSWORD" \
  --sku-name Standard_D4s_v3 \
  --tier GeneralPurpose \
  --storage-size 128 \
  --version 16 \
  --high-availability Enabled \
  --zone 1 \
  --standby-zone 2 \
  --backup-retention 35 \
  --public-access 0.0.0.0-255.255.255.255

# Create database
az postgres flexible-server db create \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$PG_SERVER_NAME" \
  --database-name "$PG_DATABASE"

# Enable pgvector extension
az postgres flexible-server parameter set \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$PG_SERVER_NAME" \
  --name azure.extensions \
  --value VECTOR

# Get connection string
PG_CONNECTION_STRING="postgresql://${PG_ADMIN_USER}:${PG_ADMIN_PASSWORD}@${PG_SERVER_NAME}.postgres.database.azure.com:5432/${PG_DATABASE}?sslmode=require"

echo "PostgreSQL Connection String: $PG_CONNECTION_STRING"
```

#### 2.2 Azure Cosmos DB for MongoDB (Alternative)

```bash
COSMOS_ACCOUNT_NAME="librechat-cosmos-$(openssl rand -hex 4)"

az cosmosdb create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$COSMOS_ACCOUNT_NAME" \
  --kind MongoDB \
  --locations regionName="$LOCATION" failoverPriority=0 \
  --default-consistency-level Session \
  --enable-automatic-failover true \
  --capabilities EnableMongo \
  --server-version 4.2

# Create MongoDB database
az cosmosdb mongodb database create \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$COSMOS_ACCOUNT_NAME" \
  --name "LibreChat"

# Get connection string
MONGO_CONNECTION_STRING=$(az cosmosdb keys list \
  --resource-group "$RESOURCE_GROUP" \
  --name "$COSMOS_ACCOUNT_NAME" \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv)

echo "MongoDB Connection String: $MONGO_CONNECTION_STRING"
```

#### 2.3 Azure Cache for Redis

```bash
REDIS_NAME="librechat-redis-$(openssl rand -hex 4)"

az redis create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REDIS_NAME" \
  --location "$LOCATION" \
  --sku Premium \
  --vm-size P1 \
  --enable-non-ssl-port false \
  --minimum-tls-version 1.2 \
  --redis-version 6 \
  --zones 1 2 3

# Get Redis connection details
REDIS_HOST=$(az redis show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REDIS_NAME" \
  --query "hostName" -o tsv)

REDIS_KEY=$(az redis list-keys \
  --resource-group "$RESOURCE_GROUP" \
  --name "$REDIS_NAME" \
  --query "primaryKey" -o tsv)

REDIS_CONNECTION_STRING="rediss://:${REDIS_KEY}@${REDIS_HOST}:6380/0"

echo "Redis Connection String: $REDIS_CONNECTION_STRING"
```

#### 2.4 Azure Storage Account

```bash
STORAGE_ACCOUNT="librechat$(openssl rand -hex 4)"

az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$STORAGE_ACCOUNT" \
  --location "$LOCATION" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot \
  --https-only true \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false

# Create containers
STORAGE_KEY=$(az storage account keys list \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$STORAGE_ACCOUNT" \
  --query "[0].value" -o tsv)

az storage container create \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY" \
  --name "uploads"

az storage container create \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY" \
  --name "avatars"

az storage container create \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY" \
  --name "images"

az storage container create \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY" \
  --name "screenshots"

# Create file share for configs
az storage share create \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY" \
  --name "config-files" \
  --quota 10

STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=${STORAGE_ACCOUNT};AccountKey=${STORAGE_KEY};EndpointSuffix=core.windows.net"

echo "Storage Connection String: $STORAGE_CONNECTION_STRING"
```

#### 2.5 Azure Key Vault (Secrets Management)

```bash
KEY_VAULT_NAME="librechat-kv-$(openssl rand -hex 4)"

az keyvault create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$KEY_VAULT_NAME" \
  --location "$LOCATION" \
  --enabled-for-deployment true \
  --enabled-for-template-deployment true \
  --sku standard

# Store secrets
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "PostgreSQL-ConnectionString" --value "$PG_CONNECTION_STRING"
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "MongoDB-ConnectionString" --value "$MONGO_CONNECTION_STRING"
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "Redis-ConnectionString" --value "$REDIS_CONNECTION_STRING"
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "Storage-ConnectionString" --value "$STORAGE_CONNECTION_STRING"

# Store API keys (replace with your actual keys)
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "OpenAI-ApiKey" --value "$OPENAI_API_KEY"
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "Anthropic-ApiKey" --value "$ANTHROPIC_API_KEY"
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "Google-ApiKey" --value "$GOOGLE_KEY"

echo "Key Vault Created: $KEY_VAULT_NAME"
```

### Step 3: Deploy Meilisearch

```bash
MEILI_MASTER_KEY="$(openssl rand -base64 32)"

az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-meilisearch" \
  --image "getmeili/meilisearch:v1.12.3" \
  --cpu 2 \
  --memory 4 \
  --ports 7700 \
  --protocol TCP \
  --restart-policy Always \
  --environment-variables \
    MEILI_MASTER_KEY="$MEILI_MASTER_KEY" \
    MEILI_NO_ANALYTICS="true" \
  --dns-name-label "librechat-meili-$(openssl rand -hex 4)" \
  --azure-file-volume-account-name "$STORAGE_ACCOUNT" \
  --azure-file-volume-account-key "$STORAGE_KEY" \
  --azure-file-volume-share-name "config-files" \
  --azure-file-volume-mount-path "/meili_data"

MEILI_HOST=$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-meilisearch" \
  --query "ipAddress.fqdn" -o tsv)

MEILI_URL="http://${MEILI_HOST}:7700"

echo "Meilisearch URL: $MEILI_URL"
echo "Meilisearch Master Key: $MEILI_MASTER_KEY"
```

### Step 4: Deploy RAG API (pgvector)

```bash
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-rag-api" \
  --image "ghcr.io/danny-avila/librechat-rag-api-dev-lite:latest" \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --protocol TCP \
  --restart-policy Always \
  --environment-variables \
    DB_HOST="${PG_SERVER_NAME}.postgres.database.azure.com" \
    RAG_PORT="8000" \
    POSTGRES_DB="$PG_DATABASE" \
    POSTGRES_USER="$PG_ADMIN_USER" \
    POSTGRES_PASSWORD="$PG_ADMIN_PASSWORD" \
  --dns-name-label "librechat-rag-$(openssl rand -hex 4)"

RAG_API_HOST=$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-rag-api" \
  --query "ipAddress.fqdn" -o tsv)

RAG_API_URL="http://${RAG_API_HOST}:8000"

echo "RAG API URL: $RAG_API_URL"
```

### Step 5: Deploy LibreChat Application

```bash
# Generate secure session secret
SESSION_SECRET="$(openssl rand -base64 48)"
JWT_SECRET="$(openssl rand -base64 48)"
CREDS_KEY="$(openssl rand -base64 32)"
CREDS_IV="$(openssl rand -hex 16)"

az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-app" \
  --image "ghcr.io/danny-avila/librechat-dev:latest" \
  --cpu 4 \
  --memory 8 \
  --ports 3080 \
  --protocol TCP \
  --restart-policy Always \
  --environment-variables \
    HOST="0.0.0.0" \
    PORT="3080" \
    MONGO_URI="$MONGO_CONNECTION_STRING" \
    REDIS_URI="$REDIS_CONNECTION_STRING" \
    MEILI_HOST="$MEILI_URL" \
    MEILI_MASTER_KEY="$MEILI_MASTER_KEY" \
    RAG_API_URL="$RAG_API_URL" \
    SESSION_EXPIRY="1000 * 60 * 15" \
    REFRESH_TOKEN_EXPIRY="1000 * 60 * 60 * 24 * 7" \
    JWT_SECRET="$JWT_SECRET" \
    JWT_REFRESH_SECRET="$JWT_SECRET" \
    CREDS_KEY="$CREDS_KEY" \
    CREDS_IV="$CREDS_IV" \
    DOMAIN_CLIENT="https://librechat-app.azurewebsites.net" \
    DOMAIN_SERVER="https://librechat-app.azurewebsites.net" \
  --dns-name-label "librechat-app-$(openssl rand -hex 4)" \
  --secure-environment-variables \
    OPENAI_API_KEY="$OPENAI_API_KEY" \
    ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    GOOGLE_KEY="$GOOGLE_KEY"

LIBRECHAT_HOST=$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-app" \
  --query "ipAddress.fqdn" -o tsv)

LIBRECHAT_URL="http://${LIBRECHAT_HOST}:3080"

echo "LibreChat URL: $LIBRECHAT_URL"
```

### Step 6: Configure Application Gateway (Optional - Production)

```bash
# Create public IP
az network public-ip create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-pip" \
  --sku Standard \
  --allocation-method Static \
  --zone 1 2 3

# Create VNet
az network vnet create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-vnet" \
  --address-prefix 10.0.0.0/16 \
  --subnet-name "appgw-subnet" \
  --subnet-prefix 10.0.1.0/24

# Create Application Gateway (with WAF)
az network application-gateway create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-appgw" \
  --location "$LOCATION" \
  --sku WAF_v2 \
  --capacity 2 \
  --vnet-name "librechat-vnet" \
  --subnet "appgw-subnet" \
  --public-ip-address "librechat-pip" \
  --http-settings-cookie-based-affinity Enabled \
  --http-settings-port 3080 \
  --http-settings-protocol Http \
  --frontend-port 80 \
  --priority 100 \
  --servers "$LIBRECHAT_HOST"

# Enable WAF
az network application-gateway waf-config set \
  --resource-group "$RESOURCE_GROUP" \
  --gateway-name "librechat-appgw" \
  --enabled true \
  --firewall-mode Prevention \
  --rule-set-version 3.2

# Get Application Gateway IP
APP_GATEWAY_IP=$(az network public-ip show \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-pip" \
  --query "ipAddress" -o tsv)

echo "Application Gateway IP: $APP_GATEWAY_IP"
echo "Access LibreChat at: http://$APP_GATEWAY_IP"
```

---

## 🔬 Agentic Analytics Stack Deployment

The Agentic Analytics components are Python-based and can run as Azure Functions or Container Instances.

### Option A: Deploy as Azure Container Instances

Create a custom Docker image containing all Python analytics scripts:

```dockerfile
# File: azure-agentic-analytics.Dockerfile

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python scripts
COPY tech_analyzer_v2.py .
COPY dependency_mapper.py .
COPY stack_generator.py .
COPY config_engine.py .
COPY database_adapter_registry.py .
COPY rag_pipeline.py .
COPY ingest.py .
COPY query.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    google-generativeai \
    psycopg2-binary \
    pymongo \
    redis \
    python-dotenv \
    pyyaml \
    docker \
    requests

# Create entrypoint script
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

echo "Starting Agentic Analytics Stack..."

# Run tech analyzer
echo "Running Tech Analyzer..."
python tech_analyzer_v2.py

# Run dependency mapper
echo "Running Dependency Mapper..."
python dependency_mapper.py

# Run stack generator
echo "Running Stack Generator..."
python stack_generator.py

# Run config engine
echo "Running Config Engine..."
python config_engine.py

# Keep container running
tail -f /dev/null
EOF

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
```

Build and push to Azure Container Registry:

```bash
# Create Azure Container Registry
ACR_NAME="librechatacr$(openssl rand -hex 4)"

az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Standard \
  --admin-enabled true

# Login to ACR
az acr login --name "$ACR_NAME"

# Build and push image
docker build -f azure-agentic-analytics.Dockerfile -t "${ACR_NAME}.azurecr.io/agentic-analytics:latest" .
docker push "${ACR_NAME}.azurecr.io/agentic-analytics:latest"

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

# Deploy container
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "agentic-analytics" \
  --image "${ACR_NAME}.azurecr.io/agentic-analytics:latest" \
  --cpu 2 \
  --memory 4 \
  --restart-policy Always \
  --registry-login-server "${ACR_NAME}.azurecr.io" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --environment-variables \
    GOOGLE_KEY="$GOOGLE_KEY" \
    DB_HOST="${PG_SERVER_NAME}.postgres.database.azure.com" \
    POSTGRES_DB="$PG_DATABASE" \
    POSTGRES_USER="$PG_ADMIN_USER" \
    POSTGRES_PASSWORD="$PG_ADMIN_PASSWORD"

echo "Agentic Analytics Stack deployed!"
```

### Option B: Deploy as Azure Functions

For event-driven execution, deploy each component as an Azure Function:

```bash
# Create Function App
FUNCTION_APP_NAME="librechat-analytics-$(openssl rand -hex 4)"

az functionapp create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_APP_NAME" \
  --storage-account "$STORAGE_ACCOUNT" \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux \
  --consumption-plan-location "$LOCATION"

# Configure app settings
az functionapp config appsettings set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$FUNCTION_APP_NAME" \
  --settings \
    GOOGLE_KEY="$GOOGLE_KEY" \
    DB_CONNECTION_STRING="$PG_CONNECTION_STRING" \
    MONGO_CONNECTION_STRING="$MONGO_CONNECTION_STRING"

echo "Function App created: $FUNCTION_APP_NAME"
```

---

## 🎭 Playwright E2E Testing Deployment

Deploy Playwright tests as a scheduled Azure Container Instance with VNC for debugging.

### Create Playwright Container with GUI Support

```dockerfile
# File: azure-playwright-e2e.Dockerfile

FROM mcr.microsoft.com/playwright:v1.50.0-jammy

# Install VNC server for visual debugging
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    fluxbox \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy E2E tests
COPY e2e/ ./e2e/
COPY package.json .

# Install dependencies
RUN npm install

# Create VNC startup script
COPY <<EOF /app/start-vnc.sh
#!/bin/bash
set -e

# Start Xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

# Start window manager
fluxbox &

# Start VNC server
x11vnc -display :99 -forever -shared -rfbport 5900 -passwd librechat &

# Run tests
echo "Starting Playwright E2E Tests..."
cd /app
node e2e/single_window_runner.js

# Keep container running
tail -f /dev/null
EOF

RUN chmod +x /app/start-vnc.sh

EXPOSE 5900

ENTRYPOINT ["/app/start-vnc.sh"]
```

Build and deploy:

```bash
# Build and push to ACR
docker build -f azure-playwright-e2e.Dockerfile -t "${ACR_NAME}.azurecr.io/playwright-e2e:latest" .
docker push "${ACR_NAME}.azurecr.io/playwright-e2e:latest"

# Deploy container with VNC
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "playwright-e2e" \
  --image "${ACR_NAME}.azurecr.io/playwright-e2e:latest" \
  --cpu 4 \
  --memory 8 \
  --ports 5900 \
  --protocol TCP \
  --restart-policy OnFailure \
  --registry-login-server "${ACR_NAME}.azurecr.io" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --environment-variables \
    E2E_URL="$LIBRECHAT_URL" \
    HEADLESS="false" \
  --dns-name-label "playwright-vnc-$(openssl rand -hex 4)"

VNC_HOST=$(az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "playwright-e2e" \
  --query "ipAddress.fqdn" -o tsv)

echo "VNC Server: $VNC_HOST:5900"
echo "VNC Password: librechat"
echo "Connect using: vncviewer $VNC_HOST:5900"
```

### MCP Event Streaming to Azure Event Hub

```bash
# Create Event Hub namespace
EVENT_HUB_NAMESPACE="librechat-events-$(openssl rand -hex 4)"

az eventhubs namespace create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$EVENT_HUB_NAMESPACE" \
  --location "$LOCATION" \
  --sku Standard

# Create Event Hub
az eventhubs eventhub create \
  --resource-group "$RESOURCE_GROUP" \
  --namespace-name "$EVENT_HUB_NAMESPACE" \
  --name "e2e-test-events" \
  --message-retention 7 \
  --partition-count 4

# Get connection string
EVENT_HUB_CONNECTION=$(az eventhubs namespace authorization-rule keys list \
  --resource-group "$RESOURCE_GROUP" \
  --namespace-name "$EVENT_HUB_NAMESPACE" \
  --name RootManageSharedAccessKey \
  --query "primaryConnectionString" -o tsv)

echo "Event Hub Connection String: $EVENT_HUB_CONNECTION"

# Update MCP forwarder to use Event Hub
# Modify e2e/mcp-forwarder.js to use Azure Event Hub SDK
```

---

## 📊 Monitoring and Logging Setup

### Application Insights

```bash
# Create Application Insights
APP_INSIGHTS_NAME="librechat-insights"

az monitor app-insights component create \
  --resource-group "$RESOURCE_GROUP" \
  --app "$APP_INSIGHTS_NAME" \
  --location "$LOCATION" \
  --kind web \
  --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --resource-group "$RESOURCE_GROUP" \
  --app "$APP_INSIGHTS_NAME" \
  --query "instrumentationKey" -o tsv)

echo "Application Insights Key: $INSTRUMENTATION_KEY"

# Update container with Application Insights
az container update \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-app" \
  --set containers[0].environmentVariables=[{ \
    "name": "APPLICATIONINSIGHTS_CONNECTION_STRING", \
    "value": "InstrumentationKey=${INSTRUMENTATION_KEY}" \
  }]
```

### Log Analytics Workspace

```bash
# Create Log Analytics workspace
LOG_WORKSPACE_NAME="librechat-logs"

az monitor log-analytics workspace create \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_WORKSPACE_NAME" \
  --location "$LOCATION" \
  --retention-time 90

# Link Application Insights to Log Analytics
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_WORKSPACE_NAME" \
  --query "customerId" -o tsv)

az monitor app-insights component update \
  --resource-group "$RESOURCE_GROUP" \
  --app "$APP_INSIGHTS_NAME" \
  --workspace "$WORKSPACE_ID"

echo "Log Analytics Workspace created: $LOG_WORKSPACE_NAME"
```

### Alert Rules

```bash
# Create action group for notifications
az monitor action-group create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-alerts" \
  --short-name "LibreChat" \
  --email-receiver name="Admin" email="admin@example.com"

# Create alert for high CPU usage
az monitor metrics alert create \
  --resource-group "$RESOURCE_GROUP" \
  --name "high-cpu-alert" \
  --description "Alert when CPU usage is above 80%" \
  --scopes "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/${RESOURCE_GROUP}" \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action "librechat-alerts"

# Create alert for container restart
az monitor metrics alert create \
  --resource-group "$RESOURCE_GROUP" \
  --name "container-restart-alert" \
  --description "Alert when container restarts" \
  --scopes "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/${RESOURCE_GROUP}" \
  --condition "total Restart Count > 3" \
  --window-size 15m \
  --evaluation-frequency 5m \
  --action "librechat-alerts"
```

---

## 🔒 Security Best Practices

### 1. Enable Azure Private Link

```bash
# Create private endpoint for PostgreSQL
az network vnet subnet create \
  --resource-group "$RESOURCE_GROUP" \
  --vnet-name "librechat-vnet" \
  --name "database-subnet" \
  --address-prefix 10.0.2.0/24 \
  --disable-private-endpoint-network-policies true

az network private-endpoint create \
  --resource-group "$RESOURCE_GROUP" \
  --name "postgres-private-endpoint" \
  --vnet-name "librechat-vnet" \
  --subnet "database-subnet" \
  --private-connection-resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.DBforPostgreSQL/flexibleServers/${PG_SERVER_NAME}" \
  --group-id postgresqlServer \
  --connection-name "postgres-connection"
```

### 2. Configure Network Security Groups

```bash
# Create NSG for database subnet
az network nsg create \
  --resource-group "$RESOURCE_GROUP" \
  --name "database-nsg"

# Allow only internal traffic to PostgreSQL
az network nsg rule create \
  --resource-group "$RESOURCE_GROUP" \
  --nsg-name "database-nsg" \
  --name "allow-postgres" \
  --priority 100 \
  --source-address-prefixes 10.0.0.0/16 \
  --destination-port-ranges 5432 \
  --protocol Tcp \
  --access Allow

# Deny all other inbound traffic
az network nsg rule create \
  --resource-group "$RESOURCE_GROUP" \
  --nsg-name "database-nsg" \
  --name "deny-all-inbound" \
  --priority 4096 \
  --source-address-prefixes '*' \
  --destination-port-ranges '*' \
  --protocol '*' \
  --access Deny

# Associate NSG with subnet
az network vnet subnet update \
  --resource-group "$RESOURCE_GROUP" \
  --vnet-name "librechat-vnet" \
  --name "database-subnet" \
  --network-security-group "database-nsg"
```

### 3. Enable Azure Defender

```bash
# Enable Security Center for subscription
az security pricing create \
  --name VirtualMachines \
  --tier Standard

az security pricing create \
  --name AppServices \
  --tier Standard

az security pricing create \
  --name SqlServers \
  --tier Standard

az security pricing create \
  --name Storage \
  --tier Standard
```

### 4. Rotate Secrets Regularly

```bash
# Create rotation script
cat > /tmp/rotate-secrets.sh << 'ROTATE_EOF'
#!/bin/bash
set -e

RESOURCE_GROUP="$1"
KEY_VAULT_NAME="$2"

# Generate new JWT secret
NEW_JWT_SECRET=$(openssl rand -base64 48)
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "JWT-Secret" --value "$NEW_JWT_SECRET"

# Generate new CREDS key
NEW_CREDS_KEY=$(openssl rand -base64 32)
az keyvault secret set --vault-name "$KEY_VAULT_NAME" --name "CREDS-Key" --value "$NEW_CREDS_KEY"

echo "Secrets rotated successfully!"
ROTATE_EOF

chmod +x /tmp/rotate-secrets.sh

# Schedule via Azure Automation (manual setup required in Azure Portal)
```

---

## 💰 Cost Optimization

### 1. Use Azure Reserved Instances

Save up to 72% by committing to 1 or 3-year reservations for:
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Virtual Machines (if using AKS)

### 2. Implement Auto-Shutdown for Dev/Test

```bash
# Create Azure Automation account
AUTOMATION_ACCOUNT="librechat-automation"

az automation account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AUTOMATION_ACCOUNT" \
  --location "$LOCATION" \
  --sku Free

# Create runbook to stop/start containers (manual configuration required)
```

### 3. Use Azure Spot Instances for Testing

For non-production Playwright tests, use Spot VMs:

```bash
az vm create \
  --resource-group "$RESOURCE_GROUP" \
  --name "playwright-spot-vm" \
  --image UbuntuLTS \
  --size Standard_D4s_v3 \
  --priority Spot \
  --max-price 0.05 \
  --eviction-policy Deallocate
```

### 4. Configure Storage Lifecycle Policies

```bash
# Create lifecycle policy for Blob Storage
az storage account management-policy create \
  --account-name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --policy @- << 'LIFECYCLE_EOF'
{
  "rules": [
    {
      "enabled": true,
      "name": "move-old-screenshots-to-cool",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            },
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 90
            },
            "delete": {
              "daysAfterModificationGreaterThan": 180
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["screenshots/"]
        }
      }
    }
  ]
}
LIFECYCLE_EOF
```

---

## 📝 Post-Deployment Checklist

- [ ] **DNS Configuration**: Point custom domain to Application Gateway IP
- [ ] **SSL Certificate**: Install SSL certificate in Application Gateway
- [ ] **Backup Verification**: Test database restore procedure
- [ ] **Monitoring Alerts**: Configure alert thresholds
- [ ] **Security Scan**: Run Azure Security Center recommendations
- [ ] **Load Testing**: Execute performance tests with Apache JMeter or k6
- [ ] **Disaster Recovery**: Document and test DR procedures
- [ ] **Documentation**: Update internal wiki with Azure resource details
- [ ] **Cost Analysis**: Set up budget alerts in Azure Cost Management
- [ ] **Compliance Check**: Verify GDPR/HIPAA compliance if applicable

---

## 🔧 Troubleshooting

### Container Won't Start

```bash
# Check container logs
az container logs \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-app" \
  --tail 100

# Check container events
az container show \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-app" \
  --query "instanceView"
```

### Database Connection Issues

```bash
# Test PostgreSQL connectivity
az postgres flexible-server connect \
  --name "$PG_SERVER_NAME" \
  --admin-user "$PG_ADMIN_USER" \
  --admin-password "$PG_ADMIN_PASSWORD" \
  --database-name "$PG_DATABASE"

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group "$RESOURCE_GROUP" \
  --name "$PG_SERVER_NAME"
```

### High Memory Usage

```bash
# Check container metrics
az monitor metrics list \
  --resource "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerInstance/containerGroups/librechat-app" \
  --metric "MemoryUsage" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-12-31T23:59:59Z" \
  --interval PT1M

# Increase memory allocation
az container create \
  --resource-group "$RESOURCE_GROUP" \
  --name "librechat-app" \
  --memory 16  # Increase from 8GB to 16GB
```

---

## 📚 Additional Resources

### Official Documentation
- [LibreChat Documentation](https://www.librechat.ai/docs/)
- [Azure Container Instances](https://learn.microsoft.com/en-us/azure/container-instances/)
- [Azure Kubernetes Service](https://learn.microsoft.com/en-us/azure/aks/)
- [Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/)
- [Playwright Testing](https://playwright.dev/docs/intro)

### Support Channels
- LibreChat Discord: https://discord.librechat.ai
- Azure Support: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- GitHub Issues: https://github.com/danny-avila/LibreChat/issues

---

## 🎉 Conclusion

You now have a complete, production-ready LibreChat deployment on Azure with:
- ✅ High-availability databases (PostgreSQL, MongoDB, Redis)
- ✅ Scalable containerized applications
- ✅ LLM-powered agentic analytics stack
- ✅ Automated E2E testing with Playwright
- ✅ Comprehensive monitoring and logging
- ✅ Enterprise-grade security

**Total Deployment Time**: 60-90 minutes
**Monthly Cost Estimate**: $400-800 (production) | $150-250 (dev/test)

Happy deploying! 🚀
