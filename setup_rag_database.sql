-- RAG Database Setup with pgvector
-- This script creates the necessary tables and extensions for RAG pipeline

-- Create extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Create RAG database
CREATE DATABASE rag_demo WITH TEMPLATE template0;

-- Connect to rag_demo database
\c rag_demo;

-- Create vector extension in rag_demo
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- ====== DOCUMENTS TABLE ======
-- Stores the original documents/chunks for RAG
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_url VARCHAR(2000),
    source_type VARCHAR(100), -- 'web', 'file', 'database', etc.
    file_path VARCHAR(2000),
    document_hash VARCHAR(64), -- SHA256 hash for deduplication
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);
CREATE INDEX IF NOT EXISTS idx_documents_source_type ON documents(source_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(document_hash);
CREATE INDEX IF NOT EXISTS idx_documents_active ON documents(is_active);

-- ====== DOCUMENT_CHUNKS TABLE ======
-- Stores chunked documents for embedding
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_length INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_index ON document_chunks(chunk_index);

-- ====== EMBEDDINGS TABLE ======
-- Stores vector embeddings (768-dimensional for many models, 1536 for OpenAI)
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    embedding vector(768), -- 768-dim for models like all-minilm-l6-v2
    model_name VARCHAR(100), -- e.g., 'all-minilm-l6-v2', 'text-embedding-3-large'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model_name);
-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ====== QUERIES TABLE ======
-- Stores user queries for analysis and improvement
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50), -- 'semantic', 'keyword', 'hybrid'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    session_id VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);

-- ====== SEARCH_RESULTS TABLE ======
-- Stores search results for analytics
CREATE TABLE IF NOT EXISTS search_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID REFERENCES queries(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES document_chunks(id),
    relevance_score FLOAT,
    rank INTEGER,
    was_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_search_results_query_id ON search_results(query_id);
CREATE INDEX IF NOT EXISTS idx_search_results_chunk_id ON search_results(chunk_id);

-- ====== CONVERSATIONS TABLE ======
-- Stores chat history for context
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- ====== CONVERSATION_MESSAGES TABLE ======
-- Stores individual messages in a conversation
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20), -- 'user', 'assistant', 'system'
    message_text TEXT NOT NULL,
    sources JSONB, -- Array of referenced documents
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON conversation_messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON conversation_messages(created_at);

-- ====== INGESTION_LOGS TABLE ======
-- Tracks document ingestion for monitoring
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    source_path VARCHAR(2000),
    total_chunks INTEGER,
    chunks_embedded INTEGER,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_ingestion_logs_status ON ingestion_logs(status);
CREATE INDEX IF NOT EXISTS idx_ingestion_logs_document_id ON ingestion_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_logs_created_at ON ingestion_logs(completed_at);

-- ====== DEMO DATA ======
-- Insert sample documents for testing

