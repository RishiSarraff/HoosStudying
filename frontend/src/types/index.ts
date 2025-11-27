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