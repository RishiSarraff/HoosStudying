import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, documentFunctions, pipelineFunctions, pipelineDocumentFunctions
import random

def get_db():
    db = localSession()
    return db

class TestPipelineDocumentFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_user_ids = []
        self.test_document_ids = []
        self.test_pipeline_ids = []
        self.test_chunk_ids = []

    def run_all_tests(self):
        print("Run ALL Pipeline Documents Function Tests")

        try:
            print("Create Test Pipeline Documents")
            self.setup_test_document_pipelines() 
            
            print("Test All Read Functions")

            self.test_add_document_to_pipeline()
            self.test_get_count_of_documents_by_pipeline()
            self.test_add_multiple_documents_to_pipeline()
            self.test_get_documents_in_pipeline()
            self.test_get_active_documents_in_pipeline()
            self.test_toggle_document_active_status()
            self.test_remove_document_from_pipeline()
            self.test_remove_all_documents_from_pipeline()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_document_pipelines(self):
        test_data = [
            ("Alice", "Johnson", f"alice.j{random.randint(1000,9999)}@test.com", 
             "ML Pipeline", "Machine Learning documents",
             [
                 ("neural_networks.pdf", "pdf"),
                 ("deep_learning.pdf", "pdf"),
                 ("tensorflow_guide.docx", "docx")
             ]),
            ("Bob", "Smith", f"bob.s{random.randint(1000,9999)}@test.com",
             "Web Dev Pipeline", "Web development resources",
             [
                 ("react_basics.pdf", "pdf"),
                 ("node_tutorial.pdf", "pdf"),
                 ("javascript_guide.txt", "txt"),
                 ("css_tricks.pdf", "pdf")
             ]),
            ("Carol", "Williams", f"carol.w{random.randint(1000,9999)}@test.com",
             "Data Science Pipeline", "Data science materials",
             [
                 ("pandas_tutorial.pdf", "pdf"),
                 ("numpy_guide.pdf", "pdf")
             ])
        ]

        for first_name, last_name, email, pipeline_name, pipeline_desc, documents in test_data:
            # Create user
            user = userFunctions.create_user(
                self.db,
                first_name,
                last_name,
                email
            )
            user_id = user['user_id']
            self.test_user_ids.append(user_id)
            print(f"Created user: {user_id}")

            pipeline = pipelineFunctions.create_pipeline(
                self.db,
                user_id=user_id,
                pipeline_name=pipeline_name,
                description=pipeline_desc
            )
            pipeline_id = pipeline['pipeline_id']
            self.test_pipeline_ids.append(pipeline_id)
            print(f"Created pipeline: {pipeline_id}")

            for file_name, file_type in documents:
                document = documentFunctions.create_document(
                    self.db,
                    user_id=user_id,
                    file_name=file_name,
                    file_type=file_type
                )
                document_id = document['document_id']
                self.test_document_ids.append(document_id)
                print(f"Created document: {document_id}")

        print(f"Setup complete: {len(self.test_user_ids)} users, {len(self.test_pipeline_ids)} pipelines, {len(self.test_document_ids)} documents")

    def test_add_document_to_pipeline(self):
        pipeline_id = self.test_pipeline_ids[0]
        document_id = self.test_document_ids[0]
        
        result = pipelineDocumentFunctions.add_document_to_pipeline(
            self.db,
            pipeline_id=pipeline_id,
            document_id=document_id,
            is_active=True
        )
        
        assert result is not None, "Failed to add document to pipeline"
        assert 'pipeline_id' in result, "Missing pipeline_id in result"
        assert 'document_id' in result, "Missing document_id in result"
        assert result['pipeline_id'] == pipeline_id, "Wrong pipeline_id"
        assert result['document_id'] == document_id, "Wrong document_id"
        assert result['is_active'] == True, "Document should be active by default"
        
        print(f"Added document {document_id} to pipeline {pipeline_id}")
        
        try:
            duplicate_result = pipelineDocumentFunctions.add_document_to_pipeline(
                self.db,
                pipeline_id=pipeline_id,
                document_id=document_id
            )
            print("Checked for duplicate addition gracefully")
        except:
            print("Prevented duplicate addition")

    def test_get_count_of_documents_by_pipeline(self):
        pipeline_id = self.test_pipeline_ids[1]
        
        docs_to_add = self.test_document_ids[3:6]
        for doc_id in docs_to_add:
            pipelineDocumentFunctions.add_document_to_pipeline(
                self.db,
                pipeline_id=pipeline_id,
                document_id=doc_id,
                is_active=True
            )
        
        count = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            self.db,
            pipeline_id
        )
        
        assert count == len(docs_to_add), f"Expected {len(docs_to_add)} documents, got {count}"
        print(f"Retrieved {count} documents in pipeline {pipeline_id}")
        
        empty_pipeline_id = self.test_pipeline_ids[2]
        empty_count = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            self.db,
            empty_pipeline_id
        )
        assert empty_count == 0, f"Expected 0 documents in empty pipeline, got {empty_count}"
        print(f"Retrieved 0 for empty pipeline")

    def test_add_multiple_documents_to_pipeline(self):
        pipeline_id = self.test_pipeline_ids[2]
        document_ids = self.test_document_ids[6:9] 
        
        results = pipelineDocumentFunctions.add_multiple_documents_to_pipeline(
            self.db,
            pipeline_id=pipeline_id,
            document_ids=document_ids
        )
        
        assert results is not None, "Failed to add multiple documents"
        assert isinstance(results, list), "Results should be a list"
        assert len(results) == len(document_ids), f"Expected {len(document_ids)} results, got {len(results)}"
        
        for result in results:
            assert 'pipeline_id' in result, "Missing pipeline_id"
            assert 'document_id' in result, "Missing document_id"
            assert result['pipeline_id'] == pipeline_id, "Wrong pipeline_id"
            assert result['is_active'] == True, "Document should be active"
        
        print(f"Retrieved {len(results)} documents to pipeline {pipeline_id}")

    def test_get_documents_in_pipeline(self):
        pipeline_id = self.test_pipeline_ids[1]
        
        documents = pipelineDocumentFunctions.get_documents_in_pipeline(
            self.db,
            pipeline_id
        )
        
        assert documents is not None, "Failed to get documents"
        assert isinstance(documents, list), "Documents should be a list"
        assert len(documents) > 0, "Should have documents in pipeline"

        for doc in documents:
            assert 'document_id' in doc, "Missing document_id"
            assert 'file_name' in doc, "Missing file_name"
            assert 'file_type' in doc, "Missing file_type"
            assert 'upload_date' in doc, "Missing upload_date"
            assert 'is_active' in doc, "Missing is_active status"
            assert 'added_at' in doc, "Missing added_at timestamp"
        
        invalid_docs = pipelineDocumentFunctions.get_documents_in_pipeline(
            self.db,
            99999
        )
        assert invalid_docs == [] or invalid_docs is None, "Should return empty for invalid pipeline"
        print("Handled invalid pipeline_id")

    def test_get_active_documents_in_pipeline(self):
        pipeline_id = self.test_pipeline_ids[1]
        
        active_documents = pipelineDocumentFunctions.get_active_documents_in_pipeline(
            self.db,
            pipeline_id
        )
        
        assert active_documents is not None, "Failed to get active documents"
        assert isinstance(active_documents, list), "Active documents should be a list"
        
        
        for doc in active_documents:
            assert doc['is_active'] == True, f"Document {doc['document_id']} should be active"
            assert 'document_id' in doc, "Missing document_id"
            assert 'file_name' in doc, "Missing file_name"
        
        print(f"Retrieved {len(active_documents)} active documents from pipeline {pipeline_id}")

    def test_toggle_document_active_status(self):
        pipeline_id = self.test_pipeline_ids[1]
        document_id = self.test_document_ids[3]
        
        try:
            pipelineDocumentFunctions.add_document_to_pipeline(
                self.db,
                pipeline_id=pipeline_id,
                document_id=document_id,
                is_active=True
            )
        except:
            pass
        
        docs = pipelineDocumentFunctions.get_documents_in_pipeline(self.db, pipeline_id)
        initial_doc = next((d for d in docs if d['document_id'] == document_id), None)
        
        assert initial_doc is not None, f"Document {document_id} should be in pipeline {pipeline_id}"
        
        result = pipelineDocumentFunctions.toggle_document_active_status(
            self.db,
            pipeline_id=pipeline_id,
            document_id=document_id,
            is_active=False
        )
        
        assert result is not None, "Failed to toggle status to inactive"
        assert result['is_active'] == False, "Document should be inactive"
        print(f"Toggled document {document_id} to inactive")
        
        result = pipelineDocumentFunctions.toggle_document_active_status(
            self.db,
            pipeline_id=pipeline_id,
            document_id=document_id,
            is_active=True
        )
        
        assert result is not None, "Failed to toggle status to active"
        assert result['is_active'] == True, "Document should be active"
        print(f"Toggled document {document_id} back to active")

    def test_remove_document_from_pipeline(self):
        pipeline_id = self.test_pipeline_ids[1]
        document_id = self.test_document_ids[4]
        
        count_before = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            self.db,
            pipeline_id
        )
        
        result = pipelineDocumentFunctions.remove_document_from_pipeline(
            self.db,
            pipeline_id=pipeline_id,
            document_id=document_id
        )
        
        assert result == True, "Failed to remove document from pipeline"
        
        count_after = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            self.db,
            pipeline_id
        )
        
        assert count_after == count_before - 1, "Document count should decrease by 1"
        print(f"Removed document {document_id} from pipeline {pipeline_id}")
        
        result = pipelineDocumentFunctions.remove_document_from_pipeline(
            self.db,
            pipeline_id=pipeline_id,
            document_id=99999
        )
        assert result == False or result is None, "Should handle non-existent document gracefully"
        print("Accurately handled non-existent/invalid document removal")

    def test_remove_all_documents_from_pipeline(self):
        pipeline_id = self.test_pipeline_ids[2]
        
        count_before = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            self.db,
            pipeline_id
        )
        
        assert count_before > 0, "Pipeline should have documents for this test"
        
        result = pipelineDocumentFunctions.remove_all_documents_from_pipeline(
            self.db,
            pipeline_id
        )
        
        assert result >= 0, "Failed to remove all documents"
        
        count_after = pipelineDocumentFunctions.get_count_of_documents_by_pipeline(
            self.db,
            pipeline_id
        )
        
        assert count_after == 0, f"Expected 0 documents, found {count_after}"
        print(f"Deleted {count_before} documents from pipeline {pipeline_id}")

    def cleanup(self):
        print("Cleaning up test document data and user data...")

        deleted_users = 0

        for user_id in self.test_user_ids:
            try:
                if userFunctions.delete_user_by_id(self.db, user_id):
                    deleted_users += 1
            except Exception as e:
                print(f"Error deleting user {user_id}: {e}")

        print(f"Removed {deleted_users}/{len(self.test_user_ids)} users")

        self.test_user_ids.clear()
        self.test_document_ids.clear()
        self.test_chunk_ids.clear()
        self.test_pipeline_ids.clear()

        self.db.close()

if __name__ == "__main__":
    tester = TestPipelineDocumentFunctionsComplete()
    tester.run_all_tests()