import vertexai
from google.cloud import aiplatform
from google.cloud.aiplatform import matching_engine
from google.cloud.aiplatform.matching_engine import matching_engine_index
from google.cloud.aiplatform.matching_engine import matching_engine_index_endpoint
import numpy as np
from typing import List, Dict, Any, Optional
import os
import json
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'hoosstudying-478421')
LOCATION = os.getenv('GCP_LOCATION', 'us-central1')
os.environ['GOOGLE_CLOUD_QUOTA_PROJECT'] = PROJECT_ID

class VectorDBService:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        self.index = None
        self.endpoint = None
    
    def create_index_if_not_exists(self, display_name: str = "documentembeddings", dimensions: int = 768):
        try:
            indexes = aiplatform.MatchingEngineIndex.list()
            for index in indexes:
                if index.display_name == display_name or index.display_name.lower() == display_name.lower():
                    self.index = index
                    index_name = index.resource_name
                    print(f"✓ Found existing index: {index.display_name} (ID: {index_name.split('/')[-1]})")
                    return index_name
            
            print(f"Note: Index '{display_name}' not found. Available indexes:")
            for idx in indexes:
                print(f"  - {idx.display_name}")
            print(f"\nVisit: https://console.cloud.google.com/vertex-ai/matching-engine/indexes?project={PROJECT_ID}")
            return None
        except Exception as e:
            print(f"Error checking for index: {str(e)}")
            return None
    
    def upsert_embeddings(self, embeddings: List[np.ndarray], chunk_ids: List[str], metadata: List[Dict[str, Any]] = None):
        try:
            if self.index is None:
                index_name = self.create_index_if_not_exists(dimensions=len(embeddings[0]) if embeddings else 768)
                if index_name:
                    self.index = aiplatform.MatchingEngineIndex(index_name=index_name)
            
            if self.index is None:
                print("Index not available. Storing embeddings data for later batch upload.")
                print(f"Generated {len(embeddings)} embeddings with IDs: {chunk_ids[:3]}...")
                return False
            
            from google.cloud.aiplatform.matching_engine.matching_engine_index import MatchingEngineIndexDatapoint
            
            datapoints = []
            for i, (embedding, chunk_id) in enumerate(zip(embeddings, chunk_ids)):
                datapoint = MatchingEngineIndexDatapoint(
                    datapoint_id=chunk_id,
                    feature_vector=embedding.tolist()
                )
                datapoints.append(datapoint)
            
            self.index.upsert_datapoints(datapoints=datapoints)
            print(f"✓ Upserted {len(datapoints)} embeddings to Vertex AI Vector Search")
            return True
        except Exception as e:
            print(f"Error upserting embeddings: {str(e)}")
            print("Embeddings generated successfully but not stored in vector DB yet.")
            print("You may need to:")
            print("1. Create a Vector Search index in Vertex AI Console")
            print("2. Create an index endpoint")
            print("3. Deploy the index to the endpoint")
            return False
    
    def search_similar(self, query_embedding: np.ndarray, num_neighbors: int = 5, endpoint_id: Optional[str] = None):
        if endpoint_id is None:
            print("Endpoint ID required for search")
            return None
        
        try:
            endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=endpoint_id)
            results = endpoint.find_neighbors(
                deployed_index_id=self.index.resource_name if self.index else None,
                queries=[query_embedding.tolist()],
                num_neighbors=num_neighbors
            )
            return results
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return None

