import os
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv

# 1. Load your API Key from a .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str):
  """Turns a piece of text into a list of numbers (vector)"""
  response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
  )
  return response.data[0].embedding

def analyze_originality(digital_library):
  # This list will hold every single 'chunk' of text across all docs
  all_chunks = []
  
  # 2. Break documents into chunks
  for doc in digital_library:
    # simple chunking: split by double newlines (paragraphs)
    paragraphs = doc["content"].split("\n\n")
    for i, para in enumerate(paragraphs):
      # Skip parts with non-semantic-meaning e.g., section1.1, page 4,...
      # Too short strings don't have enough dimensions to compare
      # Cost efficiency due to not using Openai tokens
      # Cleaner UI with both meaningful paragraphs
      # Accuracy based on real originality except their structures
      if len(para.strip()) < 20: continue