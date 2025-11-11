# Azure Deployment Package for LibreChat + Agentic Analytics + Playwright E2E

This directory contains all the necessary files and documentation to deploy your complete LibreChat environment to Microsoft Azure.

---

## 📦 Package Contents

### 📖 Documentation

| File | Purpose | Read Time |
|------|---------|-----------|
| **AZURE_DEPLOYMENT_GUIDE.md** | Complete step-by-step deployment guide with architecture diagrams | 45 min |
| **TESTING_AND_VALIDATION_GUIDE.md** | Comprehensive testing procedures and troubleshooting | 30 min |
| **README.md** | This file - quick start guide | 5 min |

### 🐳 Docker Images

| File | Description | Build Time |
|------|-------------|------------|
| **Dockerfile.agentic-analytics** | Multi-mode Python analytics container | ~3 min |
| **Dockerfile.playwright-e2e** | VNC-enabled E2E testing container | ~5 min |
| **Dockerfile.mcp-forwarder** | Azure Event Hub event streaming | ~2 min |

### ⚙️ Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| **.env.azure.example** | Environment variable template | ✅ Yes - Copy to `.env.azure` |
| **docker-compose.azure.yml** | Local testing environment | ⚠️ Optional - For local validation |
| **requirements-analytics.txt** | Python dependencies for analytics | ✅ Yes - Used by Dockerfile |

### 🚀 Automation Scripts

| File | Purpose | When to Use |
|------|---------|-------------|
| **deploy-to-azure.sh** | Automated 15-step Azure deployment | Production deployment |

---

## 🎯 Quick Start (5 Minutes)

### Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Azure Account** with active subscription
- [ ] **Azure CLI** installed (`az --version`)
- [ ] **Docker** installed (`docker --version`)
- [ ] **API Keys** ready:
  - OpenAI API key
  - Anthropic API key (optional)
  - Google Gemini API key (for analytics)
- [ ] **20 minutes** of focused time
- [ ] **$150-800/month** budget (depending on deployment type)

### Step 1: Configure Environment (2 minutes)

```bash
# Navigate to azure directory
cd /home/yuvaraj/Projects/LibreChat/azure

# Copy environment template
cp .env.azure.example .env.azure

# Edit with your values
nano .env.azure
```

**Critical variables to set:**

```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_RESOURCE_GROUP="librechat-prod"
AZURE_LOCATION="eastus"

# API Keys
OPENAI_API_KEY="sk-..."
GOOGLE_KEY="AIza..."

# Security (generate random values)
JWT_SECRET="$(openssl rand -hex 32)"
CREDS_KEY="$(openssl rand -base64 32)"
CREDS_IV="$(openssl rand -hex 8)"
SESSION_SECRET="$(openssl rand -hex 32)"
```

### Step 2: Choose Deployment Strategy (1 minute)

| Strategy | Cost/Month | Setup Time | Best For |
|----------|------------|------------|----------|
| **Container Instances (ACI)** | $150-250 | 15 min | Development, POC, Testing |
| **Kubernetes Service (AKS)** | $400-800 | 60 min | Production, High Availability |
| **Container Apps** | $100-300 | 30 min | Serverless, Auto-scaling |

**Recommended for first deployment: Container Instances (ACI)**

### Step 3: Deploy to Azure (10 minutes)

```bash
# Make script executable (if not already)
chmod +x deploy-to-azure.sh

# Run deployment with Container Instances
./deploy-to-azure.sh \
    --env production \
    --region eastus \
    --type aci

# Expected output:
# [1/15] Checking Azure CLI... ✅
# [2/15] Creating Resource Group... ✅
# [3/15] Setting up Container Registry... ✅
# ...
# [15/15] Deployment Complete! 🎉
```

### Step 4: Validate Deployment (5 minutes)

```bash
# Get deployment info
cat deployment-info.json

# Test LibreChat URL
curl -f "http://$(jq -r '.librechat_url' deployment-info.json):3080/api/health"
# Expected: {"status":"ok"}

# Run comprehensive tests
cd ..
./azure/test-deployment.sh "librechat-prod" "$(jq -r '.librechat_url' deployment-info.json)"
```

---

## 📊 What Gets Deployed

### Azure Resources Created

