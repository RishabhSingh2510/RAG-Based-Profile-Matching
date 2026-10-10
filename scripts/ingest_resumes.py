"""
ingest_resumes.py - Batch Resume Vector Indexing Script
-------------------------------------------------------
Reads all 33 sample resumes (.pdf, .docx, .txt) from ./resumes/,
parses them into section-aware chunks via chunker.py,
generates 768-dim embeddings via Gemini text-embedding-004,
and upserts them into the Pinecone vector database.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Ensure src directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from chunker import SectionAwareChunker
from vector_store import GeminiEmbedder, PineconeVectorStore

load_dotenv()


def run_ingestion(resumes_dir: str = "resumes"):
    print("=" * 65)
    print("     RAG Resume Profile Matcher - Resume Vector Ingestion")
    print("=" * 65)

    if not os.path.exists(resumes_dir):
        print(f"[ERROR] Resumes directory '{resumes_dir}' not found.")
        sys.exit(1)

    print(f"\n[STEP 1] Parsing & Chunking resumes from '{resumes_dir}'...")
    chunker = SectionAwareChunker()
    chunks = chunker.chunk_directory(resumes_dir)
    
    unique_candidates = {c.candidate_id for c in chunks}
    print(f"[INFO] Generated {len(chunks)} section chunks across {len(unique_candidates)} unique candidates.")

    print("\n[STEP 2] Initializing Gemini Embedder (text-embedding-004)...")
    embedder = GeminiEmbedder()

    print("\n[STEP 3] Connecting to Pinecone Vector Database...")
    store = PineconeVectorStore()

    print("\n[STEP 4] Executing batch embedding and vector store upsert...")
    start_time = time.time()
    result = store.upsert_chunks(chunks, embedder)
    elapsed = round(time.time() - start_time, 2)

    print("\n" + "=" * 65)
    print("                  INGESTION SUMMARY REPORT")
    print("=" * 65)
    total_files = len([f for f in os.listdir(resumes_dir) if f.endswith(('.pdf', '.docx', '.txt'))])
    print(f"Status:             {result.get('status')}")
    print(f"Resumes Processed:  {total_files}")
    print(f"Unique Candidates:  {len(unique_candidates)}")
    print(f"Total Vector Chunks: {len(chunks)}")
    print(f"Vectors Upserted:   {result.get('upserted_count')}")
    print(f"Target Index:       {result.get('index_name')}")
    print(f"Time Elapsed:       {elapsed} seconds")
    print(f"Details:            {result.get('message')}")
    print("=" * 65)

if __name__ == "__main__":
    run_ingestion()
