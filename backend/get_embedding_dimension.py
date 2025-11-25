import os
from dotenv import load_dotenv

load_dotenv()

project_id = os.getenv('GCP_PROJECT_ID', 'hoosstudying-478421')
location = os.getenv('GCP_LOCATION', 'us-central1')
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = project_id

import vertexai
from vertexai.language_models import TextEmbeddingModel

vertexai.init(
    project=project_id,
    location=location
)

embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
test_result = embedding_model.get_embeddings(["test"])[0]
dimension = len(test_result.values)

print(f"Embedding dimension for text-embedding-004: {dimension}")
print(f"\nUse this dimension when creating your Vector Search index: {dimension}")

