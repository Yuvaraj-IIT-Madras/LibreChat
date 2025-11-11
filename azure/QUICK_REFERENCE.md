# Azure Deployment - Quick Reference Card

**One-page reference for common Azure operations**

---

## 🚀 Initial Deployment

```bash
# Quick start (15 minutes)
cd /home/yuvaraj/Projects/LibreChat/azure
cp .env.azure.example .env.azure
nano .env.azure  # Fill in your values
./deploy-to-azure.sh --env production --region eastus --type aci
```

---

## 📊 Status Checks

```bash
# Set variables
export RG="librechat-prod"

# All container instances
az container list --resource-group $RG --output table

# Specific container status
az container show --resource-group $RG --name librechat-app --query "instanceView.state" -o tsv

# Database status
az postgres flexible-server show --resource-group $RG --name librechat-pg-server --query "{Name:name,State:state}" -o table
az cosmosdb show --resource-group $RG --name librechat-cosmos --query "{Name:name,State:provisioningState}" -o table
az redis show --resource-group $RG --name librechat-redis --query "{Name:name,State:provisioningState}" -o table

# Get LibreChat URL
az container show --resource-group $RG --name librechat-app --query "ipAddress.fqdn" -o tsv
```

---

## 📝 Logs & Debugging

```bash
# Container logs (last 100 lines)
az container logs --resource-group $RG --name librechat-app --tail 100

# Follow logs in real-time
az container logs --resource-group $RG --name librechat-app --follow

# All container events
az container show --resource-group $RG --name librechat-app --query "instanceView.events" -o table

# Application Insights logs (last hour)
az monitor app-insights events show \
    --app librechat-insights \
    --resource-group $RG \
    --type traces \
    --start-time "1 hour ago" \
    --output table
```

---

## 🔄 Container Management

```bash
# Restart container
az container restart --resource-group $RG --name librechat-app

# Stop container
az container stop --resource-group $RG --name librechat-app

# Delete and recreate container
az container delete --resource-group $RG --name librechat-app --yes
# Then redeploy with deploy-to-azure.sh

# Update container image
docker build -t yourregistry.azurecr.io/librechat:latest .
docker push yourregistry.azurecr.io/librechat:latest
az container create --resource-group $RG --name librechat-app \
    --image yourregistry.azurecr.io/librechat:latest \
    --restart-policy Always
```

---

## 🗄️ Database Operations

```bash
# PostgreSQL connection
PG_HOST=$(az postgres flexible-server show --resource-group $RG --name librechat-pg-server --query "fullyQualifiedDomainName" -o tsv)
psql -h $PG_HOST -U librechat_admin -d librechat

# List backups
az postgres flexible-server backup list --resource-group $RG --server-name librechat-pg-server --output table

# Restore to point in time
az postgres flexible-server restore \
    --resource-group $RG \
    --name librechat-pg-restored \
    --source-server librechat-pg-server \
    --restore-time "2024-01-15T10:00:00Z"

# Redis connection info
az redis show --resource-group $RG --name librechat-redis --query "{HostName:hostName,Port:sslPort}" -o table
az redis list-keys --resource-group $RG --name librechat-redis --query "primaryKey" -o tsv

# Cosmos DB connection string
az cosmosdb keys list --resource-group $RG --name librechat-cosmos --type connection-strings --query "connectionStrings[0].connectionString" -o tsv
```

---

## 🧪 Testing

```bash
# Health check
LIBRECHAT_URL=$(az container show --resource-group $RG --name librechat-app --query "ipAddress.fqdn" -o tsv)
curl -f "http://${LIBRECHAT_URL}:3080/api/health"

# Full test suite
cd /home/yuvaraj/Projects/LibreChat
./azure/test-deployment.sh $RG $LIBRECHAT_URL

# VNC access to E2E tests
VNC_URL=$(az container show --resource-group $RG --name playwright-e2e --query "ipAddress.fqdn" -o tsv)
echo "VNC: vnc://${VNC_URL}:5900"
echo "Web VNC: http://${VNC_URL}:6080"
vncviewer "${VNC_URL}:5900"  # Password: librechat

# Download E2E screenshots
STORAGE_ACCOUNT=$(az storage account list --resource-group $RG --query "[0].name" -o tsv)
az storage blob download-batch \
    --account-name $STORAGE_ACCOUNT \
    --source screenshots \
    --destination ./e2e-screenshots/ \
    --pattern "e2e-tests/*.png"
```

---

## 🔒 Security

