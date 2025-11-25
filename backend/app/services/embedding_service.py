import vertexai
from vertexai.language_models import TextEmbeddingModel
import numpy as np
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        project_id = os.getenv('GCP_PROJECT_ID', 'hoosstudying-478421')
        location = os.getenv('GCP_LOCATION', 'us-central1')
        os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = project_id
        vertexai.init(
            project=project_id,
            location=location
        )
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    
    def generate_embeddings(self, chunks: List[str]) -> List[np.ndarray]:
        embeddings = []
        for chunk in chunks:
            embedding_result = self.embedding_model.get_embeddings([chunk])[0]
            embedding = np.array(embedding_result.values)
            embeddings.append(embedding)
        return embeddings

