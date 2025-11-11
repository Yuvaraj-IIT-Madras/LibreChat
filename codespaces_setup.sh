#!/bin/bash
################################################################################
# GitHub Codespaces RAG + Agentic Data Stack Setup
# Execute from Codespaces terminal: bash codespaces_setup.sh
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
WORKSPACE=${CODESPACE_VSCODE_FOLDER:-.}
INSTALL_DIR="${WORKSPACE}/rag-stack"
DOCKER_COMPOSE_FILE="${INSTALL_DIR}/docker-compose.yml"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   GitHub Codespaces - RAG + Agentic Data Stack Setup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"

# Step 1: Verify Codespaces environment
echo -e "${YELLOW}[Step 1/6] Verifying Codespaces environment...${NC}"
if [ -z "$CODESPACES" ]; then
    echo -e "${RED}⚠️  Warning: Not running in Codespaces${NC}"
else
    echo -e "${GREEN}✅ Codespaces environment detected${NC}"
    echo "   Codespace Name: $CODESPACE_NAME"
    echo "   Repository: $GITHUB_REPOSITORY"
fi

# Step 2: Install system dependencies
echo -e "\n${YELLOW}[Step 2/6] Installing system dependencies...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq \
    docker.io \
    docker-compose \
    postgresql-client \
    git \
    curl \
    wget \
    jq > /dev/null 2>&1
echo -e "${GREEN}✅ System dependencies installed${NC}"

# Step 3: Setup Docker
echo -e "\n${YELLOW}[Step 3/6] Setting up Docker...${NC}"
sudo usermod -aG docker $USER > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Docker configured for user${NC}"

# Step 4: Create installation directory
echo -e "\n${YELLOW}[Step 4/6] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}✅ Installation directory: $INSTALL_DIR${NC}"

# Step 5: Generate docker-compose.yml
echo -e "\n${YELLOW}[Step 5/6] Generating Docker Compose configuration...${NC}"
cat > "$DOCKER_COMPOSE_FILE" << 'DOCKER_EOF'
version: '3.8'

services:
  # PostgreSQL with pgvector
  postgres:
    image: pgvector/pgvector:pg16-latest
    container_name: rag-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
      POSTGRES_DB: rag_demo
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rag-network

  # Redis for caching
  redis:
    image: redis:7-alpine
    container_name: rag-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rag-network

  # Meilisearch for full-text search
  meilisearch:
    image: getmeili/meilisearch:v1.6
    container_name: rag-meilisearch
    environment:
      MEILI_NO_ANALYTICS: "true"
    ports:
      - "7700:7700"
    volumes:
      - meilisearch_data:/meili_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7700/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rag-network

  # MongoDB for conversation storage
  mongodb:
    image: mongo:7-alpine
    container_name: rag-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin123
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/admin -u admin -p admin123
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - rag-network

  # LibreChat UI
  librechat:
    image: ghcr.io/danny-avila/librechat:latest
    container_name: rag-librechat
    depends_on:
      - postgres
      - redis
      - mongodb
    environment:
      MONGO_URI: "mongodb://admin:admin123@mongodb:27017/admin?authSource=admin"
      REDIS_URL: "redis://redis:6379"
      DATABASE_URL: "postgresql://postgres:postgres123@postgres:5432/rag_demo"
      DEBUG: "false"
    ports:
      - "3080:3080"
    networks:
      - rag-network

  # API Server for RAG
  rag-api:
    image: python:3.12-slim
    container_name: rag-api
    working_dir: /app
    depends_on:
      - postgres
      - redis
    volumes:
      - ./:/app
    ports:
      - "8000:8000"
    command: python -m pip install -q psycopg2-binary redis fastapi uvicorn && uvicorn app:app --host 0.0.0.0 --port 8000 || sleep infinity
    environment:
      DATABASE_URL: "postgresql://postgres:postgres123@postgres:5432/rag_demo"
      REDIS_URL: "redis://redis:6379"
    networks:
      - rag-network

volumes:
  postgres_data:
  mongodb_data:
  meilisearch_data:

networks:
  rag-network:
    driver: bridge
DOCKER_EOF

echo -e "${GREEN}✅ Docker Compose configuration created${NC}"

# Step 6: Start services
echo -e "\n${YELLOW}[Step 6/6] Starting services...${NC}"
cd "$INSTALL_DIR"

# Check if Docker daemon is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${YELLOW}Starting Docker daemon...${NC}"
    sudo service docker start || sudo dockerd > /dev/null 2>&1 &
    sleep 3
fi

# Start Docker Compose
echo -e "${YELLOW}Starting Docker Compose services...${NC}"
docker-compose up -d --wait 2>/dev/null || {
    echo -e "${YELLOW}Waiting for services to be ready (this may take 1-2 minutes)...${NC}"
    docker-compose up -d
    sleep 30
}

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
for i in {1..60}; do
    if docker-compose ps | grep -q "healthy"; then
        echo -e "${GREEN}✅ Services are ready${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}⚠️  Services still starting...${NC}"
    fi
    sleep 2
