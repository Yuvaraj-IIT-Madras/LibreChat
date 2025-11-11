#!/bin/bash
################################################################################
# COMPLETE AZURE DEPLOYMENT AUTOMATION SCRIPT
# Deploys LibreChat + Agentic Analytics + Playwright E2E to Azure
# Usage: ./deploy-to-azure.sh [--env production|staging] [--region eastus]
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default configuration
ENVIRONMENT="production"
REGION="eastus"
DEPLOYMENT_TYPE="aci"  # aci, aks, or container-apps
SKIP_TESTS=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--env production|staging] [--region eastus] [--type aci|aks] [--skip-tests] [--dry-run]"
            exit 1
            ;;
    esac
done

# Load environment variables
ENV_FILE="azure/.env.azure"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Environment file not found: $ENV_FILE${NC}"
    echo -e "${YELLOW}Please copy azure/.env.azure.example to azure/.env.azure and configure it${NC}"
    exit 1
fi

source "$ENV_FILE"

# Validate required variables
REQUIRED_VARS=(
    "AZURE_RESOURCE_GROUP"
    "AZURE_SUBSCRIPTION_ID"
    "OPENAI_API_KEY"
    "GOOGLE_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required variable not set: $var${NC}"
        exit 1
    fi
done

# Banner
echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   LibreChat + Agentic Analytics + Playwright - Azure Deployment${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
echo -e "${GREEN}Environment:${NC} $ENVIRONMENT"
echo -e "${GREEN}Region:${NC} $REGION"
echo -e "${GREEN}Deployment Type:${NC} $DEPLOYMENT_TYPE"
echo -e "${GREEN}Resource Group:${NC} $AZURE_RESOURCE_GROUP"
echo -e "${GREEN}Dry Run:${NC} $DRY_RUN"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

# Function to execute or print command
run_cmd() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} $*"
    else
        eval "$*"
    fi
}

# Step 1: Azure CLI Check
echo -e "${YELLOW}[1/15] Checking Azure CLI...${NC}"
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Install from: https://aka.ms/azure-cli${NC}"
    exit 1
fi

# Login check
if ! az account show > /dev/null 2>&1; then
    echo -e "${YELLOW}Logging into Azure...${NC}"
    az login
fi

# Set subscription
run_cmd "az account set --subscription \"$AZURE_SUBSCRIPTION_ID\""
echo -e "${GREEN}✅ Azure CLI ready${NC}\n"

# Step 2: Create Resource Group
echo -e "${YELLOW}[2/15] Creating Resource Group...${NC}"
run_cmd "az group create \
    --name \"$AZURE_RESOURCE_GROUP\" \
    --location \"$REGION\" \
    --tags environment=$ENVIRONMENT project=librechat owner=$OWNER"
echo -e "${GREEN}✅ Resource Group created${NC}\n"

# Step 3: Create Container Registry
echo -e "${YELLOW}[3/15] Setting up Azure Container Registry...${NC}"
ACR_NAME="${AZURE_CONTAINER_REGISTRY:-librechatacr$(openssl rand -hex 4)}"

run_cmd "az acr create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"$ACR_NAME\" \
    --sku Standard \
    --admin-enabled true"

ACR_SERVER=$(az acr show --name "$ACR_NAME" --query "loginServer" -o tsv)
ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query "passwords[0].value" -o tsv)

echo -e "${GREEN}✅ Container Registry ready: $ACR_SERVER${NC}\n"

# Step 4: Build and Push Docker Images
echo -e "${YELLOW}[4/15] Building and pushing Docker images...${NC}"

# Login to ACR
run_cmd "az acr login --name \"$ACR_NAME\""

# Build Agentic Analytics image
echo -e "${BLUE}Building Agentic Analytics image...${NC}"
run_cmd "docker build -f azure/Dockerfile.agentic-analytics -t \"${ACR_SERVER}/agentic-analytics:latest\" ."
run_cmd "docker push \"${ACR_SERVER}/agentic-analytics:latest\""

# Build Playwright E2E image
echo -e "${BLUE}Building Playwright E2E image...${NC}"
run_cmd "docker build -f azure/Dockerfile.playwright-e2e -t \"${ACR_SERVER}/playwright-e2e:latest\" ."
run_cmd "docker push \"${ACR_SERVER}/playwright-e2e:latest\""

# Build MCP Forwarder image
echo -e "${BLUE}Building MCP Forwarder image...${NC}"
run_cmd "docker build -f azure/Dockerfile.mcp-forwarder -t \"${ACR_SERVER}/mcp-forwarder:latest\" ."
run_cmd "docker push \"${ACR_SERVER}/mcp-forwarder:latest\""

echo -e "${GREEN}✅ All images built and pushed${NC}\n"

