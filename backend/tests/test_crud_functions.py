import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from ..app.crudFunctions import (
    userFunctions,
    pipelineFunctions,
    documentFunctions,
    conversationFunctions,
    pipelineTagFunctions,
    pipelineDocumentFunctions,
    tagFunctions,
    userFunctions
)

from ..app.database import get_db

from ..app.models import SenderType

class testCRUDFunctions:
    def __init__(self):
        self.db = next(get_db())
        self.test_user_id = None
        self.test_pipeline_id = None
        self.test_document_id = None
        self.test_conversation_id = None
        self.test_message_id = None
        self.test_tag_id = None

    def run_all_tests(self):
        print("STARTING ALL TESTS:")

        try:
            self.test_user_functions()
            self.test_pipeline_functions()
            self.test_document_functions()
            self.test_conversation_functions()
            self.test_message_functions()
            self.test_tag_functions()
            self.test_pipeline_document_functions()
            self.test_pipeline_tag_functions()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def test_user_functions(self):
        print("Testing User CRUD Operations")

        #Create Functions:
        user = userFunctions.create_user(
            self.db,
            "Test",
            "User",
            f"test_{os.urandom(4).hex()}@test.com"
        )

        assert user is not None, "Failed to create User"

        self.test_user_id = user['user_id']

        print(f"Created the test user with {self.test_user_id}")

        #READ Functions:
        fetched_user = userFunctions.get_user_by_id(
            self.db,
            self.test_user_id
        )

        assert fetched_user is not None, "Failed to get User"
        assert fetched_user['first_name'] == "Test", "User First Name Mismatch"
        assert fetched_user['last_name'] == "User", "User Last Name Mismatch"
        print(f"Retrieved user {fetched_user['first_name']} {fetched_user['last_name']}")

        invalid_user = userFunctions.get_user_by_id(
            self.db,
            999999
        )

        fetched_user = userFunctions.get_all_users()
        
        fetched_user = userFunctions.get_user_by_email()
        fetched_user = userFunctions.get_user_by_name()
        fetched_user = userFunctions.get_users_name()
        fetched_user = userFunctions.get_user_count()


        #UPDATE Functions:
        updated_user = userFunctions.update_user()


        #DELETE Functions:
        deleted_user = userFunctions.delete_user_by_id()




