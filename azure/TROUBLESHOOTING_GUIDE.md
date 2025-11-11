# Azure Troubleshooting Guide

Common issues, solutions, and debugging procedures for LibreChat + Agentic Analytics + Playwright E2E on Azure.

---

## 📋 Table of Contents

1. [Deployment Issues](#deployment-issues)
2. [Application Issues](#application-issues)
3. [Database Issues](#database-issues)
4. [Storage Issues](#storage-issues)
5. [Network Issues](#network-issues)
6. [Performance Issues](#performance-issues)
7. [E2E Testing Issues](#e2e-testing-issues)
8. [Authentication Issues](#authentication-issues)
9. [Monitoring Issues](#monitoring-issues)
10. [Cost Issues](#cost-issues)

---

## Deployment Issues

### Issue 1: Container Instance Won't Start

**Symptoms:**
- Container status shows "Failed" or "Terminated"
- Application not accessible

**Diagnosis:**
```bash
# Check container logs
az container logs \
  --resource-group librechat-rg \
  --name librechat-app

# Check container events
az container show \
  --resource-group librechat-rg \
  --name librechat-app \
  --query "containers[0].instanceView.events"
```

**Common Causes & Solutions:**

1. **Missing environment variables**
   ```bash
   # Verify all required env vars are set
   az container show \
     --resource-group librechat-rg \
     --name librechat-app \
     --query "containers[0].environmentVariables"
   ```
   **Solution**: Add missing variables, recreate container

2. **Image pull failure**
   - Error: "Failed to pull image"
   - **Solution**: Check ACR credentials, image name, network connectivity
   ```bash
   # Verify ACR login
   az acr login --name <registry-name>
   
   # Check image exists
   az acr repository show-tags --name <registry-name> --repository librechat
   ```

3. **Port conflict**
   - Error: "Port already in use"
   - **Solution**: Use different port or remove conflicting container

4. **Resource limits too low**
   - Error: "OOMKilled" or "CPU limit exceeded"
   - **Solution**: Increase CPU/memory limits
   ```bash
   az container create \
     --cpu 2 \
     --memory 4
   ```

### Issue 2: Database Connection Timeout During Deployment

**Symptoms:**
- Application starts but can't connect to database
- Error: "ETIMEDOUT" or "Connection refused"

**Diagnosis:**
```bash
# Test connection from your machine
psql -h <postgres-host>.postgres.database.azure.com \
     -U <username> \
     -d postgres \
     -c "SELECT version();"

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group librechat-rg \
  --name <server-name>
```

**Solutions:**

1. **Add firewall rule for container subnet**
   ```bash
   az postgres flexible-server firewall-rule create \
     --resource-group librechat-rg \
     --name <server-name> \
     --rule-name allow-container-subnet \
     --start-ip-address 10.0.3.0 \
     --end-ip-address 10.0.3.255
   ```

2. **Enable private endpoint** (recommended for production)
   ```bash
   az network private-endpoint create \
     --name postgres-private-endpoint \
     --resource-group librechat-rg \
     --vnet-name librechat-vnet \
     --subnet database-subnet \
     --private-connection-resource-id <postgres-resource-id> \
     --group-id postgresqlServer \
     --connection-name postgres-connection
   ```

3. **Verify connection string format**
   ```
   postgres://<username>:<password>@<host>:5432/<database>?sslmode=require
   ```

### Issue 3: Docker Compose Fails on Azure

**Symptoms:**
- `docker-compose up` fails with various errors

**Common Issues:**

1. **Missing .env file**
   ```bash
   # Copy template
   cp azure/.env.azure.example .env.azure
   
   # Edit with actual values
   nano .env.azure
   ```

2. **Network not created**
   ```bash
   # Create network manually
   docker network create librechat-network
   ```

3. **Volume mount permissions**
   ```bash
   # Fix permissions
   sudo chown -R $(whoami):$(whoami) ./uploads ./logs
   chmod 755 ./uploads ./logs
   ```

---

## Application Issues

### Issue 1: 500 Internal Server Error

**Symptoms:**
- API returns 500 errors
- Chat interface shows "Something went wrong"

**Diagnosis:**
```bash
# Check application logs
az container logs --resource-group librechat-rg --name librechat-app --tail 100

# Check Application Insights
# Navigate to Application Insights → Failures → 500 errors
```

**Common Causes:**

1. **Missing API keys**
   - Check OpenAI/Anthropic API key in environment variables
   - Verify key is valid: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

2. **Database connection lost**
   - Check MongoDB/PostgreSQL connection
   - Verify connection pool settings
   ```javascript
   // Increase connection pool size
   mongoose.connect(process.env.MONGO_URI, {
     maxPoolSize: 50,
     minPoolSize: 10,
   });
   ```

3. **Memory leak**
   - Container OOM killed
   - **Solution**: Increase memory limit or investigate leak
   ```bash
   # Check memory usage
   az monitor metrics list \
     --resource <container-id> \
     --metric "MemoryUsage" \
     --start-time 2025-11-09T00:00:00Z \
     --interval PT1H
   ```

### Issue 2: Slow Response Times

**Symptoms:**
- Chat messages take > 5 seconds to respond
- API latency > 3 seconds

**Diagnosis:**
```kql
// Application Insights query
requests
| where timestamp > ago(1h)
| summarize avg(duration), percentile(duration, 95) by operation_Name
| order by avg_duration desc
```

**Solutions:**

1. **Enable Redis caching**
   ```javascript
   // Cache frequently accessed data
   const cachedData = await redis.get(key);
   if (cachedData) return JSON.parse(cachedData);
   
   const data = await database.query(...);
   await redis.setex(key, 3600, JSON.stringify(data));
   ```

2. **Optimize database queries**
   ```sql
   -- Add indexes
   CREATE INDEX idx_user_id ON conversations(user_id);
   CREATE INDEX idx_created_at ON messages(created_at);
   
   -- Analyze slow queries
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 20;
   ```

3. **Scale up container resources**
   ```bash
   az container create \
     --cpu 4 \
     --memory 8
   ```

### Issue 3: File Upload Fails

**Symptoms:**
- File upload returns error
- Files not appearing in blob storage

**Diagnosis:**
```bash
# Check storage account access
az storage account show \
  --name <storage-account> \
  --query "networkRuleSet.defaultAction"

# List containers
az storage container list \
  --account-name <storage-account> \
  --auth-mode login
```

**Solutions:**

1. **CORS not configured**
   ```bash
   az storage cors add \
     --services b \
     --methods GET POST PUT \
     --origins '*' \
     --allowed-headers '*' \
     --exposed-headers '*' \
     --max-age 3600 \
     --account-name <storage-account>
   ```

2. **Container doesn't exist**
   ```bash
   az storage container create \
     --name uploads \
     --account-name <storage-account> \
     --public-access off
   ```

3. **File size limit exceeded**
   - Increase `FILE_UPLOAD_SIZE_LIMIT` in .env
   - Default Azure Blob limit: 4.77 TB per file

---

## Database Issues

### Issue 1: PostgreSQL Connection Pool Exhausted

**Symptoms:**
- Error: "Too many connections"
- Application hangs

**Diagnosis:**
```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- View connections by database
SELECT datname, count(*) 
FROM pg_stat_activity 
GROUP BY datname;
```

**Solutions:**

1. **Increase max connections**
   ```bash
   az postgres flexible-server parameter set \
     --resource-group librechat-rg \
     --server-name <server-name> \
     --name max_connections \
     --value 200
   ```

2. **Fix connection leaks in application**
   ```javascript
   // Always close connections
   try {
     const result = await pool.query('SELECT * FROM users');
     return result.rows;
   } finally {
     // Connection automatically returned to pool with node-postgres
   }
   ```

3. **Use connection pooler (PgBouncer)**
   ```bash
   # Install PgBouncer container
   docker run -d \
     --name pgbouncer \
     -e DATABASES_HOST=<postgres-host> \
     -e DATABASES_PORT=5432 \
     -e DATABASES_USER=<username> \
     -e DATABASES_PASSWORD=<password> \
     -e POOL_MODE=transaction \
     -e MAX_CLIENT_CONN=1000 \
     -e DEFAULT_POOL_SIZE=25 \
     -p 6432:6432 \
     edoburu/pgbouncer
   ```

### Issue 2: MongoDB Slow Queries

**Symptoms:**
- Queries taking > 1 second
- High CPU usage on Cosmos DB

**Diagnosis:**
```javascript
// Enable profiling
db.setProfilingLevel(2);

// View slow queries
db.system.profile.find({ millis: { $gt: 1000 } }).sort({ ts: -1 }).limit(10);
```

**Solutions:**

1. **Add indexes**
   ```javascript
   // Create compound index
   db.conversations.createIndex({ userId: 1, createdAt: -1 });
   
   // Create text index for search
   db.messages.createIndex({ content: "text" });
   ```

2. **Optimize queries**
   ```javascript
   // Bad: Fetch all then filter in app
   const allDocs = await db.collection.find({}).toArray();
   const filtered = allDocs.filter(doc => doc.userId === userId);
   
   // Good: Filter in database
   const filtered = await db.collection.find({ userId }).toArray();
   ```

3. **Increase RU/s (Cosmos DB)**
   ```bash
   az cosmosdb sql database throughput update \
     --account-name <account-name> \
     --resource-group librechat-rg \
     --name LibreChat \
     --throughput 1000
   ```

### Issue 3: Redis Cache Evictions

**Symptoms:**
- High cache miss rate
- "maxmemory" errors

**Diagnosis:**
```bash
# Connect to Redis
redis-cli -h <redis-host> -p 6380 --tls -a <password>

# Check memory usage
INFO memory

# Check eviction stats
INFO stats | grep evicted
```

**Solutions:**

1. **Increase cache size**
   ```bash
   az redis update \
     --resource-group librechat-rg \
     --name <redis-name> \
     --sku Standard \
     --vm-size C1  # 1 GB → 2.5 GB
   ```

2. **Configure eviction policy**
   ```bash
   az redis patch-schedule set \
     --resource-group librechat-rg \
     --name <redis-name> \
     --schedule-entries '[{"dayOfWeek":"Sunday","startHourUtc":2,"maintenanceWindow":"PT5H"}]'
   ```

3. **Optimize cache usage**
   ```javascript
   // Set expiration on all keys
   await redis.setex(key, 3600, value);  // 1 hour TTL
   
   // Use shorter TTL for frequently changing data
   await redis.setex(`session:${userId}`, 1800, sessionData);  // 30 min
   ```

---

## Storage Issues

### Issue 1: Blob Not Found (404)

**Symptoms:**
- Images/files return 404
- Broken image links in chat

**Diagnosis:**
```bash
# List blobs in container
az storage blob list \
  --container-name uploads \
  --account-name <storage-account> \
  --output table

# Check blob exists
az storage blob exists \
  --container-name uploads \
  --name <blob-name> \
  --account-name <storage-account>
```

**Solutions:**

1. **Fix blob path in application**
   ```javascript
   // Ensure correct URL format
   const blobUrl = `https://${accountName}.blob.core.windows.net/${containerName}/${blobName}`;
   ```

2. **Check container public access**
   ```bash
   # Make container publicly readable (for avatars)
   az storage container set-permission \
     --name avatars \
     --public-access blob \
     --account-name <storage-account>
   ```

3. **Generate SAS token for private blobs**
   ```javascript
   const { generateBlobSASQueryParameters, BlobSASPermissions } = require('@azure/storage-blob');
   
   const sasToken = generateBlobSASQueryParameters({
     containerName: 'uploads',
     blobName: fileName,
     permissions: BlobSASPermissions.parse('r'),
     startsOn: new Date(),
     expiresOn: new Date(new Date().valueOf() + 3600 * 1000),
   }, sharedKeyCredential).toString();
   
   const urlWithSAS = `${blobUrl}?${sasToken}`;
   ```

### Issue 2: Upload Timeout

**Symptoms:**
- Large file uploads fail
- Timeout errors after 60 seconds

**Solutions:**

1. **Increase upload timeout**
   ```javascript
   const { BlobServiceClient } = require('@azure/storage-blob');
   
   const blobServiceClient = BlobServiceClient.fromConnectionString(
     process.env.AZURE_STORAGE_CONNECTION_STRING
   );
   
   const blockBlobClient = containerClient.getBlockBlobClient(fileName);
   await blockBlobClient.uploadData(buffer, {
     blockSize: 4 * 1024 * 1024, // 4MB blocks
     concurrency: 20,
     onProgress: (ev) => console.log(ev),
     timeout: 300000, // 5 minutes
   });
   ```

2. **Use chunked upload for large files**
   ```javascript
   const uploadStream = blockBlobClient.uploadStream(
     buffer.byteLength,
     4 * 1024 * 1024, // 4MB chunks
     20 // concurrency
   );
   ```

### Issue 3: Storage Account Throttling

**Symptoms:**
- HTTP 503 "Server Busy" errors
- High latency for blob operations

**Diagnosis:**
```kql
AzureMetrics
| where ResourceProvider == "MICROSOFT.STORAGE"
| where MetricName == "Transactions"
| summarize sum(Total) by bin(TimeGenerated, 5m), ResponseType
| render timechart
```

**Solutions:**

1. **Implement retry logic with exponential backoff**
   ```javascript
   const { BlobServiceClient } = require('@azure/storage-blob');
   const { exponentialRetryPolicy } = require('@azure/storage-blob');
   
   const retryOptions = {
     maxRetries: 4,
     retryDelayInMs: 4000,
     maxRetryDelayInMs: 120000,
   };
   ```

2. **Use Premium tier for high IOPS**
   ```bash
   az storage account create \
     --name <account-name> \
     --resource-group librechat-rg \
     --location eastus \
     --sku Premium_LRS \
     --kind BlockBlobStorage
   ```

3. **Distribute load across multiple storage accounts**

---

## Network Issues

### Issue 1: Cannot Connect to Application

**Symptoms:**
- Application not accessible from browser
- Timeout when accessing public IP

**Diagnosis:**
```bash
# Check container is running
az container show \
  --resource-group librechat-rg \
  --name librechat-app \
  --query "instanceView.state"

# Check public IP
az container show \
  --resource-group librechat-rg \
  --name librechat-app \
  --query "ipAddress.ip"

# Test connectivity
curl -v http://<public-ip>:3080
```

**Solutions:**

1. **Check NSG rules**
   ```bash
   az network nsg rule list \
     --resource-group librechat-rg \
     --nsg-name librechat-nsg \
     --output table
   
   # Add rule if missing
   az network nsg rule create \
     --resource-group librechat-rg \
     --nsg-name librechat-nsg \
     --name allow-http \
     --priority 100 \
     --destination-port-ranges 3080 \
     --protocol Tcp \
     --access Allow
   ```

2. **Verify container port mapping**
   ```bash
   az container show \
     --resource-group librechat-rg \
     --name librechat-app \
     --query "ipAddress.ports"
   ```

3. **Check application is listening**
   ```bash
   # Exec into container
   az container exec \
     --resource-group librechat-rg \
     --name librechat-app \
     --exec-command "/bin/sh"
   
   # Inside container
   netstat -tuln | grep 3080
   curl localhost:3080
   ```

### Issue 2: Intermittent Connection Drops

**Symptoms:**
- Websocket connections dropping
- Chat messages fail randomly

**Solutions:**

1. **Increase session affinity**
   ```bash
   # For App Service
   az webapp update \
     --resource-group librechat-rg \
     --name librechat-app \
     --client-affinity-enabled true
   ```

2. **Configure load balancer timeout**
   ```bash
   az network lb rule update \
     --resource-group librechat-rg \
     --lb-name librechat-lb \
     --name http-rule \
     --idle-timeout 30  # minutes
   ```

3. **Implement websocket reconnection**
   ```javascript
   // Client-side reconnection
   let socket;
   const connect = () => {
     socket = new WebSocket('wss://...');
     socket.onclose = () => {
       console.log('Disconnected, reconnecting in 5s...');
       setTimeout(connect, 5000);
     };
   };
   connect();
   ```

---

## Performance Issues

### Issue 1: High CPU Usage

**Diagnosis:**
```kql
Perf
| where ObjectName == "K8SContainer"
| where CounterName == "cpuUsageNanoCores"
| summarize avg(CounterValue) by bin(TimeGenerated, 5m)
| render timechart
```

**Solutions:**

1. **Profile application**
   ```javascript
   // Use Node.js profiler
   node --prof server.js
   
   // Analyze profile
   node --prof-process isolate-0x*.log > profile.txt
   ```

2. **Optimize hot paths**
   - Cache expensive computations
   - Use database indexes
   - Implement pagination
   - Lazy load data

3. **Scale horizontally**
   ```bash
   # Add more container instances behind load balancer
   az container create --name librechat-app-2 ...
   ```

### Issue 2: Memory Leaks

**Diagnosis:**
```javascript
// Take heap snapshots
const v8 = require('v8');
const fs = require('fs');

const snapshot = v8.writeHeapSnapshot();
console.log(`Heap snapshot written to ${snapshot}`);
```

**Solutions:**

1. **Use memory profiler**
   ```bash
   npm install -g clinic
   clinic doctor -- node server.js
   ```

2. **Fix common leaks**
   ```javascript
   // Bad: Event listener leak
   setInterval(() => {
     socket.on('message', handler);
   }, 1000);
   
   // Good: Remove listeners
   const interval = setInterval(() => {
     socket.on('message', handler);
   }, 1000);
   
   // Cleanup
   clearInterval(interval);
   socket.removeListener('message', handler);
   ```

3. **Restart containers periodically**
   ```bash
   # Use Azure Functions to restart daily
   az container restart \
     --resource-group librechat-rg \
     --name librechat-app
   ```

---

## E2E Testing Issues

### Issue 1: Playwright Tests Timeout

**Symptoms:**
- Tests fail with timeout errors
- Steps hang indefinitely

**Diagnosis:**
```javascript
// Check test logs
cat e2e/test-manual-upload.txt | grep "timeout"

// Check browser console
page.on('console', msg => console.log('Browser:', msg.text()));
```

**Solutions:**

1. **Increase timeouts**
   ```javascript
   // playwright.config.ts
   export default {
     timeout: 60000, // 60 seconds per test
     expect: {
       timeout: 10000, // 10 seconds per assertion
     },
   };
   ```

2. **Wait for network idle**
   ```javascript
   await page.waitForLoadState('networkidle', { timeout: 30000 });
   ```

3. **Add explicit waits**
   ```javascript
   // Wait for element before clicking
   await page.waitForSelector('button[data-testid="send"]', { timeout: 10000 });
   await page.click('button[data-testid="send"]');
   ```

### Issue 2: Screenshots Not Captured

**Symptoms:**
- Screenshot directory empty
- No visual evidence of failures

**Solutions:**

1. **Check permissions**
   ```bash
   chmod 755 e2e/test-screenshots
   ls -la e2e/test-screenshots
   ```

2. **Verify screenshot function**
   ```javascript
   async function takeScreenshot(name) {
     const path = `test-screenshots/${Date.now()}-${name}.png`;
     await page.screenshot({ path, fullPage: false });
     console.log(`   📸 Screenshot: ${path}`);
   }
   ```

3. **Configure Playwright to save on failure**
   ```javascript
   // playwright.config.ts
   use: {
     screenshot: 'only-on-failure',
     video: 'retain-on-failure',
   }
   ```

### Issue 3: Headless Mode Issues

**Symptoms:**
- Tests pass in headed mode, fail in headless
- Different rendering in headless

**Solutions:**

1. **Use Xvfb for virtual display**
   ```bash
   # Install Xvfb
   apt-get install -y xvfb
   
   # Run with virtual display
   xvfb-run --auto-servernum --server-args="-screen 0 1280x960x24" \
     node e2e/single_window_runner.js
   ```

2. **Match headed configuration**
   ```javascript
   const browser = await chromium.launch({
     headless: true,
     args: [
       '--disable-gpu',
       '--no-sandbox',
       '--disable-dev-shm-usage',
       '--disable-setuid-sandbox',
     ],
   });
   ```

3. **Debug with screenshots**
   ```javascript
   // Take screenshot at each step in headless mode
   if (process.env.HEADLESS === 'true') {
     await takeScreenshot(stepName);
   }
   ```

---

## Authentication Issues

### Issue 1: OAuth Redirect Loop

**Symptoms:**
- Infinite redirect after OAuth login
- Error: "state mismatch"

**Solutions:**

1. **Check callback URL**
   - Must exactly match registered OAuth app
   - Include correct protocol (https://)
   - No trailing slash

2. **Verify session storage**
   ```javascript
   // Ensure Redis/MongoDB is accessible
   const session = require('express-session');
   const RedisStore = require('connect-redis')(session);
   
   app.use(session({
     store: new RedisStore({ client: redisClient }),
     secret: process.env.SESSION_SECRET,
     resave: false,
     saveUninitialized: false,
   }));
   ```

3. **Check cookie settings**
   ```javascript
   app.use(session({
     cookie: {
       secure: true,  // HTTPS only
       httpOnly: true,
       sameSite: 'lax',  // Allow OAuth redirects
       maxAge: 24 * 60 * 60 * 1000,  // 24 hours
     },
   }));
   ```

### Issue 2: JWT Token Expired

**Symptoms:**
- Error: "jwt expired"
- User logged out unexpectedly

**Solutions:**

1. **Increase token expiration**
   ```javascript
   const token = jwt.sign(
     { userId: user.id },
     process.env.JWT_SECRET,
     { expiresIn: '7d' }  // 7 days instead of 24h
   );
   ```

2. **Implement token refresh**
   ```javascript
   // Generate refresh token
   const refreshToken = jwt.sign(
     { userId: user.id, type: 'refresh' },
     process.env.JWT_REFRESH_SECRET,
     { expiresIn: '30d' }
   );
   
   // Store refresh token in database
   await db.refreshTokens.insert({ userId: user.id, token: refreshToken });
   ```

3. **Auto-refresh on expiration**
   ```javascript
   // Frontend: Refresh token before expiration
   axios.interceptors.response.use(
     response => response,
     async error => {
       if (error.response?.status === 401) {
         const newToken = await refreshAccessToken();
         error.config.headers['Authorization'] = `Bearer ${newToken}`;
         return axios.request(error.config);
       }
       return Promise.reject(error);
     }
   );
   ```

---

## Monitoring Issues

### Issue 1: No Data in Application Insights

**Diagnosis:**
```bash
# Verify instrumentation key
echo $APPINSIGHTS_INSTRUMENTATION_KEY

# Check network connectivity to Application Insights
curl -v https://dc.services.visualstudio.com/v2/track
```

**Solutions:**

1. **Verify SDK initialization**
   ```javascript
   const appInsights = require('applicationinsights');
   appInsights.setup(process.env.APPINSIGHTS_INSTRUMENTATION_KEY);
   appInsights.start();
   console.log('✅ Application Insights started');
   ```

2. **Check sampling configuration**
   ```javascript
   // Ensure sampling is not too aggressive
   appInsights.defaultClient.config.samplingPercentage = 100; // Temporarily
   ```

3. **Manually flush telemetry**
   ```javascript
   // Force flush before shutdown
   process.on('SIGTERM', async () => {
     await appInsights.defaultClient.flush();
     process.exit(0);
   });
   ```

### Issue 2: Log Queries Return No Results

**Solutions:**

1. **Check time range**
   ```kql
   // Explicitly set time range
   ContainerInstanceLog_CL
   | where TimeGenerated > ago(24h)
   ```

2. **Verify table name**
   ```kql
   // List all tables
   search *
   | distinct $table
   ```

3. **Wait for ingestion (5-10 minutes)**

---

## Cost Issues

### Issue 1: Unexpectedly High Costs

**Diagnosis:**
```bash
# View cost breakdown
az consumption usage list \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --query "[].{Service:meterName,Cost:pretaxCost}" \
  --output table
```

**Solutions:**

1. **Identify expensive resources**
   ```kql
   AzureCostManagement
   | where TimeGenerated > ago(30d)
   | summarize TotalCost = sum(todouble(PreTaxCost)) by ResourceId
   | order by TotalCost desc
   | limit 20
   ```

2. **Right-size resources**
   - Downgrade oversized databases
   - Use spot instances for dev/test
   - Stop non-production environments overnight

3. **Enable cost alerts**
   ```bash
   az consumption budget create \
     --resource-group librechat-rg \
     --budget-name monthly-budget \
     --amount 500 \
     --time-grain Monthly \
     --notification enabled=true threshold=80
   ```

---

## Emergency Procedures

### Complete System Down

1. **Check Azure Service Health**
   - https://status.azure.com

2. **Verify all resources running**
   ```bash
   az resource list --resource-group librechat-rg --query "[].{Name:name,Type:type,State:properties.provisioningState}" --output table
   ```

3. **Restart all services**
   ```bash
   # Restart containers
   az container restart --resource-group librechat-rg --name librechat-app
   az container restart --resource-group librechat-rg --name agentic-analytics
   az container restart --resource-group librechat-rg --name playwright-e2e
   ```

4. **Check database connectivity**
   ```bash
   psql -h <postgres-host> -U <user> -d postgres -c "SELECT 1;"
   mongosh "mongodb://<connection-string>" --eval "db.stats()"
   redis-cli -h <redis-host> -p 6380 --tls -a <password> PING
   ```

5. **Review logs for errors**
   ```bash
   az monitor activity-log list --resource-group librechat-rg --max-events 50
   ```

6. **Escalate to Azure Support**
   - Open support ticket: https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade

---

## Getting Help

### Internal Resources
- **Runbook**: `AZURE_DEPLOYMENT_GUIDE.md`
- **Monitoring**: `MONITORING_AND_OBSERVABILITY.md`
- **Deployment**: `DEPLOYMENT_CHECKLIST.md`

### External Resources
- **Azure Documentation**: https://docs.microsoft.com/azure
- **LibreChat GitHub**: https://github.com/danny-avila/LibreChat/issues
- **Playwright Docs**: https://playwright.dev/docs/intro
- **Stack Overflow**: Tag questions with `azure`, `librechat`, `playwright`

### Support Channels
- **Azure Support Portal**: https://portal.azure.com
- **LibreChat Discord**: https://discord.gg/librechat
- **Internal Slack**: #librechat-azure

---

**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Maintainer**: DevOps Team
