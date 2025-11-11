# Azure Monitoring & Observability Guide

Comprehensive guide for monitoring, logging, and observability for LibreChat + Agentic Analytics + Playwright E2E on Azure.

---

## 📊 Table of Contents

1. [Overview](#overview)
2. [Azure Monitor Setup](#azure-monitor-setup)
3. [Application Insights](#application-insights)
4. [Log Analytics](#log-analytics)
5. [Metrics & Dashboards](#metrics--dashboards)
6. [Alerts & Notifications](#alerts--notifications)
7. [Distributed Tracing](#distributed-tracing)
8. [Custom Monitoring](#custom-monitoring)
9. [Performance Monitoring](#performance-monitoring)
10. [Security Monitoring](#security-monitoring)
11. [Cost Monitoring](#cost-monitoring)
12. [Troubleshooting](#troubleshooting)

---

## Overview

### Monitoring Stack Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Monitor Ecosystem                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐       ┌──────────────────┐            │
│  │  Application     │       │  Log Analytics   │            │
│  │  Insights        │       │  Workspace       │            │
│  └────────┬─────────┘       └────────┬─────────┘            │
│           │                          │                       │
│           ├──────────────────────────┤                       │
│           │                          │                       │
│  ┌────────▼─────────┐       ┌───────▼──────────┐            │
│  │  Metrics         │       │  Logs            │            │
│  │  Explorer        │       │  Query (KQL)     │            │
│  └────────┬─────────┘       └───────┬──────────┘            │
│           │                          │                       │
│           ├──────────────────────────┤                       │
│           │                          │                       │
│  ┌────────▼─────────┐       ┌───────▼──────────┐            │
│  │  Dashboards      │       │  Alerts          │            │
│  └────────┬─────────┘       └───────┬──────────┘            │
│           │                          │                       │
│           └──────────┬───────────────┘                       │
│                      │                                        │
│           ┌──────────▼──────────┐                            │
│           │  Action Groups      │                            │
│           │  (Email/Teams/SMS)  │                            │
│           └─────────────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Collection Points

1. **LibreChat Application**
   - HTTP requests/responses
   - API latency
   - Error rates
   - User sessions
   - Chat messages (metadata only)

2. **Databases**
   - MongoDB: Query performance, connection pool, storage
   - PostgreSQL: Query execution, locks, replication lag
   - Redis: Hit/miss ratio, memory usage, evictions

3. **Storage**
   - Blob operations (upload/download)
   - Transaction counts
   - Latency metrics
   - Quota usage

4. **Agentic Analytics**
   - Document ingestion rate
   - Vector search latency
   - Embedding generation time
   - RAG pipeline performance

5. **Playwright E2E**
   - Test execution duration
   - Step success/failure rates
   - Screenshot generation
   - Browser resource usage

---

## Azure Monitor Setup

### 1. Create Log Analytics Workspace

```bash
# Create workspace
az monitor log-analytics workspace create \
  --resource-group librechat-rg \
  --workspace-name librechat-logs \
  --location eastus \
  --retention-time 90

# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group librechat-rg \
  --workspace-name librechat-logs \
  --query id -o tsv)

echo "Workspace ID: $WORKSPACE_ID"
```

### 2. Enable Diagnostic Settings

**For Container Instances:**
```bash
az monitor diagnostic-settings create \
  --name librechat-diagnostics \
  --resource <container-instance-resource-id> \
  --workspace $WORKSPACE_ID \
  --logs '[{"category":"ContainerInstanceLog","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'
```

**For PostgreSQL:**
```bash
az monitor diagnostic-settings create \
  --name postgres-diagnostics \
  --resource <postgresql-resource-id> \
  --workspace $WORKSPACE_ID \
  --logs '[
    {"category":"PostgreSQLLogs","enabled":true},
    {"category":"QueryStoreRuntimeStatistics","enabled":true},
    {"category":"QueryStoreWaitStatistics","enabled":true}
  ]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'
```

**For Redis:**
```bash
az monitor diagnostic-settings create \
  --name redis-diagnostics \
  --resource <redis-resource-id> \
  --workspace $WORKSPACE_ID \
  --logs '[
    {"category":"ConnectedClientList","enabled":true}
  ]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'
```

**For Storage Account:**
```bash
az monitor diagnostic-settings create \
  --name storage-diagnostics \
  --resource <storage-account-resource-id> \
  --workspace $WORKSPACE_ID \
  --logs '[
    {"category":"StorageRead","enabled":true},
    {"category":"StorageWrite","enabled":true},
    {"category":"StorageDelete","enabled":true}
  ]' \
  --metrics '[{"category":"Transaction","enabled":true}]'
```

---

## Application Insights

### 1. Create Application Insights Instance

```bash
az monitor app-insights component create \
  --app librechat-insights \
  --location eastus \
  --resource-group librechat-rg \
  --workspace $WORKSPACE_ID

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app librechat-insights \
  --resource-group librechat-rg \
  --query instrumentationKey -o tsv)

echo "Instrumentation Key: $INSTRUMENTATION_KEY"
```

### 2. Configure Application Insights in LibreChat

Add to your `.env.azure`:
```bash
# Application Insights
APPINSIGHTS_INSTRUMENTATION_KEY=$INSTRUMENTATION_KEY
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSTRUMENTATION_KEY"
```

### 3. Integrate Application Insights SDK

**For Node.js (LibreChat):**

Install package:
```bash
npm install applicationinsights --save
```

Add to `api/server/index.js`:
```javascript
const appInsights = require('applicationinsights');

// Initialize Application Insights
if (process.env.APPINSIGHTS_INSTRUMENTATION_KEY) {
  appInsights
    .setup(process.env.APPINSIGHTS_INSTRUMENTATION_KEY)
    .setAutoDependencyCorrelation(true)
    .setAutoCollectRequests(true)
    .setAutoCollectPerformance(true, true)
    .setAutoCollectExceptions(true)
    .setAutoCollectDependencies(true)
    .setAutoCollectConsole(true)
    .setUseDiskRetryCaching(true)
    .setSendLiveMetrics(true)
    .setDistributedTracingMode(appInsights.DistributedTracingModes.AI_AND_W3C)
    .start();

  console.log('✅ Application Insights initialized');
}
```

### 4. Custom Telemetry

Track custom events:
```javascript
const appInsights = require('applicationinsights');

// Track custom event
appInsights.defaultClient.trackEvent({
  name: 'ChatMessageSent',
  properties: {
    model: 'gpt-4',
    userId: user.id,
    conversationId: conversation.id,
  },
});

// Track custom metric
appInsights.defaultClient.trackMetric({
  name: 'ChatResponseTime',
  value: responseTime,
});

// Track dependency (external API call)
appInsights.defaultClient.trackDependency({
  target: 'https://api.openai.com',
  name: 'OpenAI API',
  data: 'POST /v1/chat/completions',
  duration: duration,
  resultCode: 200,
  success: true,
  dependencyTypeName: 'HTTP',
});
```

---

## Log Analytics

### 1. Kusto Query Language (KQL) Examples

**View all application logs:**
```kql
ContainerInstanceLog_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
| limit 100
```

**Find errors:**
```kql
ContainerInstanceLog_CL
| where TimeGenerated > ago(24h)
| where Message contains "error" or Message contains "exception"
| summarize count() by Message
| order by count_ desc
```

**Track API request duration:**
```kql
requests
| where timestamp > ago(1h)
| summarize avg(duration), percentile(duration, 95) by operation_Name
| order by avg_duration desc
```

**Database query performance:**
```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.DBFORPOSTGRESQL"
| where Category == "QueryStoreRuntimeStatistics"
| summarize avg(todouble(mean_time_s)) by query_id_d
| order by avg_ desc
| limit 20
```

**Failed login attempts:**
```kql
customEvents
| where name == "UserLogin"
| where customDimensions.success == "false"
| summarize count() by tostring(customDimensions.userId)
| order by count_ desc
```

**E2E test results:**
```kql
customEvents
| where name == "PlaywrightTestCompleted"
| summarize successRate = count(customDimensions.status == "passed") * 100.0 / count() by bin(timestamp, 1d)
| render timechart
```

### 2. Saved Queries

Create commonly used queries:

```bash
az monitor log-analytics workspace saved-search create \
  --resource-group librechat-rg \
  --workspace-name librechat-logs \
  --name "Recent Errors" \
  --category "Application" \
  --query "ContainerInstanceLog_CL | where Message contains 'error' | order by TimeGenerated desc | limit 50"
```

---

## Metrics & Dashboards

### 1. Key Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Response time (P50, P95, P99)
- Error rate (%)
- Active users (concurrent)
- Session duration

**Database Metrics:**
- Connection count
- Query execution time
- Deadlocks
- Storage used (%)
- Replication lag (if applicable)

**Storage Metrics:**
- Blob operations/sec
- Latency (ms)
- Bandwidth used (MB/s)
- Storage capacity (%)

**E2E Test Metrics:**
- Test success rate (%)
- Test duration (seconds)
- Failed step count
- Screenshot count

### 2. Create Azure Dashboard

**Using Azure Portal:**
1. Navigate to **Azure Portal** → **Dashboards**
2. Click **+ New dashboard**
3. Name: "LibreChat Production Monitoring"
4. Add tiles:
   - **Metrics Chart**: LibreChat request rate
   - **Metrics Chart**: PostgreSQL CPU usage
   - **Metrics Chart**: Redis memory usage
   - **Logs Query**: Recent errors
   - **Logs Query**: E2E test results

**Using ARM Template:**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {},
  "resources": [
    {
      "type": "Microsoft.Portal/dashboards",
      "apiVersion": "2020-09-01-preview",
      "name": "LibreChatDashboard",
      "location": "[resourceGroup().location]",
      "properties": {
        "lenses": [
          {
            "order": 0,
            "parts": [
              {
                "position": {"x": 0, "y": 0, "rowSpan": 4, "colSpan": 6},
                "metadata": {
                  "type": "Extension/HubsExtension/PartType/MonitorChartPart",
                  "settings": {
                    "content": {
                      "options": {
                        "chart": {
                          "metrics": [
                            {
                              "resourceMetadata": {
                                "id": "/subscriptions/{subscription}/resourceGroups/librechat-rg/providers/Microsoft.Insights/components/librechat-insights"
                              },
                              "name": "requests/count",
                              "aggregationType": 7
                            }
                          ],
                          "title": "Request Rate"
                        }
                      }
                    }
                  }
                }
              }
            ]
          }
        ]
      }
    }
  ]
}
```

### 3. Create Workbook for Deep Analysis

```bash
# Workbooks provide interactive reports
# Create via Azure Portal:
# Monitor → Workbooks → + New → Add visualizations
```

**Example Workbook Sections:**
1. **Overview**: Request rate, error rate, active users
2. **Performance**: Response time trends, slow queries
3. **Errors**: Error breakdown by type, stack traces
4. **Database**: Connection pool, query performance, storage
5. **E2E Tests**: Test pass/fail trends, failed steps analysis
6. **User Behavior**: Popular models, file upload stats

---

## Alerts & Notifications

### 1. Create Action Group

```bash
az monitor action-group create \
  --name librechat-alerts \
  --resource-group librechat-rg \
  --short-name lc-alerts \
  --email-receiver name=ops email=ops@example.com \
  --webhook-receiver name=teams uri=https://outlook.office.com/webhook/...
```

### 2. Configure Alerts

**High Error Rate Alert:**
```bash
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group librechat-rg \
  --scopes <app-insights-resource-id> \
  --condition "avg requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action librechat-alerts \
  --description "Alert when error rate exceeds 10 requests in 5 minutes"
```

**High CPU Usage Alert:**
```bash
az monitor metrics alert create \
  --name high-cpu \
  --resource-group librechat-rg \
  --scopes <container-instance-resource-id> \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action librechat-alerts \
  --description "Alert when CPU usage exceeds 80% for 5 minutes"
```

**Database Connection Failure Alert:**
```bash
az monitor metrics alert create \
  --name db-connection-failure \
  --resource-group librechat-rg \
  --scopes <postgresql-resource-id> \
  --condition "total failed_connections > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action librechat-alerts \
  --description "Alert when database connection failures exceed 5 in 5 minutes"
```

**E2E Test Failure Alert (Log Query):**
```bash
az monitor scheduled-query create \
  --name e2e-test-failure \
  --resource-group librechat-rg \
  --scopes $WORKSPACE_ID \
  --condition "count 'Heartbeat | where Computer contains \"playwright\" and Status == \"Failed\"' > 0" \
  --window-size 15m \
  --evaluation-frequency 5m \
  --action librechat-alerts \
  --description "Alert when E2E test fails"
```

### 3. Smart Detection (Anomaly Detection)

Enable automatic anomaly detection in Application Insights:

```bash
az monitor app-insights component update \
  --app librechat-insights \
  --resource-group librechat-rg \
  --enable-smart-detection true
```

Smart Detection automatically alerts on:
- Abnormal rise in exception rate
- Abnormal rise in failed request rate
- Performance degradation
- Memory leak detection
- Slow server response time

---

## Distributed Tracing

### 1. Enable Distributed Tracing

Distributed tracing tracks requests across multiple services (LibreChat → OpenAI API, LibreChat → Database, etc.).

**Already enabled with Application Insights SDK:**
```javascript
appInsights
  .setDistributedTracingMode(appInsights.DistributedTracingModes.AI_AND_W3C)
```

### 2. View Distributed Traces

1. Navigate to **Application Insights** → **Transaction search**
2. Select a request
3. Click **View end-to-end transaction**
4. See the full request flow across services

Example trace:
```
Request: POST /api/chat
  ├─ Dependency: MongoDB (150ms)
  ├─ Dependency: OpenAI API (1200ms)
  │   └─ HTTP POST https://api.openai.com/v1/chat/completions
  └─ Dependency: PostgreSQL (45ms)
Total: 1395ms
```

### 3. Correlation with Custom Events

```javascript
const { CorrelationContext } = require('applicationinsights');

// All events within this context are correlated
const correlationContext = CorrelationContext.startOperation('ProcessChatMessage');

appInsights.defaultClient.trackEvent({ name: 'ChatMessageReceived' });
appInsights.defaultClient.trackDependency({ name: 'OpenAI API' });
appInsights.defaultClient.trackEvent({ name: 'ChatMessageStored' });

CorrelationContext.endOperation(correlationContext);
```

---

## Custom Monitoring

### 1. E2E Test Monitoring

**Instrument single_window_runner.js:**

```javascript
const appInsights = require('applicationinsights');

// Initialize Application Insights for E2E tests
if (process.env.APPINSIGHTS_INSTRUMENTATION_KEY) {
  appInsights
    .setup(process.env.APPINSIGHTS_INSTRUMENTATION_KEY)
    .start();
}

// Track test start
appInsights.defaultClient.trackEvent({
  name: 'PlaywrightTestStarted',
  properties: { testSuite: 'E2E-33-Steps' },
});

// Track each step
async function logStep(stepName) {
  const startTime = Date.now();
  
  appInsights.defaultClient.trackEvent({
    name: 'PlaywrightStepStarted',
    properties: { step: stepName },
  });
  
  // ... step execution ...
  
  const duration = Date.now() - startTime;
  appInsights.defaultClient.trackMetric({
    name: 'PlaywrightStepDuration',
    value: duration,
    properties: { step: stepName },
  });
}

// Track test completion
appInsights.defaultClient.trackEvent({
  name: 'PlaywrightTestCompleted',
  properties: {
    status: 'passed',
    totalSteps: 33,
    duration: totalDuration,
  },
});
```

### 2. RAG Pipeline Monitoring

**Instrument rag_pipeline.py:**

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace, metrics
import os

# Initialize Azure Monitor for Python
configure_azure_monitor(
    connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
)

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create custom metrics
document_ingestion_counter = meter.create_counter(
    name="rag.documents.ingested",
    description="Number of documents ingested"
)

embedding_duration = meter.create_histogram(
    name="rag.embedding.duration",
    description="Embedding generation duration in ms"
)

# Track document ingestion
with tracer.start_as_current_span("ingest_document") as span:
    span.set_attribute("document.id", doc_id)
    span.set_attribute("document.size", doc_size)
    
    # ... ingestion logic ...
    
    document_ingestion_counter.add(1)
    embedding_duration.record(duration_ms)
```

### 3. Database Adapter Monitoring

**Instrument database_adapter_registry.py:**

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class DatabaseAdapter:
    def execute_query(self, query):
        with tracer.start_as_current_span("database.query") as span:
            span.set_attribute("db.system", "postgresql")
            span.set_attribute("db.statement", query[:100])  # First 100 chars
            
            start = time.time()
            result = self._execute(query)
            duration = time.time() - start
            
            span.set_attribute("db.duration_ms", duration * 1000)
            span.set_attribute("db.rows_affected", len(result))
            
            return result
```

---

## Performance Monitoring

### 1. Application Performance

**Track key performance indicators:**

```javascript
// Track page load time
appInsights.defaultClient.trackPageView({
  name: 'ChatInterface',
  url: '/chat',
  duration: loadTime,
});

// Track API call performance
const startTime = Date.now();
const response = await fetch('/api/chat', { method: 'POST', body: data });
const duration = Date.now() - startTime;

appInsights.defaultClient.trackDependency({
  name: 'ChatAPI',
  data: '/api/chat',
  duration: duration,
  resultCode: response.status,
  success: response.ok,
});
```

**Query slow requests:**
```kql
requests
| where timestamp > ago(1h)
| where duration > 3000  // > 3 seconds
| order by duration desc
| project timestamp, name, url, duration, resultCode
| limit 50
```

### 2. Database Performance

**PostgreSQL slow query log:**

Enable slow query logging:
```sql
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();
```

**Query in Log Analytics:**
```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.DBFORPOSTGRESQL"
| where Message contains "duration"
| parse Message with * "duration: " duration:double " ms" *
| where duration > 1000
| order by duration desc
| limit 50
```

### 3. Resource Utilization

**Container CPU/Memory:**
```kql
Perf
| where ObjectName == "K8SContainer"
| where CounterName == "cpuUsageNanoCores"
| summarize avg(CounterValue) by bin(TimeGenerated, 5m), InstanceName
| render timechart
```

**Database connection pool:**
```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.DBFORPOSTGRESQL"
| where MetricName == "active_connections"
| summarize avg(Maximum) by bin(TimeGenerated, 5m)
| render timechart
```

---

## Security Monitoring

### 1. Security Events

**Failed login attempts:**
```kql
customEvents
| where name == "UserLoginFailed"
| summarize count() by tostring(customDimensions.ipAddress), tostring(customDimensions.userId)
| where count_ > 5  // More than 5 failed attempts
| order by count_ desc
```

**Suspicious file uploads:**
```kql
customEvents
| where name == "FileUploaded"
| where customDimensions.fileSize > 100000000  // > 100MB
   or customDimensions.fileType in ("exe", "sh", "bat")
| project timestamp, userId = tostring(customDimensions.userId), 
          fileName = tostring(customDimensions.fileName),
          fileType = tostring(customDimensions.fileType)
```

**Unusual API access patterns:**
```kql
requests
| where timestamp > ago(1h)
| summarize count() by client_IP
| where count_ > 1000  // > 1000 requests/hour from single IP
| order by count_ desc
```

### 2. Azure Defender for Cloud

Enable Azure Defender:
```bash
az security pricing create \
  --name VirtualMachines \
  --tier 'Standard'

az security pricing create \
  --name SqlServers \
  --tier 'Standard'

az security pricing create \
  --name AppServices \
  --tier 'Standard'
```

### 3. Audit Logs

Enable Azure Activity Log:
```bash
az monitor diagnostic-settings create \
  --name activity-log \
  --resource-group librechat-rg \
  --resource <subscription-id> \
  --workspace $WORKSPACE_ID \
  --logs '[{"category":"Administrative","enabled":true},
           {"category":"Security","enabled":true},
           {"category":"Alert","enabled":true}]'
```

---

## Cost Monitoring

### 1. Cost Analysis Dashboard

Create cost alerts:
```bash
az consumption budget create \
  --resource-group librechat-rg \
  --budget-name monthly-budget \
  --amount 1000 \
  --time-grain Monthly \
  --start-date 2025-01-01 \
  --end-date 2026-01-01 \
  --notification enabled=true threshold=80 contact-emails ops@example.com
```

### 2. Cost Optimization Queries

**Top expensive resources:**
```kql
AzureCostManagement
| where TimeGenerated > ago(30d)
| summarize TotalCost = sum(todouble(PreTaxCost)) by ResourceId, ResourceType
| order by TotalCost desc
| limit 20
```

**Daily cost trend:**
```kql
AzureCostManagement
| where TimeGenerated > ago(30d)
| summarize DailyCost = sum(todouble(PreTaxCost)) by bin(TimeGenerated, 1d)
| render timechart
```

---

## Troubleshooting

### Common Issues

**1. No logs appearing in Log Analytics**

- Check diagnostic settings are enabled
- Verify workspace connection
- Allow 5-10 minutes for initial data ingestion
- Check workspace retention period

**2. Application Insights not receiving data**

```bash
# Verify instrumentation key
az monitor app-insights component show \
  --app librechat-insights \
  --resource-group librechat-rg \
  --query instrumentationKey

# Check SDK initialization in application logs
docker logs <container-id> | grep "Application Insights"
```

**3. Alerts not triggering**

- Verify action group configuration
- Check alert query syntax
- Ensure evaluation frequency is appropriate
- Review alert history for throttling

**4. High ingestion costs**

- Review sampling settings (reduce to 10-20% for high-traffic apps)
- Disable verbose logging in production
- Filter out noisy metrics
- Use log retention policies

**5. Missing metrics**

- Ensure diagnostic settings include "AllMetrics"
- Check resource provider supports metrics
- Verify time range in queries

---

## Best Practices

### 1. Log Sampling

For high-traffic applications:
```javascript
appInsights.defaultClient.config.samplingPercentage = 20;  // Sample 20%
```

### 2. Sensitive Data Filtering

```javascript
appInsights.defaultClient.addTelemetryProcessor((envelope) => {
  // Remove sensitive data
  if (envelope.data.baseData) {
    const data = envelope.data.baseData;
    if (data.properties) {
      delete data.properties.password;
      delete data.properties.apiKey;
      delete data.properties.token;
    }
  }
  return true;
});
```

### 3. Correlation IDs

Always use correlation IDs to track requests:
```javascript
const correlationId = uuid.v4();
appInsights.defaultClient.trackEvent({
  name: 'ChatMessageProcessed',
  properties: { correlationId, userId, conversationId },
});
```

### 4. Health Checks

Implement health check endpoints:
```javascript
app.get('/health', (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {
      database: await checkDatabase(),
      redis: await checkRedis(),
      storage: await checkStorage(),
    },
  };
  
  appInsights.defaultClient.trackMetric({
    name: 'HealthCheckStatus',
    value: health.status === 'healthy' ? 1 : 0,
  });
  
  res.json(health);
});
```

### 5. Retention Policies

Configure appropriate retention:
```bash
# 90 days for production, 30 days for dev
az monitor log-analytics workspace update \
  --resource-group librechat-rg \
  --workspace-name librechat-logs \
  --retention-time 90
```

---

## Summary

**Monitoring Maturity Levels:**

**Level 1: Basic**
- ✅ Azure Monitor enabled
- ✅ Basic metrics collected
- ✅ Simple alerts configured

**Level 2: Intermediate**
- ✅ Application Insights integrated
- ✅ Custom events tracked
- ✅ Dashboards created
- ✅ Log queries optimized

**Level 3: Advanced**
- ✅ Distributed tracing enabled
- ✅ Custom telemetry extensive
- ✅ Anomaly detection active
- ✅ Security monitoring comprehensive
- ✅ Cost optimization automated

**Next Steps:**
1. Review `DEPLOYMENT_CHECKLIST.md` monitoring section
2. Configure alerts based on your SLAs
3. Create custom dashboards for your team
4. Schedule regular monitoring reviews
5. Refer to `TROUBLESHOOTING_GUIDE.md` for issue resolution

---

**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Owner**: DevOps Team
