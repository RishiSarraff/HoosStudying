import type { MySQLConversation, MySQLPipeline, MySQLTag } from "../types"
import axios from "axios";

export async function getDefaultUserPipeline(token: string): Promise<MySQLPipeline>{

    const response = await axios.post("http://localhost:8000/api/pipeline/get-default-pipeline",
        { token },
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return response.data;
}

export async function getAllNonDefaultPipelines(token: string): Promise<MySQLPipeline[]>{
    const response = await axios.post("http://localhost:8000/api/pipeline/get-non-default-pipelines",
        { token },
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return response.data;
}

export async function createNewPipeline(token: string, pipeline_name: string, pipeline_description: string, system_tag_id: number): Promise<MySQLPipeline>{
    const response = await axios.post("http://localhost:8000/api/pipeline/create-new-pipeline",
        {pipeline_name, pipeline_description, system_tag_id},
        {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
        }
    );

    return response.data;
}

export async function deletePipeline(token: string, pipeline_id: number): Promise<boolean>{
    const response = await axios.delete(`http://localhost:8000/api/pipeline/delete-pipeline/${pipeline_id}`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            },
        }
    );

    return response.data.success || true;
}

export async function editPipeline(token: string, pipeline_id: number, pipeline_name: string, pipeline_description: string, system_tag_id: number): Promise<MySQLPipeline>{
    const response = await axios.post("http://localhost:8000/api/pipeline/edit-pipeline",
        {pipeline_id, pipeline_name, pipeline_description, system_tag_id},
        {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
        }
    );

    return response.data;
}

export async function getSystemTags(token: string): Promise<MySQLTag[]>{
    const response = await axios.post("http://localhost:8000/api/tag/get-system-tags",
        { token },
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return response.data;
}