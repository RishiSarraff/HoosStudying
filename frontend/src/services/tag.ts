import axios from "axios";
import type { MySQLTag, MySQLMessage } from "../types";

export async function createCustomTag(
    token: string,
    name: string,
    color: string,
    user_id: number, 
    pipeline_id: number,
  ): Promise<MySQLTag> {
    const response = await axios.post(
      `http://localhost:8000/api/tag/create-custom-tag/`,
      {token, name, color, user_id, pipeline_id},
      {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
      }
    );
    return response.data;
  }