# Step 5: Create PostgreSQL Database
echo -e "${YELLOW}[5/15] Creating Azure Database for PostgreSQL...${NC}"

PG_SERVER="${PG_SERVER_NAME:-librechat-pg-$(openssl rand -hex 4)}"

run_cmd "az postgres flexible-server create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"$PG_SERVER\" \
    --location \"$REGION\" \
    --admin-user \"$PG_ADMIN_USER\" \
    --admin-password \"$PG_ADMIN_PASSWORD\" \
    --sku-name Standard_D4s_v3 \
    --tier GeneralPurpose \
    --storage-size 128 \
    --version 16 \
    --high-availability Enabled \
    --public-access 0.0.0.0-255.255.255.255"

# Create database
run_cmd "az postgres flexible-server db create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --server-name \"$PG_SERVER\" \
    --database-name \"$PG_DATABASE\""

# Enable pgvector
run_cmd "az postgres flexible-server parameter set \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --server-name \"$PG_SERVER\" \
    --name azure.extensions \
    --value VECTOR"

echo -e "${GREEN}✅ PostgreSQL database created${NC}\n"

# Step 6: Create Cosmos DB for MongoDB
echo -e "${YELLOW}[6/15] Creating Azure Cosmos DB (MongoDB API)...${NC}"

COSMOS_ACCOUNT="${COSMOS_ACCOUNT_NAME:-librechat-cosmos-$(openssl rand -hex 4)}"

run_cmd "az cosmosdb create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"$COSMOS_ACCOUNT\" \
    --kind MongoDB \
    --locations regionName=\"$REGION\" failoverPriority=0 \
    --default-consistency-level Session \
    --enable-automatic-failover true \
    --capabilities EnableMongo"

# Create database
run_cmd "az cosmosdb mongodb database create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --account-name \"$COSMOS_ACCOUNT\" \
    --name \"LibreChat\""

echo -e "${GREEN}✅ Cosmos DB created${NC}\n"

# Step 7: Create Redis Cache
echo -e "${YELLOW}[7/15] Creating Azure Cache for Redis...${NC}"

REDIS_INSTANCE="${REDIS_NAME:-librechat-redis-$(openssl rand -hex 4)}"

run_cmd "az redis create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"$REDIS_INSTANCE\" \
    --location \"$REGION\" \
    --sku Premium \
    --vm-size P1 \
    --enable-non-ssl-port false"

echo -e "${GREEN}✅ Redis cache created${NC}\n"

# Step 8: Create Storage Account
echo -e "${YELLOW}[8/15] Creating Azure Storage Account...${NC}"

STORAGE_ACCOUNT="${AZURE_STORAGE_ACCOUNT:-librechat$(openssl rand -hex 4)}"

run_cmd "az storage account create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"$STORAGE_ACCOUNT\" \
    --location \"$REGION\" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot"

STORAGE_KEY=$(az storage account keys list \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --account-name "$STORAGE_ACCOUNT" \
    --query "[0].value" -o tsv)

# Create containers
for container in uploads avatars images screenshots; do
    run_cmd "az storage container create \
        --account-name \"$STORAGE_ACCOUNT\" \
        --account-key \"$STORAGE_KEY\" \
        --name \"$container\""
done

# Create file share
run_cmd "az storage share create \
    --account-name \"$STORAGE_ACCOUNT\" \
    --account-key \"$STORAGE_KEY\" \
    --name \"config-files\" \
    --quota 10"

echo -e "${GREEN}✅ Storage account created${NC}\n"

# Step 9: Create Key Vault
echo -e "${YELLOW}[9/15] Creating Azure Key Vault...${NC}"

KEY_VAULT="${AZURE_KEY_VAULT_NAME:-librechat-kv-$(openssl rand -hex 4)}"

run_cmd "az keyvault create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"$KEY_VAULT\" \
    --location \"$REGION\""

# Store secrets
secrets=(
    "OpenAI-ApiKey:$OPENAI_API_KEY"
    "Anthropic-ApiKey:$ANTHROPIC_API_KEY"
    "Google-ApiKey:$GOOGLE_KEY"
    "JWT-Secret:$JWT_SECRET"
    "CREDS-Key:$CREDS_KEY"
    "PostgreSQL-Password:$PG_ADMIN_PASSWORD"
)

for secret in "${secrets[@]}"; do
    IFS=':' read -r name value <<< "$secret"
    if [ -n "$value" ]; then
        run_cmd "az keyvault secret set --vault-name \"$KEY_VAULT\" --name \"$name\" --value \"$value\""
    fi
done

echo -e "${GREEN}✅ Key Vault created and secrets stored${NC}\n"

# Step 10: Deploy Meilisearch
echo -e "${YELLOW}[10/15] Deploying Meilisearch...${NC}"

