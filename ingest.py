import os
from pathlib import Path
from docling.document_converter import DocumentConverter

def process_documents(folder_path):
  # 1. Setup the "Reader" (the coverter)
  converter = DocumentConverter()
  
  # 2. This List will hold all our Dictionaries (Your "Digital Library")
  digital_library = []
  
  # 3. Look at every file in the folder and its subdirectories
  files = list(Path(folder_path).glob("**/*"))
  
  # print(files)
  
  for file_path in files:
    # We only want PDFs and Word documents
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
      continue # means skip to the next iteration
    
    print(f"--- Processing: {file_path.name}")
    
    # 4. Conversion: Transform the file into structured Markdown
    # Markdown is better than plain text because it keeps headers (#) and tables intact
    result = converter.convert(file_path)
    markdown_content = result.document.export_to_markdown()
    
    # 5. The Dictionary: This is the "Data Package" for this specific file
    # We store metadata here so we don't lose track of who wrote what
    doc_entry = {
      "filename": file_path.name,
      "writer": "System detected", # Later we can extract this from metadata,
      "content": markdown_content,
      "file_size": os.path.getsize(file_path),
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