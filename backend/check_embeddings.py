#!/usr/bin/env python3
"""
Script to check if embeddings exist in Firestore for a specific file and pipeline.
Usage: python check_embeddings.py <file_name> <pipeline_id>
Example: python check_embeddings.py "Project3 Writeup.pdf" 30
python check_embeddings.py "Shiv Patel Resume - McMaster-Carr (2).pdf" 31
"""

import sys
from app.services.firestore_service import FirestoreService

def check_embeddings(file_name: str, pipeline_id: int):
    service = FirestoreService()
    
    print(f"\n{'=' * 60}")
    print(f"Checking embeddings for:")
    print(f"  File: {file_name}")
    print(f"  Pipeline ID: {pipeline_id}")
    print(f"{'=' * 60}\n")
    
    try:
        docs = service.query_collection(
            'embeddings', 
            [('file_name', '==', file_name), ('pipeline_id', '==', pipeline_id)]
        )
        doc_list = list(docs)
        
        print(f"Found {len(doc_list)} embedding(s)\n")
        
        if len(doc_list) > 0:
            print("Sample embedding metadata:")
            sample = doc_list[0]
            for key, value in sample.items():
                if key != 'embedding':
                    print(f"  {key}: {value}")
            print()
        else:
            print("⚠️  No embeddings found! The document may not have been properly embedded.")
            print("\nChecking for embeddings with this file name in other pipelines...")
            
            all_docs = service.query_collection('embeddings', [('file_name', '==', file_name)])
            all_list = list(all_docs)
            
            if len(all_list) > 0:
                print(f"\nFound {len(all_list)} embedding(s) with this file name in other pipelines:")
                pipeline_ids = set()
                for doc in all_list:
                    pid = doc.get('pipeline_id')
                    if pid is not None:
                        pipeline_ids.add(pid)
                print(f"  Pipeline IDs: {sorted(pipeline_ids)}")
                print(f"  This suggests the file was embedded for different pipeline(s).")
            else:
                print("\n❌ No embeddings found with this file name at all.")
                print("   The document was likely never embedded successfully.")
        
    except Exception as e:
        print(f"Error checking embeddings: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python check_embeddings.py <file_name> <pipeline_id>")
        print('Example: python check_embeddings.py "Project3 Writeup.pdf" 30')
        sys.exit(1)
    
    file_name = sys.argv[1]
    try:
        pipeline_id = int(sys.argv[2])
    except ValueError:
        print("Error: pipeline_id must be an integer")
        sys.exit(1)
    
    check_embeddings(file_name, pipeline_id)
