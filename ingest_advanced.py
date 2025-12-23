import os
import fitz
import docx
from datetime import datetime
from pathlib import Path

def get_file_metadata(file_path: Path) -> dict:
    """Extracts creation date and author from file properties."""
    stats = os.stat(file_path)
    created_timestamp = getattr(stats, 'st_birthtime', stats.st_ctime)
    meta = {"created_at": created_timestamp, "author": "Unknown"}

    # Try to get specific internal metadata
    if file_path.suffix == ".pdf":
        try:
            doc = fitz.open(file_path)
            pdf_meta = doc.metadata
            if pdf_meta.get("creationDate"):
                meta["created_at"] = pdf_meta["creationDate"]
            if pdf_meta.get("author"):
                meta["author"] = pdf_meta["author"]
            doc.close()
        except Exception as e:
            print(f"Warning: Could not extract PDF metadata from {file_path.name}: {e}")

    elif file_path.suffix == ".docx":
        try:
            doc = docx.Document(file_path)
            core_props = doc.core_properties
            if core_props.created:
                meta["created_at"] = core_props.created.timestamp()
            if core_props.author:
                meta["author"] = core_props.author
        except Exception as e:
            print(f"Warning: Could not extract DOCX metadata from {file_path.name}: {e}")

    return meta

def ingest_documents_advanced(folder_path: str) -> list[dict]:
    digital_library = []
    files = list(Path(folder_path).glob("**/*"))
    
    for file_path in files:
        if file_path.suffix not in [".pdf", ".docx"]:
            continue
        
        print(f"Reading {file_path.name}...")
        
        # 1. Extract text
        text_content = ""
        try:
            if file_path.suffix == ".pdf":
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text_content += f"{page.get_text()}\n\n"
            elif file_path.suffix == ".docx":
                doc = docx.Document(file_path)
                text_content = "\n\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Warning: Failed to extract text from {file_path.name}: {e}")
        
        # 2. Extract metadata
        metadata = get_file_metadata(file_path)
        
        # 3. Build the universal dictionary
        doc_entry = {
            "id": file_path.name,
            "full_text": text_content,
            "metadata": metadata,
            "chunks": []
        }
        
        digital_library.append(doc_entry)
    
    return digital_library