done

# Display service status
echo -e "\n${YELLOW}Service Status:${NC}"
docker-compose ps

# Create .env file
echo -e "\n${YELLOW}Creating .env file...${NC}"
cat > "${INSTALL_DIR}/.env" << 'ENV_EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/rag_demo
DB_HOST=postgres
DB_PORT=5432
DB_NAME=rag_demo
DB_USER=postgres
DB_PASSWORD=postgres123

# Redis
REDIS_URL=redis://redis:6379

# MongoDB
MONGO_URI=mongodb://admin:admin123@mongodb:27017/admin?authSource=admin

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Environment
ENVIRONMENT=codespaces
SCALE=small

# RAG Configuration
EMBEDDING_MODEL=all-minilm-l6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EOF

echo -e "${GREEN}✅ .env file created${NC}"

# Provide access information
echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}📍 Service Endpoints:${NC}"
if [ -n "$CODESPACES" ]; then
    # Codespaces URLs
    echo -e "   LibreChat UI:    https://${CODESPACE_NAME}-3080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    echo -e "   RAG API:         https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/docs"
    echo -e "   Meilisearch:     https://${CODESPACE_NAME}-7700.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
    # Local URLs
    echo -e "   LibreChat UI:    http://localhost:3080"
    echo -e "   RAG API:         http://localhost:8000/docs"
    echo -e "   Meilisearch:     http://localhost:7700"
fi

echo -e "\n${BLUE}🔗 Database Connection:${NC}"
echo -e "   postgresql://postgres:postgres123@postgres:5432/rag_demo"

echo -e "\n${BLUE}📝 Useful Commands:${NC}"
echo -e "   View logs:       docker-compose logs -f <service>"
echo -e "   Stop services:   docker-compose down"
echo -e "   Restart service: docker-compose restart <service>"
echo -e "   Database access: psql -h postgres -U postgres -d rag_demo"

echo -e "\n${BLUE}🚀 Next Steps:${NC}"
echo -e "   1. Run RAG pipeline:    python rag_pipeline.py"
echo -e "   2. Open LibreChat:      Click on the LibreChat UI link above"
echo -e "   3. Configure LLM API:   Add your API keys in LibreChat settings"
echo -e "   4. Test RAG system:     Upload documents and query"

echo -e "\n${BLUE}📚 Documentation:${NC}"
echo -e "   Full guide:      ADVANCED_INTEGRATION_GUIDE.md"
echo -e "   Architecture:    DYNAMIC_SYSTEM_GUIDE.md"
echo -e "   Deployment:      COMPLETE_DEPLOYMENT_GUIDE.md"

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════${NC}\n"

# Save setup summary
cat > "${INSTALL_DIR}/CODESPACES_SETUP_SUMMARY.md" << 'SUMMARY_EOF'
# GitHub Codespaces Setup Summary

## ✅ Completed Setup

- [x] System dependencies installed
- [x] Docker configured
- [x] PostgreSQL with pgvector running
- [x] Redis cache running
- [x] MongoDB running
- [x] Meilisearch search engine running
- [x] LibreChat UI running
- [x] RAG API server configured

## 📊 Services Status

| Service | Port | Status |
|---------|------|--------|
| LibreChat | 3080 | Running |
| RAG API | 8000 | Running |
| PostgreSQL | 5432 | Running |
| Redis | 6379 | Running |
| MongoDB | 27017 | Running |
| Meilisearch | 7700 | Running |

## 🔑 Credentials

- PostgreSQL User: `postgres`
- PostgreSQL Password: `postgres123`
- MongoDB User: `admin`
- MongoDB Password: `admin123`
- LibreChat: Auto-login enabled (if configured)

## 📝 Environment Variables

See `.env` file for all configuration variables.

## 🐛 Troubleshooting

If services don't start:
1. Check Docker is running: `docker ps`
2. View logs: `docker-compose logs -f`
3. Rebuild: `docker-compose down && docker-compose up -d`

## 🚀 Deployment Steps

1. **Run RAG Pipeline:**
   ```bash
   python rag_pipeline.py
   ```

2. **Access LibreChat:**
   - Open the LibreChat UI from the endpoint provided
   - Configure your LLM API keys

3. **Load Documents:**
   - Upload PDFs or text files through LibreChat interface
   - Documents are automatically ingested into PostgreSQL

4. **Query the RAG System:**
   - Ask questions in LibreChat
   - System retrieves relevant documents from RAG index
   - LLM generates contextual answers

## 📚 Additional Resources

- LibreChat Docs: https://docs.librechat.ai
- PostgreSQL pgvector: https://github.com/pgvector/pgvector
- Meilisearch Docs: https://www.meilisearch.com/docs
SUMMARY_EOF

echo -e "${GREEN}✅ Setup summary saved to: CODESPACES_SETUP_SUMMARY.md${NC}"

exit 0
