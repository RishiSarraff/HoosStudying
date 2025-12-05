import { type HsvaColor, type ColorResult } from '@uiw/color-convert';
import { type SwatchProps } from '@uiw/react-color-swatch';

export interface MySQLUser {
    user_id: number,
    firebase_uid: string,
    first_name: string,
    last_name: string,
    email: string,
    created_user: boolean
    needs_name: boolean
}

export interface UploadResponse{
    success: boolean;
    message: string;
    file_name: string;
    storage_path: string;
    download_url: string;
    chunk_count: number;
    embedding_count: number;
    vector_db_stored: boolean;
}

export interface UploadFormProps {
    user: MySQLUser;
    pipeline: MySQLPipeline;
    onUploadSuccess?: () => void
}

export interface NameModalProps {
    onSubmit: (first_name: string, last_name: string) => void;
}

export interface UserUpdateNameRequest {
    first_name: string;
    last_name?: string;
}

export interface GeneralChatContainerComponents {
    user: MySQLUser;
    isGeneral: boolean;
    pipeline?: MySQLPipeline;
}

export interface PipelineChatContainerComponents{
    user: MySQLUser;
    pipeline?: MySQLPipeline;
}

export interface MainScreenInputs {
    user: MySQLUser;
    pipeline: MySQLPipeline;
    listOfPipelines: MySQLPipeline[];
}

export interface MySQLPipeline {
    user_id: number,
    pipeline_id: number,
    pipeline_name: string,
    description: string,
    created_at: Date
    number_of_documents?: number
    pipeline_tags: MySQLTag[]
}

export interface NewPipelineModalProps{
    user_id: number
    open: boolean,
    onClose: () => void,
    onSubmit: (data: { pipelineName: string; pipelineDescription: string; user_id: number; system_tag_id: number}) => void,
    isEditMode: boolean
    pipeline?: MySQLPipeline
}

export interface MySQLTag{
    tag_id: number
    user_id?: number
    name: string
    color: string
    tag_type: string
    created_at: Date
}

export interface PipelineCardProps{
    pipeline_name: string
    pipeline_description: string
    number_of_documents?: number
    index: number
    pipeline_tags?: MySQLTag[]
    onDelete: () => void;
}

export interface AlertProps {
    message: string;
    open: boolean;
    onClose: () => void;
    severity?: 'success' | 'error' | 'warning' | 'info';
}

export interface PipelineContainerProps{
    user: MySQLUser;
    pipeline: MySQLPipeline;
    showChat: boolean;
    refreshKey?: number;
    onDocumentChange?: () => void;
}

export interface PipelineFilesContainerProps{
    user: MySQLUser;
    pipeline: MySQLPipeline;
    onDocumentChange?: () => void;
}

export interface ChatButtonProps{
    onClick: () => void;
    isActive: boolean;
}

export interface FileButtonProps{
    onClick: () => void;
    isActive: boolean;
}

export interface PipelineDocument {
    document_id: number;
    file_name: string;
    file_type: string;
    upload_date: string;
    is_active: boolean;
    added_at: string;
  }

export interface DocumentMetadata {
    metadata_id: number
    document_id: number
    file_size: number
    page_count: number
    word_count: number
    language: string
    encoding: string
    firebase_storage_path: string
    firebase_download_url: string
    checksum: string
    mime_type: string
    created_at: Date
}

export interface MySQLConversation{
    conversation_id: number
    user_id: number
    pipeline_id: number
    created_at: Date
    last_message_at: Date
    first_message_content?: string
}

export interface MySQLMessage{
    message_id: number
    conversation_id: number
    sender_type: string
    message_text: string
    timestamp: Date
}

export interface ConversationCardProps{
    conversation: MySQLConversation
    index: number
    onDelete: () => void;
    isActive: boolean
}

export interface ConversationViewProps {
  messages: MySQLMessage[];
  user: MySQLUser;
  onSendMessage: (messageText: string) => void;
}

export interface MessageBoxProps {
  message: MySQLMessage;
  userName?: string;
}

export interface PipelineTagProps{
    pipeline_tag: MySQLTag;
    index: number;
}

export interface CreateTagModalProps{
    pipeline_id: number,
    user_id: number,
    open: boolean,
    onClose: () => void,
    onSubmit: (data: { name: string; color: string; user_id: number; pipeline_id: number}) => void,
}

export interface ColorCircleProps extends Omit<SwatchProps, 'color' | 'onChange'> {
  color?: string | HsvaColor;
  onChange?: (color: ColorResult) => void;
  pointProps?: React.HTMLAttributes<HTMLDivElement>;
}