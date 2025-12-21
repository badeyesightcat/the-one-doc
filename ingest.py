import os
from pathlib import Path
from docling.document_converter import DocumentConverter
from typing import Dict

def process_documents(folder_path: str) -> list[Dict[str, str]]:
  """Process PDF and DOCX documents from a folder into a digital library.
  
  Args:
    folder_path: Path to the folder containing documents to process
    
  Returns:
    List of document metadata dictionaries
    
  Raises:
    FileNotFoundError: If the folder_path does not exist
  """

  if not Path(folder_path).exists():
    raise FileNotFoundError(f"Folder not found: {folder_path}")
  
  # 1. Setup the "Reader" (the converter)
  converter = DocumentConverter()
  
  # 2. This List will hold all our Dictionaries (Your "Digital Library")
  digital_library = []
  
  # 3. Look at every file in the folder and its subdirectories
  files = list(Path(folder_path).glob("**/*"))
    
  for file_path in files:
    # We only want PDFs and Word documents
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
      continue # means skip to the next iteration
    
    print(f"--- Processing: {file_path.name}")
    
    try:
      # 4. Conversion: Transform the file into structured Markdown
      # Markdown is better than plain text because it keeps headers (#) and tables intact
      result = converter.convert(file_path)
      markdown_content = result.document.export_to_markdown()
    except Exception as e:
      print(f"ERROR: Failed to process {file_path.name}: {e}")
      continue
    
    # 5. The Dictionary: This is the "Data Package" for this specific file
    # We store metadata here so we don't lose track of who wrote what
    
    try: 
      file_size = os.path.getsize(file_path)
    except OSError:
      file_size = 0

    doc_entry = {
      "filename": file_path.name,
      "writer": "System detected", # Later we can extract this from metadata,
      "content": markdown_content,
      "file_size": file_size,
      "status": "ready_for_ai"
    }
    
    digital_library.append(doc_entry)
    
  return digital_library

if __name__ == "__main__":
  # Create an "uploads" folder if it doesn't exist
  os.makedirs("uploads", exist_ok=True)
  
  print("Put your PDF or Word files in the 'uploads' folder and press Enter.")
  input("Press Enter once files are ready...")
  
  results = process_documents("uploads")
  
  print(f"\nSuccessfully ingested {len(results)} documents.")
  
  for doc in results:
    print(f"- {doc["filename"]} ({len(doc["content"])} characters captured)")