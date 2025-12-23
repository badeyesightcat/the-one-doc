# Table of Contents

### :hammer: Setup

- Install python: I am using python@3.12.11
- Install VS code: I skipped this since it's already installed on mine
- Get an API key: I got one from OPENAI but after trial I want to exchage that into one in Gemini
- Create a project folder: which is named "the-one-doc"
- Use UV as a Python package and project manager
- Add docling and python-docx as dependencies

  ```
  // pymupdf: PDF surgeon
  // python-docx: A backup for Word files if you need deeper control
  // python-dateutil: converting messy date formats used in files

  uv add pymupdf python-docx python-dateutil
  ```

---

### :eye: Storing documents into dictionaries as a universal data structure

:triangular_flag_on_post: Tracking the writer and storing data in dictionaries

- Purpose: extract metadata such as creation date, author, ... (Expressing the writer's info and authenticity)
- Create ingest_advanced.py file for the step: Generate a version of more dedicated logic based on the file extensions
- import below:

  ```
  import os
  import fitz  # PyMuPDF
  import docx
  from datetime import datetime
  from pathlib import Path
  ```

- after works done, run the command:
  `uv run ingest_advanced.py`

- digital_library looks like

```json
[
  {
    "id": "Doc_A.pdf",
    "full_text": "This is unique text...",
    "metadata": { "created_at": 1703001600.0, "author": "John Doe" },
    "chunks": []
  },
  {
    "id": "Doc_B.docx",
    "full_text": "This is duplicated text...",
    "metadata": { "created_at": 1703088000.0, "author": "Jane Smith" },
    "chunks": []
  }
]
```

- its purpose: record keeping
- why using markdown as its form: due to its structural cues

---

### :brain: Analytical understanding and comparing documents for authenticity and originality checks: Embeddings

##### 1. Chunk intelligently :knife:

- Purpose: splitting documents into smaller pieces, 1-2 paragraphs in average and the each piece

```
uv add openai scikit-learn python-dotenv
```

##### 2. Embed chunks which turn them to math :triangular_ruler:

##### 3. Compare them to find duplicates

##### 4. Arbitrate which one is the most authentic and genuine
