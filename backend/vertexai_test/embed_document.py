import os
import sys
import types
import importlib
import numpy as np

import vertexai
from vertexai.language_models import TextEmbeddingModel

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)
 
crud_package = importlib.import_module("app.crudFunctions")
pipeline_stub = types.ModuleType("pipelineDocumentFunctions")
sys.modules["app.crudFunctions.pipelineDocumentFunctions"] = pipeline_stub
setattr(crud_package, "pipelineDocumentFunctions", pipeline_stub)

from app.services.document_processor import DocumentProcessor

FILE_PATH = "/Users/shivpatel/Downloads/technosonics notes (1).pdf"

def main() -> None:
    processor = DocumentProcessor.__new__(DocumentProcessor)
    file_type = processor.get_file_type_from_path(FILE_PATH)
    text, _ = DocumentProcessor.extract_text(processor, FILE_PATH, file_type)
    chunks = DocumentProcessor.chunk_text(processor, text)

    # Print the full extracted text
    print("=" * 50)
    print("FULL EXTRACTED TEXT:")
    print("=" * 50)
    print(text)
    print(f"\nTotal characters: {len(text)}")
    
    # Print each chunk separately
    print("\n" + "=" * 50)
    print(f"CHUNKS ({len(chunks)} total):")
    print("=" * 50)
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i} ({len(chunk)} chars) ---")
        print(chunk[:500])  # First 500 chars of each chunk
        if len(chunk) > 500:
            print("... [truncated]")

    if not chunks:
        raise ValueError("No text chunks produced from document.")

  
    vertexai.init(
        project="hoosstudying-478421",
        location="us-central1"
    )

    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

    embeddings = []
    for i, chunk in enumerate(chunks):
        embedding_result = embedding_model.get_embeddings([chunk])[0]
        # Convert to numpy array for easier use
        embedding = np.array(embedding_result.values)
        embeddings.append(embedding)
        
        # Simple verification
        print(f"\n--- Embedding {i} ---")
        print(f"Shape: {embedding.shape}")
        print(f"Min: {embedding.min():.4f}, Max: {embedding.max():.4f}, Mean: {embedding.mean():.4f}")
        print(f"First 5 values: {embedding[:5]}")
    
    print(f"\n{'=' * 50}")
    print(f"SUCCESS: Generated {len(embeddings)} embeddings")
    print(f"All embeddings have shape: {embeddings[0].shape}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()