```bash
# List secrets in Key Vault
KEY_VAULT=$(az keyvault list --resource-group $RG --query "[0].name" -o tsv)
az keyvault secret list --vault-name $KEY_VAULT --output table

# Get specific secret
az keyvault secret show --vault-name $KEY_VAULT --name "OpenAI-ApiKey" --query "value" -o tsv

# Set new secret
az keyvault secret set --vault-name $KEY_VAULT --name "New-Secret" --value "secret-value"

# Network Security Group rules
NSG=$(az network nsg list --resource-group $RG --query "[0].name" -o tsv)
az network nsg rule list --resource-group $RG --nsg-name $NSG --output table

# Security alerts
az security alert list --resource-group $RG --output table
```

---

## 💰 Cost Management

```bash
# Current month costs
az consumption usage list \
    --start-date "$(date -d 'first day of this month' +%Y-%m-%d)" \
    --end-date "$(date +%Y-%m-%d)" \
    --query "[?contains(instanceName,'librechat')].{Resource:instanceName,Cost:pretaxCost}" \
    --output table

# Cost alerts
az consumption budget list --resource-group $RG --output table

# Create cost alert (monthly budget $500)
az consumption budget create \
    --resource-group $RG \
    --budget-name "librechat-monthly" \
    --amount 500 \
    --time-grain Monthly \
    --time-period "$(date -d 'first day of this month' +%Y-%m-%d)" \
    --category Cost

# Azure Advisor cost recommendations
az advisor recommendation list --category Cost --resource-group $RG --output table

# Right-sizing recommendations
az monitor metrics list \
    --resource "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.ContainerInstance/containerGroups/librechat-app" \
    --metric "CpuUsage,MemoryUsage" \
    --start-time "$(date -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)"
```

---

## 📊 Monitoring

```bash
# Application Insights metrics
az monitor app-insights metrics show \
    --app librechat-insights \
    --resource-group $RG \
    --metric requests/count \
    --interval PT1H

# Recent exceptions
az monitor app-insights events show \
    --app librechat-insights \
    --resource-group $RG \
    --type exceptions \
    --start-time "1 hour ago" \
    --output table

# Create alert rule (high error rate)
az monitor metrics alert create \
    --name "high-error-rate" \
    --resource-group $RG \
    --scopes "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Insights/components/librechat-insights" \
    --condition "count exceptions/count > 10" \
    --window-size 5m \
    --evaluation-frequency 1m \
    --action email your-email@example.com
```

---

## 🔄 Scaling

```bash
# Container Instances (recreate with more resources)
az container create \
    --resource-group $RG \
    --name librechat-app \
    --cpu 8 \
    --memory 16

# PostgreSQL (scale up/down)
az postgres flexible-server update \
    --resource-group $RG \
    --name librechat-pg-server \
    --sku-name Standard_D4s_v3 \
    --tier GeneralPurpose

# Redis (scale to higher tier)
az redis update \
    --resource-group $RG \
    --name librechat-redis \
    --sku Premium \
    --vm-size P2

# Cosmos DB (increase RU/s)
az cosmosdb sql database throughput update \
    --resource-group $RG \
    --account-name librechat-cosmos \
    --name LibreChat \
    --throughput 2000
```

---

## 🔧 Troubleshooting

```bash
# Container won't start
az container show --resource-group $RG --name librechat-app --query "instanceView"
az container logs --resource-group $RG --name librechat-app --tail 200

# Database connection issues
az container exec \
    --resource-group $RG \
    --name librechat-app \
    --exec-command "/bin/bash -c 'apt-get update && apt-get install -y postgresql-client && psql -h DB_HOST -U DB_USER -d DB_NAME -c \"SELECT 1;\"'"

# Network connectivity test
az container exec \
    --resource-group $RG \
    --name librechat-app \
    --exec-command "/bin/bash -c 'apt-get update && apt-get install -y curl && curl -v http://target-service:port'"

# Check resource quota
az vm list-usage --location eastus --output table | grep -i "Container"

# Azure service health
az rest --method get --uri "https://management.azure.com/subscriptions/SUBSCRIPTION_ID/providers/Microsoft.ResourceHealth/availabilityStatuses?api-version=2020-05-01" --query "value[?properties.availabilityState=='Unavailable']"
```

---

## 🗑️ Cleanup

```bash
# Stop all containers (keep data)
for container in $(az container list --resource-group $RG --query "[].name" -o tsv); do
    az container stop --resource-group $RG --name $container
done

# Delete specific container
az container delete --resource-group $RG --name librechat-app --yes

# Delete entire resource group (WARNING: DELETES EVERYTHING!)
az group delete --name $RG --yes --no-wait

# Verify deletion
az group exists --name $RG
```

---

## 📦 Backup & Restore

