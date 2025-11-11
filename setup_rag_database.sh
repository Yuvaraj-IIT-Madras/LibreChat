#!/bin/bash
# RAG Database Setup Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== RAG Database Setup ==========${NC}\n"

# Step 1: Create RAG database
echo -e "${YELLOW}Step 1: Creating RAG database...${NC}"
sudo -u postgres createdb rag_demo 2>/dev/null || echo "Database rag_demo already exists"

# Step 2: Create extensions
echo -e "${YELLOW}Step 2: Creating PostgreSQL extensions...${NC}"
sudo -u postgres psql rag_demo << EOF
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF

# Step 3: Create tables
echo -e "${YELLOW}Step 3: Creating RAG tables...${NC}"
sudo -u postgres psql rag_demo << 'EOF'
-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_url VARCHAR(2000),
    source_type VARCHAR(100),
    file_path VARCHAR(2000),
    document_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);
CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

-- Document chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_length INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);

-- Embeddings table (768-dimensional vectors)
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(768),
    model_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model_name);
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops);

-- Queries table
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    session_id VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);

-- Search results table
CREATE TABLE IF NOT EXISTS search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks(id),
    relevance_score FLOAT,
    rank INTEGER,
    was_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_results_query_id ON search_results(query_id);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- Conversation messages table
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20),
    message_text TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON conversation_messages(conversation_id);

-- Ingestion logs table
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    status VARCHAR(50),
    source_path VARCHAR(2000),
    total_chunks INTEGER,
    chunks_embedded INTEGER,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_ingestion_logs_status ON ingestion_logs(status);

-- Create sample view
CREATE OR REPLACE VIEW v_document_statistics AS
SELECT 
    COUNT(DISTINCT d.id) as total_documents,
    COUNT(DISTINCT dc.id) as total_chunks,
    COUNT(DISTINCT e.id) as total_embeddings
FROM documents d
LEFT JOIN document_chunks dc ON d.id = dc.document_id
LEFT JOIN embeddings e ON dc.id = e.chunk_id
WHERE d.is_active = TRUE;

EOF

# Step 4: Insert sample data
echo -e "${YELLOW}Step 4: Inserting sample documents...${NC}"
sudo -u postgres psql rag_demo << 'EOF'
INSERT INTO documents (title, content, source_type, metadata) VALUES
(
    'Introduction to RAG Systems',
    'Retrieval-Augmented Generation (RAG) is a powerful technique that combines large language models with information retrieval. RAG systems allow language models to access external knowledge bases, enabling more accurate and contextually relevant responses. The RAG pipeline typically consists of three main components: a retriever that fetches relevant documents, a reader that processes them, and a generator that produces the final response.',
    'documentation',
    '{"category": "ai", "language": "en"}'::jsonb
),
(
    'PostgreSQL Vector Database',
    'PostgreSQL with pgvector extension provides native vector data type and operations. pgvector stores vectors as a new SQL data type, allowing you to store embedding vectors directly in your database. The extension supports L2 distance, inner product, and cosine distance operations. It also provides IVFFLAT and HNSW index types for efficient similarity search.',
    'documentation',
    '{"category": "database", "language": "en"}'::jsonb
),
(
    'Building Semantic Search',
    'Semantic search goes beyond keyword matching by understanding the intent and meaning behind a user query. By converting both documents and queries into dense vector embeddings, semantic search can find documents with similar meaning even if they do not share keywords. Modern embedding models can create high-quality embeddings that capture semantic relationships.',
    'documentation',
    '{"category": "search", "language": "en"}'::jsonb
),
(
    'Docker Compose for Local Development',
    'Docker Compose simplifies multi-container Docker applications. With a single compose file, you can define all services, networks, and volumes needed for your application. This is particularly useful for RAG systems that require PostgreSQL, a search index, a cache layer, and the application server.',
    'documentation',
    '{"category": "devops", "language": "en"}'::jsonb
),
(
    'LLM Integration Best Practices',
    'When integrating large language models into your application, consider API rate limits, token costs, latency requirements, and error handling. Many LLM providers offer async APIs for better throughput. Implement caching strategies to avoid repeated API calls for similar queries.',
    'documentation',
    '{"category": "ai", "language": "en"}'::jsonb
),
(
    'Vector Similarity Metrics',
    'Different similarity metrics serve different purposes. Cosine similarity measures the angle between vectors and is robust to magnitude differences. Euclidean (L2) distance measures the straight-line distance and is useful when magnitude matters.',
    'documentation',
    '{"category": "ml", "language": "en"}'::jsonb
);

-- Insert sample chunks
INSERT INTO document_chunks (document_id, chunk_index, chunk_text, chunk_length) 
SELECT id, 1, content, char_length(content)
FROM documents
WHERE title = 'Introduction to RAG Systems' LIMIT 1;

SELECT 'Setup complete!' as status;
EOF

# Step 5: Display status
echo -e "\n${YELLOW}Step 5: Verifying setup...${NC}"
sudo -u postgres psql rag_demo << 'EOF'
SELECT * FROM v_document_statistics;
EOF

echo -e "\n${GREEN}========== RAG Database Setup Complete ==========${NC}"
echo -e "${GREEN}Database: rag_demo${NC}"
echo -e "${GREEN}Host: localhost${NC}"
echo -e "${GREEN}Port: 5432${NC}"
echo -e "${GREEN}User: postgres${NC}"
echo ""
echo -e "${BLUE}Connection string:${NC}"
echo "postgresql://postgres@localhost:5432/rag_demo"
