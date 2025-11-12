import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, tagFunctions, pipelineFunctions, pipelineTagFunctions
import random

def get_db():
    db = localSession()
    return db

class TestPipelineTagFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_user_ids = []
        self.test_pipeline_ids = []
        self.test_tag_ids = []

    def run_all_tests(self):
        print("Run ALL Tag Function Tests")

        try:
            print("Create Test Pipeline Tags")
            self.setup_test_pipeline_tags()

            print("Test All Read Functions")
            self.test_get_tags_for_pipeline()
            self.test_get_pipelines_with_tag()

        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_pipeline_tags(self):
        pipeline_tag_test_data = [
            ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com", "Test Pipeline 1", "Pipeline for testing",
             [
                ("Tag Name #1", "#18b1c2"),
                ("Tag Name #2", "#7531b9"),
                ("Tag Name #3", "#2a9e2f")
             ]),
            ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com", "Test Pipeline 2", "Another test pipeline",
             [
                ("Tag Name #4", "#4c608b"),
             ]),
            ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com", "Study Notes", "Bob's study materials",
             [
                ("Tag Name #5", "#164af0"),
                ("Tag Name #6", "#2c85bd"),
                ("Tag Name #7", "#82127c")
             ])
        ]

        for first_name, last_name, email, pipeline_name, pipeline_description, listOfTags in pipeline_tag_test_data:
            user = userFunctions.create_user(
                self.db,
                first_name, 
                last_name,
                email
            )
            user_id = user['user_id']
            self.test_user_ids.append(user_id)

            pipeline = pipelineFunctions.create_pipeline(
                self.db,
                user_id=user['user_id'],
                pipeline_name=pipeline_name,
                description = pipeline_description
            )

            pipeline_id = pipeline['pipeline_id']
            self.test_pipeline_ids.append(pipeline_id)

            tag_ids = []
            for tag_name, tag_color in listOfTags:
                tag = tagFunctions.create_custom_tag(
                    self.db,
                    user_id=user_id,
                    name=tag_name,
                    color=tag_color
                )

                tag_id = tag['tag_id']
                tag_ids.append(tag_id)

            if len(tag_ids) == 1:
                pipeline_tag = pipelineTagFunctions.add_tag_to_pipeline(
                    self.db,
                    pipeline_id=pipeline_id,
                    tag_id=tag_ids[0]
                )

            else:
                pipeline_tag = pipelineTagFunctions.add_multiple_tags_to_pipeline(
                    self.db,
                    pipeline_id=pipeline_id,
                    tag_ids=tag_ids
                )

    def test_get_tags_for_pipeline(self):
        pipeline_id = self.test_pipeline_ids[1]

        list_of_tags = pipelineTagFunctions.get_tags_for_pipeline(
            self.db,
            pipeline_id
        )
        assert list_of_tags is not None, "Could not retrieve list of pipeline tags"
        assert isinstance(list_of_tags, list), "The type of list_of_pipeline_tags wasn't a list"
        print("Retrieved all the pipeline tags from table") 

        for each_tag in list_of_tags:
            assert each_tag['tag_type'] == 'custom', f"Tag {each_tag['tag_id']} is not a custom tag"

            assert 'tag_id' in each_tag, "Missing tag_id"
            assert 'name' in each_tag, "Missing name"
            assert 'color' in each_tag, "Missing color"
            assert 'tag_type' in each_tag, "Missing tag_type"

        print(f"All custom tags have the correct fields for pipeline {pipeline_id}")

        invalid_tags_list = pipelineTagFunctions.get_tags_for_pipeline(
            self.db,
            99999
        )
        assert invalid_tags_list == [] or invalid_tags_list is None, "List of pipeline tags is not empty/invalid"
        print("Correctly handled invalid pipeline Id case")

    def test_get_pipelines_with_tag(self):
        pipeline_id = self.test_pipeline_ids[1]
        tags = pipelineTagFunctions.get_tags_for_pipeline(
            self.db,
            pipeline_id
        )
        assert len(tags) > 0, "No tags found for test pipeline"
        
        single_pipeline_tag_id = tags[0]['tag_id']
        
        list_of_pipelines = pipelineTagFunctions.get_pipelines_with_tag(
            self.db,
            single_pipeline_tag_id
        )
        assert list_of_pipelines is not None, "Could not retrieve list of pipelines for tag"
        assert isinstance(list_of_pipelines, list), "The type of list_of_pipelines wasn't a list"
        assert len(list_of_pipelines) == 1, f"Expected 1 pipeline, found {len(list_of_pipelines)}"
        print(f"Retrieved pipeline with tag {single_pipeline_tag_id}")
        
        for each_pipeline in list_of_pipelines:
            assert 'pipeline_id' in each_pipeline, "Missing pipeline_id"
            assert 'user_id' in each_pipeline, "Missing user_id"
            assert 'pipeline_name' in each_pipeline, "Missing pipeline_name"
            assert 'description' in each_pipeline, "Missing description"
            assert 'created_at' in each_pipeline, "Missing created_at"
        
        print(f"All pipelines have the correct fields for tag {single_pipeline_tag_id}")
        
        assert list_of_pipelines[0]['pipeline_id'] == pipeline_id, "Wrong pipeline returned"
        print(f"Verified correct pipeline {pipeline_id} returned for tag {single_pipeline_tag_id}")

        invalid_pipelines_list = pipelineTagFunctions.get_pipelines_with_tag(
            self.db,
            99999
        )
        assert invalid_pipelines_list == [] or invalid_pipelines_list is None, "List of pipelines is not empty for invalid tag"
        print("Correctly handled invalid tag_id case")

    def cleanup(self):
        print("Cleaning up test data...")
        
        deleted_users = 0
        for user_id in self.test_user_ids:
            try:
                if userFunctions.delete_user_by_id(self.db, user_id):
                    deleted_users += 1
            except:
                pass
                
        print(f"Users deleted: {deleted_users}/{len(self.test_user_ids)}")

        self.test_user_ids.clear()
        self.test_pipeline_ids.clear()
        self.test_tag_ids.clear()

        self.db.close()

if __name__ == "__main__":
    tester = TestPipelineTagFunctionsComplete()
    tester.run_all_tests()
