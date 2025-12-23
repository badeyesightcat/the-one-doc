import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

from ingest_advanced import ingest_documents_advanced

load_dotenv()
client = OpenAI()

def get_embeddings_batch(texts):
    """
    Sends a list of texts to OpenAI and gets vectors back.
    Batching is faster and cheaper than doing it one by one.
    """
    # Remove newlines to improve embedding accuracy
    clean_texts = [t.replace("\n", " ") for t in texts]
    response = client.embeddings.create(
        model="text-embedding-3-small", input=clean_texts
    )

    return [d.embedding for d in response.data]


def analyze_and_score(digital_library):
    # --- STEP 1: CHUNKING & EMBEDDING ---
    all_chunks_registry = [] # A flat list of every paragraph in existence
    
    print("Chunking and embedding...")
    for doc in digital_library:
        # Split by double newline (paragraphs)
        raw_paragraphs = doc["full_text"].split("\n\n")
        
        # Filter clean paragraphs
        clean_paragraphs = [p.strip() for p in raw_paragraphs if len(p.strip()) > 50]
        
        if not clean_paragraphs:
            continue
        
        # Get embeddings for ALL paragraphs in this doc at once
        embeddings = get_embeddings_batch(clean_paragraphs)
        
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
            doc["chunks"].append(chunk_data)
            all_chunks_registry.append(chunk_data)
    
    # --- STEP 2: COMPARISON MATRIX ---
    print("Comparing chunks...")
    # We compare every chunk against every other chunk
    # This is an O(N^2) operation.
    
    for i, chunk_A in enumerate(all_chunks_registry):
        if not chunk_A["is_original"]:
            continue # Already marked as a copy, skip it
        
        for j, chunk_B in enumerate(all_chunks_registry):
            if i == j:
                continue # do not compare to self
            if chunk_A["doc_id"] == chunk_B["doc_id"]:
                continue # do not compare within same doc
            
            # calculate similarity
            similarity = cosine_similarity([chunk_A["embedding"]], [chunk_B["embedding"]])[0][0]
            
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
        
        print(f"Document: {doc["id"]}")
        print(f"  - Author: {doc["metadata"]["author"]}")
        print(f"  - Authenticity score: {score:.1f}%")
        print(f"  - Contribution: Contributed {unique_chunks} original paragraphs to the final merge.\n")
        
# Execution
library = ingest_documents_advanced("uploads")
processed_lib, flat_chunks = analyze_and_score(library)
generate_report(processed_lib)