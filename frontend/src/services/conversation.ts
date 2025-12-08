import axios from "axios";
import type { MySQLConversation, MySQLMessage } from "../types";

export async function getConversations(
    token: string, 
    pipeline_id: number
  ): Promise<MySQLConversation[]> {
    const response = await axios.get(
      `http://localhost:8000/api/conversation/pipeline/${pipeline_id}/conversations`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  }
  
  export async function getMessagesForConversation(
    token: string, 
    conversation_id: number
  ): Promise<MySQLMessage[]> {
    const response = await axios.get(
      `http://localhost:8000/api/conversation/conversation/${conversation_id}/messages`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  }

  export async function deleteConversation(
    token: string,
    conversation_id: number
  ): Promise<boolean> {
    try {
      const response = await axios.delete(
        `http://localhost:8000/api/chat/conversation/${conversation_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log(response)
      return response.status === 200;
    } catch (error) {
      console.error("Error deleting conversation:", error);
      return false;
    }
  }