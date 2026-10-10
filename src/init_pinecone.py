"""
init_pinecone.py - Pinecone Vector Database Initializer
------------------------------------------------------
This module initializes the Pinecone serverless index configured for
768-dimensional dense vector embeddings (Google Gemini text-embedding-004)
using Cosine Similarity distance metric.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_pinecone_client():
    """Validates API key and initializes Pinecone client instance."""
    api_key = os.getenv("PINECONE_API_KEY")
    
    if not api_key or api_key.strip() in ["your_pinecone_api_key_here", ""]:
        print("[ERROR] PINECONE_API_KEY is not set or contains default placeholder.")
        print("        Please obtain a free API key from https://app.pinecone.io/ and update your .env file.")
        return None, None
        
    try:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=api_key)
        return pc, ServerlessSpec
    except ImportError:
        print("[ERROR] 'pinecone' package is not installed in your current environment.")
        print("        Please run: pip install pinecone")
        return None, None
    except Exception as e:
        print(f"[ERROR] Failed to initialize Pinecone client: {e}")
        return None, None


def initialize_pinecone_index(
    index_name: str = None,
    dimension: int = 768,
    metric: str = "cosine",
    cloud: str = "aws",
    region: str = "us-east-1"
):
    """
    Creates or connects to a Pinecone Serverless Index.
    
    Parameters:
    - index_name (str): Name of the Pinecone index (default: from .env PINECONE_INDEX_NAME or 'resume-profile-matcher')
    - dimension (int): Vector dimension (default: 768 for Gemini text-embedding-004)
    - metric (str): Distance metric (default: 'cosine')
    - cloud (str): Serverless cloud provider (default: 'aws')
    - region (str): Serverless cloud region (default: 'us-east-1')
    
    Returns:
    - index: Active Pinecone Index instance or None if setup failed.
    """
    if not index_name:
        index_name = os.getenv("PINECONE_INDEX_NAME", "resume-profile-matcher")
        
    pc, ServerlessSpec = get_pinecone_client()
    if not pc:
        return None

    print(f"[INFO] Checking Pinecone index status for: '{index_name}'...")
    
    try:
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"[INFO] Index '{index_name}' not found. Creating Pinecone Serverless Index...")
            print(f"       - Dimension: {dimension}")
            print(f"       - Metric: {metric}")
            print(f"       - Cloud/Region: {cloud}/{region}")
            
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            
            print("[INFO] Waiting for index initialization to complete...")
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(2)
                
            print(f"[SUCCESS] Pinecone Index '{index_name}' created and ready!")
        else:
            print(f"[INFO] Index '{index_name}' already exists.")
            
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        print(f"[INFO] Pinecone Index Stats:")
        print(f"       - Total Vectors Indexed: {stats.total_vector_count}")
        print(f"       - Vector Dimension: {stats.dimension}")
        return index

    except Exception as e:
        print(f"[ERROR] An error occurred while initializing Pinecone index: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("      RAG Resume Matcher - Pinecone Index Initialization")
    print("=" * 60)
    idx = initialize_pinecone_index()
    if idx:
        print("\n[COMPLETE] Pinecone initialization complete.")
    else:
        print("\n[ACTION REQUIRED] Update PINECONE_API_KEY in .env to complete setup.")
