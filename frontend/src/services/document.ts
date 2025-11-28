import axios from 'axios';
import {type PipelineDocument} from "../types/index"


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