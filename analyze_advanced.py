import json
import os
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

CACHE_FILE = "document_cache.json"

# --- NEW: Cache Management Functions ---
def load_cache():
    """Loads the database of previously processed files."""
    if os.path.exists(CACHE_FILE):
        with  open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache_data):
    """Saves the processed data to disk."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f)
        
def get_embeddings_batch(texts):
    """
    Sends a list of texts to OpenAI and gets vectors back.
    Batching is faster and cheaper than doing it one by one.
    """
    if not texts:
        return []
    
    # Remove newlines to improve embedding accuracy
    clean_texts = [t.replace("\n", " ") for t in texts]
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small", input=clean_texts
        )

        return [d.embedding for d in response.data]
    except Exception as e:
        print(f"Warning: Failed to get embeddings: {e}")
        # Return zero vectors as fallback to allow processing to continue
        return [[0.0] * 1536 for _ in texts]

def analyze_and_score(digital_library):
    # 1. Load the Memory
    vector_cache = load_cache()
    all_chunks_registry = [] # A flat list of every paragraph in existence
    
    print("Chunking and embedding...")
    # --- STEP 1: CHUNKING & EMBEDDING (With Cache Check) ---
    for doc in digital_library:
        doc_hash = doc["file_hash"]
        
        # CACHE CHECK: Have we seen this EXACT file version before?
        if doc_hash in vector_cache:
            print(f"[CACHE HIT] Skipping AI for {doc['id']}")
            # Load the chunks & embeddings directly from disk
            doc["chunks"] = vector_cache[doc_hash]
        else:
            print(f"[CACHE MISS] Generating embeddings for {doc['id']}...")
            
            # Perform the expensive work
            raw_paragraphs = doc["full_text"].split("\n\n")
            clean_paragraphs = [p.strip() for p in raw_paragraphs if len(p.strip()) > 50]
        
            if not clean_paragraphs:
                continue
        
            # Get embeddings for ALL paragraphs in this doc at once
            # Call OpenAI API
            embeddings = get_embeddings_batch(clean_paragraphs)
            
            # Build the chunks list
            generated_chunks = []        
            for i, text in enumerate(clean_paragraphs):
                chunk_data = {
                    "doc_id": doc["id"],
                    "chunk_id": f"{doc['id']}_{i}",
                    "text": text,
                    "embedding": embeddings[i],
                    "timestamp": doc["metadata"]["created_at"],
                    "is_original": True, # Assume innocent until proven guilty
                    "duplicate_of": None
                }
                generated_chunks.append(chunk_data)
            
        doc["chunks"] = generated_chunks
        vector_cache[doc_hash] = generated_chunks # Update memmory

    # Save the updated cache to disk for next time
    save_cache(vector_cache)

    # Populate the flat registry for comparison
    for doc in digital_library:
        all_chunks_registry.extend(doc["chunks"])

    # --- STEP 2: COMPARISON MATRIX ---
    print("Comparing chunks...")

    # Note: We re-run comparison every time because a NEW file might 
    # conflict with an OLD cached file.
    # We compare every chunk against every other chunk
    # This is an O(N^2) operation.
    
    for i, chunk_A in enumerate(all_chunks_registry):
        if not chunk_A["is_original"]: continue # Already marked as a copy, skip it
        
        for j, chunk_B in enumerate(all_chunks_registry):
            if i == j: continue # do not compare to self
            if chunk_A["doc_id"] == chunk_B["doc_id"]: continue # do not compare within same doc
            
            # calculate similarity
            similarity = cosine_similarity(
                [chunk_A["embedding"]],
                [chunk_B["embedding"]]
            )[0][0]
            
            # --- STEP 3: ARBITRATION LOGIC ---
            if similarity > 0.92: # high confidence duplicate
                
                # who is the parent?
                # The one with the OLDER timestamp is the Original.             
                if chunk_A["timestamp"] <= chunk_B["timestamp"]: # Chunk A is older (or same), so Chunk B is the copy
                    chunk_B["is_original"] = False
                    chunk_B["duplicate_of"] = chunk_A["doc_id"]
                    
                else: # Chunk B is older, so Chunk A is the copy
                    chunk_A["is_original"] = False
                    chunk_A["duplicate_of"] = chunk_B["doc_id"]
                    break
    
    return digital_library, all_chunks_registry

def generate_report(digital_library):
    """Calculate the authenticity percentage"""
    print("\n--- AUTHENTICITY REPORT---")
    
    for doc in digital_library:
        total_chunks = len(doc["chunks"])
        
        if total_chunks == 0:
            continue
        
        unique_chunks = len([c for c in doc["chunks"] if c["is_original"]])
        
        score = (unique_chunks / total_chunks) * 100
        
        print(f"Document: {doc['id']}")
        print(f"  - Author: {doc['metadata']['author']}")
        print(f"  - Authenticity score: {score:.1f}%")
        print(f"  - Contribution: Contributed {unique_chunks} original paragraphs to the final merge.\n")
        
# Execution
if __name__ == "__main__":
    from ingest_advanced import ingest_documents_advanced
    
    library = ingest_documents_advanced("uploads")
    processed_lib, flat_chunks = analyze_and_score(library)
    # generate_report(processed_lib)
    print(f"\n Processing complete.")
    for doc in processed_lib:
        unique_count = len([c for c in doc["chunks"] if c["is_original"]])
        print(f"Doc: {doc["id"]} | Unique Chunks: {unique_count}")        