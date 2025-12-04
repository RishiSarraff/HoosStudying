import os
import numpy as np
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

from app.services.firestore_service import FirestoreService
from app.services.embedding_service import EmbeddingService

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class RAGService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.firestore_service = FirestoreService()
        self.embedding_service = EmbeddingService()
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.7
        )
    
    def embed_query(self, query: str) -> List[float]:
        embeddings = self.embedding_service.generate_embeddings([query])
        if embeddings:
            return embeddings[0].tolist()
        return []
    
    def similarity_search(
        self, 
        query_embedding: List[float], 
        pipeline_id: Optional[int],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        results = self.firestore_service.find_nearest_embeddings(
            query_vector=query_embedding,
            pipeline_id=pipeline_id,
            top_k=top_k,
            distance_measure="COSINE"
        )
        
        return results
    
    def build_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        if not relevant_chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(relevant_chunks, 1):
            text = chunk.get('text', '')
            file_name = chunk.get('file_name', 'Unknown')
            context_parts.append(f"[Source {i}: {file_name}]\n{text}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def generate_response(
        self, 
        query: str, 
        context: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        
        system_prompt = """You are a helpful study assistant for HoosStudying. 
Your role is to help students understand their study materials by answering questions based on the documents they've uploaded.

Instructions:
- Answer questions based ONLY on the provided context from the user's documents
- If the context doesn't contain enough information to answer, say so clearly
- Be concise but thorough in your explanations
- If referencing specific parts of the documents, mention which source you're using
- Use a friendly, educational tone appropriate for students

Context from uploaded documents:
{context}
"""
        
        messages = [SystemMessage(content=system_prompt.format(context=context))]
        
        if conversation_history:
            for msg in conversation_history[-10:]:
                if msg.get('role') == 'user':
                    messages.append(HumanMessage(content=msg.get('content', '')))
                elif msg.get('role') == 'assistant':
                    messages.append(SystemMessage(content=msg.get('content', '')))
        
        messages.append(HumanMessage(content=query))
        
        response = self.llm.invoke(messages)
        return response.content
    
    def chat(
        self, 
        query: str, 
        pipeline_id: Optional[int],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        
        if not query or not query.strip():
            return {
                "response": "Please provide a question or message.",
                "sources": [],
                "has_context": False
            }
        
        query_embedding = self.embed_query(query)
        
        if not query_embedding:
            return {
                "response": "I encountered an error processing your query. Please try again.",
                "sources": [],
                "has_context": False
            }
        
        relevant_chunks = self.similarity_search(
            query_embedding=query_embedding,
            pipeline_id=pipeline_id,
            top_k=top_k
        )
        
        if not relevant_chunks:
            return {
                "response": "I don't have any documents to reference for this pipeline yet. Please upload some documents first!",
                "sources": [],
                "has_context": False
            }
        
        context = self.build_context(relevant_chunks)
        
        response = self.generate_response(query, context, conversation_history)
        
        sources = [
            {
                "file_name": chunk.get('file_name', 'Unknown'),
                "chunk_index": chunk.get('chunk_index', 0),
                "similarity_score": chunk.get('similarity_score', 0),
                "text_preview": chunk.get('text', '')[:200] + "..." if len(chunk.get('text', '')) > 200 else chunk.get('text', '')
            }
            for chunk in relevant_chunks
        ]
        
        return {
            "response": response,
            "sources": sources,
            "has_context": True,
            "chunks_used": len(relevant_chunks)
        }
