#!/bin/bash
################################################################################
# Azure Container Instances / AKS RAG + Agentic Data Stack Deployment
# Execute: bash azure_deploy.sh --resource-group <name> --location <region>
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default configuration
RESOURCE_GROUP="rag-stack-rg"
LOCATION="eastus"
DEPLOYMENT_TYPE="aci"  # Options: aci (Container Instances), aks (Kubernetes)
CONTAINER_REGISTRY_NAME="ragstackregistry"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        --registry)
            CONTAINER_REGISTRY_NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Azure RAG + Agentic Data Stack Deployment${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

# Step 1: Verify Azure CLI
echo -e "${YELLOW}[Step 1/5] Verifying Azure CLI...${NC}"
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI not found. Install from: https://aka.ms/azure-cli${NC}"
    exit 1
fi

# Check if logged in
if ! az account show > /dev/null 2>&1; then
    echo -e "${YELLOW}Logging into Azure...${NC}"
    az login
fi

ACCOUNT=$(az account show --query "name" -o tsv)
SUBSCRIPTION=$(az account show --query "id" -o tsv)
echo -e "${GREEN}✅ Connected to Azure${NC}"
echo "   Account: $ACCOUNT"
echo "   Subscription: $SUBSCRIPTION"

# Step 2: Create Resource Group
echo -e "\n${YELLOW}[Step 2/5] Creating Resource Group...${NC}"
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --tags environment=production app=rag-stack > /dev/null

echo -e "${GREEN}✅ Resource Group created: $RESOURCE_GROUP${NC}"
echo "   Location: $LOCATION"

# Step 3: Setup Container Registry
echo -e "\n${YELLOW}[Step 3/5] Setting up Container Registry...${NC}"
REGISTRY_EXISTS=$(az acr check-name --name "$CONTAINER_REGISTRY_NAME" --query "nameAvailable" -o tsv)

if [ "$REGISTRY_EXISTS" == "false" ]; then
    echo -e "${YELLOW}Using existing registry: $CONTAINER_REGISTRY_NAME${NC}"
else
    echo -e "${YELLOW}Creating new Container Registry...${NC}"
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$CONTAINER_REGISTRY_NAME" \
        --sku Basic \
        --admin-enabled true > /dev/null
fi

REGISTRY_URL=$(az acr show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CONTAINER_REGISTRY_NAME" \
    --query "loginServer" -o tsv)

echo -e "${GREEN}✅ Container Registry ready${NC}"
echo "   URL: $REGISTRY_URL"

# Step 4: Deploy based on type
if [ "$DEPLOYMENT_TYPE" == "aci" ]; then
    echo -e "\n${YELLOW}[Step 4/5] Deploying to Container Instances...${NC}"
    
    # Create storage account for data persistence
    STORAGE_ACCOUNT="ragstorage${RANDOM}"
    echo -e "${YELLOW}Creating Storage Account: $STORAGE_ACCOUNT${NC}"
    
    az storage account create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$STORAGE_ACCOUNT" \
        --sku Standard_LRS > /dev/null
    
    STORAGE_KEY=$(az storage account keys list \
        --resource-group "$RESOURCE_GROUP" \
        --account-name "$STORAGE_ACCOUNT" \
        --query "[0].value" -o tsv)
    
    # Create file share
    az storage share create \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --name "rag-data" > /dev/null
    
    echo -e "${GREEN}✅ Storage configured${NC}"
    
    # Deploy PostgreSQL
    echo -e "${YELLOW}Deploying PostgreSQL container...${NC}"
    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name rag-postgres \
        --image pgvector/pgvector:pg16-latest \
        --cpu 1 \
        --memory 2 \
        --environment-variables POSTGRES_PASSWORD=postgres123 POSTGRES_DB=rag_demo \
        --ports 5432 \
        --protocol TCP \
        --restart-policy OnFailure > /dev/null
    
    # Deploy Redis
    echo -e "${YELLOW}Deploying Redis container...${NC}"
    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name rag-redis \
        --image redis:7-alpine \
        --cpu 0.5 \
        --memory 1 \
        --ports 6379 \
        --protocol TCP \
        --restart-policy OnFailure > /dev/null
    
    # Deploy MongoDB
    echo -e "${YELLOW}Deploying MongoDB container...${NC}"
    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name rag-mongodb \
        --image mongo:7-alpine \
        --cpu 1 \
        --memory 2 \
        --environment-variables MONGO_INITDB_ROOT_USERNAME=admin MONGO_INITDB_ROOT_PASSWORD=admin123 \
        --ports 27017 \
        --protocol TCP \
        --restart-policy OnFailure > /dev/null
    
    # Deploy LibreChat with Azure Application Gateway
    echo -e "${YELLOW}Deploying LibreChat...${NC}"
    az container create \
        --resource-group "$RESOURCE_GROUP" \
        --name rag-librechat \
        --image ghcr.io/danny-avila/librechat:latest \
        --cpu 2 \
        --memory 4 \
        --environment-variables \
            DATABASE_URL="postgresql://postgres:postgres123@rag-postgres.internal.cloudapp.net:5432/rag_demo" \
            REDIS_URL="redis://rag-redis.internal.cloudapp.net:6379" \
            MONGO_URI="mongodb://admin:admin123@rag-mongodb.internal.cloudapp.net:27017/admin?authSource=admin" \
            DEBUG=false \
        --ports 3080 \
        --protocol TCP \
        --dns-name-label "rag-librechat-${RANDOM}" \
        --restart-policy OnFailure > /dev/null
    
    echo -e "${GREEN}✅ Containers deployed${NC}"
    
elif [ "$DEPLOYMENT_TYPE" == "aks" ]; then
    echo -e "\n${YELLOW}[Step 4/5] Deploying to Azure Kubernetes Service...${NC}"
    
    AKS_CLUSTER_NAME="rag-aks-cluster"
    AKS_NODE_COUNT=3
    
    echo -e "${YELLOW}Creating AKS cluster (this may take 10-15 minutes)...${NC}"
    az aks create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$AKS_CLUSTER_NAME" \
        --node-count "$AKS_NODE_COUNT" \
        --vm-set-type VirtualMachineScaleSets \
        --enable-managed-identity \
        --network-plugin azure \
        --enable-addons monitoring \
        --generate-ssh-keys \
        --attach-acr "$CONTAINER_REGISTRY_NAME" > /dev/null
    
    echo -e "${GREEN}✅ AKS cluster created${NC}"
    
    # Get credentials
    az aks get-credentials \
        --resource-group "$RESOURCE_GROUP" \
        --name "$AKS_CLUSTER_NAME"
    
    # Create Kubernetes manifests
    cat > "${INSTALL_DIR}/k8s-deployment.yaml" << 'K8S_EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: rag-stack
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: rag-config
  namespace: rag-stack
data:
  DATABASE_URL: "postgresql://postgres:postgres123@postgres:5432/rag_demo"
  REDIS_URL: "redis://redis:6379"
  MONGO_URI: "mongodb://admin:admin123@mongodb:27017/admin"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: rag-stack
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: pgvector/pgvector:pg16-latest
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          value: "postgres123"
        - name: POSTGRES_DB
          value: "rag_demo"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: rag-stack
spec:
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: librechat
  namespace: rag-stack
spec:
  replicas: 2
  selector:
    matchLabels:
      app: librechat
  template:
    metadata:
      labels:
        app: librechat
    spec:
      containers:
      - name: librechat
        image: ghcr.io/danny-avila/librechat:latest
        ports:
        - containerPort: 3080
        envFrom:
        - configMapRef:
            name: rag-config
---
apiVersion: v1
kind: Service
metadata:
  name: librechat
  namespace: rag-stack
spec:
  selector:
    app: librechat
  ports:
  - protocol: TCP
    port: 3080
    targetPort: 3080
  type: LoadBalancer
K8S_EOF
    
    # Deploy
    kubectl apply -f k8s-deployment.yaml
    echo -e "${GREEN}✅ Kubernetes manifests deployed${NC}"
    
else
    echo -e "${RED}❌ Unknown deployment type: $DEPLOYMENT_TYPE${NC}"
    exit 1
fi

# Step 5: Verify deployment
echo -e "\n${YELLOW}[Step 5/5] Verifying deployment...${NC}"

if [ "$DEPLOYMENT_TYPE" == "aci" ]; then
    echo -e "${YELLOW}Checking container status...${NC}"
    for container in rag-postgres rag-redis rag-mongodb rag-librechat; do
        STATUS=$(az container show \
            --resource-group "$RESOURCE_GROUP" \
            --name "$container" \
            --query "containers[0].instanceView.currentState.state" -o tsv 2>/dev/null || echo "NotFound")
        echo "   $container: $STATUS"
    done
    
    # Get LibreChat IP
    LIBRECHAT_IP=$(az container show \
        --resource-group "$RESOURCE_GROUP" \
        --name rag-librechat \
        --query "ipAddress.ip" -o tsv 2>/dev/null || echo "Pending")
    
    LIBRECHAT_URL="http://${LIBRECHAT_IP}:3080"
fi

# Display summary
echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}📍 Deployment Details:${NC}"
echo -e "   Resource Group: $RESOURCE_GROUP"
echo -e "   Location: $LOCATION"
echo -e "   Deployment Type: $DEPLOYMENT_TYPE"
echo -e "   Registry: $REGISTRY_URL"

if [ "$DEPLOYMENT_TYPE" == "aci" ]; then
    echo -e "\n${BLUE}🌐 Access:${NC}"
    echo -e "   LibreChat: $LIBRECHAT_URL"
else
    echo -e "\n${BLUE}🌐 Access:${NC}"
    echo -e "   Get LoadBalancer IP: kubectl get svc -n rag-stack librechat"
    echo -e "   Port forward: kubectl port-forward -n rag-stack svc/librechat 3080:3080"
fi

echo -e "\n${BLUE}📊 Monitor Logs:${NC}"
if [ "$DEPLOYMENT_TYPE" == "aci" ]; then
    echo -e "   PostgreSQL: az container logs --resource-group $RESOURCE_GROUP --name rag-postgres"
    echo -e "   LibreChat: az container logs --resource-group $RESOURCE_GROUP --name rag-librechat"
else
    echo -e "   kubectl logs -n rag-stack deployment/librechat"
    echo -e "   kubectl logs -n rag-stack deployment/postgres"
fi

echo -e "\n${BLUE}🧹 Cleanup:${NC}"
echo -e "   Delete all resources: az group delete --name $RESOURCE_GROUP --yes"

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

exit 0
