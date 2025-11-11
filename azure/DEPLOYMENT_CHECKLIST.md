# Azure Deployment Checklist

Complete checklist for deploying LibreChat + Agentic Analytics + Playwright E2E to Azure.

---

## 📋 Pre-Deployment Phase

### 1. Azure Account Setup
- [ ] Azure account created and verified
- [ ] Billing alerts configured
- [ ] Azure CLI installed locally (`az --version`)
- [ ] Logged into Azure CLI (`az login`)
- [ ] Correct subscription selected (`az account set --subscription <id>`)
- [ ] Resource quotas verified (vCPUs, storage, networking)

### 2. Domain & Networking
- [ ] Domain name registered (if using custom domain)
- [ ] DNS provider accessible
- [ ] SSL certificate prepared (or plan for Let's Encrypt)
- [ ] VNet CIDR ranges planned (e.g., 10.0.0.0/16)
- [ ] Subnet allocations designed
- [ ] NSG rules documented

### 3. Tools & Dependencies
- [ ] Docker installed locally
- [ ] Azure CLI installed and configured
- [ ] Git installed
- [ ] Node.js 18+ installed (for local testing)
- [ ] Python 3.11+ installed (for analytics stack)
- [ ] Playwright dependencies reviewed

### 4. Secrets & Configuration
- [ ] OpenAI API keys obtained (if using)
- [ ] Anthropic API keys obtained (if using)
- [ ] GitHub OAuth app created (if using GitHub auth)
- [ ] Google OAuth credentials obtained (if using Google auth)
- [ ] Strong passwords generated for databases
- [ ] JWT secrets generated (`openssl rand -hex 32`)
- [ ] Creds token secret generated
- [ ] All secrets stored in password manager

### 5. Repository Setup
- [ ] LibreChat repository cloned
- [ ] All azure/* files reviewed
- [ ] `.env.azure.example` copied to `.env.azure`
- [ ] Configuration files customized for your needs

---

## 🏗️ Deployment Phase

### Phase 1: Core Infrastructure (30-45 minutes)

#### Resource Group
- [ ] Resource group created
  ```bash
  az group create --name librechat-rg --location eastus
  ```
- [ ] Tags applied (environment, project, owner)

#### Virtual Network
- [ ] VNet created with proper CIDR
- [ ] Subnets created:
  - [ ] App subnet (10.0.1.0/24)
  - [ ] Database subnet (10.0.2.0/24)
  - [ ] Container subnet (10.0.3.0/24)
- [ ] Network Security Groups created
- [ ] NSG rules configured:
  - [ ] HTTPS (443)
  - [ ] HTTP (80)
  - [ ] PostgreSQL (5432) - restricted
  - [ ] Redis (6379) - restricted
  - [ ] Meilisearch (7700) - restricted

#### Storage Account
- [ ] Storage account created
- [ ] Containers created:
  - [ ] `uploads` (private)
  - [ ] `avatars` (blob, public read)
  - [ ] `backups` (private)
  - [ ] `rag-documents` (private)
  - [ ] `screenshots` (private)
- [ ] CORS configured for blob access
- [ ] SAS tokens generated (if needed)
- [ ] Connection string saved to .env

### Phase 2: Database Services (20-30 minutes)

#### MongoDB
- [ ] Azure Cosmos DB for MongoDB created
  - [ ] API: MongoDB
  - [ ] Capacity: Provisioned or Serverless
  - [ ] Geo-redundancy configured (if needed)
- [ ] Database `LibreChat` created
- [ ] Connection string obtained
- [ ] Firewall rules configured
- [ ] Private endpoint created (optional, recommended)

#### PostgreSQL
- [ ] Azure Database for PostgreSQL Flexible Server created
  - [ ] Version: 15 or 16
  - [ ] SKU: B_Standard_B1ms (dev) or higher (prod)
  - [ ] Storage: 32 GB minimum
- [ ] Databases created:
  - [ ] `agentic_analytics`
  - [ ] `rag_data`
- [ ] Admin user configured
- [ ] Firewall rules set
- [ ] Connection strings saved
- [ ] SSL enforcement enabled

#### Redis Cache
- [ ] Azure Cache for Redis created
  - [ ] SKU: Basic C0 (dev) or Standard C1+ (prod)
  - [ ] TLS enabled
- [ ] Access keys obtained
- [ ] Connection string formatted:
  ```
  redis://:PASSWORD@HOSTNAME:6380
  ```

#### Meilisearch
- [ ] Container instance or VM prepared
- [ ] Meilisearch 1.12+ deployed
- [ ] Master key configured
- [ ] Index created
- [ ] Health check verified (`GET /health`)

### Phase 3: Application Deployment (45-60 minutes)

#### LibreChat Application
- [ ] Container registry created (ACR)
- [ ] Docker image built locally:
  ```bash
  docker build -t librechat:azure -f Dockerfile .
  ```
- [ ] Image tagged for ACR:
  ```bash
  docker tag librechat:azure <registry>.azurecr.io/librechat:latest
  ```
- [ ] Image pushed to ACR:
  ```bash
  docker push <registry>.azurecr.io/librechat:latest
  ```
- [ ] Azure Container Instance or App Service created
- [ ] Environment variables configured (50+ variables)
- [ ] Persistent storage mounted
- [ ] Health checks configured
- [ ] Application started
- [ ] Logs verified
- [ ] Application accessible via public IP/URL

#### LibreChat Configuration
- [ ] `librechat.yaml` customized
- [ ] Endpoints configured (OpenAI, Anthropic, etc.)
- [ ] Model parameters set
- [ ] File upload settings configured
- [ ] Configuration uploaded to container

### Phase 4: Agentic Analytics Stack (30-45 minutes)

#### RAG Database Setup
- [ ] PostgreSQL extensions installed:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  ```
- [ ] Schema created:
  ```bash
  psql -h <host> -U <user> -d agentic_analytics -f setup_rag_database.sql
  ```
- [ ] Tables verified:
  - [ ] `documents`
  - [ ] `chunks`
  - [ ] `embeddings`
  - [ ] `queries`

#### Analytics Container
- [ ] Dockerfile.agentic-analytics built:
  ```bash
  docker build -t agentic-analytics:azure -f azure/Dockerfile.agentic-analytics .
  ```
- [ ] Image pushed to ACR
- [ ] Container instance created
- [ ] Python dependencies verified
- [ ] PostgreSQL connection tested
- [ ] File storage mounted

#### Document Ingestion
- [ ] Sample documents uploaded to blob storage
- [ ] Ingestion script tested:
  ```bash
  python ingest.py --source azure-blob --container rag-documents
  ```
- [ ] Embeddings verified in database
- [ ] Vector search tested:
  ```bash
  python query.py "test query"
  ```

#### Analytics Tools
- [ ] `tech_analyzer_v2.py` configured
- [ ] `stack_generator.py` tested
- [ ] `dependency_mapper.py` functional
- [ ] Database adapters registered
- [ ] Configuration engine validated

### Phase 5: Playwright E2E Testing (45-60 minutes)

#### E2E Infrastructure Setup
- [ ] Playwright container built:
  ```bash
  docker build -t playwright-e2e:azure -f azure/Dockerfile.playwright-e2e .
  ```
- [ ] Container pushed to ACR
- [ ] Test VM or container instance created
- [ ] Xvfb configured (for headless browsers)
- [ ] VNC server setup (optional, for debugging)
- [ ] Screenshot storage configured (blob storage)

#### Playwright Configuration
- [ ] `playwright.config.ts` customized for Azure
- [ ] Base URL set to Azure LibreChat URL
- [ ] Timeouts configured (30s default, 60s navigation)
- [ ] Screenshot settings configured
- [ ] Video recording enabled (on failure)
- [ ] Trace collection enabled (on failure)

#### Test Execution
- [ ] 33-step E2E test suite deployed
- [ ] `single_window_runner.js` configured
- [ ] Test credentials configured in .env
- [ ] Dry run executed:
  ```bash
  node e2e/single_window_runner.js
  ```
- [ ] All 33 steps passed
- [ ] Screenshots captured (31+ images)
- [ ] Event logs generated (`e2e-events.log`)

#### MCP Integration
- [ ] MCP server endpoint configured (if using)
- [ ] `mcp-forwarder.js` container deployed
- [ ] API key configured
- [ ] Event streaming tested
- [ ] NDJSON events forwarded successfully
- [ ] MCP server receiving events

#### Inspector Mode Setup
- [ ] `run-with-inspector.sh` tested locally
- [ ] PWDEBUG mode verified
- [ ] Inspector UI accessible
- [ ] Breakpoints working (F8 resume)
- [ ] Visual debugging validated

#### Automated Test Scheduling
- [ ] Azure Logic App or Function created for scheduling
- [ ] Daily test run configured (e.g., 2 AM UTC)
- [ ] Test results notifications configured
- [ ] Failed test alerts set up (email/Teams/Slack)
- [ ] Screenshot artifacts retained (30 days)

---

## 🔍 Post-Deployment Validation

### Application Health
- [ ] LibreChat homepage loads (`https://<your-domain>`)
- [ ] User registration works
- [ ] User login works
- [ ] Chat interface functional
- [ ] Message sending/receiving works
- [ ] File upload works
- [ ] Avatar upload works
- [ ] Settings page accessible
- [ ] Model selection works
- [ ] Conversation history persists

### Backend Services
- [ ] MongoDB connection healthy
  ```bash
  mongosh "mongodb://<connection-string>"
  ```
- [ ] PostgreSQL connection healthy
  ```bash
  psql -h <host> -U <user> -d agentic_analytics -c "SELECT version();"
  ```
- [ ] Redis connection healthy
  ```bash
  redis-cli -h <host> -p 6380 --tls -a <password> PING
  ```
- [ ] Meilisearch healthy
  ```bash
  curl https://<meilisearch-url>/health
  ```

### Analytics Stack
- [ ] Document ingestion works
- [ ] Vector search returns results
- [ ] Tech analyzer generates reports
- [ ] Stack generator creates diagrams
- [ ] Database adapters functional
- [ ] Configuration engine reads configs

### E2E Testing
- [ ] All 33 test steps pass
- [ ] Screenshots captured successfully
- [ ] Event logs generated
- [ ] MCP events forwarded (if enabled)
- [ ] Inspector mode accessible
- [ ] Automated runs scheduled

### Security
- [ ] SSL/TLS enabled on all services
- [ ] Firewall rules restrictive (least privilege)
- [ ] Secrets not exposed in logs
- [ ] Private endpoints configured (where applicable)
- [ ] NSG rules audited
- [ ] Storage account access restricted
- [ ] Database access restricted to VNet

### Performance
- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms (average)
- [ ] Chat message latency < 2 seconds
- [ ] File upload completes successfully (< 100MB)
- [ ] Vector search response < 1 second
- [ ] E2E test suite completes in < 5 minutes

---

## 📊 Monitoring & Observability

### Azure Monitor Setup
- [ ] Application Insights enabled for LibreChat
- [ ] Log Analytics workspace created
- [ ] Diagnostic settings configured for:
  - [ ] Container instances
  - [ ] PostgreSQL
  - [ ] Redis
  - [ ] Storage account
  - [ ] Virtual network
- [ ] Custom metrics configured
- [ ] Dashboards created

### Alerts Configuration
- [ ] High CPU alert (> 80% for 5 min)
- [ ] High memory alert (> 90% for 5 min)
- [ ] Database connection failures
- [ ] Storage account quota alerts (> 80%)
- [ ] Failed login attempts (> 10 in 5 min)
- [ ] E2E test failures
- [ ] Application errors (500 responses)

### Log Aggregation
- [ ] Application logs forwarded to Log Analytics
- [ ] PostgreSQL logs forwarded
- [ ] Redis logs forwarded
- [ ] E2E test logs stored in blob storage
- [ ] MCP event logs archived
- [ ] Log retention policies set (90 days default)

### Uptime Monitoring
- [ ] Azure Monitor availability tests created
- [ ] Endpoint health checks configured
- [ ] Ping tests scheduled (every 5 minutes)
- [ ] Downtime alerts configured
- [ ] SLA tracking enabled

---

## 🔐 Security Hardening

### Network Security
- [ ] Private endpoints enabled for databases
- [ ] VNet integration configured
- [ ] NSG rules minimal (deny-by-default)
- [ ] No public IPs exposed (except load balancer)
- [ ] DDoS protection enabled
- [ ] Azure Firewall configured (optional)

### Identity & Access
- [ ] Managed identities enabled
- [ ] RBAC roles assigned (least privilege)
- [ ] Service principals created (for automation)
- [ ] Azure AD authentication enabled (where possible)
- [ ] MFA required for admin access
- [ ] Conditional access policies configured

### Data Protection
- [ ] Database encryption at rest enabled
- [ ] Transparent Data Encryption (TDE) enabled
- [ ] Backup encryption enabled
- [ ] Storage account encryption enabled
- [ ] Secrets stored in Azure Key Vault
- [ ] Key rotation policy configured

### Compliance
- [ ] Azure Security Center recommendations reviewed
- [ ] Compliance reports generated
- [ ] Audit logs enabled
- [ ] Data residency requirements met
- [ ] GDPR compliance verified (if applicable)
- [ ] Security baselines applied

---

## 🔄 Backup & Disaster Recovery

### Backup Configuration
- [ ] MongoDB automated backups enabled (daily)
- [ ] PostgreSQL automated backups enabled (daily)
- [ ] Retention period set (30 days minimum)
- [ ] Geo-redundant backups enabled
- [ ] Storage account blob versioning enabled
- [ ] Application configuration backed up

### Disaster Recovery Plan
- [ ] Recovery Time Objective (RTO) defined
- [ ] Recovery Point Objective (RPO) defined
- [ ] Secondary region identified
- [ ] Geo-replication configured (for critical data)
- [ ] Failover procedures documented
- [ ] DR testing scheduled (quarterly)

### Restore Testing
- [ ] MongoDB restore tested successfully
- [ ] PostgreSQL restore tested successfully
- [ ] Storage account restore tested
- [ ] Full environment restore documented
- [ ] Restore time measured (RTO validation)

---

## 📈 Scaling & Optimization

### Auto-Scaling Configuration
- [ ] Container instance scaling rules defined
- [ ] Database scaling plan documented
- [ ] Redis cache tier upgrade path identified
- [ ] Storage account scaling monitored
- [ ] Load balancer configured (for multi-instance)

### Performance Optimization
- [ ] CDN configured for static assets
- [ ] Image optimization enabled
- [ ] Database query optimization reviewed
- [ ] Indexing strategy validated
- [ ] Caching strategy implemented
- [ ] Connection pooling configured

### Cost Optimization
- [ ] Reserved instances purchased (if applicable)
- [ ] Unused resources identified and removed
- [ ] Cost alerts configured
- [ ] Budget limits set
- [ ] Resource tagging for cost allocation
- [ ] Spending trends reviewed monthly

---

## 📚 Documentation

### Technical Documentation
- [ ] Architecture diagram created and updated
- [ ] Network diagram documented
- [ ] API documentation complete
- [ ] Database schema documented
- [ ] Environment variables documented
- [ ] Configuration files explained

### Operational Documentation
- [ ] Deployment runbook created
- [ ] Troubleshooting guide written
- [ ] Incident response plan documented
- [ ] On-call procedures defined
- [ ] Escalation paths documented
- [ ] Change management process defined

### User Documentation
- [ ] Admin guide created
- [ ] User guide written
- [ ] API usage examples provided
- [ ] FAQ documented
- [ ] Support contact information provided

---

## ✅ Final Sign-Off

### Stakeholder Approval
- [ ] Technical lead approval obtained
- [ ] Security team review completed
- [ ] Cost approval received
- [ ] Go-live date confirmed
- [ ] Communication plan executed

### Handoff
- [ ] Operations team trained
- [ ] Support team briefed
- [ ] Documentation reviewed and accepted
- [ ] Access credentials transferred (securely)
- [ ] Knowledge transfer sessions completed

### Go-Live
- [ ] Production deployment completed
- [ ] DNS cutover executed (if applicable)
- [ ] Monitoring dashboards reviewed
- [ ] 24-hour stability period observed
- [ ] Post-deployment review scheduled

---

## 🎯 Success Metrics

### Deployment Success
- ✅ All services running and healthy
- ✅ Zero critical errors in first 24 hours
- ✅ Performance targets met
- ✅ Security baselines achieved
- ✅ Backup verification completed

### User Acceptance
- ✅ User login success rate > 99%
- ✅ Chat functionality working for all users
- ✅ File uploads successful > 95%
- ✅ Page load time < 3 seconds
- ✅ No user-reported blockers

### Operational Readiness
- ✅ Monitoring and alerts functional
- ✅ Backup and restore validated
- ✅ DR plan documented and tested
- ✅ Team trained and ready
- ✅ Runbooks complete and accessible

---

## 📞 Support Contacts

### Azure Support
- Azure Support Portal: https://portal.azure.com
- Azure Support Phone: [Your region-specific number]
- Support Plan: [Basic/Developer/Standard/Professional Direct]

### Internal Contacts
- Technical Lead: [Name, Email, Phone]
- DevOps Team: [Email, Teams Channel]
- Security Team: [Email, Teams Channel]
- Database Admin: [Name, Email, Phone]

### Vendor Support
- OpenAI Support: https://help.openai.com
- MongoDB Support: https://www.mongodb.com/support
- Playwright Support: https://playwright.dev/docs/intro

---

## 📝 Notes

**Last Updated**: {{ Date }}
**Deployment Version**: {{ Version }}
**Environment**: {{ Production/Staging/Development }}
**Primary Region**: {{ Azure Region }}
**Backup Region**: {{ Azure Region }}

**Custom Notes**:
- [Add any environment-specific notes here]
- [Document any deviations from standard deployment]
- [Record any known issues or workarounds]

---

**🎉 Deployment Complete!**

Once all checklist items are completed, your LibreChat + Agentic Analytics + Playwright E2E stack is fully operational on Azure.

For ongoing operations, refer to:
- `AZURE_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `TESTING_AND_VALIDATION_GUIDE.md` - Testing procedures
- `MONITORING_AND_OBSERVABILITY.md` - Monitoring setup (next document)
- `TROUBLESHOOTING_GUIDE.md` - Common issues and solutions (next document)