```bash
# PostgreSQL manual backup
PG_HOST=$(az postgres flexible-server show --resource-group $RG --name librechat-pg-server --query "fullyQualifiedDomainName" -o tsv)
pg_dump -h $PG_HOST -U librechat_admin -d librechat > backup-$(date +%Y%m%d).sql

# Restore PostgreSQL
psql -h $PG_HOST -U librechat_admin -d librechat < backup-20240115.sql

# Blob Storage backup (create snapshot)
STORAGE_ACCOUNT=$(az storage account list --resource-group $RG --query "[0].name" -o tsv)
az storage blob snapshot --account-name $STORAGE_ACCOUNT --container-name data --name important-file.db

# Download all blob storage
az storage blob download-batch \
    --account-name $STORAGE_ACCOUNT \
    --source data \
    --destination ./backup/

# Upload backup to blob storage
az storage blob upload-batch \
    --account-name $STORAGE_ACCOUNT \
    --destination data \
    --source ./backup/
```

---

## 🔐 Secret Rotation

```bash
# Rotate JWT secret
NEW_JWT_SECRET=$(openssl rand -hex 32)
az keyvault secret set --vault-name $KEY_VAULT --name "JWT-Secret" --value "$NEW_JWT_SECRET"

# Update container with new secret
az container restart --resource-group $RG --name librechat-app

# Rotate database password
NEW_DB_PASSWORD=$(openssl rand -base64 24)
az postgres flexible-server update \
    --resource-group $RG \
    --name librechat-pg-server \
    --admin-password "$NEW_DB_PASSWORD"
az keyvault secret set --vault-name $KEY_VAULT --name "PostgreSQL-Password" --value "$NEW_DB_PASSWORD"

# Rotate Redis key
az redis regenerate-keys --resource-group $RG --name librechat-redis --key-type Primary
NEW_REDIS_KEY=$(az redis list-keys --resource-group $RG --name librechat-redis --query "primaryKey" -o tsv)
az keyvault secret set --vault-name $KEY_VAULT --name "Redis-Key" --value "$NEW_REDIS_KEY"
```

---

## 📱 Mobile Quick Commands

```bash
# One-liner: Get LibreChat URL
az container show -g librechat-prod -n librechat-app --query "ipAddress.fqdn" -o tsv

# One-liner: Check if healthy
curl -sf http://$(az container show -g librechat-prod -n librechat-app --query "ipAddress.fqdn" -o tsv):3080/api/health && echo "✅ Healthy" || echo "❌ Down"

# One-liner: View recent errors
az monitor app-insights events show --app librechat-insights -g librechat-prod --type exceptions --start-time "1 hour ago" --query "[].{Time:timestamp,Error:exception.outerMessage}" -o table

# One-liner: Today's cost
az consumption usage list --start-date $(date +%Y-%m-%d) --end-date $(date +%Y-%m-%d) --query "[?contains(instanceName,'librechat')].{Resource:instanceName,Cost:pretaxCost}" -o table

# One-liner: Restart all containers
for c in $(az container list -g librechat-prod --query "[].name" -o tsv); do az container restart -g librechat-prod -n $c & done; wait
```

---

## 🎯 Performance Tuning

```bash
# Check current resource utilization
az monitor metrics list \
    --resource "/subscriptions/SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.ContainerInstance/containerGroups/librechat-app" \
    --metric "CpuUsage,MemoryUsage" \
    --start-time "$(date -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)" \
    --interval PT5M \
    --output table

# PostgreSQL performance insights
az postgres flexible-server show --resource-group $RG --name librechat-pg-server --query "{SKU:sku.name,Storage:storage.storageSizeGB,IOPS:storage.iops}"

# Enable query store (PostgreSQL)
az postgres flexible-server parameter set \
    --resource-group $RG \
    --server-name librechat-pg-server \
    --name pg_qs.query_capture_mode \
    --value TOP

# Redis cache hit rate
az redis show-statistics --resource-group $RG --name librechat-redis --query "cacheHitRate"
```

---

## 🌐 Networking

```bash
# Get all IP addresses
az container list --resource-group $RG --query "[].{Name:name,IP:ipAddress.ip,FQDN:ipAddress.fqdn}" -o table

# Whitelist IP in PostgreSQL firewall
az postgres flexible-server firewall-rule create \
    --resource-group $RG \
    --name librechat-pg-server \
    --rule-name "allow-my-ip" \
    --start-ip-address YOUR_IP \
    --end-ip-address YOUR_IP

# Test connectivity between containers
az container exec \
    --resource-group $RG \
    --name librechat-app \
    --exec-command "/bin/bash -c 'apt-get update && apt-get install -y telnet && telnet postgres-host 5432'"
```

---

## 📚 Quick Links

- **Main Guide**: `azure/AZURE_DEPLOYMENT_GUIDE.md`
- **Testing Guide**: `azure/TESTING_AND_VALIDATION_GUIDE.md`
- **Full Index**: `azure/INDEX.md`
- **README**: `azure/README.md`

---

## 🆘 Emergency Contacts

- **Azure Support Portal**: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade
- **Azure Status**: https://status.azure.com/
- **LibreChat Discord**: https://discord.librechat.ai

---

**Print this reference card and keep it handy! 📄**
