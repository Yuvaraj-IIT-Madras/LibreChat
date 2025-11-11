# Quick Reference Card
## Dynamic RAG + Agentic Data Analytics Stack v2.0

---

## Installation Quick Commands

```bash
# Setup
git clone https://github.com/danny-avila/LibreChat.git && cd LibreChat
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt google-generativeai pyyaml psycopg2-binary pymongo
export GOOGLE_KEY="your-gemini-api-key"

# Go!
docker-compose up -d
```

---

## Core Modules

| Module | Command | Output |
|--------|---------|--------|
| **Tech Analyzer** | `python tech_analyzer_v2.py /path [--generate-ignore]` | Tech stack + .documentignore |
| **Dependency Mapper** | `python dependency_mapper.py /path [--export]` | Dependency report |
| **Stack Generator** | `python stack_generator.py <db> [--with-monitoring]` | docker-compose.yml |
| **Config Engine** | `python config_engine.py <env> <db> [--scale=X]` | config.yaml |

---

## Database Options

```bash
# PostgreSQL (Recommended)
python stack_generator.py postgresql

# MongoDB
python stack_generator.py mongodb

# MySQL
python stack_generator.py mysql

# ClickHouse (Analytics)
python stack_generator.py clickhouse

# Redis (Caching)
python stack_generator.py redis
```

---

## Environment Configurations

```bash
# Development
python config_engine.py development postgresql --scale=small

# Staging
python config_engine.py staging postgresql --scale=medium

# Production
python config_engine.py production postgresql --scale=large
```

---

## Docker Compose Commands

```bash
# Start services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f <service>

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Restart service
docker-compose restart <service>
```

---

## Service Endpoints

| Service | URL/Port | Purpose |
|---------|----------|---------|
| **LibreChat** | http://localhost:3080 | Web UI |
| **RAG API** | http://localhost:8000 | API endpoint |
| **PostgreSQL** | localhost:5432 | Vector database |
| **MongoDB** | localhost:27017 | Message storage |
| **Redis** | localhost:6379 | Cache |
| **Meilisearch** | http://localhost:7700 | Full-text search |
| **ClickHouse** | http://localhost:8123 | Analytics |

---

## Deployment Quick Links

### Local
1. `python tech_analyzer_v2.py /path --generate-ignore`
2. `python stack_generator.py postgresql`
3. `docker-compose up -d`

### Azure
1. `az group create --name rag-rg --location eastus`
2. Generate configs locally (steps above)
3. `az container create ...` or `kubectl apply -f config.yaml`

### GitHub Codespaces
1. Open GitHub repo → Code → Codespaces → Create
2. `python tech_analyzer_v2.py /path`
3. `docker-compose up -d`

---

## Technology Detection

### Supported Languages
```
✅ Python    ✅ Node.js    ✅ Java      ✅ Go
✅ Rust      ✅ PHP        ✅ .NET      ✅ Ruby
```

### Detected Frameworks
```
✅ Django        ✅ Flask         ✅ FastAPI
✅ Express.js    ✅ React         ✅ Angular
✅ Spring        ✅ Rails         ✅ Laravel
```

### Package Managers
```
✅ pip         ✅ npm          ✅ maven
✅ gradle      ✅ composer     ✅ bundler
✅ cargo       ✅ poetry       ✅ pipenv
```

---

## Troubleshooting Quick Fixes

```bash
# LLM Analysis Issues
export GOOGLE_KEY="your-key"
python -c "import google.generativeai as genai; genai.configure(api_key='$GOOGLE_KEY')"

# Docker Issues
docker system prune -a
docker-compose down -v && docker-compose up -d

# Database Connection
docker exec vectordb pg_isready -U myuser

# Check Logs
docker-compose logs --tail=100 -f <service>

# Port Already in Use
sudo lsof -i :3080  # Find what's using port
docker-compose down  # Stop docker services
```

---

## Performance Tips

```bash
# Scale services
docker-compose up -d --scale worker=5

# Resource limits
# Edit docker-compose.yml services.api.resources.limits

# Connection pooling
# Set DB_POOL_SIZE in .env

# Cache optimization
# Use redis_max_memory=512mb in docker-compose.yml
```

---

## Security Checklist

- [ ] Set strong passwords in .env
- [ ] Enable HTTPS in production
- [ ] Use secrets manager for API keys
- [ ] Enable network policies
- [ ] Rotate API keys regularly
- [ ] Enable monitoring and alerting
- [ ] Use private container registry
- [ ] Implement RBAC