INSERT INTO documents (title, content, source_type, metadata) VALUES
(
    'Introduction to RAG Systems',
    'Retrieval-Augmented Generation (RAG) is a powerful technique that combines large language models with information retrieval. RAG systems allow language models to access external knowledge bases, enabling more accurate and contextually relevant responses. The RAG pipeline typically consists of three main components: a retriever that fetches relevant documents, a reader that processes them, and a generator that produces the final response.',
    'documentation',
    '{"category": "ai", "language": "en"}'::jsonb
),
(
    'PostgreSQL Vector Database',
    'PostgreSQL with pgvector extension provides native vector data type and operations. pgvector stores vectors as a new SQL data type, allowing you to store embedding vectors directly in your database. The extension supports L2 distance, inner product, and cosine distance operations. It also provides IVFFLAT and HNSW index types for efficient similarity search over high-dimensional vectors.',
    'documentation',
    '{"category": "database", "language": "en"}'::jsonb
),
(
    'Building Semantic Search',
    'Semantic search goes beyond keyword matching by understanding the intent and meaning behind a user query. By converting both documents and queries into dense vector embeddings, semantic search can find documents with similar meaning even if they don\'t share keywords. Modern embedding models like BERT, GPT-2, and proprietary models from OpenAI can create high-quality embeddings that capture semantic relationships.',
    'documentation',
    '{"category": "search", "language": "en"}'::jsonb
),
(
    'Docker Compose for Local Development',
    'Docker Compose simplifies multi-container Docker applications. With a single compose file, you can define all services, networks, and volumes needed for your application. This is particularly useful for RAG systems that require PostgreSQL, a search index like Meilisearch or Elasticsearch, a cache layer like Redis, and the application server itself. Docker Compose ensures consistent environments across development, testing, and production.',
    'documentation',
    '{"category": "devops", "language": "en"}'::jsonb
),
(
    'LLM Integration Best Practices',
    'When integrating large language models into your application, consider API rate limits, token costs, latency requirements, and error handling. Many LLM providers offer async APIs for better throughput. Implement caching strategies to avoid repeated API calls for similar queries. Monitor token usage and costs. Use prompt engineering techniques to optimize model performance for your specific use case.',
    'documentation',
    '{"category": "ai", "language": "en"}'::jsonb
),
(
    'Vector Similarity Metrics',
    'Different similarity metrics serve different purposes. Cosine similarity measures the angle between vectors and is robust to magnitude differences. Euclidean (L2) distance measures the straight-line distance and is useful when magnitude matters. Inner product is computationally efficient and works well with normalized vectors. HNSW indexes provide approximate nearest neighbor search with excellent performance characteristics.',
    'documentation',
    '{"category": "ml", "language": "en"}'::jsonb
);

-- Insert sample chunks for the first document
INSERT INTO document_chunks (document_id, chunk_index, chunk_text, chunk_length) 
SELECT 
    (SELECT id FROM documents WHERE title = 'Introduction to RAG Systems' LIMIT 1),
    1,
    'Retrieval-Augmented Generation (RAG) is a powerful technique that combines large language models with information retrieval.',
    114;

INSERT INTO document_chunks (document_id, chunk_index, chunk_text, chunk_length) 
SELECT 
    (SELECT id FROM documents WHERE title = 'Introduction to RAG Systems' LIMIT 1),
    2,
    'RAG systems allow language models to access external knowledge bases, enabling more accurate and contextually relevant responses.',
    118;

-- Create sample views for common queries
CREATE OR REPLACE VIEW v_document_statistics AS
SELECT 
    COUNT(DISTINCT d.id) as total_documents,
    COUNT(DISTINCT dc.id) as total_chunks,
    COUNT(DISTINCT e.id) as total_embeddings,
    AVG(dc.chunk_length) as avg_chunk_length,
    MAX(dc.chunk_length) as max_chunk_length,
    MIN(dc.chunk_length) as min_chunk_length
FROM documents d
LEFT JOIN document_chunks dc ON d.id = dc.document_id
LEFT JOIN embeddings e ON dc.id = e.chunk_id
WHERE d.is_active = TRUE;

-- Create sample stored procedure for similarity search
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(768),
    similarity_threshold FLOAT DEFAULT 0.7,
    limit_results INT DEFAULT 5
)
RETURNS TABLE(
    chunk_id UUID,
    chunk_text TEXT,
    document_title VARCHAR,
    similarity_score FLOAT,
    rank INT
) AS $$
    SELECT 
        e.chunk_id,
        dc.chunk_text,
        d.title,
        1 - (e.embedding <=> query_embedding) as similarity_score,
        ROW_NUMBER() OVER (ORDER BY e.embedding <=> query_embedding) as rank
    FROM embeddings e
    JOIN document_chunks dc ON e.chunk_id = dc.id
    JOIN documents d ON dc.document_id = d.id
    WHERE d.is_active = TRUE
    AND (1 - (e.embedding <=> query_embedding)) > similarity_threshold
    ORDER BY similarity_score DESC
    LIMIT limit_results;
$$ LANGUAGE SQL;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Display summary
\echo '====== RAG Database Setup Complete ======'
\echo 'Tables created:'
\dt
\echo ''
\echo 'Extensions installed:'
\dx
\echo ''
\echo 'Sample statistics:'
SELECT * FROM v_document_statistics;