```
Resource Group: librechat-prod
├── Compute
│   ├── Container Registry (ACR)
│   ├── Container Instance: librechat-app (4 CPU, 8GB RAM)
│   ├── Container Instance: librechat-rag-api (2 CPU, 4GB RAM)
│   ├── Container Instance: librechat-meilisearch (1 CPU, 2GB RAM)
│   ├── Container Instance: agentic-analytics (2 CPU, 4GB RAM)
│   └── Container Instance: playwright-e2e (2 CPU, 4GB RAM, VNC enabled)
│
├── Databases
│   ├── PostgreSQL Flexible Server (2vCores, 4GB RAM, pgvector enabled)
│   ├── Cosmos DB for MongoDB (1000 RU/s)
│   └── Azure Cache for Redis (Premium P1, 6GB)
│
├── Storage
│   ├── Storage Account
│   │   ├── Blob Container: data (Hot tier)
│   │   ├── Blob Container: uploads
│   │   ├── Blob Container: screenshots (E2E tests)
│   │   └── File Share: logs (Premium, 100GB)
│
├── Security
│   ├── Key Vault (secrets, API keys, connection strings)
│   └── Network Security Groups (NSGs)
│
└── Monitoring
    ├── Application Insights
    ├── Log Analytics Workspace
    └── Azure Monitor Alerts
```

### Deployed Applications

1. **LibreChat** - Main chat interface
   - Port: 3080
   - Features: Multi-model AI chat, file upload, RAG search
   
2. **RAG API** - Document retrieval and vector search
   - Port: 8000
   - Database: PostgreSQL with pgvector
   
3. **Meilisearch** - Fast search engine
   - Port: 7700
   - Indexes: conversations, messages, users
   
4. **Agentic Analytics** - Tech stack analysis
   - Mode: Full (tech_stack → dependencies → stack_generation → config → rag_pipeline)
   - Output: /app/output (analysis results)
   
5. **Playwright E2E** - Automated testing
   - Tests: 33 automated test steps
   - VNC: Port 5900 (remote desktop)
   - Web VNC: Port 6080 (browser access)

---

## 🎓 Usage Guide

### For Developers

**Local Testing Before Azure Deployment:**

```bash
# Test with Azure-optimized Docker Compose
docker-compose -f azure/docker-compose.azure.yml up -d

# Check service health
docker-compose -f azure/docker-compose.azure.yml ps

# View logs
docker-compose -f azure/docker-compose.azure.yml logs -f librechat-api

# Stop services
docker-compose -f azure/docker-compose.azure.yml down
```

### For DevOps Engineers

**Monitoring Deployment:**

```bash
# Resource group overview
az group show --name librechat-prod

# Container status
az container list --resource-group librechat-prod --output table

# Database health
az postgres flexible-server show \
    --resource-group librechat-prod \
    --name librechat-pg-server \
    --query "{Name:name,State:state,Version:version}"

# View container logs
az container logs \
    --resource-group librechat-prod \
    --name librechat-app \
    --tail 100

# Application Insights metrics
az monitor app-insights metrics show \
    --app librechat-insights \
    --resource-group librechat-prod \
    --metric requests/count \
    --interval PT1H
```

### For QA Engineers

**Running E2E Tests:**

```bash
# Access VNC for visual debugging
VNC_URL=$(az container show \
    --resource-group librechat-prod \
    --name playwright-e2e \
    --query "ipAddress.fqdn" -o tsv)

echo "VNC Server: vnc://${VNC_URL}:5900"
echo "Web VNC: http://${VNC_URL}:6080"
echo "Password: librechat"

# Connect with VNC viewer
vncviewer "${VNC_URL}:5900"

# Or open in browser
xdg-open "http://${VNC_URL}:6080"

# Download test screenshots
az storage blob download-batch \
    --account-name "your-storage-account" \
    --source screenshots \
    --destination ./test-results/ \
    --pattern "e2e-tests/*.png"
```

---

## 🔧 Common Operations

### Update Application

```bash
# Rebuild and push new image
docker build -t your-registry.azurecr.io/librechat:v2 ../../
docker push your-registry.azurecr.io/librechat:v2

# Update container
az container create \
    --resource-group librechat-prod \
    --name librechat-app \
    --image your-registry.azurecr.io/librechat:v2 \
    --restart-policy Always
```

### Scale Resources

```bash
# Increase LibreChat resources
az container create \
    --resource-group librechat-prod \
    --name librechat-app \
    --cpu 8 \
    --memory 16

# Scale PostgreSQL
az postgres flexible-server update \
    --resource-group librechat-prod \
    --name librechat-pg-server \
    --tier Burstable \
    --sku-name Standard_B4ms
```

