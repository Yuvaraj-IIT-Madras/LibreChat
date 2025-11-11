import os
import argparse
import psycopg2
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    CSVLoader,
    PythonLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from pgvector.psycopg2 import register_vector
import numpy as np

# --- Database Configuration ---
DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"
DB_HOST = "vectordb"
DB_PORT = "5432"
TABLE_NAME = "documents"

# --- File Handlers ---
DOCUMENT_LOADERS = {
    ".txt": TextLoader,
    ".pdf": PyPDFLoader,
    ".csv": CSVLoader,
    ".py": PythonLoader,
    ".html": UnstructuredHTMLLoader,
    ".md": UnstructuredMarkdownLoader,
    ".js": TextLoader,
    ".ts": TextLoader,
    ".java": TextLoader,
}

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

def setup_database():
    """Sets up the database table with pgvector extension."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        source TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding VECTOR(768)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database setup complete.")

def load_ignore_patterns(ignore_file_path):
    """Loads ignore patterns from a .documentignore file."""
    if not os.path.exists(ignore_file_path):
        return PathSpec.from_lines(GitWildMatchPattern, [])
    with open(ignore_file_path, 'r') as f:
        patterns = f.readlines()
    return PathSpec.from_lines(GitWildMatchPattern, patterns)

def process_directory(directory_path, ignore_spec):
    """Recursively finds, loads, and splits documents from a directory."""
    all_docs = []
    for root, _, files in os.walk(directory_path):
        # Create a relative path from the directory_path for matching
        relative_root = os.path.relpath(root, directory_path)
        if ignore_spec.match_file(relative_root):
            print(f"Ignoring directory: {root}")
            continue

        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, directory_path)
            
            if ignore_spec.match_file(relative_file_path):
                continue

            ext = os.path.splitext(file)[1].lower()
            try:
                if ext in DOCUMENT_LOADERS:
                    LoaderClass = DOCUMENT_LOADERS[ext]
                    # Loaders that accept encoding
                    if ext in [".txt", ".md", ".js", ".ts", ".java", ".html", ".csv"]:
                        loader = LoaderClass(file_path, encoding='utf-8')
                    # Loaders that do not
                    else:
                        loader = LoaderClass(file_path)
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata['source'] = file_path
                    all_docs.extend(docs)
                    print(f"Loaded: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)
    return splits

def main(directory_path):
    """Main function to run the ingestion pipeline."""
    # Load environment variables from the .env file in the current directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    api_key = os.getenv("GOOGLE_KEY")
    if not api_key:
        raise ValueError("GOOGLE_KEY not found in .env file")
    genai.configure(api_key=api_key)

    # 1. Setup Database
    setup_database()

    # 2. Load Ignore Patterns
    ignore_file_path = os.path.join(os.path.dirname(__file__), '.documentignore')
    ignore_spec = load_ignore_patterns(ignore_file_path)
    print("Loaded ignore patterns.")

    # 3. Process Documents
    print(f"Starting to process directory: {directory_path}")
    splits = process_directory(directory_path, ignore_spec)
    if not splits:
        print("No documents to process.")
        return
    print(f"Created {len(splits)} document splits.")

    # 4. Create Embeddings
    print("Creating embeddings with Gemini...")
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    
    # Get embeddings in batches
    contents = [doc.page_content for doc in splits]
    embeddings = embeddings_model.embed_documents(contents)
    print(f"Successfully created {len(embeddings)} embeddings.")

    # 5. Store in Database
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("Storing documents and embeddings in the database...")
    for i, doc in enumerate(splits):
        source = doc.metadata.get('source', 'Unknown')
        content = doc.page_content
        embedding = np.array(embeddings[i])
        cur.execute(
            f"INSERT INTO {TABLE_NAME} (source, content, embedding) VALUES (%s, %s, %s)",
            (source, content, embedding)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully stored {len(splits)} documents in the database.")
    print("Ingestion complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents from a directory into a vector database.")
    parser.add_argument("path", type=str, help="The path to the directory to ingest.")
    args = parser.parse_args()
    main(args.path)
