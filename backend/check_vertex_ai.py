import os
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = 'hoosstudying-478421'

import vertexai
from vertexai.language_models import TextEmbeddingModel

try:
    vertexai.init(
        project="hoosstudying-478421",
        location="us-central1"
    )
    print("✓ Vertex AI initialized successfully")
    
    embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    print("✓ Embedding model loaded successfully")
    
    test_result = embedding_model.get_embeddings(["test"])[0]
    print("✓ Test embedding generated successfully")
    print(f"✓ Embedding dimension: {len(test_result.values)}")
    print("\n Vertex AI is properly configured and working!")
    
except Exception as e:
    print(f"\n Error: {str(e)}")
    print("\nTo fix this:")
    print("1. Enable Vertex AI API at: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project=hoosstudying-478421")
    print("2. Make sure you're authenticated with: gcloud auth application-default login")
    print("3. Set quota project: gcloud auth application-default set-quota-project hoosstudying-478421")

