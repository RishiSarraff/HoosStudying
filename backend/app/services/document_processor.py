### This processor handles file upload, text extraction, chunking, and storage

from typing import List, Dict, Any, Optional, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
from langdetect import detect, LangDetectException
import hashlib
import mimetypes
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import credentials, storage
from app.crudFunctions import documentFunctions, pipelineDocumentFunctions
import os
from datetime import datetime, timedelta

firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')

class DocumentProcessor:

    ## CONSTRUCTOR
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': firebase_storage_bucket
            })

        self.bucket = storage.bucket()
    
    ## EXTRACT TEXT FROM PDF FILE
    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                fullText = ""
                language = ""

                for page in pdf_reader.pages:
                    fullText += page.extract_text() + "\n"

                fullText = fullText.strip()

                try:
                    language = detect(fullText) if fullText.strip() else 'unknown'
                except LangDetectException:
                    language = 'unknown'

                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'word_count': len(fullText.split()),
                    'language': language, 
                    'encoding': 'utf-8',
                    'file_size': os.path.getsize(file_path)
                }

                return fullText, metadata

        except Exception as e:
            raise e
        
    ## EXTRACT TEXT FROM DOCX FILE
    def extract_text_from_docx(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        try:
            doc = DocxDocument(file_path)

            fullText = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            fullText = fullText.strip()

            try:
                language = detect(fullText) if fullText.strip() else 'unknown'
            except LangDetectException:
                language = 'unknown'
            
            metadata = {
                'page_count': None,
                'word_count': len(fullText.split()),
                'language': language,
                'encoding': 'utf-8',
                'file_size': os.path.getsize(file_path)
            }

            return fullText, metadata
        
        except Exception as e:
            raise RuntimeError(f"Error extracting text from DOCX ({file_path}): {e}") from e

    ## EXTRACT TEXT FROM TXT FILE
    def extract_text_from_txt(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        possible_encodings = ['utf-8', 'latin-1', 'utf-16', 'cp1252', 'iso-8859-1']

        for current_encoding in possible_encodings:
            try:
                with open(file_path, 'r', encoding=current_encoding) as file:
                    fullText = file.read().strip()
                
                try:
                    language = detect(fullText) if fullText.strip() else 'unknown'
                except LangDetectException:
                    language = 'unknown'

                metadata = {
                    'page_count': None,
                    'word_count': len(fullText.split()),
                    'language': language,
                    'encoding': current_encoding,
                    'file_size': os.path.getsize(file_path)
                }

                return fullText, metadata
            
            except UnicodeDecodeError:
                continue

        raise Exception("Could not decode text file with any known encoding")
    

    ## EXTRACT TEXT FOR DOCUMENT_PROCESSOR
    def extract_text(self, file_path: str, file_type: str) -> List[str]:

        file_type = file_type.lower()

        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            return self.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        

    ## NEED CHUNK_TEXT FOR DOCUMENT_CHUNK
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        if not text:
            return []
        
        listOfDelimiters = ['. ', '.\n', '! ', '!\n', '? ', '?\n', '; ', ';\n', '\n']
        
        chunks = []
        start = 0
        text = text.strip()
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            
            if end < text_length:
                chunk_segment = text[start:end]

                for eachDelimiter in listOfDelimiters:
                    indexOfLastDelimiter = chunk_segment.rfind(eachDelimiter)

                    if indexOfLastDelimiter > chunk_size - 100:
                        end = start + indexOfLastDelimiter + len(eachDelimiter)
                        break
                
                else:
                    last_space = chunk_segment.rfind(' ')
                    if last_space > 0:
                        end = start + last_space

            chunk = text[start:end].strip()
        
            if chunk:
                chunks.append(chunk)

            start = end - overlap

            if start <= (start - overlap):
                start = end
            
        return chunks

    ## NEED CHECK TYPE FOR DOCUMENT_METADATA
    def calculate_checksum(self, file_path: str) -> str:
        hash_md5 = hashlib.md5()

        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    ## NEED MIME TYPE FOR DOCUMENT_METADATA
    def get_mime_type(self, file_path: str, file_type: str) -> str:
        mime_type = mimetypes.guess_type(file_path)[0]

        if not mime_type:
            mime_types = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'doc': 'application/msword',
                'txt': 'text/plain'
            }

            mime_type = mime_types.get(file_type.lower(), 'application/octet-stream')

        return mime_type

    ## GET FILE TYPE FOR THE PROCESSING FUNCTION
    def get_file_type_from_path(self, file_path: str) -> str:
        _, fileType = os.path.splitext(file_path)
        return fileType[1:].lower()

    ## UPLOAD TO FIREBASE STORAGE
    def upload_to_firebase(self, file_path: str, user_id: int, document_id: int, file_name: str) -> Tuple[str, str]:
        try:

            storage_path = f"users/{user_id}/documents/{document_id}/{file_name}"

            blob = self.bucket.blob(storage_path)
            blob.upload_from_filename(file_path)

            download_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET"
            )

            return storage_path, download_url

        except Exception as e:
            raise Exception(f"Error uploading to Firebase: {str(e)}")
        
    ## PROCESS THE DOCUMENT AND SPREAD ACROSS TABLES/DATABASES:

    def process_document(self, 
                         db: Session, 
                         file_path: str, 
                         file_name: str,
                         user_id: int,
                         pipeline_id: int,
                         chunk_size: int = 500,
                         overlap: int = 100
    ) -> Dict[str, Any]:
        # Complete process of document processing:
        # 1) 

        try:
            # Step 1 get the file type
            file_type = self.get_file_type_from_path(file_name)
            print(f"Processing file: {file_name}, of type: {file_type}")

            # Step 2, Extract text, "metadata" using the file type
            fullText, extracted_metadata = self.extract_text(file_path, file_type)

            if not fullText:
                raise ValueError("No text could be extracted from the document")

            # Step 3, Chunk the Text into pieces
            text_chunks = self.chunk_text(fullText, chunk_size, overlap)

            if not text_chunks:
                raise ValueError("No chunks could be created from the text")
            
            # Step 4, Create Document Entry, so insert the document using the trigger and function from crudFunctions/documentFunctions.py
            document_record = documentFunctions.create_document(
                db=db,
                user_id=user_id,
                file_name=file_name,
                file_type=file_type
            )

            document_id = document_record['document_id']
            # when we create a document and associate it with a specific pipeline id and user id, we have to lead the cascasde of it.
            print(f"Created Document record with ID: {document_id}")

            # Step 5, Upload document to firebase storage
            storage_path, download_url = self.upload_to_firebase(
                file_path=file_path,
                user_id=user_id,
                document_id=document_id,
                file_name=file_name
            )
            print(f"Uploaded document ({document_id}) to Firebase Storage at path: {storage_path}")

            # Step 6, Calculate checksum and mime type for metadata
            checksum = self.calculate_checksum(file_path)
            mime_type = self.get_mime_type(file_path, file_type)

            # Step 7, Create Document Metadata Entry 
            documentFunctions.create_document_metadata(
                db=db,
                document_id=document_id,
                file_size=extracted_metadata.get('file_size'),
                page_count=extracted_metadata.get('page_count') if file_type == 'pdf' else None,
                word_count=extracted_metadata.get('word_count'),
                language=extracted_metadata.get('language'),
                encoding=extracted_metadata.get('encoding'),
                firebase_storage_path=storage_path,
                checksum=checksum,
                mime_type=mime_type
            )

            # Step 8: Document Chunks Creation
            created_chunks = documentFunctions.create_document_chunks_batch(
                db=db, 
                document_id=document_id,
                chunks=text_chunks
            )

            # Step 9: Link document to the specific pipeline:
            pipelineDocumentFunctions.add_document_to_pipeline(
                db=db,
                pipeline_id=pipeline_id,
                document_id=document_id,
                is_active=True
            )

            # Return Summary:

            return{
                "success": True,
                "document_id": document_id,
                "file_name": file_name,
                "file_type": file_type,
                "word_count": extracted_metadata['word_count'],
                "page_count": extracted_metadata.get('page_count'),
                "language": extracted_metadata['language'],
                "chunk_count": len(created_chunks),
                "file_size": extracted_metadata['file_size'],
                "firebase_storage_path": storage_path,
                "firebase_download_url": download_url,
                "checksum": checksum,
                "chunks": [{"chunk_id": c['chunk_id'], "chunk_index": c['chunk_index']} for c in created_chunks]
            }

        except Exception as e:
            print(f"Error processing document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file_name": file_name
            }

    

    



