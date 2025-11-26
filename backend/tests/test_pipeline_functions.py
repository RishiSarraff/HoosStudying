import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, pipelineFunctions
import random

def get_db():
    db = localSession()
    return db

class TestPipelineFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_pipelines = [] 
        self.test_user_ids = []
        ## We will keep the test_pipelines and the test_user_ids in an array to clean them up after successes, fails and so on

    def run_all_tests(self):
        print("Run ALL Pipeline Function Tests")

        try:
            print("Create Test Pipelines")
            self.setup_test_pipelines()

            print("Test All Read Functions")
            self.test_get_pipeline_by_id()
            self.test_get_pipelines_by_user_id()
            self.test_get_all_pipelines()
            self.test_get_general_pipeline_id()

            print("Test All Update Functions")
            self.test_update_pipeline()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_pipelines(self):
        test_data = [
            ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com", "Test Pipeline 1", "Pipeline for testing"),
            ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com", "Test Pipeline 2", "Another test pipeline"),
            ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com", "Study Notes", "Bob's study materials"),
            ("Alice", "Williams", f"alice.w{random.randint(1000,9999)}@test.com", "Project Documents", "Project Documentation"),
            ("Charlie", "Brown", f"charlie.b{random.randint(1000,9999)}@test.com", "Research", "Research Pipeline"),
        ]

        for first_name, last_name, email, pipeline_name, pipeline_description in test_data:
            user = userFunctions.create_user(self.db, first_name, last_name, email)
            self.test_user_ids.append(user['user_id'])
            print(f"Created test user: {email} with ID {user['user_id']}")

            pipeline = pipelineFunctions.create_pipeline(
                self.db,
                user_id=user['user_id'],
                pipeline_name=pipeline_name,
                description = pipeline_description
            )

            self.test_pipelines.append(pipeline['pipeline_id'])
            print(f"Created the test pipeline {pipeline_name} with ID {pipeline['pipeline_id']}")

    def test_get_pipeline_by_id(self):
        pipeline_id = self.test_pipelines[0]
        user_id = self.test_user_ids[0]

        fetched_pipeline = pipelineFunctions.get_pipeline_by_id(self.db, pipeline_id)
        assert fetched_pipeline is not None, "Failed to get User"
        assert fetched_pipeline['pipeline_name'] == "Test Pipeline 1", "Test Pipeline Name Mismatch"
        assert fetched_pipeline['user_id'] == user_id, "User ID Mismatch"
        print(f"Retrieved pipeline {fetched_pipeline['pipeline_name']} from user User ID: {fetched_pipeline['user_id']}")

        invalid_pipeline = pipelineFunctions.get_pipeline_by_id(self.db, 999999)
        assert invalid_pipeline is None, "Should return None for invalid pipeline ID"
        print("Correctly returns None for invalid pipeline Id")

    def test_get_pipelines_by_user_id(self):
        user_id = self.test_user_ids[0]

        pipelines = pipelineFunctions.get_pipelines_by_user_id(self.db, user_id)

        assert pipelines is not None, "Failed to get pipelines"
        assert isinstance(pipelines, list), "Should return a list of pipelines"

        assert len(pipelines) >= 1, f"User should have found at least 1 pipeline, but find {len(pipelines)}"
        print(f"User {user_id} has {len(pipelines)} pipelines")

        pipeline_names = [pipeline['pipeline_name'] for pipeline in pipelines]
        assert "Test Pipeline 1" in pipeline_names, "Test pipeline 1 should be in the list"

        test_pipeline = next(pipeline for pipeline in pipelines if pipeline['pipeline_name'] == 'Test Pipeline 1')
        assert test_pipeline['user_id'] == user_id, "User ID mismatch"
        assert test_pipeline['description'] == "Pipeline for testing", "Description Mismatch"
        print(f"Retrieved pipelines: {pipeline_names}")

        invalid_pipelines = pipelineFunctions.get_pipelines_by_user_id(self.db, 99999)
        assert invalid_pipelines == [] or invalid_pipelines is None, \
            "Should return empty list or None for invalid user ID"
        print("Correctly returns empty result for invalid user ID")

        for pipeline in pipelines:
            assert pipeline['user_id'] == user_id, \
                f"Pipeline {pipeline['pipeline_id']} has wrong user_id"
        print(f"All pipelines correctly belong to user {user_id}")
            

    def test_get_all_pipelines(self):
        all_pipelines = pipelineFunctions.get_all_pipelines(self.db)
        assert all_pipelines is not None, "Failed to fetch all pipelines"
        assert isinstance(all_pipelines, list), "Should return a list"

        assert len(all_pipelines) >= len(self.test_pipelines), f"Should have at least {len(self.test_pipelines)} pipelines"

        test_pipeline_ids_set = set(self.test_pipelines)
        fetched_user_ids_set = set(pipeline['pipeline_id'] for pipeline in all_pipelines)

        assert test_pipeline_ids_set.issubset(fetched_user_ids_set), "Not all test pipelines found in results"

        print(f"Successfully got {len(all_pipelines)} total pipelines")
        print(f"Found all {len(self.test_pipelines)} test pipelines in results")

        for pipeline in all_pipelines:
            assert 'pipeline_id' in pipeline, "Pipeline missing pipeline_id"
            assert 'user_id' in pipeline, "Pipeline missing user_id"
            assert 'pipeline_name' in pipeline, "Pipeline missing pipeline_name"
        print("All pipelines have required fields")

    def test_get_general_pipeline_id(self):
        user_id = self.test_user_ids[0]

        general_pipeline_id = pipelineFunctions.get_general_pipeline_id(self.db, user_id)

        ## general_pipeline id is an int, so we need to find the row in 
        general_pipeline = pipelineFunctions.get_pipeline_by_id(self.db, general_pipeline_id)

        assert general_pipeline is not None, "Failed to get general pipeline"
        assert general_pipeline['pipeline_name'] == "general", \
            "Pipeline name should be 'general'"
        assert general_pipeline['user_id'] == user_id, "User ID Mismatch"
        assert general_pipeline['pipeline_name'] == "general", \
            "Description mismatch"
        print(f"Retrieved general pipeline ID: {general_pipeline['pipeline_id']}, for user {user_id}")

        invalid_general_pipeline = pipelineFunctions.get_general_pipeline_id(self.db, 99999)
        assert invalid_general_pipeline is None, \
            "Should return None for invalid user ID"
        print("Correctly returns None for invalid user ID")

    def test_update_pipeline(self):
        ## to update tha pipeline i need
        pipeline_id = self.test_pipelines[3]

        updated_user = pipelineFunctions.update_pipeline(
            self.db,
            pipeline_id,
            pipeline_name="Project Documents (changed)"
        )

        assert updated_user['pipeline_name'] == "Project Documents (changed)", "Pipeline name is not updated"
        assert updated_user['description'] == "Project Documentation", "Description should remain unchanged"
        print("Successfully updated pipeline")

        # Update last name only
        updated = pipelineFunctions.update_pipeline(
            self.db,
            pipeline_id,
            description="changed"
        )

        assert updated['pipeline_name'] == "Project Documents (changed)", "Pipeline name should remain unchanged"
        assert updated['description'] == "changed", "Description is not updated"
        print("Successfully updated description only")
    
        
        # Update all fields at once
        updated = pipelineFunctions.update_pipeline(
            self.db,
            pipeline_id,
            pipeline_name="last change name",
            description="last change description",
        )
        assert updated['pipeline_name'] == "last change name", "Failed to update all fields"
        assert updated['description'] == "last change description", "Failed to update all fields"
        print("Successfully updated all fields at once")


    def cleanup(self):
        print("Cleaning up test pipeline data and user data...")

        for user_id in self.test_user_ids:
            try:
                userFunctions.delete_user_by_id(self.db, user_id)
                print(f"Deleted user {user_id}")
            except Exception as e:
                print(f"Error deleting user {user_id}: {e}")

        self.test_pipelines.clear()
        self.test_user_ids.clear()

if __name__ == "__main__":
    tester = TestPipelineFunctionsComplete()
    tester.run_all_tests()