### Backup and Restore

```bash
# Backup PostgreSQL
az postgres flexible-server backup list \
    --resource-group librechat-prod \
    --server-name librechat-pg-server

# Restore to point in time
az postgres flexible-server restore \
    --resource-group librechat-prod \
    --name librechat-pg-restored \
    --source-server librechat-pg-server \
    --restore-time "2024-01-15T10:00:00Z"

# Backup Blob Storage
az storage blob snapshot \
    --account-name "your-storage" \
    --container-name data \
    --name important-file.db
```

---

## 🛡️ Security Best Practices

### Before Deployment

- [ ] Change all default passwords
- [ ] Generate strong random secrets (JWT_SECRET, CREDS_KEY, etc.)
- [ ] Store API keys in Azure Key Vault (automated by deploy script)
- [ ] Review Network Security Group rules
- [ ] Enable Azure Defender for Cloud

### After Deployment

- [ ] Enable Private Link for databases
- [ ] Configure Azure Application Gateway with SSL
- [ ] Set up Azure DDoS Protection
- [ ] Enable diagnostic logging
- [ ] Configure backup retention policies
- [ ] Set up Azure Security Center alerts
- [ ] Review Azure Advisor recommendations

### Ongoing

- [ ] Rotate secrets every 90 days
- [ ] Review access logs weekly
- [ ] Update container images monthly
- [ ] Run security scans quarterly
- [ ] Test disaster recovery procedures

---

## 💰 Cost Management

### Daily Costs (Approximate)

**Container Instances (ACI) Strategy:**
```
PostgreSQL Flexible Server (B2ms):     $3.50/day
Cosmos DB (1000 RU/s):                 $2.00/day
Azure Cache for Redis (P1):            $2.80/day
Storage Account (100GB):               $0.30/day
Container Instances (total):           $4.00/day
Application Insights:                  $0.50/day
                                    ---------------
Total:                                ~$13.10/day (~$393/month)
```

### Cost Optimization Tips

1. **Auto-Shutdown Dev Environments:**
   ```bash
   # Stop containers during off-hours
   az container stop --resource-group librechat-dev --name librechat-app
   ```

2. **Use Reserved Instances:**
   - 1-year: 40% savings
   - 3-year: 60% savings

3. **Enable Storage Lifecycle Policies:**
   ```bash
   # Move old screenshots to Cool tier after 30 days
   az storage account management-policy create \
       --account-name "your-storage" \
       --policy @lifecycle-policy.json
   ```

4. **Right-Size Databases:**
   - Monitor actual CPU/memory usage
   - Scale down during low-traffic periods

---

## 🐛 Troubleshooting

### Issue: Deployment Script Fails

**Check:**
```bash
# Azure CLI logged in?
az account show

# Correct subscription selected?
az account list --output table
az account set --subscription "Your Subscription Name"

# Required providers registered?
az provider register --namespace Microsoft.ContainerInstance
az provider register --namespace Microsoft.DBforPostgreSQL
```

### Issue: Container Won't Start

**Diagnose:**
```bash
# View logs
az container logs --resource-group librechat-prod --name librechat-app --tail 100

# Check events
az container show --resource-group librechat-prod --name librechat-app --query "instanceView.events"

# Common fixes:
# 1. Check environment variables set correctly
# 2. Verify image exists in ACR
# 3. Increase CPU/memory limits
# 4. Check network connectivity to dependencies
```

### Issue: Database Connection Errors

**Diagnose:**
```bash
# Test from container
az container exec \
    --resource-group librechat-prod \
    --name librechat-app \
    --exec-command "/bin/bash -c 'nc -zv your-pg-server.postgres.database.azure.com 5432'"

# Common fixes:
# 1. Add container IP to PostgreSQL firewall rules
# 2. Check connection string format
# 3. Verify credentials in Key Vault
```

### Need More Help?

See **TESTING_AND_VALIDATION_GUIDE.md** for comprehensive troubleshooting procedures.

---

## 📚 Documentation Index

### Start Here
1. **README.md** (this file) - Overview and quick start
2. **AZURE_DEPLOYMENT_GUIDE.md** - Complete deployment walkthrough
3. **TESTING_AND_VALIDATION_GUIDE.md** - Testing procedures and troubleshooting

### Reference
- `.env.azure.example` - All environment variables explained
- `docker-compose.azure.yml` - Local testing environment
- `deploy-to-azure.sh` - Deployment automation script

