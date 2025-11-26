import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, conversationFunctions, pipelineFunctions
import random

def get_db():
    db = localSession()
    return db

class TestConversationFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_conversation_ids = [] 
        self.test_pipeline_ids = []
        self.test_user_ids = []
        self.test_general_conversation_ids = []

    def run_all_tests(self):
        print("Run ALL Conversation Function Tests")

        try:
            print("Create Test Conversation")
            self.setup_test_conversations()

            print("Test All Read Functions")
            self.test_get_conversations_by_user()
            self.test_get_conversations_by_pipeline()
            self.test_get_general_conversations_for_user()
            self.test_get_recent_conversations()

            print("Test All Update Functions")
            self.test_update_conversation_timestamp()

            #print("Test All Delete Functions")
            #self.test_delete_conversation()
            #self.test_delete_all_conversations_for_user()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_conversations(self):
        test_data = [
            ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com", "Pipeline Name 1", "Pipeline Description 1"),
            ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com", "Pipeline Name 2", "Pipeline Description 2"),
            ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com", "Pipeline Name 3", "Pipeline Description 3"),
            ("Alice", "Williams", f"alice.w{random.randint(1000,9999)}@test.com", "Pipeline Name 4", "Pipeline Description 4"),
            ("Charlie", "Brown", f"charlie.b{random.randint(1000,9999)}@test.com", "Pipeline Name 5", "Pipeline Description 5"),
        ]

        for first_name, last_name, email, pipeline_name, description in test_data:
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
                user_id,
                pipeline_name,
                description
            )

            pipeline_id = pipeline['pipeline_id']

            self.test_pipeline_ids.append(pipeline_id)

            conversation = conversationFunctions.create_conversation(
                self.db, 
                user_id,
                pipeline_id
            )

            conversation_id = conversation['conversation_id']

            self.test_conversation_ids.append(conversation_id)

            general_conversation = conversationFunctions.create_general_conversation(
                self.db,
                user_id
            )
            general_conversation_id = general_conversation['conversation_id']

            self.test_conversation_ids.append(general_conversation_id)
            self.test_general_conversation_ids.append(general_conversation_id)

            print(f"Created the test user {user_id} with {conversation['user_id']} in pipeline {pipeline_id}")


    def test_get_conversations_by_user(self):
        user_id = self.test_user_ids[0]

        conversations_list = conversationFunctions.get_conversations_by_user(
            self.db,
            user_id
        )
        assert conversations_list is not None, "Could not retrieve conversations from user"
        assert isinstance(conversations_list, list), "The type of conversations_list wasn't a list"
        assert len(conversations_list) >= 1, "All Users must have at least 1 conversation as a general conversation"
        print("Retrieved all the conversations from a user")

        for each_conversation in conversations_list:
            assert each_conversation['user_id'] == user_id, f"Conversation {each_conversation['conversation_id']} has the wrong user ID"

        print(f"Every conversation is correctly aligned with user {user_id}.")

        invalid_list = conversationFunctions.get_conversations_by_user(
            self.db,
            99999
        )
        assert invalid_list is None or invalid_list == [], "Mistakenly receieved conversations from a non-existing user"
        print("Correctly returns an empty list or none for a non-existing user")

    def test_get_conversations_by_pipeline(self):
        pipeline_id = self.test_pipeline_ids[0]

        conversations_list = conversationFunctions.get_conversations_by_pipeline(
            self.db,
            pipeline_id
        )
        assert conversations_list is not None, "Could not retrieve conversations from pipeline"
        assert isinstance(conversations_list, list), "The type of conversations_list wasn't a list"
        assert len(conversations_list) >= 1, "All Pipelines must have at least 1 conversation as a general conversation"
        print("Retrieved all the conversations from a pipeline")

        for each_conversation in conversations_list:
            assert each_conversation['pipeline_id'] == pipeline_id, f"Conversation {each_conversation['conversation_id']} has the wrong pipeline ID"

        print(f"Every conversation is correctly aligned with pipeline {pipeline_id}.")

        invalid_list = conversationFunctions.get_conversations_by_pipeline(
            self.db,
            99999
        )
        assert invalid_list == [] or len(invalid_list) == 0, "Mistakenly receieved conversations from a non-existing pipeline"
        print("Correctly returns an empty list or none for a non-existing pipeline")

    def test_get_general_conversations_for_user(self):
        user_id = self.test_user_ids[1]

        general_conversations_list = conversationFunctions.get_general_conversations_for_user(
            self.db,
            user_id
        )
        assert general_conversations_list is not None, "Could not retrieve general conversations from user"
        assert isinstance(general_conversations_list, list), "The type of general_conversations_list wasn't a list"
        assert len(general_conversations_list) >= 1, "All Users must have at least 1 conversation as a general conversation"
        print("Retrieved all the general conversations from a users")

        for each_general_conversation in general_conversations_list:
            assert each_general_conversation['user_id'] == user_id, f"Conversation {each_general_conversation['conversation_id']} has the wrong user ID"

        print(f"Every general conversation is correctly aligned with user {user_id}.")

        invalid_list = conversationFunctions.get_general_conversations_for_user(
            self.db,
            99999
        )
        assert invalid_list is None or invalid_list == [], "Mistakenly receieved general conversations from a non-existing pipeline"
        print("Correctly returns an empty list or none for a non-existing user")
    
    def test_get_recent_conversations(self):
        user_id = self.test_user_ids[0]
        
        recent = conversationFunctions.get_recent_conversations(self.db, user_id)
        assert isinstance(recent, list), "Should return a list"
        assert len(recent) >= 1, "Should have at least 1 conversation"
        print(f"Retrieved {len(recent)} recent conversations")
        
        limited = conversationFunctions.get_recent_conversations(self.db, user_id, limit=2)
        assert len(limited) <= 2, "Should respect limit"
        print(f"Limited to {len(limited)} conversations")
        
        invalid = conversationFunctions.get_recent_conversations(self.db, 99999)
        assert invalid == [], "Should return empty for invalid user"
        print("Correctly handles invalid user ID")

    def test_update_conversation_timestamp(self):
        conversation_id = self.test_conversation_ids[0]
        
        before = conversationFunctions.get_conversation_by_id(self.db, conversation_id)
        timestamp_before = before['last_message_at']

        time.sleep(1)
        result = conversationFunctions.update_conversation_timestamp(self.db, conversation_id)
        assert result is True or result > 0, "Update should succeed"
        print(f"Updated timestamp for conversation {conversation_id}")
        
        after = conversationFunctions.get_conversation_by_id(self.db, conversation_id)
        timestamp_after = after['last_message_at']
        assert timestamp_after is not None, "Timestamp should be set"
        if timestamp_before:
            assert timestamp_after > timestamp_before, "Timestamp should be newer"
        print("Timestamp successfully updated")
        
        invalid = conversationFunctions.update_conversation_timestamp(self.db, 99999)
        assert invalid is False, "Should return False for invalid ID"
        print("Correctly handles invalid conversation ID")

    def cleanup(self):
        print("Cleaning up conversation, pipeline, and user test data...")
        
        deleted_count = 0
        for user_id in self.test_user_ids:
            try:
                if userFunctions.delete_user_by_id(self.db, user_id):
                    deleted_count += 1
            except:
                pass
                
        print(f"Cleaned up {deleted_count}/{len(self.test_user_ids)} test users")
        self.db.close()

        self.test_conversation_ids.clear()
        self.test_user_ids.clear()
        self.test_general_conversation_ids.clear()
        self.test_pipeline_ids.clear()

if __name__ == "__main__":
    tester = TestConversationFunctionsComplete()
    tester.run_all_tests()