run_cmd "az container create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"librechat-meilisearch\" \
    --image \"getmeili/meilisearch:v1.12.3\" \
    --cpu 2 \
    --memory 4 \
    --ports 7700 \
    --restart-policy Always \
    --environment-variables \
        MEILI_MASTER_KEY=\"$MEILI_MASTER_KEY\" \
        MEILI_NO_ANALYTICS=\"true\" \
    --dns-name-label \"librechat-meili-$(openssl rand -hex 4)\""

echo -e "${GREEN}✅ Meilisearch deployed${NC}\n"

# Step 11: Deploy RAG API
echo -e "${YELLOW}[11/15] Deploying RAG API...${NC}"

run_cmd "az container create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"librechat-rag-api\" \
    --image \"ghcr.io/danny-avila/librechat-rag-api-dev-lite:latest\" \
    --cpu 2 \
    --memory 4 \
    --ports 8000 \
    --restart-policy Always \
    --environment-variables \
        DB_HOST=\"${PG_SERVER}.postgres.database.azure.com\" \
        RAG_PORT=\"8000\" \
        POSTGRES_DB=\"$PG_DATABASE\" \
        POSTGRES_USER=\"$PG_ADMIN_USER\" \
        POSTGRES_PASSWORD=\"$PG_ADMIN_PASSWORD\" \
    --dns-name-label \"librechat-rag-$(openssl rand -hex 4)\""

echo -e "${GREEN}✅ RAG API deployed${NC}\n"

# Step 12: Deploy LibreChat Application
echo -e "${YELLOW}[12/15] Deploying LibreChat Application...${NC}"

MEILI_FQDN=$(az container show --resource-group "$AZURE_RESOURCE_GROUP" --name "librechat-meilisearch" --query "ipAddress.fqdn" -o tsv)
RAG_FQDN=$(az container show --resource-group "$AZURE_RESOURCE_GROUP" --name "librechat-rag-api" --query "ipAddress.fqdn" -o tsv)
MONGO_CONN=$(az cosmosdb keys list --resource-group "$AZURE_RESOURCE_GROUP" --name "$COSMOS_ACCOUNT" --type connection-strings --query "connectionStrings[0].connectionString" -o tsv)
REDIS_CONN="rediss://:$(az redis list-keys --resource-group "$AZURE_RESOURCE_GROUP" --name "$REDIS_INSTANCE" --query "primaryKey" -o tsv)@${REDIS_INSTANCE}.redis.cache.windows.net:6380/0"

run_cmd "az container create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"librechat-app\" \
    --image \"ghcr.io/danny-avila/librechat-dev:latest\" \
    --cpu 4 \
    --memory 8 \
    --ports 3080 \
    --restart-policy Always \
    --environment-variables \
        HOST=\"0.0.0.0\" \
        PORT=\"3080\" \
        MONGO_URI=\"$MONGO_CONN\" \
        REDIS_URI=\"$REDIS_CONN\" \
        MEILI_HOST=\"http://${MEILI_FQDN}:7700\" \
        MEILI_MASTER_KEY=\"$MEILI_MASTER_KEY\" \
        RAG_API_URL=\"http://${RAG_FQDN}:8000\" \
        JWT_SECRET=\"$JWT_SECRET\" \
        CREDS_KEY=\"$CREDS_KEY\" \
        CREDS_IV=\"$CREDS_IV\" \
    --secure-environment-variables \
        OPENAI_API_KEY=\"$OPENAI_API_KEY\" \
        ANTHROPIC_API_KEY=\"$ANTHROPIC_API_KEY\" \
        GOOGLE_KEY=\"$GOOGLE_KEY\" \
    --dns-name-label \"librechat-app-$(openssl rand -hex 4)\""

LIBRECHAT_FQDN=$(az container show --resource-group "$AZURE_RESOURCE_GROUP" --name "librechat-app" --query "ipAddress.fqdn" -o tsv)

echo -e "${GREEN}✅ LibreChat deployed at: http://${LIBRECHAT_FQDN}:3080${NC}\n"

# Step 13: Deploy Agentic Analytics
echo -e "${YELLOW}[13/15] Deploying Agentic Analytics Stack...${NC}"

run_cmd "az container create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --name \"agentic-analytics\" \
    --image \"${ACR_SERVER}/agentic-analytics:latest\" \
    --cpu 2 \
    --memory 4 \
    --restart-policy OnFailure \
    --registry-login-server \"$ACR_SERVER\" \
    --registry-username \"$ACR_USERNAME\" \
    --registry-password \"$ACR_PASSWORD\" \
    --environment-variables \
        GOOGLE_KEY=\"$GOOGLE_KEY\" \
        DB_HOST=\"${PG_SERVER}.postgres.database.azure.com\" \
        POSTGRES_DB=\"$PG_DATABASE\" \
        POSTGRES_USER=\"$PG_ADMIN_USER\" \
        POSTGRES_PASSWORD=\"$PG_ADMIN_PASSWORD\" \
        ANALYSIS_MODE=\"full\""

