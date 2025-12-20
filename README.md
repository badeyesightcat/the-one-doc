# Table of Contents

### :hammer: Setup

- Install python: I am using python@3.12.11
- Install VS code: I skipped this since it's already installed on mine
- Get an API key: I got one from OPENAI but after trial I want to exchage that into one in Gemini
- Create a project folder: which is named "the-one-doc"
- Use UV as a Python package and project manager
- Add docling and python-docx as dependencies

  ```
  // docling: A powerful, modern library (developed by IBM) that is excellent for GenAI because it handles layout, tables, and multiple formats (PDF, DOCX) in one go

  // python-docx: A backup for Word files if you need deeper control

  uv add docling python-docx
  ```

### :books: Storing documents into dictionaries

:triangular_flag_on_post: Tracking the writer and storing data in dictionaries

- Create ingest.py file for the step
- import below:
  ```
  import os
  from pathlib import Path
  from docling.document_converter import DocumentConverter
  ```
