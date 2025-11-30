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

export interface ChatContainerComponents {
    user: MySQLUser;
    isGeneral: boolean;
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
}

export interface NewPipelineModalProps{
    user_id: number
    open: boolean
    onClose: () => void; 
    onSubmit: (data: { pipelineName: string; pipelineDescription: string; user_id: number }) => void;
}

export interface PipelineCardProps{
    pipeline_id: number
    pipeline_name: string
    pipeline_description: string
    number_of_documents?: number
    index: number
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