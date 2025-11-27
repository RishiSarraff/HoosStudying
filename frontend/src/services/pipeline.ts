import type { MySQLPipeline } from "../types"
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