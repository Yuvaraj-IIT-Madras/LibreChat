import os
import argparse
import psycopg2
import numpy as np
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from pgvector.psycopg2 import register_vector

# --- Database Configuration ---
DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"
DB_HOST = "172.20.0.2" # Using the container's internal IP
DB_PORT = "5432"
TABLE_NAME = "documents"

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    register_vector(conn)
    return conn

def query_rag_db(query_text, top_k=5):
    """Queries the RAG database for the most similar documents."""
    # Load environment variables and configure API key
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.getenv("GOOGLE_KEY")
    if not api_key:
        raise ValueError("GOOGLE_KEY not found in .env file")
    genai.configure(api_key=api_key)

    # 1. Generate embedding for the query
    print("Generating embedding for your query...")
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    query_embedding = embeddings_model.embed_query(query_text)
    print("Embedding generated.")

    # 2. Connect to the database and perform similarity search
    conn = None
    results = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Using cosine similarity (1 - cosine distance)
        # The vector column is named 'embedding'
        # The <=> operator calculates cosine distance
        cur.execute(
            f"""
            SELECT source, content, 1 - (embedding <=> %s) AS similarity
            FROM {TABLE_NAME}
            ORDER BY similarity DESC
            LIMIT %s;
            """,
            (np.array(query_embedding), top_k)
        )

        results = cur.fetchall()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

    return results

def main():
    """Main function to run the query script."""
    parser = argparse.ArgumentParser(description="Query the RAG database with a text string.")
    parser.add_argument("query", type=str, help="The text query to search for.")
    parser.add_argument("--top_k", type=int, default=5, help="Number of top results to return.")
    args = parser.parse_args()

    print(f"Querying for: '{args.query}'")
    results = query_rag_db(args.query, args.top_k)

    if results:
        print(f"\n--- Top {len(results)} results ---")
        for i, (source, content, similarity) in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"  Source: {source}")
            print(f"  Similarity: {similarity:.4f}")
            print(f"  Content: {content}\n")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
