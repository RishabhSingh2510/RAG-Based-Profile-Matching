"""
vector_store.py - Gemini Embedding Generator & Pinecone Vector Store Integration
----------------------------------------------------------------------------------
This module handles generating 768-dimensional dense vector embeddings using Google
Gemini text-embedding-004/gemini-embedding-001 and indexing/retrieving chunk vectors
in Pinecone with rich metadata.
Includes local persistent vector caching and true batch API calls to stay strictly under rate limits.
"""

import os
import json
import time
import math
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from chunker import ResumeChunk
from init_pinecone import get_pinecone_client, initialize_pinecone_index

load_dotenv()

CACHE_FILE = Path(".embedding_cache.json")


class GeminiEmbedder:
    """
    Embedding generator class using Google Gemini API (gemini-embedding-001).
    Produces 768-dimensional dense floating-point vector representations.
    Includes persistent local caching and batching to strictly respect API rate limits (RPD/RPM/TPM).
    """

    MODEL_NAME = "gemini-embedding-001"
    DIMENSION = 768

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.cache: Dict[str, List[float]] = {}
        self.api_request_count = 0
        self._load_cache()
        self._init_client()

    def _load_cache(self):
        """Loads cached embeddings from local JSON file to save API quota."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
                print(f"[CACHE] Loaded {len(self.cache)} cached vector embeddings from '{CACHE_FILE.name}'.")
            except Exception as e:
                print(f"[WARN] Could not load embedding cache: {e}")
                self.cache = {}

    def _save_cache(self):
        """Saves cached embeddings to local JSON file."""
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"[WARN] Could not save embedding cache: {e}")

    def _init_client(self):
        if not self.api_key or self.api_key.strip() in ["your_gemini_api_key_here", ""]:
            print("[WARN] GEMINI_API_KEY is missing or contains placeholder. Using fallback/cached embedding mode.")
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"[WARN] Failed to initialize Google GenAI Client: {e}. Fallback embedder active.")
            self.client = None

    def _get_text_hash(self, text: str) -> str:
        """Returns SHA-256 hash string for text content."""
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generates a deterministic 768-dim normalized pseudo-embedding for testing when offline."""
        seed_hash = hashlib.sha256(text.encode('utf-8')).digest()
        vector = []
        for i in range(self.DIMENSION):
            val = (seed_hash[i % len(seed_hash)] + i * 17) % 256
            norm_val = (val - 128.0) / 128.0
            vector.append(norm_val)
        
        magnitude = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [round(x / magnitude, 6) for x in vector]

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single string into a 768-dimensional vector, utilizing cache if available.
        """
        if not text or not text.strip():
            return [0.0] * self.DIMENSION

        text_hash = self._get_text_hash(text)
        if text_hash in self.cache:
            return self.cache[text_hash]

        if self.client:
            try:
                self.api_request_count += 1
                res = self.client.models.embed_content(
                    model=self.MODEL_NAME,
                    contents=text,
                    config={"output_dimensionality": self.DIMENSION}
                )
                vec = []
                if hasattr(res, 'embeddings') and len(res.embeddings) > 0:
                    vec = list(res.embeddings[0].values)
                elif hasattr(res, 'embedding') and hasattr(res.embedding, 'values'):
                    vec = list(res.embedding.values)

                if vec and len(vec) == self.DIMENSION:
                    self.cache[text_hash] = vec
                    self._save_cache()
                    return vec
            except Exception as e:
                print(f"[WARN] Gemini embedding API call failed: {e}. Utilizing fallback vector.")

        fallback_vec = self._generate_fallback_embedding(text)
        self.cache[text_hash] = fallback_vec
        self._save_cache()
        return fallback_vec

    def embed_batch(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        """
        Embeds a list of text strings in true API batches to minimize RPD (Requests Per Day).
        E.g., 160 texts embedded in 8 API requests instead of 160 requests!
        """
        results: Dict[int, List[float]] = {}
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        # Check local cache first
        cache_hits = 0
        for idx, text in enumerate(texts):
            text_hash = self._get_text_hash(text)
            if text_hash in self.cache:
                results[idx] = self.cache[text_hash]
                cache_hits += 1
            else:
                uncached_indices.append(idx)
                uncached_texts.append(text)

        print(f"[EMBEDDER] Total: {len(texts)} | Cache Hits: {cache_hits} | API Batches Required: {math.ceil(len(uncached_texts) / batch_size) if uncached_texts else 0}")

        # Process uncached texts in true multi-item API batches
        if uncached_texts and self.client:
            for i in range(0, len(uncached_texts), batch_size):
                batch_text_slice = uncached_texts[i:i + batch_size]
                batch_idx_slice = uncached_indices[i:i + batch_size]

                try:
                    self.api_request_count += 1
                    res = self.client.models.embed_content(
                        model=self.MODEL_NAME,
                        contents=batch_text_slice,
                        config={"output_dimensionality": self.DIMENSION}
                    )
                    
                    batch_embeddings = []
                    if hasattr(res, 'embeddings') and len(res.embeddings) > 0:
                        batch_embeddings = [list(e.values) for e in res.embeddings]

                    if len(batch_embeddings) == len(batch_text_slice):
                        for original_idx, text_content, vec in zip(batch_idx_slice, batch_text_slice, batch_embeddings):
                            results[original_idx] = vec
                            text_h = self._get_text_hash(text_content)
                            self.cache[text_h] = vec
                    else:
                        raise ValueError("Mismatch in returned batch embedding count.")

                except Exception as e:
                    print(f"[WARN] Batch embedding API call failed ({e}). Falling back for batch slice...")
                    for original_idx, text_content in zip(batch_idx_slice, batch_text_slice):
                        vec = self._generate_fallback_embedding(text_content)
                        results[original_idx] = vec
                        self.cache[self._get_text_hash(text_content)] = vec

                # Save updated cache after each batch & apply rate-limiting delay (0.4s)
                self._save_cache()
                time.sleep(0.4)

        # Handle any remaining uncached items if client was offline/failed
        for idx, text in zip(uncached_indices, uncached_texts):
            if idx not in results:
                vec = self.embed_text(text)
                results[idx] = vec

        # Re-assemble in original order
        final_vectors = [results[i] for i in range(len(texts))]
        return final_vectors


class PineconeVectorStore:
    """
    Pinecone Vector Store Interface managing resume chunk indexing and vector similarity queries.
    """

    def __init__(self, index_name: Optional[str] = None):
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "resume-profile-matcher")
        self.index = None
        self.connect()

    def connect(self) -> bool:
        """Connects to or initializes the Pinecone index."""
        self.index = initialize_pinecone_index(index_name=self.index_name)
        return self.index is not None

    def upsert_chunks(self, chunks: List[ResumeChunk], embedder: GeminiEmbedder, batch_size: int = 50) -> Dict[str, Any]:
        """
        Embeds and upserts ResumeChunk objects into Pinecone index with rich payload metadata.
        """
        if not chunks:
            return {"status": "success", "upserted_count": 0, "message": "No chunks provided for upsert."}

        if not self.index:
            if not self.connect():
                return {
                    "status": "dry_run",
                    "upserted_count": 0,
                    "message": "Pinecone index not connected. Operating in dry-run metadata mode."
                }

        print(f"[INFO] Processing embeddings for {len(chunks)} chunks using Gemini {embedder.MODEL_NAME}...")
        texts = [chunk.text for chunk in chunks]
        vectors = embedder.embed_batch(texts, batch_size=20)

        pinecone_vectors = []
        for chunk, vec in zip(chunks, vectors):
            pinecone_vectors.append({
                "id": chunk.chunk_id,
                "values": vec,
                "metadata": {
                    "candidate_id": chunk.candidate_id,
                    "candidate_name": chunk.candidate_name,
                    "resume_path": chunk.resume_path,
                    "section_type": chunk.section_type,
                    "experience_years": float(chunk.experience_years),
                    "skills": chunk.skills_list,
                    "chunk_text": chunk.text
                }
            })

        print(f"[INFO] Upserting {len(pinecone_vectors)} vectors into Pinecone index '{self.index_name}'...")
        upserted_total = 0
        for i in range(0, len(pinecone_vectors), batch_size):
            batch = pinecone_vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                upserted_total += len(batch)
            except Exception as e:
                print(f"[ERROR] Failed to upsert batch {i // batch_size + 1}: {e}")

        return {
            "status": "success",
            "upserted_count": upserted_total,
            "index_name": self.index_name,
            "api_requests_used": embedder.api_request_count,
            "message": f"Successfully upserted {upserted_total} vectors into Pinecone using {embedder.api_request_count} API requests."
        }

    def query_similarity(self, query_vector: List[float], top_k: int = 20, filter_dict: Optional[dict] = None) -> List[Dict[str, Any]]:
        """
        Queries Pinecone index using Cosine Similarity vector search.
        """
        if not self.index:
            print("[WARN] Pinecone index unavailable for similarity search.")
            return []

        try:
            res = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )

            matches = []
            if hasattr(res, 'matches'):
                for m in res.matches:
                    matches.append({
                        "id": m.id,
                        "score": round(float(m.score), 4),
                        "metadata": m.metadata
                    })
            return matches
        except Exception as e:
            print(f"[ERROR] Pinecone similarity query failed: {e}")
            return []


if __name__ == "__main__":
    print("=== Testing Vector Store & Embedder Rate-Limit Optimized Integration ===")
    embedder = GeminiEmbedder()
    test_vec = embedder.embed_text("Senior Python Developer with LangChain and Pinecone experience.")
    print(f"Generated Vector Dimension: {len(test_vec)}")
    print(f"Sample Vector Values (first 5): {test_vec[:5]}")
    print(f"API Requests Consumed: {embedder.api_request_count}")
