import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import localSession
from app.crudFunctions import userFunctions, pipelineFunctions, documentFunctions
import random

def get_db():
    db = localSession()
    return db

class TestDocumentFunctionsComplete:
    def __init__(self):
        self.db = get_db()
        self.test_user_ids = []
        self.test_document_ids = []
        self.test_metadata_ids = []
        self.test_chunk_ids = []

    def run_all_tests(self):
        print("Run ALL Document Function Tests")

        try:
            print("Create Test Documents")
            self.setup_test_documents() 
            ## here we have 3 creates:
            ### 1) Create Document
            ### 2) Create Document Metadata
            ### 3) Create Document Chunks Batch
            
            print("Test All Read Functions")
            self.test_get_document_by_document_id()
            self.test_get_documents_by_user_id()
            self.test_get_document_file_info()
            self.test_get_all_chunks_by_user()
            self.test_get_chunk_by_id()
            self.test_get_chunks_by_document()
            self.test_get_chunks_by_document_and_user()
            self.test_get_chunks_from_list()

            self.test_delete_document_by_id()

            self.test_delete_all_documents_for_user()
        except Exception as e:
            print(f"TEST FAILED: {e}")
            raise
        finally:
            self.cleanup()

    def setup_test_documents(self):
        test_data = [
            {
                "user": ("John", "Doe", f"john.doe{random.randint(1000,9999)}@test.com"),
                "documents": [
                    ("Lecture_Notes.pdf", "pdf", 3),  # Structure for this is the file name, then file type, and number of chunks
                    ("Assignment_1.docx", "docx", 2),
                ]
            },
            {
                "user": ("Jane", "Smith", f"jane.smith{random.randint(1000,9999)}@test.com"),
                "documents": [
                    ("Research_Paper.pdf", "pdf", 5),
                    ("Study_Guide.txt", "txt", 2),
                    ("Project_Proposal.docx", "docx", 4),
                ]
            },
            {
                "user": ("Bob", "Johnson", f"bob.j{random.randint(1000,9999)}@test.com"),
                "documents": [
                    ("Database_Notes.pdf", "pdf", 3),
                ]
            },
        ]

        # For each user we will attach documents
        for user_doc_information in test_data:
            first_name, last_name, email = user_doc_information['user']

            user = userFunctions.create_user(self.db, first_name, last_name, email)
            user_id = user['user_id']
            self.test_user_ids.append(user_id)
            print(f"Created User: {user_id}")

            # for each created user get their documents and create 3 things:
            # Create the document, document_metadata, and document_chunks
            for file_name, file_type, num_chunks in user_doc_information['documents']:
                document = documentFunctions.create_document(
                    self.db,
                    user_id, 
                    file_name, 
                    file_type
                )

                document_id = document['document_id']
                self.test_document_ids.append(document_id)

                document_metadata = documentFunctions.create_document_metadata(
                    self.db,
                    document_id=document_id,
                    file_size=100000 + random.randint(0, 50000),
                    page_count=random.randint(5, 50),
                    word_count=random.randint(500, 5000),
                    language="en",
                    encoding="UTF-8",
                    firebase_storage_path=f"users/{user_id}/documents/{document_id}.{file_type}",
                    checksum=f"checksum_{document_id}_{random.randint(1000,9999)}",
                    mime_type=self.get_mime_type_helper(file_type)
                )
                self.test_metadata_ids.append(document_metadata['metadata_id'])
                print(f"    Created metadata for document {document_id}")

                chunks_data = [
                {
                    "chunk_text": f"This is chunk {i} of {file_name}. " + 
                                  f"Content here for testing purposes. " * 5,
                    "chunk_index": i
                }
                for i in range(num_chunks)
                ]

                created_chunks = documentFunctions.create_document_chunks_batch(
                    self.db,
                    document_id,
                    chunks=chunks_data
                )

                for chunk in created_chunks:
                    self.test_chunk_ids.append(chunk['chunk_id'])
                print(f"    Created {len(created_chunks)} chunks for document {document_id}")

        print(f"\nTest Setup complete:")
        print(f"  Users: {len(self.test_user_ids)}")
        print(f"  Documents: {len(self.test_document_ids)}")
        print(f"  Metadata: {len(self.test_metadata_ids)}")
        print(f"  Chunks: {len(self.test_chunk_ids)}\n")

    def get_mime_type_helper(self, file_type: str) -> str:
        """Helper to get MIME type from file extension"""
        mime_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "doc": "application/msword",
        }
        return mime_types.get(file_type, "application/octet-stream")

    def test_get_document_by_document_id(self):
        document_id = self.test_document_ids[0]
        
        fetched_document = documentFunctions.get_document_by_document_id(self.db, document_id)

        assert fetched_document is not None, "Failed to get Document"
        assert fetched_document['file_name'] == "Lecture_Notes.pdf"
        assert fetched_document['file_type'] == "pdf"
        print(f"Retrieved pipeline {fetched_document['file_name']} from user User ID: {fetched_document['user_id']}")

        invalid_document = documentFunctions.get_document_by_document_id(self.db, 999999)
        assert invalid_document is None, "Should return None for invalid document Id"
        print("Correctly returns None for invalid document Id")

    def test_get_documents_by_user_id(self):
        user_id = self.test_user_ids[0]

        fetched_documents = documentFunctions.get_documents_by_user_id(self.db, user_id)
        assert fetched_documents is not None, "Failed to failed documents"
        assert isinstance(fetched_documents, list), "Should return a list of fetched_documents"
        assert len(fetched_documents) >= 2, f"User 1 should have at least 2 documents, found {len(fetched_documents)}"
        print(f"User {user_id} has {len(fetched_documents)} document(s)")

        for each_document in fetched_documents:
            assert each_document is not None, f"Failed to get user {user_id}'s documents"
            assert each_document['user_id'] == user_id, f"Incorrect User id for document {each_document['document_id']}"

            assert 'document_id' in each_document, "Document missing document_id"
            assert 'file_name' in each_document, "Document missing file_name"
            assert 'file_type' in each_document, "Document missing file_type"
            assert 'upload_date' in each_document, "Document missing upload_date"

        invalid_documents = documentFunctions.get_documents_by_user_id(self.db, 999999)
        assert invalid_documents == [] or invalid_documents is None, \
            "Should return empty list or None for invalid user ID"
        print("Correctly returns empty result for invalid user ID")

    def test_get_document_file_info(self):
        metadata_id = self.test_metadata_ids[0]
        document_id = self.test_document_ids[0]

        fetched_metadata = documentFunctions.get_document_metadata_by_document_ids(self.db, document_id)
        assert fetched_metadata is not None, f"Failed to Retrieve Metadata for document {document_id}"
        assert fetched_metadata['document_id'] == document_id, "Document Id does not match"
        assert fetched_metadata['metadata_id'] == metadata_id, "Metadata Id does not match"

        required_fields = [
            'metadata_id', 'document_id', 'file_size', 'page_count', 
            'word_count', 'language', 'encoding', 'firebase_storage_path',
            'checksum', 'mime_type', 'created_at'
        ]
        for field in required_fields:
            assert field in fetched_metadata, f"Metadata missing required field: {field}"
        print("All required metadata fields present")

        assert fetched_metadata['file_size'] > 0, "Invalid file_size"
        assert fetched_metadata['page_count'] > 0, "Invalid page_count"
        assert fetched_metadata['word_count'] > 0, "Invalid word_count"
        assert fetched_metadata['language'] == "en", "Language mismatch"
        assert fetched_metadata['encoding'] == "UTF-8", "Encoding mismatch"
        assert fetched_metadata['mime_type'] == "application/pdf", "MIME type mismatch"

        print(f"Retrieved valid metadata for document {document_id}")

        invalid_metadata = documentFunctions.get_document_metadata_by_document_ids(self.db, 999999)
        assert invalid_metadata is None, "Should return None for invalid document ID"
        print("Correctly returns None for invalid document ID")

    def test_get_all_chunks_by_user(self):
        user_id = self.test_user_ids[0]

        fetched_chunks = documentFunctions.get_all_chunks_by_user(self.db, user_id)
        assert fetched_chunks is not None, "Failed to failed document chunks"
        assert isinstance(fetched_chunks, list), "Should return a list of fetched chunks"
        assert len(fetched_chunks) >= 1, f"User 1 should have at least 1 document chunks, found {len(fetched_chunks)}"
        print(f"User {user_id} has {len(fetched_chunks)} chunk(s)")

        user_documents = documentFunctions.get_documents_by_user_id(self.db, user_id)
        user_document_ids = set(document['document_id'] for document in user_documents)

        for chunk in fetched_chunks:
            assert chunk is not None, f"Failed to get user {user_id}'s document chunks"

            assert 'chunk_id' in chunk, "Chunk missing chunk_id"
            assert 'document_id' in chunk, "Chunk missing document_id"
            assert 'chunk_text' in chunk, "Chunk missing chunk_text"
            assert 'chunk_index' in chunk, "Chunk missing chunk_index"
            
            assert chunk['document_id'] in user_document_ids, \
                f"Chunk {chunk['chunk_id']} belongs to document {chunk['document_id']} which doesn't belong to user {user_id}"
            
            assert chunk['chunk_index'] >= 0, "chunk_index should be positive or 0"
            
            assert chunk['chunk_text'], "chunk_text should not be empty"

        invalid_documents = documentFunctions.get_all_chunks_by_user(self.db, 999999)
        assert invalid_documents == [] or invalid_documents is None, \
            "Should return empty list or None for invalid user ID"
        print("Correctly returns empty result for invalid user ID")

    def test_get_chunk_by_id(self):
        chunk_id = self.test_chunk_ids[0]
        
        fetched_chunk = documentFunctions.get_chunk_by_id(self.db, chunk_id)
        
        assert fetched_chunk is not None, f"Failed to get chunk {chunk_id}"
        assert fetched_chunk['chunk_id'] == chunk_id, "Chunk Id mismatch"
        print(f"Retrieved chunk {chunk_id}")
        
        assert 'document_id' in fetched_chunk, "Chunk missing document_id"
        assert 'chunk_text' in fetched_chunk, "Chunk missing chunk_text"
        assert 'chunk_index' in fetched_chunk, "Chunk missing chunk_index"
        assert 'created_at' in fetched_chunk, "Chunk missing created_at"
        
        assert fetched_chunk['document_id'] == self.test_document_ids[0], \
            "Chunk should belong to first document"
        assert fetched_chunk['chunk_index'] == 0, "First chunk should have index 0"
        assert "Lecture_Notes.pdf" in fetched_chunk['chunk_text'], \
            "Chunk text should reference the document name"
        print("Chunk has all required fields and correct values")
        
        invalid_chunk = documentFunctions.get_chunk_by_id(self.db, 999999)
        assert invalid_chunk is None, "Should return None for invalid chunk ID"
        print("Correctly returns None for invalid chunk ID")

    def test_get_chunks_by_document(self):
        document_id = self.test_document_ids[0]

        chunks_of_document = documentFunctions.get_chunks_by_document(self.db, document_id)
        assert chunks_of_document is not None, f"Failed to failed document chunks from Document {document_id}"
        assert isinstance(chunks_of_document, list), f"Should return a list of fetched chunks from Document {document_id}"
        assert len(chunks_of_document) >= 1, f"Document {document_id} should have at least 1 document chunks, found {len(chunks_of_document)}"
        print(f"Document {document_id} has {len(chunks_of_document)} document(s)")

        for chunk in chunks_of_document:
            assert chunk['document_id'] == document_id, \
                f"Chunk has wrong document_id"
            assert 'chunk_text' in chunk, "Chunk missing chunk_text"
            assert 'chunk_index' in chunk, "Chunk missing chunk_index"
            assert chunk['chunk_index'] >= 0, "chunk_index should be positive"

        print(f"All chunks correctly belong to document {document_id}")

        chunk_indices = [chunk['chunk_index'] for chunk in chunks_of_document]
        assert chunk_indices == [0, 1, 2], f"Chunks should be indexed 0-2, got {chunk_indices}"
        print("Chunks are correctly ordered")

        invalid_document_chunks = documentFunctions.get_chunks_by_document(self.db, 999999)
        assert invalid_document_chunks == [] or invalid_document_chunks is None, \
            "Should return empty list or None for invalid document chunk IDs"
        print("Correctly returns empty result for invalid document chunk IDs")

    def test_get_chunks_by_document_and_user(self):
        document_id = self.test_document_ids[0]
        user_id = self.test_user_ids[0]

        chunks = documentFunctions.get_chunks_by_document_and_user(self.db, document_id, user_id)

        assert chunks is not None, f"Failed to failed chunks from Document {document_id} and User {user_id}"
        assert isinstance(chunks, list), f"Should return a list of chunks"
        assert len(chunks) == 3, f"Should have 3 chunks, found {len(chunks)}"
        print(f"Retrieved {len(chunks)} chunks for document {document_id} and user {user_id}")

        wrong_document_chunks = documentFunctions.get_chunks_by_document_and_user(
            self.db,
            document_id,
            self.test_user_ids[1]
        )
        assert wrong_document_chunks == [] or wrong_document_chunks is None, \
            "Should return empty list or None for invalid document chunk IDs from documents and users"
        print("Correctly returns empty result for invalid document chunk IDs from documents and users")
 
    def test_get_chunks_from_list(self):
        chunk_ids = self.test_chunk_ids[0:3]

        chunks = documentFunctions.get_chunks_from_list(self.db, chunk_ids)
        assert chunks is not None, f"Failed to get chunks"
        assert len(chunks) == 3, f"Should retrieve 3 chunks"

        retrieved_chunks = set(chunk['chunk_id'] for chunk in chunks) 
        expected_chunks = set(chunk_ids)

        assert retrieved_chunks == expected_chunks, "Retrieved wrong chunks"
        print(f"Successfully retrieved {len(chunks)} chunks by ID list")

        empty = documentFunctions.get_chunks_from_list(self.db, [])
        assert empty == [] or empty is None, "Empty list should return empty"

        invalid = documentFunctions.get_chunks_from_list(self.db, [999999])
        assert invalid == [] or invalid is None, "Invalid IDs should return empty"
        print("Correctly handles empty and invalid inputs")

    def test_delete_document_by_id(self):
        pass

    def test_delete_all_documents_for_user(self):
        pass

    def cleanup(self):
        print("Cleaning up test document data and user data...")

        for user_id in self.test_user_ids:
            try:
                userFunctions.delete_user_by_id(self.db, user_id)
                print(f"Deleted user {user_id}")
            except Exception as e:
                print(f"Error deleting user {user_id}: {e}")

        self.test_user_ids.clear()
        self.test_document_ids.clear()
        self.test_chunk_ids.clear()
        self.test_metadata_ids.clear()

if __name__ == "__main__":
    tester = TestDocumentFunctionsComplete()
    tester.run_all_tests()