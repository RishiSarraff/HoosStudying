#!/usr/bin/env python3
"""
Firestore Vector Search - Complete Test
Populates sample data and runs all similarity search tests
"""

from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


def main():
    print("=" * 70)
    print("🚀 FIRESTORE VECTOR SEARCH TEST")
    print("=" * 70)
    
    # Initialize Firestore
    print("\n📦 Initializing Firestore client...")
    db = firestore.Client()
    collection = db.collection("embeddings")
    print("✓ Connected to Firestore\n")
    
    # ========================================================================
    # STEP 1: POPULATE SAMPLE DATA
    # ========================================================================
    print("=" * 70)
    print("STEP 1: POPULATING SAMPLE DATA")
    print("=" * 70)
    
    sample_data = {
        "coffee_ethiopia": {
            "text": "Ethiopian Yirgacheffe coffee beans",
            "embedding": [0.1] * 512,
            "category": "coffee",
            "origin": "Ethiopia"
        },
        "coffee_colombia": {
            "text": "Colombian Supremo coffee beans",
            "embedding": [0.15] * 512,
            "category": "coffee",
            "origin": "Colombia"
        },
        "coffee_dark_roast": {
            "text": "Dark roast espresso blend",
            "embedding": [0.2] * 512,
            "category": "coffee",
            "origin": "Brazil"
        },
        "coffee_light_roast": {
            "text": "Light roast single origin",
            "embedding": [0.25] * 512,
            "category": "coffee",
            "origin": "Kenya"
        },
        "coffee_espresso": {
            "text": "Italian espresso roast",
            "embedding": [0.3] * 512,
            "category": "coffee",
            "origin": "Italy"
        },
        "coffee_french_press": {
            "text": "French press medium roast",
            "embedding": [0.35] * 512,
            "category": "coffee",
            "origin": "Guatemala"
        },
        "tea_green": {
            "text": "Japanese Sencha green tea",
            "embedding": [0.5] * 512,
            "category": "tea",
            "origin": "Japan"
        },
        "tea_black": {
            "text": "Assam black tea",
            "embedding": [0.55] * 512,
            "category": "tea",
            "origin": "India"
        },
        "tea_oolong": {
            "text": "Taiwanese High Mountain Oolong",
            "embedding": [0.6] * 512,
            "category": "tea",
            "origin": "Taiwan"
        },
        "tea_white": {
            "text": "Silver Needle white tea",
            "embedding": [0.65] * 512,
            "category": "tea",
            "origin": "China"
        }
    }
    
    print(f"\n📝 Adding {len(sample_data)} documents with 512-dimensional embeddings...")
    print("   Coffee docs: embeddings from 0.1 to 0.35")
    print("   Tea docs: embeddings from 0.5 to 0.65\n")
    
    for doc_id, data in sample_data.items():
        doc_ref = collection.document(doc_id)
        doc_ref.set({
            "text": data["text"],
            "embedding": Vector(data["embedding"]),
            "category": data["category"],
            "origin": data["origin"]
        })
        print(f"  ✓ {doc_id}")
    
    print(f"\n✅ Successfully added {len(sample_data)} documents!")
    
    # Query vector (similar to coffee for testing)
    query_vector = [0.18] * 512
    print(f"\n🔍 Query vector: [0.18] * 512 (closest to coffee embeddings)")
    
    # ========================================================================
    # STEP 2: BASIC SIMILARITY SEARCH
    # ========================================================================
    print("\n" + "=" * 70)
    print("STEP 2: BASIC SIMILARITY SEARCH (Top 5)")
    print("=" * 70)
    
    try:
        vector_query = collection.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_vector),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=5
        )
        
        docs = vector_query.stream()
        
        print("\nResults:")
        for i, doc in enumerate(docs, 1):
            data = doc.to_dict()
            print(f"  {i}. {doc.id}")
            print(f"     Text: {data.get('text')}")
            print(f"     Category: {data.get('category')}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # ========================================================================
    # STEP 3: SEARCH WITH DISTANCE CALCULATIONS
    # ========================================================================
    print("=" * 70)
    print("STEP 3: SEARCH WITH DISTANCE CALCULATIONS")
    print("=" * 70)
    
    try:
        vector_query = collection.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_vector),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=5,
            distance_result_field="vector_distance"
        )
        
        docs = vector_query.stream()
        
        print("\nResults with distances:")
        for i, doc in enumerate(docs, 1):
            data = doc.to_dict()
            distance = data.get('vector_distance', 'N/A')
            print(f"  {i}. {doc.id}")
            if isinstance(distance, float):
                print(f"     Distance: {distance:.4f}")
            else:
                print(f"     Distance: {distance}")
            print(f"     Text: {data.get('text')}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # ========================================================================
    # STEP 4: SEARCH WITH DISTANCE THRESHOLD
    # ========================================================================
    print("=" * 70)
    print("STEP 4: SEARCH WITH DISTANCE THRESHOLD")
    print("=" * 70)
    print("(Only return documents with distance <= 5.0)")
    
    try:
        vector_query = collection.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_vector),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=10,
            distance_threshold=5.0,
            distance_result_field="vector_distance"
        )
        
        docs = vector_query.stream()
        
        print("\nResults within threshold:")
        count = 0
        for doc in docs:
            count += 1
            data = doc.to_dict()
            distance = data.get('vector_distance', 'N/A')
            print(f"  {count}. {doc.id}")
            if isinstance(distance, float):
                print(f"     Distance: {distance:.4f}")
            else:
                print(f"     Distance: {distance}")
            print(f"     Text: {data.get('text')}")
            print()
        
        if count == 0:
            print("  No documents found within threshold.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # ========================================================================
    # STEP 5: COMPARE DISTANCE MEASURES
    # ========================================================================
    print("=" * 70)
    print("STEP 5: COMPARE DIFFERENT DISTANCE MEASURES")
    print("=" * 70)
    
    distance_measures = [
        ("EUCLIDEAN", DistanceMeasure.EUCLIDEAN),
        ("COSINE", DistanceMeasure.COSINE),
        ("DOT_PRODUCT", DistanceMeasure.DOT_PRODUCT)
    ]
    
    for measure_name, measure in distance_measures:
        print(f"\n{measure_name} Distance (Top 3):")
        try:
            vector_query = collection.find_nearest(
                vector_field="embedding",
                query_vector=Vector(query_vector),
                distance_measure=measure,
                limit=3,
                distance_result_field="vector_distance"
            )
            
            docs = vector_query.stream()
            
            for i, doc in enumerate(docs, 1):
                data = doc.to_dict()
                distance = data.get('vector_distance', 'N/A')
                if isinstance(distance, float):
                    print(f"  {i}. {doc.id} - Distance: {distance:.6f}")
                else:
                    print(f"  {i}. {doc.id} - Distance: {distance}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED!")
    print("=" * 70)
    print("\n📊 EXPECTED RESULTS:")
    print("   • Coffee documents should appear first (embeddings 0.1-0.35)")
    print("   • Tea documents should appear last (embeddings 0.5-0.65)")
    print("   • Query [0.18] is closest to coffee_colombia [0.15]")
    print("\n💡 If coffee docs ranked first, vector search is working correctly!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()