---

## Monitoring Commands

```bash
# Real-time stats
docker stats --no-stream

# Database size
docker exec vectordb psql -U myuser -d mydatabase \
  -c "SELECT pg_size_pretty(pg_database_size('mydatabase'));"

# API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Container events
docker events --filter type=container

# Health check status
docker inspect --format='{{json .State.Health}}' librechat
```

---

## File Structure

```
LibreChat/
├── tech_analyzer_v2.py          # Tech detection
├── dependency_mapper.py         # Dependency analysis
├── stack_generator.py           # Docker config generation
├── config_engine.py             # Microservice configuration
├── .env                         # Environment variables
├── .documentignore              # RAG ingestion filters
├── docker-compose.yml           # Service orchestration
├── config-prod.yaml             # Production config
├── COMPLETE_DEPLOYMENT_GUIDE.md # Full deployment guide
├── DYNAMIC_SYSTEM_GUIDE.md      # Architecture & advanced usage
├── ADVANCED_INTEGRATION_GUIDE.md # Integration workflows
└── QUICK_REFERENCE.md           # This file
```

---

## Environment Variables Cheat Sheet

```bash
# API & Authentication
GOOGLE_KEY=your-gemini-api-key

# Database
DB_HOST=vectordb
DB_PORT=5432
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=password

# Stack Configuration
DATABASE_TYPE=postgresql
ENVIRONMENT=production
SCALE=medium
ENABLE_MONITORING=true
ENABLE_CI=true

# Logging & Debugging
LOG_LEVEL=INFO
DEBUG=false

# Performance Tuning
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_INGESTION_FILES=5000
DB_POOL_SIZE=20
```

---

## Common Workflows

### Workflow 1: Analyze & Deploy
```bash
python tech_analyzer_v2.py /project --generate-ignore
python stack_generator.py postgresql
docker-compose up -d
```

### Workflow 2: Compare Databases
```bash
for db in postgresql mongodb mysql clickhouse; do
  python stack_generator.py $db > docker-compose-$db.yml
done
```

### Workflow 3: Multi-Environment
```bash
for env in dev staging prod; do
  python config_engine.py $env postgresql > config-$env.yaml
done
```

### Workflow 4: Full Pipeline
```bash
python tech_analyzer_v2.py /project --generate-ignore
python dependency_mapper.py /project --export
python stack_generator.py postgresql --with-monitoring
python config_engine.py production postgresql --scale=large
docker-compose up -d
python ingest.py /project
```

---

## API Examples

### Query RAG System
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I deploy this?"}'
```

### Health Check
```bash
curl http://localhost:8000/health
```

### List Indexed Documents
```bash
curl http://localhost:8000/documents
```

### Get Configuration
```bash
curl http://localhost:8000/config
```

---

## Useful Links

| Resource | URL |
|----------|-----|
| Google Gemini API | https://ai.google.dev/ |
| LibreChat Docs | https://docs.librechat.ai |
| Docker Docs | https://docs.docker.com |
| PostgreSQL pgvector | https://github.com/pgvector/pgvector |
| Meilisearch | https://www.meilisearch.com |
| ClickHouse | https://clickhouse.com |

---

## Support & Help

```bash
# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Test connectivity
docker-compose exec vectordb pg_isready

# Python debugging
python -u tech_analyzer_v2.py /path 2>&1 | tee debug.log

# Get system info
docker system info
```

---

## Version Info

- **System Version**: 2.0
- **Last Updated**: November 7, 2025
- **Status**: Production Ready
- **Python**: 3.12+
- **Docker**: 20+
- **Tested On**: Linux, macOS, Windows (WSL2)

---

## What's Included

✅ Advanced Tech Detection (LLM-powered)
✅ Multi-Package Manager Support
✅ Dynamic Docker-Compose Generation
✅ Intelligent Configuration Engine
✅ Multi-Database Support
✅ Environment-Specific Configs
✅ Azure Cloud Integration
✅ GitHub Codespaces Ready
✅ RAG Optimization
✅ Agentic Data Analytics Stack

---

**Start Now**: `python tech_analyzer_v2.py /path && docker-compose up -d` 🚀

For detailed documentation, see COMPLETE_DEPLOYMENT_GUIDE.md or DYNAMIC_SYSTEM_GUIDE.md
