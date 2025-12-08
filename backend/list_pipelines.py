#!/usr/bin/env python3
"""
Quick script to list all pipelines with their IDs and names.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.crudFunctions import pipelineFunctions, userFunctions
from sqlalchemy.orm import Session

def list_pipelines():
    db = next(get_db())
    
    try:
        print("\n" + "=" * 60)
        print("ALL PIPELINES")
        print("=" * 60 + "\n")
        
        users = db.execute("SELECT user_id, first_name, last_name, email FROM User").mappings().all()
        
        for user in users:
            user_id = user['user_id']
            pipelines = pipelineFunctions.get_pipelines_by_user_id(db, user_id)
            
            if pipelines:
                print(f"User: {user['first_name']} {user['last_name']} ({user['email']})")
                for pipeline in pipelines:
                    print(f"  Pipeline ID: {pipeline['pipeline_id']:3d} | Name: {pipeline['pipeline_name']}")
                print()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_pipelines()
