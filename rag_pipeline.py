#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, db_name="rag_demo"):
        self.db_name = db_name
        logger.info(f"Initializing RAG Pipeline (Database: {self.db_name})")
    
    def execute_query(self, query: str) -> list:
        try:
            cmd = ["sudo", "-u", "postgres", "psql", "-d", self.db_name, "-t", "-A", "-F|", "-c", query]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Query error: {result.stderr}")
                return []
            lines = result.stdout.strip().split("\n")
            return [line.split("|") for line in lines if line]
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return []
    
    def get_statistics(self) -> dict:
        logger.info("Fetching database statistics...")
        results = self.execute_query("SELECT * FROM v_document_statistics;")
        if results and len(results) > 0:
            row = results[0]
            return {
                "total_documents": int(row[0]) if row[0] else 0,
                "total_chunks": int(row[1]) if row[1] else 0,
                "total_embeddings": int(row[2]) if row[2] else 0,
                "database": self.db_name
            }
        return {}
    
    def ingest_files(self, file_paths: list) -> dict:
        results = {"total": len(file_paths), "ingested": 0, "chunks": 0, "files": []}
        for fp in file_paths:
            try:
                path = Path(fp)
                if not path.exists():
                    continue
                content = path.read_text(encoding="utf-8", errors="ignore")
                chunks = len(content) // 1000 + 1
                title = path.name.replace("'", "''")
                content_short = content[:5000].replace("'", "''")
                query = f"INSERT INTO documents (title, content, source_type) VALUES (''{title}'', ''{content_short}...'', ''file'');"
                self.execute_query(query)
                logger.info(f"✅ Ingested: {path.name}")
                results["ingested"] += 1
                results["chunks"] += chunks
                results["files"].append({"name": path.name, "chunks": chunks})
            except Exception as e:
                logger.error(f"Error: {e}")
        return results
    
    def search_documents(self, query: str) -> list:
        logger.info(f"Searching: {query}")
        pattern = query.replace("'", "''")
        sql = f"SELECT title, file_path FROM documents WHERE content ILIKE ''%{pattern}%'' LIMIT 5;"
        results = self.execute_query(sql)
        return [{"title": r[0], "file": r[1]} for r in results if len(r) >= 2]
    
    def export_config(self):
        config = {"database": self.db_name, "stats": self.get_statistics()}
        with open("rag_config.json", "w") as f:
            json.dump(config, f, indent=2)
        logger.info("Config exported to rag_config.json")

def main():
    print("\n" + "="*70)
    print("🚀 RAG PIPELINE - PostgreSQL + pgvector".center(70))
    print("="*70 + "\n")
    
    pipeline = RAGPipeline()
    
    print("📊 Database Statistics:")
    stats = pipeline.get_statistics()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    print("\n🔄 Ingesting Files...")
    root = Path("/home/yuvaraj/Projects/Claude Code VS Code Extension/claude-skill-demo-project/hello-world")
    files = list(root.glob("*.md")) + list(root.glob("*.txt"))
    if files:
        res = pipeline.ingest_files([str(f) for f in files[:2]])
        print(f"✅ Ingested: {res['ingested']} files, {res['chunks']} chunks")
    
    print("\n📊 Updated Statistics:")
    stats = pipeline.get_statistics()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    print("\n🔍 Sample Searches:")
    for q in ["RAG", "database"]:
        r = pipeline.search_documents(q)
        print(f"\n   Query: ''{q}''")
        for item in r:
            print(f"      • {item['title']}")
    
    print("\n💾 Exporting Configuration...")
    pipeline.export_config()
    
    print("\n" + "="*70)
    print("✅ RAG PIPELINE COMPLETE".center(70))
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
