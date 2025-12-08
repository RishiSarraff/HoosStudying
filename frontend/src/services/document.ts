import axios from 'axios';
import {type PipelineDocument, type DocumentMetadata} from "../types/index"
import { getStorage, ref, getDownloadURL } from 'firebase/storage';
import { getAuth } from 'firebase/auth'


export async function getPipelineDocuments(token: string, pipeline_id: number): Promise<PipelineDocument[]> {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/pipeline/${pipeline_id}/documents`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response.data.documents || [];
    } catch (error) {
      console.error("Error fetching documents:", error);
      return [];
    }
}

export async function getDocumentMetadata(
  token: string, 
  document_id: number
): Promise<DocumentMetadata>{
  try{
    const response = await axios.get(
      `http://localhost:8000/api/document/get-document-metadata/${document_id}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data;

  } catch (error) {
    console.error(`Error fetching document metadata for document ${document_id}:`, error);
    throw error;
  }
}

export async function getFirebaseDownloadUrl(firebase_storage_path: string) {
  try{
    const auth = getAuth();
    const currentUser = auth.currentUser;

    if(!currentUser){
      throw new Error("User not authenticated");
    }

    const storage = getStorage()
    const pathReference = ref(storage, firebase_storage_path);

    return await getDownloadURL(pathReference);
  } catch (error) {
    console.error("Error getting download URL:", error);
    throw error;
  }
}

export async function deleteDocumentFromPipeline(token: string, pipeline_id: number, document_id: number): Promise<boolean>{
  const response = await axios.delete(`http://localhost:8000/api/document/delete-document/${pipeline_id}/${document_id}`,
      {
          headers: {
              "Authorization": `Bearer ${token}`
          },
      }
  );

  return response.data.success || false;
}