### Technical Details
- `Dockerfile.agentic-analytics` - Analytics container specification
- `Dockerfile.playwright-e2e` - E2E testing container specification
- `Dockerfile.mcp-forwarder` - Event streaming container specification
- `requirements-analytics.txt` - Python dependencies list

---

## 🔄 Migration from Local Docker Compose

If you're currently running LibreChat locally with Docker Compose:

### 1. Export Local Data

```bash
# Export MongoDB
docker exec librechat-mongodb mongodump --out /backup
docker cp librechat-mongodb:/backup ./mongodb-backup

# Export PostgreSQL
docker exec librechat-postgres pg_dump -U librechat librechat > postgres-backup.sql

# Export Redis
docker exec librechat-redis redis-cli SAVE
docker cp librechat-redis:/data/dump.rdb ./redis-backup.rdb

# Export uploaded files
docker cp librechat-api:/app/client/public/uploads ./uploads-backup
```

### 2. Deploy to Azure

```bash
cd azure
./deploy-to-azure.sh --env production --region eastus --type aci
```

### 3. Import Data to Azure

```bash
# Import MongoDB to Cosmos DB
mongorestore --uri "$(az keyvault secret show --vault-name your-vault --name MongoDB-ConnectionString --query value -o tsv)" ./mongodb-backup

# Import PostgreSQL
PG_HOST=$(az postgres flexible-server show --resource-group librechat-prod --name librechat-pg-server --query fullyQualifiedDomainName -o tsv)
psql -h "$PG_HOST" -U librechat_admin -d librechat < postgres-backup.sql

# Upload files to Blob Storage
az storage blob upload-batch \
    --account-name "your-storage" \
    --destination uploads \
    --source ./uploads-backup
```

---

## 🚀 Next Steps After Deployment

### Immediate (First Day)
1. ✅ Run validation tests from TESTING_AND_VALIDATION_GUIDE.md
2. ✅ Set up monitoring alerts
3. ✅ Configure backups
4. ✅ Document deployment info (save deployment-info.json)

### Short-term (First Week)
1. Configure custom domain name
2. Set up SSL certificate with Application Gateway
3. Enable Azure AD authentication
4. Configure CI/CD pipeline
5. Set up cost alerts

### Long-term (First Month)
1. Implement auto-scaling policies
2. Set up multi-region failover
3. Configure advanced monitoring dashboards
4. Establish backup/restore procedures
5. Create runbook documentation

---

## 🤝 Contributing

Found an issue or have improvements? Please:

1. Document the issue clearly
2. Test your proposed solution
3. Update relevant documentation
4. Submit changes for review

---

## 📞 Support

### Azure Support
- **Portal**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **Documentation**: https://learn.microsoft.com/azure/

### LibreChat Support
- **Discord**: https://discord.librechat.ai
- **GitHub**: https://github.com/danny-avila/LibreChat
- **Docs**: https://www.librechat.ai/docs/

### Emergency Contacts
- Azure On-Call: [Your Support Plan]
- DevOps Team: [Your Team]
- Security Team: [Your Security Team]

---

## 📄 License

This deployment package follows the same license as LibreChat (MIT License).

---

## ✨ Credits

- **LibreChat**: [Danny Avila](https://github.com/danny-avila)
- **Agentic Analytics**: Custom implementation for tech stack analysis
- **Playwright E2E**: Microsoft Playwright with VNC integration
- **Azure Deployment**: Optimized for Azure Cloud Platform

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Tested With**: LibreChat v0.8.1-rc1, Azure CLI 2.56.0, Docker 24.0.7

---

## 🎯 Quick Reference Commands

```bash
# Deploy to Azure
./deploy-to-azure.sh --env production --region eastus --type aci

# Check deployment status
az container list --resource-group librechat-prod --output table

# View logs
az container logs --resource-group librechat-prod --name librechat-app --tail 100

# Run tests
./test-deployment.sh librechat-prod your-librechat-url

# Access VNC
vncviewer "$(az container show --resource-group librechat-prod --name playwright-e2e --query 'ipAddress.fqdn' -o tsv):5900"

# Get deployment info
cat deployment-info.json

# Clean up (WARNING: Deletes everything!)
az group delete --name librechat-prod --yes --no-wait
```

---

**Ready to deploy? Start with AZURE_DEPLOYMENT_GUIDE.md!** 🚀