echo -e "${GREEN}✅ Agentic Analytics deployed${NC}\n"

# Step 14: Deploy Playwright E2E Tests (if not skipped)
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${YELLOW}[14/15] Deploying Playwright E2E Testing...${NC}"

    run_cmd "az container create \
        --resource-group \"$AZURE_RESOURCE_GROUP\" \
        --name \"playwright-e2e\" \
        --image \"${ACR_SERVER}/playwright-e2e:latest\" \
        --cpu 4 \
        --memory 8 \
        --ports 5900 6080 \
        --restart-policy OnFailure \
        --registry-login-server \"$ACR_SERVER\" \
        --registry-username \"$ACR_USERNAME\" \
        --registry-password \"$ACR_PASSWORD\" \
        --environment-variables \
            E2E_URL=\"http://${LIBRECHAT_FQDN}:3080\" \
            HEADLESS=\"false\" \
            VNC_PASSWORD=\"librechat\" \
        --dns-name-label \"playwright-vnc-$(openssl rand -hex 4)\""

    VNC_FQDN=$(az container show --resource-group "$AZURE_RESOURCE_GROUP" --name "playwright-e2e" --query "ipAddress.fqdn" -o tsv)

    echo -e "${GREEN}✅ Playwright E2E deployed${NC}"
    echo -e "${BLUE}VNC Access: vnc://${VNC_FQDN}:5900 (password: librechat)${NC}"
    echo -e "${BLUE}Web VNC: http://${VNC_FQDN}:6080${NC}\n"
else
    echo -e "${YELLOW}[14/15] Skipping Playwright E2E deployment${NC}\n"
fi

# Step 15: Create Application Insights
echo -e "${YELLOW}[15/15] Setting up Application Insights...${NC}"

run_cmd "az monitor app-insights component create \
    --resource-group \"$AZURE_RESOURCE_GROUP\" \
    --app \"librechat-insights\" \
    --location \"$REGION\" \
    --kind web"

INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --app "librechat-insights" \
    --query "instrumentationKey" -o tsv)

echo -e "${GREEN}✅ Application Insights configured${NC}\n"

# Deployment Summary
echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${GREEN}📦 Resource Group:${NC} $AZURE_RESOURCE_GROUP"
echo -e "${GREEN}📍 Region:${NC} $REGION"
echo -e "${GREEN}🌐 LibreChat URL:${NC} http://${LIBRECHAT_FQDN}:3080"
echo -e "${GREEN}🔬 RAG API:${NC} http://${RAG_FQDN}:8000"
echo -e "${GREEN}🔍 Meilisearch:${NC} http://${MEILI_FQDN}:7700"
if [ "$SKIP_TESTS" = false ]; then
    echo -e "${GREEN}🎭 VNC Access:${NC} vnc://${VNC_FQDN}:5900"
    echo -e "${GREEN}🌐 Web VNC:${NC} http://${VNC_FQDN}:6080"
fi
echo -e "${GREEN}📊 App Insights Key:${NC} $INSTRUMENTATION_KEY"

echo -e "\n${YELLOW}⚠️  IMPORTANT NEXT STEPS:${NC}"
echo -e "1. Configure custom domain and SSL certificate"
echo -e "2. Update DOMAIN_CLIENT and DOMAIN_SERVER in container env vars"
echo -e "3. Configure firewall rules for production security"
echo -e "4. Set up Azure DevOps/GitHub Actions for CI/CD"
echo -e "5. Enable Azure Backup for databases"
echo -e "6. Configure monitoring alerts and dashboards"
echo -e "7. Review and optimize resource sizing based on usage"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

# Save deployment info
cat > deployment-info.json << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "environment": "$ENVIRONMENT",
  "region": "$REGION",
  "resourceGroup": "$AZURE_RESOURCE_GROUP",
  "librechatUrl": "http://${LIBRECHAT_FQDN}:3080",
  "ragApiUrl": "http://${RAG_FQDN}:8000",
  "meilisearchUrl": "http://${MEILI_FQDN}:7700",
  "vncUrl": "http://${VNC_FQDN}:6080",
  "keyVault": "$KEY_VAULT",
  "containerRegistry": "$ACR_SERVER",
  "instrumentationKey": "$INSTRUMENTATION_KEY"
}
EOF

echo -e "${GREEN}✅ Deployment info saved to deployment-info.json${NC}\n"
