import axios from "axios";

export interface SourceInfo {
  file_name: string;
  chunk_index: number;
  similarity_score: number;
  text_preview: string;
}

export interface ChatResponse {
  message_id: number;
  conversation_id: number;
  response: string;
  sources: SourceInfo[];
  has_context: boolean;
}

export interface NewConversationResponse {
  conversation_id: number;
  pipeline_id: number;
  created_at: string;
}

export async function sendChatMessage(
  token: string,
  message_text: string,
  conversation_id?: number,
  pipeline_id?: number
): Promise<ChatResponse> {
  const response = await axios.post(
    `http://localhost:8000/api/chat/message`,
    {
      message_text,
      conversation_id,
      pipeline_id,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}

export async function createNewConversation(
  token: string,
  pipeline_id: number
): Promise<NewConversationResponse> {
  const response = await axios.post(
    `http://localhost:8000/api/chat/conversation/${pipeline_id}/new`,
    {},
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
}
