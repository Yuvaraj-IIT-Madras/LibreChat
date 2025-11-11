# Azure Deployment - Testing & Validation Guide

This guide provides comprehensive testing procedures, validation checklists, and troubleshooting steps for your LibreChat + Agentic Analytics + Playwright deployment on Azure.

---

## 📋 Table of Contents

1. [Pre-Deployment Validation](#pre-deployment-validation)
2. [Post-Deployment Testing](#post-deployment-testing)
3. [Agentic Analytics Verification](#agentic-analytics-verification)
4. [Playwright E2E Testing](#playwright-e2e-testing)
5. [Performance Testing](#performance-testing)
6. [Security Validation](#security-validation)
7. [Disaster Recovery Testing](#disaster-recovery-testing)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Monitoring Checklist](#monitoring-checklist)
10. [Cost Optimization Validation](#cost-optimization-validation)

---

## 🔍 Pre-Deployment Validation

### 1. Local Environment Test

Before deploying to Azure, validate everything works locally:

```bash
# Navigate to project directory
cd /home/yuvaraj/Projects/LibreChat

# Start all services using Azure-optimized Docker Compose
docker-compose -f azure/docker-compose.azure.yml up -d

# Wait for services to be healthy
sleep 30

# Check service health
docker-compose -f azure/docker-compose.azure.yml ps

# Expected: All services showing "healthy" status
```

**Validation Checklist:**
- [ ] All containers started successfully
- [ ] No error messages in logs
- [ ] LibreChat accessible at http://localhost:3080
- [ ] Can register new user account
- [ ] Can send message and receive AI response
- [ ] RAG API responding at http://localhost:8000
- [ ] Meilisearch search working

### 2. Configuration Validation

```bash
# Validate environment file
cd /home/yuvaraj/Projects/LibreChat
source azure/.env.azure

# Check required variables
for var in AZURE_RESOURCE_GROUP AZURE_SUBSCRIPTION_ID OPENAI_API_KEY GOOGLE_KEY; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing: $var"
    else
        echo "✅ Set: $var"
    fi
done

# Validate secrets format
python3 << 'VALIDATE_EOF'
import os
import re

# JWT Secret should be at least 32 characters
jwt_secret = os.getenv('JWT_SECRET', '')
if len(jwt_secret) < 32:
    print("❌ JWT_SECRET too short (minimum 32 chars)")
else:
    print("✅ JWT_SECRET length OK")

# CREDS_KEY should be base64, 32 chars
creds_key = os.getenv('CREDS_KEY', '')
if len(creds_key) != 44:  # base64 of 32 bytes = 44 chars
    print("⚠️  CREDS_KEY length incorrect (should be 44 chars base64)")
else:
    print("✅ CREDS_KEY format OK")

# CREDS_IV should be hex, 16 chars
creds_iv = os.getenv('CREDS_IV', '')
if not re.match(r'^[0-9a-f]{16}$', creds_iv):
    print("❌ CREDS_IV invalid (should be 16 hex chars)")
else:
    print("✅ CREDS_IV format OK")
VALIDATE_EOF
```

### 3. Dockerfile Build Test

```bash
# Test building Agentic Analytics image
docker build -f azure/Dockerfile.agentic-analytics -t agentic-analytics:test .
if [ $? -eq 0 ]; then
    echo "✅ Agentic Analytics image builds successfully"
else
    echo "❌ Agentic Analytics image build failed"
fi

# Test building Playwright E2E image
docker build -f azure/Dockerfile.playwright-e2e -t playwright-e2e:test .
if [ $? -eq 0 ]; then
    echo "✅ Playwright E2E image builds successfully"
else
    echo "❌ Playwright E2E image build failed"
fi

# Test building MCP Forwarder image
docker build -f azure/Dockerfile.mcp-forwarder -t mcp-forwarder:test .
if [ $? -eq 0 ]; then
    echo "✅ MCP Forwarder image builds successfully"
else
    echo "❌ MCP Forwarder image build failed"
fi
```

---

## ✅ Post-Deployment Testing

### 1. Service Health Checks

```bash
# Set your resource group
RESOURCE_GROUP="librechat-prod"

# Check all container instances
echo "Container Instance Status:"
az container show --resource-group "$RESOURCE_GROUP" --name "librechat-app" --query "instanceView.state" -o tsv
az container show --resource-group "$RESOURCE_GROUP" --name "librechat-rag-api" --query "instanceView.state" -o tsv
az container show --resource-group "$RESOURCE_GROUP" --name "librechat-meilisearch" --query "instanceView.state" -o tsv
az container show --resource-group "$RESOURCE_GROUP" --name "agentic-analytics" --query "instanceView.state" -o tsv

# Expected: All showing "Running"

# Check database connectivity
echo "Database Status:"
PG_SERVER_NAME="your-postgres-server"
az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$PG_SERVER_NAME" --query "state" -o tsv

COSMOS_ACCOUNT="your-cosmos-account"
az cosmosdb show --resource-group "$RESOURCE_GROUP" --name "$COSMOS_ACCOUNT" --query "provisioningState" -o tsv

REDIS_NAME="your-redis-instance"
az redis show --resource-group "$RESOURCE_GROUP" --name "$REDIS_NAME" --query "provisioningState" -o tsv

# Expected: All showing "Succeeded" or "Running"
```

### 2. Application Endpoint Tests

```bash
# Get LibreChat URL
LIBRECHAT_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-app" --query "ipAddress.fqdn" -o tsv)

# Test health endpoint
curl -f "http://${LIBRECHAT_URL}:3080/api/health"
# Expected: {"status":"ok"}

# Test RAG API
RAG_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-rag-api" --query "ipAddress.fqdn" -o tsv)
curl -f "http://${RAG_URL}:8000/health"
# Expected: {"status":"healthy"}

# Test Meilisearch
MEILI_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-meilisearch" --query "ipAddress.fqdn" -o tsv)
curl -f "http://${MEILI_URL}:7700/health"
# Expected: {"status":"available"}
```

### 3. Functional Testing Script

```bash
#!/bin/bash
# Save as: azure/test-deployment.sh

RESOURCE_GROUP="$1"
LIBRECHAT_URL="$2"

echo "Testing LibreChat Deployment..."

# Test 1: Frontend loads
echo "[1/10] Testing frontend..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://${LIBRECHAT_URL}:3080")
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Frontend loads successfully"
else
    echo "❌ Frontend failed (HTTP $HTTP_STATUS)"
fi

# Test 2: API health
echo "[2/10] Testing API health..."
HEALTH_RESPONSE=$(curl -s "http://${LIBRECHAT_URL}:3080/api/health")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
fi

# Test 3: User registration
echo "[3/10] Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "http://${LIBRECHAT_URL}:3080/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!"
    }')

if echo "$REGISTER_RESPONSE" | grep -q "token\|success"; then
    echo "✅ User registration works"
else
    echo "⚠️  User registration (may already exist)"
fi

# Test 4: User login
echo "[4/10] Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://${LIBRECHAT_URL}:3080/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "TestPassword123!"
    }')

if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
    echo "✅ User login works"
else
    echo "❌ User login failed"
    exit 1
fi

# Test 5: List models
echo "[5/10] Testing model listing..."
MODELS_RESPONSE=$(curl -s "http://${LIBRECHAT_URL}:3080/api/models" \
    -H "Authorization: Bearer $TOKEN")

if echo "$MODELS_RESPONSE" | grep -q "gpt\|claude\|gemini"; then
    echo "✅ Models API works"
else
    echo "❌ Models API failed"
fi

# Test 6: Create conversation
echo "[6/10] Testing conversation creation..."
CONV_RESPONSE=$(curl -s -X POST "http://${LIBRECHAT_URL}:3080/api/conversations" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "gpt-3.5-turbo",
        "message": "Hello, this is a test message"
    }')

if echo "$CONV_RESPONSE" | grep -q "conversationId\|id"; then
    echo "✅ Conversation creation works"
else
    echo "❌ Conversation creation failed"
fi

# Test 7: RAG API
echo "[7/10] Testing RAG API..."
RAG_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-rag-api" --query "ipAddress.fqdn" -o tsv)
RAG_HEALTH=$(curl -s "http://${RAG_URL}:8000/health")

if echo "$RAG_HEALTH" | grep -q "healthy\|ok"; then
    echo "✅ RAG API is healthy"
else
    echo "❌ RAG API health check failed"
fi

# Test 8: Meilisearch
echo "[8/10] Testing Meilisearch..."
MEILI_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-meilisearch" --query "ipAddress.fqdn" -o tsv)
MEILI_HEALTH=$(curl -s "http://${MEILI_URL}:7700/health")

if echo "$MEILI_HEALTH" | grep -q "available"; then
    echo "✅ Meilisearch is available"
else
    echo "❌ Meilisearch health check failed"
fi

# Test 9: PostgreSQL connectivity
echo "[9/10] Testing PostgreSQL..."
PG_SERVER=$(az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$(az postgres flexible-server list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv)" --query "fullyQualifiedDomainName" -o tsv)

if [ -n "$PG_SERVER" ]; then
    echo "✅ PostgreSQL server accessible"
else
    echo "❌ PostgreSQL server not found"
fi

# Test 10: Redis connectivity
echo "[10/10] Testing Redis..."
REDIS_STATUS=$(az redis show --resource-group "$RESOURCE_GROUP" --name "$(az redis list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv)" --query "provisioningState" -o tsv)

if [ "$REDIS_STATUS" = "Succeeded" ]; then
    echo "✅ Redis is provisioned"
else
    echo "❌ Redis provisioning failed"
fi

echo ""
echo "========================================="
echo "Deployment Testing Complete!"
echo "========================================="
```

Run the test:

```bash
chmod +x azure/test-deployment.sh
./azure/test-deployment.sh "librechat-prod" "your-librechat-fqdn"
```

---

## 🧪 Agentic Analytics Verification

### 1. Test Tech Analyzer

```bash
# Check if Agentic Analytics container ran successfully
az container logs --resource-group "$RESOURCE_GROUP" --name "agentic-analytics" --tail 100

# Look for success indicators:
# - "Tech Stack Analysis complete"
# - "Dependencies mapped successfully"
# - "Stack generation finished"
```

### 2. Verify Database Adapter Registry

```bash
# Run test inside the container
az container exec \
    --resource-group "$RESOURCE_GROUP" \
    --name "agentic-analytics" \
    --exec-command "python /app/test_database_adapters.py"

# Expected output:
# ✅ PostgreSQL adapter: PASSED
# ✅ MongoDB adapter: PASSED
# ✅ MySQL adapter: PASSED
# ✅ Redis adapter: PASSED
# ✅ ClickHouse adapter: PASSED
```

### 3. Test RAG Pipeline

```bash
# Test document ingestion
az container exec \
    --resource-group "$RESOURCE_GROUP" \
    --name "agentic-analytics" \
    --exec-command "python /app/rag_pipeline.py"

# Check output for:
# - Document count
# - Chunk count
# - Embedding count
```

### 4. Verify Stack Generator Output

```bash
# Retrieve generated stack configurations
az container exec \
    --resource-group "$RESOURCE_GROUP" \
    --name "agentic-analytics" \
    --exec-command "ls -la /app/output"

# Should contain:
# - tech-stack-analysis.json
# - dependency-map.json
# - generated-stack.yml
# - .documentignore
```

---

## 🎭 Playwright E2E Testing

### 1. Access VNC for Visual Debugging

```bash
# Get VNC URL
VNC_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "playwright-e2e" --query "ipAddress.fqdn" -o tsv)

echo "VNC Server: vnc://${VNC_URL}:5900"
echo "Web VNC: http://${VNC_URL}:6080"
echo "Password: librechat"

# On your local machine, connect with VNC viewer:
vncviewer "${VNC_URL}:5900"
```

### 2. Check Test Results

```bash
# View test logs
az container logs --resource-group "$RESOURCE_GROUP" --name "playwright-e2e" --tail 200

# Look for test summary:
# Expected: 33/33 tests passed
```

### 3. Download Test Screenshots

```bash
# List screenshots in Azure Blob Storage
STORAGE_ACCOUNT="your-storage-account"
az storage blob list \
    --account-name "$STORAGE_ACCOUNT" \
    --container-name "screenshots" \
    --prefix "e2e-tests/" \
    --output table

# Download all screenshots
mkdir -p azure-test-screenshots
az storage blob download-batch \
    --account-name "$STORAGE_ACCOUNT" \
    --source "screenshots" \
    --destination "azure-test-screenshots/" \
    --pattern "e2e-tests/*.png"

echo "Screenshots downloaded to: azure-test-screenshots/"
```

### 4. Verify MCP Event Streaming

If using Azure Event Hub:

```bash
# Check Event Hub metrics
EVENT_HUB_NAMESPACE="your-event-hub-namespace"
az eventhubs eventhub show \
    --resource-group "$RESOURCE_GROUP" \
    --namespace-name "$EVENT_HUB_NAMESPACE" \
    --name "e2e-test-events" \
    --query "captureDescription"

# View Event Hub events (requires Azure CLI extension)
az eventhubs eventhub consumer-group show \
    --resource-group "$RESOURCE_GROUP" \
    --namespace-name "$EVENT_HUB_NAMESPACE" \
    --eventhub-name "e2e-test-events" \
    --name "\$Default"
```

---

## ⚡ Performance Testing

### 1. Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt-get install apache2-utils -y

# Test LibreChat endpoint
LIBRECHAT_URL="your-librechat-fqdn"

# Light load test (10 concurrent, 100 requests)
ab -n 100 -c 10 "http://${LIBRECHAT_URL}:3080/api/health"

# Expected results:
# - Requests per second: > 50
# - Time per request: < 200ms
# - Failed requests: 0

# Moderate load test (50 concurrent, 500 requests)
ab -n 500 -c 50 "http://${LIBRECHAT_URL}:3080/api/health"

# Expected results:
# - Requests per second: > 30
# - Time per request: < 500ms
# - Failed requests: < 5%
```

### 2. Database Performance Test

```bash
# PostgreSQL connection pool test
cat > test-pg-performance.sh << 'PG_TEST_EOF'
#!/bin/bash
PG_HOST="$1"
PG_USER="$2"
PG_PASSWORD="$3"
PG_DATABASE="$4"

echo "Testing PostgreSQL performance..."

# Test connection time
START=$(date +%s%N)
PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -U "$PG_USER" -d "$PG_DATABASE" -c "SELECT 1;" > /dev/null 2>&1
END=$(date +%s%N)
DIFF=$((($END - $START) / 1000000))

if [ $DIFF -lt 500 ]; then
    echo "✅ Connection time: ${DIFF}ms (Good)"
elif [ $DIFF -lt 1000 ]; then
    echo "⚠️  Connection time: ${DIFF}ms (Acceptable)"
else
    echo "❌ Connection time: ${DIFF}ms (Slow)"
fi

# Test query performance
PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -U "$PG_USER" -d "$PG_DATABASE" << 'SQL_EOF'
\timing on
SELECT COUNT(*) FROM information_schema.tables;
SELECT pg_database_size(current_database());
SQL_EOF
PG_TEST_EOF

chmod +x test-pg-performance.sh

# Run test
PG_SERVER="your-pg-server.postgres.database.azure.com"
./test-pg-performance.sh "$PG_SERVER" "librechat_admin" "your-password" "librechat"
```

### 3. End-to-End Response Time Test

```bash
# Test full conversation flow
cat > test-e2e-response.sh << 'E2E_TEST_EOF'
#!/bin/bash
LIBRECHAT_URL="$1"

echo "Testing end-to-end response time..."

# Register user
START=$(date +%s%N)
REGISTER_RESPONSE=$(curl -s -X POST "http://${LIBRECHAT_URL}:3080/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"Perf Test $(date +%s)\",
        \"email\": \"perftest$(date +%s)@example.com\",
        \"password\": \"TestPassword123!\",
        \"confirm_password\": \"TestPassword123!\"
    }")
END=$(date +%s%N)
REGISTER_TIME=$((($END - $START) / 1000000))

echo "Registration time: ${REGISTER_TIME}ms"

# Login
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.token')

# Send message (with AI response)
START=$(date +%s%N)
MESSAGE_RESPONSE=$(curl -s -X POST "http://${LIBRECHAT_URL}:3080/api/conversations" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "model": "gpt-3.5-turbo",
        "message": "Say hello in one word"
    }')
END=$(date +%s%N)
MESSAGE_TIME=$((($END - $START) / 1000000))

echo "Message response time: ${MESSAGE_TIME}ms"

# Benchmarks
if [ $MESSAGE_TIME -lt 3000 ]; then
    echo "✅ Response time excellent"
elif [ $MESSAGE_TIME -lt 5000 ]; then
    echo "✅ Response time good"
elif [ $MESSAGE_TIME -lt 10000 ]; then
    echo "⚠️  Response time acceptable"
else
    echo "❌ Response time slow (> 10s)"
fi
E2E_TEST_EOF

chmod +x test-e2e-response.sh
./test-e2e-response.sh "your-librechat-fqdn"
```

---

## 🔒 Security Validation

### 1. SSL/TLS Configuration Test

```bash
# Test HTTPS endpoint (if Application Gateway configured)
APP_GATEWAY_IP="your-app-gateway-ip"

# Check SSL certificate
echo | openssl s_client -connect "${APP_GATEWAY_IP}:443" -servername "your-domain.com" 2>/dev/null | openssl x509 -noout -text

# Expected:
# - Valid certificate
# - Not expired
# - Matches domain name
```

### 2. Network Security Group Validation

```bash
# Check NSG rules
az network nsg list --resource-group "$RESOURCE_GROUP" --output table

# Verify inbound rules
az network nsg rule list \
    --resource-group "$RESOURCE_GROUP" \
    --nsg-name "your-nsg-name" \
    --output table

# Expected:
# - Port 22 (SSH) blocked or restricted to specific IPs
# - Port 3080 (LibreChat) accessible
# - Database ports (5432, 27017, 6379) internal only
```

### 3. Key Vault Access Test

```bash
# Test Key Vault connectivity
KEY_VAULT_NAME="your-key-vault"

# List secrets (without values)
az keyvault secret list --vault-name "$KEY_VAULT_NAME" --output table

# Retrieve a test secret
TEST_SECRET=$(az keyvault secret show --vault-name "$KEY_VAULT_NAME" --name "OpenAI-ApiKey" --query "value" -o tsv)

if [ -n "$TEST_SECRET" ] && [ "$TEST_SECRET" != "null" ]; then
    echo "✅ Key Vault access working"
else
    echo "❌ Key Vault access failed"
fi
```

### 4. Vulnerability Scanning

```bash
# Enable Azure Security Center scanning
az security pricing create --name VirtualMachines --tier Standard
az security pricing create --name AppServices --tier Standard
az security pricing create --name SqlServers --tier Standard

# Check security alerts
az security alert list --resource-group "$RESOURCE_GROUP" --output table

# Expected: No high or critical alerts
```

---

## 🛡️ Disaster Recovery Testing

### 1. Database Backup Verification

```bash
# Check PostgreSQL backups
az postgres flexible-server backup list \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$PG_SERVER_NAME" \
    --output table

# Expected: Recent backups available

# Test restore (to different server)
az postgres flexible-server restore \
    --resource-group "$RESOURCE_GROUP" \
    --name "librechat-pg-restore-test" \
    --source-server "$PG_SERVER_NAME" \
    --restore-time "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)" \
    --location "$REGION"

# Verify restore succeeded
az postgres flexible-server show \
    --resource-group "$RESOURCE_GROUP" \
    --name "librechat-pg-restore-test" \
    --query "state" -o tsv

# Clean up test restore
az postgres flexible-server delete \
    --resource-group "$RESOURCE_GROUP" \
    --name "librechat-pg-restore-test" \
    --yes
```

### 2. Container Instance Failover Test

```bash
# Stop LibreChat container
az container stop --resource-group "$RESOURCE_GROUP" --name "librechat-app"

# Wait for restart policy to kick in
sleep 60

# Check if container restarted
CONTAINER_STATE=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-app" --query "instanceView.state" -o tsv)

if [ "$CONTAINER_STATE" = "Running" ]; then
    echo "✅ Container auto-restart successful"
else
    echo "❌ Container did not restart (State: $CONTAINER_STATE)"
fi

# Verify application accessible
LIBRECHAT_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "librechat-app" --query "ipAddress.fqdn" -o tsv)
curl -f "http://${LIBRECHAT_URL}:3080/api/health"
```

### 3. Geo-Replication Validation (if enabled)

```bash
# Check Cosmos DB replication status
az cosmosdb show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$COSMOS_ACCOUNT" \
    --query "locations[].{Region:locationName,FailoverPriority:failoverPriority,Status:provisioningState}" \
    --output table

# Expected: Multiple regions with status "Succeeded"
```

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Container Won't Start

**Symptoms:**
- Container stuck in "Creating" or "Failed" state

**Diagnosis:**
```bash
# Check container logs
az container logs --resource-group "$RESOURCE_GROUP" --name "librechat-app" --tail 100

# Check container events
az container show --resource-group "$RESOURCE_GROUP" --name "librechat-app" --query "instanceView"
```

**Solutions:**
- Check environment variables are set correctly
- Verify Docker image exists in ACR
- Check CPU/Memory limits aren't too low
- Review network connectivity to dependencies

#### Issue 2: Database Connection Timeouts

**Symptoms:**
- LibreChat shows database connection errors
- Slow response times

**Diagnosis:**
```bash
# Test database connectivity from container
az container exec \
    --resource-group "$RESOURCE_GROUP" \
    --name "librechat-app" \
    --exec-command "/bin/bash -c 'apt-get update && apt-get install -y postgresql-client && psql -h DB_HOST -U DB_USER -d DB_NAME -c \"SELECT 1;\"'"
```

**Solutions:**
- Check firewall rules allow container IP
- Verify connection string format
- Check database server not overloaded
- Increase connection pool size

#### Issue 3: Out of Memory Errors

**Symptoms:**
- Container restarts frequently
- "OOMKilled" in container events

**Diagnosis:**
```bash
# Check memory usage
az monitor metrics list \
    --resource "/subscriptions/SUBSCRIPTION_ID/resourceGroups/RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/librechat-app" \
    --metric "MemoryUsage" \
    --start-time "2024-01-01T00:00:00Z"
```

**Solutions:**
```bash
# Increase memory allocation
az container create \
    --resource-group "$RESOURCE_GROUP" \
    --name "librechat-app" \
    --memory 16  # Increase from current value
```

#### Issue 4: Playwright Tests Fail

**Symptoms:**
- E2E tests timeout or fail
- No screenshots generated

**Diagnosis:**
```bash
# Check Playwright container logs
az container logs --resource-group "$RESOURCE_GROUP" --name "playwright-e2e" --tail 200

# Connect to VNC to see browser
VNC_URL=$(az container show --resource-group "$RESOURCE_GROUP" --name "playwright-e2e" --query "ipAddress.fqdn" -o tsv)
vncviewer "${VNC_URL}:5900"
```

**Solutions:**
- Verify E2E_URL points to correct LibreChat instance
- Check LibreChat is fully started before tests run
- Increase test timeouts
- Check network connectivity between containers

---

## 📊 Monitoring Checklist

### Daily Checks

```bash
# Health status of all services
az container list --resource-group "$RESOURCE_GROUP" --query "[].{Name:name,State:instanceView.state,Restarts:instanceView.currentState.previousState.detailStatus}" --output table

# Database health
az postgres flexible-server show --resource-group "$RESOURCE_GROUP" --name "$PG_SERVER_NAME" --query "{Name:name,State:state,Version:version}" --output table

# Redis health
az redis show --resource-group "$RESOURCE_GROUP" --name "$REDIS_NAME" --query "{Name:name,ProvisioningState:provisioningState,RedisVersion:redisVersion}" --output table

# Storage account usage
az storage account show-usage --location "$REGION" --output table
```

### Weekly Checks

```bash
# Application Insights errors
az monitor app-insights events show \
    --app "librechat-insights" \
    --resource-group "$RESOURCE_GROUP" \
    --type exceptions \
    --start-time "7 days ago" \
    --output table

# Cost analysis
az consumption usage list \
    --start-date "$(date -d '7 days ago' +%Y-%m-%d)" \
    --end-date "$(date +%Y-%m-%d)" \
    --query "[?contains(instanceName,'librechat')].{Resource:instanceName,Cost:pretaxCost}" \
    --output table
```

### Monthly Checks

```bash
# Security Center recommendations
az security assessment list --resource-group "$RESOURCE_GROUP" --query "[?properties.status.code=='Unhealthy']" --output table

# Backup retention validation
az backup policy list --resource-group "$RESOURCE_GROUP" --vault-name "your-vault" --output table
```

---

## 💰 Cost Optimization Validation

### 1. Identify Unused Resources

```bash
# Find stopped containers
az container list --resource-group "$RESOURCE_GROUP" --query "[?instanceView.state=='Stopped'].{Name:name,State:instanceView.state}" --output table

# Find underutilized databases
az postgres flexible-server list --resource-group "$RESOURCE_GROUP" --query "[].{Name:name,Tier:sku.tier,Cores:sku.capacity}" --output table
```

### 2. Right-Sizing Recommendations

```bash
# Get Azure Advisor cost recommendations
az advisor recommendation list \
    --category Cost \
    --resource-group "$RESOURCE_GROUP" \
    --output table
```

### 3. Reserved Instance Savings

```bash
# Calculate potential savings
az reservations reservation list --output table

# Expected: Recommendation to purchase reserved instances for PostgreSQL and Redis
```

---

## ✅ Final Validation Checklist

Before considering deployment complete, verify:

### Application Layer
- [ ] LibreChat accessible via public URL
- [ ] User registration working
- [ ] User login working
- [ ] AI model selection working
- [ ] Message sending/receiving functional
- [ ] File upload working
- [ ] Settings saved correctly
- [ ] Search functionality operational

### Agentic Analytics
- [ ] Tech stack analysis completed
- [ ] Dependency mapping successful
- [ ] Stack generation working
- [ ] Database adapters functional
- [ ] RAG pipeline operational

### Playwright E2E
- [ ] All 33 test steps passing
- [ ] Screenshots captured
- [ ] VNC access working
- [ ] MCP events streaming (if configured)
- [ ] Test logs available

### Infrastructure
- [ ] All containers running
- [ ] Databases healthy
- [ ] Storage accessible
- [ ] Networking configured
- [ ] SSL/TLS enabled (production)
- [ ] Firewall rules correct
- [ ] Backups configured
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Cost tracking enabled

### Security
- [ ] Secrets in Key Vault
- [ ] No hardcoded credentials
- [ ] Network security groups applied
- [ ] Private endpoints configured
- [ ] Azure Defender enabled
- [ ] Vulnerability scans clean
- [ ] Compliance requirements met

### Documentation
- [ ] Deployment info saved
- [ ] Architecture diagram updated
- [ ] Runbook created
- [ ] DR procedures documented
- [ ] Support contacts listed
- [ ] Change log maintained

---

## 📞 Support Resources

### Azure Support
- **Portal**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **Phone**: 1-800-642-7676 (US)
- **Documentation**: https://learn.microsoft.com/azure/

### LibreChat Community
- **Discord**: https://discord.librechat.ai
- **GitHub**: https://github.com/danny-avila/LibreChat
- **Documentation**: https://www.librechat.ai/docs/

### Emergency Contacts
- Azure On-Call: [Your Support Plan]
- DevOps Team: [Your Team Contact]
- Security Team: [Your Security Team]

---

## 📝 Conclusion

This testing and validation guide ensures your Azure deployment is:
- ✅ Functionally complete
- ✅ Performant under load
- ✅ Secure and compliant
- ✅ Resilient to failures
- ✅ Cost-optimized
- ✅ Well-monitored

Regular execution of these tests (daily, weekly, monthly) will maintain deployment health and catch issues early.

**Remember**: Testing is an ongoing process, not a one-time activity. Schedule regular test runs and update this guide as your deployment evolves.

Happy deploying! 🚀
